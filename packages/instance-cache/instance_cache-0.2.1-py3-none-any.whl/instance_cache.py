"""
为类实例方法提供实例级的结果缓存, 不影响类实例正常垃圾回收的装饰器

functools.lru_cache 和 cache 函数会保留对调用参数的强引用, 会影响这些参数正常的垃圾回收,
需要等待缓存超过 max_size 后弹出或手动调用 cache_clear, 比较麻烦
最常见的场景是作用在类实例方法上, 保留参数 self 的引用后会影响整个类实例的垃圾回收

>>> from functools import cache
>>>
>>> class MyClass:
...     def normal_method(self):
...         ...
...
...     @cache
...     def cached_method(self):
...         ...
...
...     def __del__(self):
...         print('delete!')
...
>>> MyClass().normal_method()  # 正常垃圾回收
delete!
>>> MyClass().cached_method()  # 无法进行垃圾回收
>>> MyClass().cached_method()
>>> MyClass().cached_method()
>>> MyClass.cached_method.cache_clear()  # 手动清理缓存才会回收
delete!
delete!
delete!

此处提供一个类实例方法的结果缓存装饰器, 提供实例级别的缓存 (为每个实例单独创建缓存空间)
通过将缓存内容作为每个类实例的属性进行存储 (类似于 functools.cached_property), 避免影响类实例 self 的正常垃圾回收
其他调用参数在类实例被回收后也会正常回收
"""

import functools
import inspect
import keyword
from collections import OrderedDict
from threading import Lock
from typing import Callable, NamedTuple, Optional, Sequence, Union
# import warnings  # 延迟导入


# python >= 3.7.0
__version__ = '0.2.1'

__all__ = ['CacheInfo', 'instance_cache']


class CacheInfo(NamedTuple):
    """缓存信息"""
    hits: int  # 缓存命中次数
    misses: int  # 缓存未命中次数
    maxsize: int  # 最大缓存数量
    currsize: int  # 当前缓存大小


class _LRUCache:
    """内部类, LRU 缓存"""
    __slots__ = ('cache', 'maxsize', 'hits', 'misses', 'lock')
    sentinel = object()

    def __init__(self, maxsize):
        """初始化方法"""
        self.cache = OrderedDict() if maxsize is not None else {}  # 缓存字典
        self.maxsize = maxsize  # 最大缓存数量
        self.hits = 0  # 统计命中缓存次数
        self.misses = 0  # 统计未命中缓存次数
        self.lock = Lock()  # 线程锁对象

    @property
    def currsize(self):
        """当前缓存大小"""
        return len(self.cache)

    def get(self, key):
        """获取缓存内容, 返回 _LRUCache.sentinel 时表示无缓存"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return _LRUCache.sentinel
            self.hits += 1
            if self.maxsize is not None:
                self.cache.move_to_end(key, last=True)
            value = self.cache[key]
            return value

    def put(self, key, value):
        """添加一条缓存"""
        with self.lock:
            if key in self.cache:  # 不更新缓存内容
                return
            self.cache[key] = value
            if self.maxsize is not None:
                if self.currsize > self.maxsize:
                    self.cache.popitem(last=False)

    def clear(self):
        """清空缓存并重置缓存信息"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def get_info(self):
        """获取缓存信息"""
        with self.lock:
            return CacheInfo(self.hits, self.misses, self.maxsize, self.currsize)


class _KeyMake:
    """内部类, 生成缓存键模板"""

    def make(self, instance, args, kwargs):
        """创建缓存键"""
        ...


class _KeyMakeNormal(_KeyMake):
    """内部类, 生成一般的缓存键"""
    __slots__ = ('cache_properties',)
    mark = object()

    def __init__(self, cache_properties):
        """初始化方法"""
        self.cache_properties = cache_properties  # 额外缓存的类属性名称

    def make(self, instance, args, kwargs):
        """创建缓存键"""
        key = []
        # 1. 加入类属性值
        if self.cache_properties:
            for item in self.cache_properties:
                key.append(getattr(instance, item, None))
        # 2. 加入调用参数
        if args:
            key.extend(args)
        if kwargs:
            key.append(_KeyMakeNormal.mark)  # 分隔 args 和 kwargs
            key.extend(kwargs.values())
            key.extend(kwargs)
        key = tuple(key)
        return key


class _KeyMakePrecise(_KeyMake):
    """内部类, 生成精确的缓存键"""
    __slots__ = ('cache_properties', 'signature', 'params', 'self_name', 'args_name', 'kwargs_name')
    mark = object()

    def __init__(self, cache_properties, signature):
        """初始化方法"""
        self.cache_properties = cache_properties  # 额外缓存的类属性名称
        self.signature = signature  # 类实例方法签名

        # 预解析函数签名信息
        self.params = {}  # 形参名称及默认值 (不包含 self)
        self.self_name = None  # 首位常规实例参数 (self) 的名称, 如果首位非 *args 的话
        self.args_name = None  # 可变位置参数 (*args) 名称
        self.kwargs_name = None  # 可变关键字参数 (**kwargs) 名称

        params = list(signature.parameters.values())
        # 去掉常规实例参数 self, 如果第一个参数就是 *args, 则不用去除
        # 比如类实例方法的参数定义被装饰器修改为 method(*args, **kwargs)
        if params[0].kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY):
            self.self_name = params.pop(0).name

        for param in params:
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                default = ()
                self.args_name = param.name
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                default = {}
                self.kwargs_name = param.name
            else:
                default = param.default
            self.params[param.name] = default

    def make(self, instance, args, kwargs):
        """创建缓存键"""
        key = []
        # 1. 加入类属性值
        if self.cache_properties:
            for item in self.cache_properties:
                key.append(getattr(instance, item, None))
        # 2. 加入调用参数
        arguments = self.signature.bind(None, *args, **kwargs).arguments
        # 去除实例对象
        if self.self_name is not None:  # 首位参数为常规参数 self
            arguments.pop(self.self_name)
        else:  # 首位参数为 *args
            arguments[self.args_name] = arguments[self.args_name][1:]
        params = self.params.copy()
        params.update(arguments)
        if self.args_name is not None:
            args_ = params.pop(self.args_name)
        if self.kwargs_name is not None:
            kwargs_ = params.pop(self.kwargs_name)
        # 2.1 加入常规参数
        key.extend(params.values())
        # 2.2 加入可变参数
        # 2.2.1 加入可变位置参数
        if self.args_name is not None and args_:
            key.extend(args_)
        # 2.2.2 加入可变关键字参数
        if self.kwargs_name is not None and kwargs_:
            if self.args_name is not None:
                key.append(_KeyMakePrecise.mark)  # 分隔 *args 和 **kwargs
            keys = sorted(kwargs_)
            key.extend(map(kwargs_.get, keys))
            key.extend(keys)
        key = tuple(key)
        return key


def _make_key(precise_key, cache_properties, signature=None):
    """获取创建缓存键的函数"""
    if precise_key:
        key_make = _KeyMakePrecise(cache_properties, signature)
    else:
        key_make = _KeyMakeNormal(cache_properties)
    return key_make.make


def instance_cache(
        maxsize: Optional[int] = 128,
        cache_properties: Union[str, Sequence[str]] = (),
        precise_key: bool = False,
        _cache_name: str = None
) -> Callable[[Callable], Callable]:
    """
    为类实例方法提供实例级的结果缓存, 不影响类实例正常垃圾回收的装饰器工厂

    该装饰器会在每个类实例首次运行时, 为其添加一个内部缓存属性, 默认的属性名称为:
        '_cached_' + method.__name__ + id(wrapper)
    用户不应当直接操作这个属性

    该装饰器会为类实例方法添加三个函数:
        cache_info(instance)    查看某一实例的缓存统计信息
        cache_clear(instance)   清空某一实例的缓存结果
        cache_parameters()      查看缓存参数信息

    由于使用字典来缓存结果, 因此所有调用参数和额外存储的类属性的值必须可哈希

    该缓存方法线程安全, 但如果另一个线程在初始调用完成并被缓存之前执行了额外的调用则被包装的函数可能会被多次调用

    参数:
    :param maxsize: 单个实例的缓存数量限制 (非所有实例共享), 为 None 时表示无限制, 默认为 128
    :param cache_properties: 额外缓存一些类属性在调用时的值, 类属性不存在时值视为 None, 默认不额外缓存
    :param precise_key: 是否以牺牲一些性能为代价, 使用更精确的参数缓存策略 (默认为 False)
        若 precise_key 为 True, 则以下调用方式的参数均视为相同 (cached_method 方法按示例中定义), 会命中同一缓存:
            foo.cached_method()
            foo.cached_method(1)
            foo.cached_method(y=2)
            foo.cached_method(1, 2)
            foo.cached_method(x=1, y=2)
            foo.cached_method(y=2, x=1)
            foo.cached_method(1, y=2)
        反之只有完全相同的调用才会被视为相同参数, 但此时性能会显著提高
        建议内部接口使用 precise_key = False, 对外接口使用 precise_key = True
    :param _cache_name: 当默认的内部缓存属性名会发生冲突时, 可以手动指定其他名称

    示例:
    >>> from instance_cache import instance_cache
    >>>
    >>> class MyClass:
    ...     @instance_cache()
    ...     def cached_method(self, x=1, y=2):
    ...         print('run')
    ...         ...  # 耗时操作
    ...         return 1
    ...
    ...     def __del__(self):
    ...         print('delete!')
    ...
    >>> foo = MyClass()
    >>> foo.cached_method(1, 2)
    run
    1
    >>> foo.cached_method(1, 2)  # 命中缓存, 不运行方法直接返回结果
    1
    >>> MyClass.cached_method.cache_info(foo)  # 查看实例的缓存信息
    CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
    >>> # MyClass.cached_method.cache_clear(foo)  # 清空实例的缓存并重置缓存信息
    >>> del foo  # 立刻进行垃圾回收
    delete!

    一个绝妙的配方: @property + @instance_cache(cache_properties=(...))
    可以实现带缓存的类实例方法转类属性功能, 与 @functools.cached_property 不同的是,
    该类属性可以绑定一些计算时用到的其他类属性, 当其他类属性发生变化时, 可以自动更新该类属性的结果
    """
    # 参数验证
    if maxsize is not None:
        if not isinstance(maxsize, int):
            raise TypeError(f'maxsize must be an integer or None, not {type(maxsize)!r}')
        if maxsize < 0:
            maxsize = 0

    if isinstance(cache_properties, str):
        cache_properties = cache_properties.replace(',', ' ').split()
    cache_properties = tuple(set(cache_properties))
    for item in cache_properties:
        if not isinstance(item, str):
            raise TypeError(f'cache_properties must be strings, not {type(item)!r}')
        if not item.isidentifier():
            raise ValueError(f'cache_properties must be valid identifiers: {item!r}')
        if keyword.iskeyword(item):
            raise ValueError(f'cache_properties can not be keywords: {item!r}')

    precise_key = bool(precise_key)

    if _cache_name is not None:
        if not isinstance(_cache_name, str):
            raise TypeError(f'_cache_name must be a string, not {type(_cache_name)!r}')
        if not _cache_name.isidentifier():
            raise ValueError(f'_cache_name must be a valid identifier: {_cache_name!r}')
        if keyword.iskeyword(_cache_name):
            raise ValueError(f'_cache_name can not be a keyword: {_cache_name!r}')

    def decorating_function(method: Callable) -> Callable:
        """类实例方法缓存装饰器"""
        actual_precise_key = precise_key  # 实际的缓存键生成模式
        signature = None  # 类实例方法签名
        try:
            signature = inspect.signature(method)
        except ValueError:
            # 缓存键精确生成模式必须要类实例方法签名, 非精确模式可以不用
            actual_precise_key = False
            if precise_key:
                import warnings
                warnings.warn('failed to get function signature, downgraded to non-precise caching',
                              UserWarning, stacklevel=2)

        # 提取调用参数中的实例对象
        self_name = None  # 常规实例参数的名称
        if signature is not None:
            params0 = next(iter(signature.parameters.values()))
            if params0.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY):
                self_name = params0.name

        def _get_instance(args, kwargs):
            """提取调用参数中的实例对象"""
            # 实例以首位位置参数传递: self.method(...)
            if args:
                return args[0], args[1:], kwargs
            # 实例以关键字参数传递: MyClass.method(self=obj, ...)
            if self_name is not None:
                return kwargs.pop(self_name), args, kwargs
            raise TypeError('failed to extract the instance from call arguments')

        # 生成装饰器
        if maxsize is None or maxsize > 0:
            make_key = _make_key(actual_precise_key, cache_properties, signature)

            @functools.wraps(method)
            def wrapper(*args, **kwargs):
                instance, args, kwargs = _get_instance(args, kwargs)
                key = make_key(instance, args, kwargs)
                cache = _get_cache(instance)
                value = cache.get(key)
                if value is _LRUCache.sentinel:  # 未命中缓存
                    value = method(instance, *args, **kwargs)
                    cache.put(key, value)
                return value

            def cache_clear(instance) -> None:
                """清空某一实例的缓存并重置缓存信息"""
                cache = _get_cache(instance)
                cache.clear()

        else:  # 无缓存
            @functools.wraps(method)
            def wrapper(*args, **kwargs):
                instance, args, kwargs = _get_instance(args, kwargs)
                cache = _get_cache(instance)
                with cache.lock:
                    cache.misses += 1
                value = method(instance, *args, **kwargs)
                return value

            def cache_clear(instance) -> None:
                """清空某一实例的缓存并重置缓存信息"""
                cache = _get_cache(instance)
                with cache.lock:
                    cache.misses = 0

        def cache_info(instance) -> CacheInfo:
            """查看某一实例的缓存信息"""
            cache = _get_cache(instance)
            return cache.get_info()

        def cache_parameters() -> dict:
            """查看缓存参数信息"""
            return {
                'maxsize': maxsize,
                'cache_properties': cache_properties,
                'precise_key': actual_precise_key
            }

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        wrapper.cache_parameters = cache_parameters

        # 内部缓存属性的添加和获取
        cache_name = _cache_name if _cache_name is not None else \
            f'_cache_{method.__name__}_{id(wrapper)}'  # 加一个 id 后缀是因为方法名可能重复 (比如类实例方法的重载), 并且降低和其他属性名冲突的概率
        method_lock = Lock()

        def _get_cache(instance):
            """为类实例添加缓存属性并获取"""
            if not hasattr(instance, cache_name):  # 减少持有锁
                with method_lock:
                    if not hasattr(instance, cache_name):
                        setattr(instance, cache_name, _LRUCache(maxsize))
            return getattr(instance, cache_name)

        return wrapper

    return decorating_function

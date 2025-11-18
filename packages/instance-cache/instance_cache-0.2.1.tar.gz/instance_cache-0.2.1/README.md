# instance_cache

为类实例方法提供实例级的结果缓存, 不影响类实例正常垃圾回收的装饰器


---

## 0. 背景

functools.lru_cache 和 cache 函数会保留对调用参数的强引用, 会影响这些参数正常的垃圾回收, \
需要等待缓存超过 max_size 后弹出或手动调用 cache_clear, 比较麻烦. \
最常见的场景是作用在类实例方法上, 保留参数 self 的引用后会影响整个类实例的垃圾回收.

```pycon
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
```

此处提供一个类实例方法的结果缓存装饰器, 提供实例级别的缓存 (为每个实例单独创建缓存空间). \
通过将缓存内容作为每个类实例的属性进行存储 (类似于 functools.cached_property), 避免影响类实例 self 的正常垃圾回收. \
其他调用参数在类实例被回收后也会正常回收.

---

## 1. 安装

使用以下命令安装该库

```commandline
pip install instance_cache
```

--- 

## 2. 使用

使用方法非常简单, 与 functools.lru_cache 基本一致

```pycon
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
```

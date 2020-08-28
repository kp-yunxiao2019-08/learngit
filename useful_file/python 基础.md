__doc__

```
时刻记住一个事实，那就是所有的模块都有能力来执行代码。最高级别的 Python 语句－－
也就是说， 那些没有缩进的代码行在模块被导入时就会执行， 不管是不是真的需要执行。由
于有这样一个“特性”，比较安全的写代码的方式就是除了那些真正需要执行的代码以外， 几
乎所有的功能代码都在函数当中。再说一遍， 通常只有主程序模块中有大量的顶级可执行代码， 
所有其它被导入的模块只应该有很少的顶级执行代码，所有的功能代码都应该封装在函数或类
当中。 
```


- 如果模块是被导入， __name__ 的值为模块名字 
如果模块是被直接执行， __name__ 的值为 '__main__' 



- 模块也是全局变量， 将经常用到的模块属性替换为一个本地引用

- 空对象、值为零的任何数字或者 Null 对象 None 的布尔值都是 False

- 可变类型 列表， 字典 
不可变类型 数字、字符串、元组

- 浅拷贝就是只拷贝了对对象的索引，而不是重新建立了一个对象！如果你想完全的拷
贝一个对象(包括递归，如果你的对象是一个包含在容器中的容器),你需要用到深拷贝


```
sorted(iter, func=None, key=None, reverse=False)	【有返回值】

接受一个可迭代对象作为参数，返回一个有序的列表;可选参数
func,key 和 reverse 的含义跟 list.sort()内建函数的参数含义一
样. 

list.sort()	【没有返回值，赋值给原list】
```

- 在做比较操作的时候，字符串是按照 ASCII 值的大小来比较的
- enumerate().   枚举，同时获取下标及对应的值   



- 深浅拷贝
  - 浅拷贝：
    - 对一个对象进行浅拷贝其实是新创建了一个类型跟原对
      象一样,其内容是原来对象元素的引用
    - 个拷贝的对象本身是新的,但是它的内容不
      是.序列类型对象的浅拷贝是默认类型拷贝
  
- 所有不可变的类型都是可哈希的，列表、字典不可hash

-  `[expr for iter_var in iterable if cond_expr] `
  这个语法在迭代时会过滤/捕获满足条件表达式 cond_expr 的序列成员
  
- 文件操作：
  - seek() 方法, 可以在文件中移动文件指针到不同的位置. offset 
    字节代表相对于某个位置偏移量. 位置的默认值为 0 , 代表从文件开头算起(即绝对偏移量), 1 代
    表从当前位置算起, 2 代表从文件末尾算起
  
- `**sys.argv 是命令行参数的列表, 下标0为脚本, len(sys.argv) 是命令行参数的个数(也就是 argc)` 

- basename() 去掉目录路径, 返回文件名 
  dirname() 去掉文件名, 返回目录路径 
  join() 将分离的各部分组合成一个路径名
  
- 判断文件是否存在并自动生成文件夹和文件
  
- ``````
  if not os.path.exists('data'):
  		os.makedirs('data')
  file_ = open('data/wenzi', 'w')
  ``````

- 生成器

  ```
  def cou(start=0):
      count = start
      while count:
          yield count
          print(count)
          count -= 1
  
  count = cou(2)
  num = count.__next__()
  print(num, '1')
  num = count.__next__()
  print(num, '2')
  num = count.send(7)
  print(num, '3')
  num = count.__next__()
  print(num, '4')
  ```

  - `send`之前必须有`__next__（）`
  - Python2 用`next()`, python3用`__next__()`

- 模块导入与导入路径查看

  - 模块搜索路径的查看(1)

    -   `print(sys.path)`一个列表， 只要这个列表中的某个目录包含这个文件, 它就会
      被正确导入。修改这个列表可以添加需要导入的模块

  - 模块路径搜索的修改时机(2)

    - 启动 Python 的 shell 
    - 命令行的 PYTHONPATH 环境变量
      -  该变量的内容是一组用冒
        号分割的目录路径。

  - 使用 sys.modules (字典)可以找到当前导入了哪些模块和它们来自什么地方。

    - 使用模块名作为键（ key） , 对应物理地址作为值（ value ）

    - ```
      代码：
      	print(e, file=sys.stderr)
      终端
      	python -u test.py >log 2>>err
      打印信息会保存到log文件错误日志会保存到err文件, -u更新(flush)
      ```

- ```
  一个 UTF-8 编码的文件可以这样指示: 
  #!/usr/bin/env python 
  # -*- coding: UTF-8 -*-
  ```

  ```
  C.__dict__ 类Ｃ的属性
  ```

  ```
  核心笔记：重写__init__不会自动调用基类的__init__ 
  类似于上面的覆盖非特殊方法，当从一个带构造器 __init()__的类派生，如果你不去覆盖
  __init__()，它将会被继承并自动调用。但如果你在子类中覆盖了__init__()，子类被实例化时，
  基类的__init__()就不会被自动调用。
  ```

- 线程，队列

  ```
  每task_done一次 就从队列里删掉一个元素，这样在最后join的时候根据队列长度是否为零来判断队列是否结束，从而执行主线程
  ```

- datetime

  ```python
  from datetime import datetime
  today = datetime.today()
  delta = datetime(today.year, today.month, today.day) - timedelta(days=days)
  
  dat1 = '2020-06-01'
  datetime(*list(map(int, dat1.split('-'))))
  # 输出：datetime(2020, 6, 1, 0, 0)
  ```

  
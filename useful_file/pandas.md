####pandas

###Series

```python
In [1]: from pandas import Series,DataFrame
In [2]: import pandas as pd
```

```python
In [46]: index1 = [ 'a','b','c','d']
In [47]: dic = {'b':1,'c':1,'d':1}
In [48]: data2 = Series(dic,index=index1)
In [49]: data2
Out[49]:
a    NaN
b    1.0
c    1.0
d    1.0
dtype: float64
```

Series的生成依据的是**index值**，index‘a’在字典dic的key中并不存在，Series自然也找不到’a’的对应value值，这种情况下Pandas就会自动生成**NaN(not a number)**来填补缺失值，这里还有个有趣的现象，原本dtype是int类型，生成NaN后就变成了float类型了，因为NaN的官方定义就是**float类型**。

```python
In [58]: data2.isnull()
Out[58]:
a     True
b    False
c    False
d    False
dtype: bool

In [59]: data2.notnull()
Out[59]:
a    False
b     True
c     True
d     True
dtype: bool

In [60]: data2[data2.isnull()==True]    #嵌套查询NaN
Out[60]:
a   NaN
dtype: float64

In [64]: data2.count()    #统计非NaN个数
Out[64]: 3
```

查询NaN值切记不要使用np.nan==np.nan这种形式来作为判断条件，结果永远是False，==是用作**值判断**的，而NaN并没有值，如果你不想使用上方的判断方法，你可以使用is作为判断方法，**is**是**对象引用判断，np.nan is np.nan**，结果就是你要的True

```python
In [72]: data1
Out[72]:
a      1
asd    1
b      1
e      1
dtype: int64

In [73]: data
Out[73]:
a    1
b    2
c    3
d    4
e    NaN
dtype: int64

In [74]: data+data1
Out[74]:
a      2.0
asd    NaN
b      3.0
c      NaN
d      NaN
e      NaN
dtype: float64
```

在算术运算中，Series会自动寻找匹配的**index值**进行运算，如果index不存在匹配则自动赋予NaN,值得注意的是，**任何数+NaN=NaN**,你可以把NaN理解为吸收一切的黑洞。

```python
In [84]: data.index.name = 'abc'
In [85]: data.name = 'test'
In [86]: data
Out[86]:
abc
a    1
b    2
c    3
d    4
Name: test, dtype: int64
```

Series**对象本身**及其**索引index**都有一个**name属性**，name属性主要发挥作用是在**DataFrame**中，当我们把一个Series对象放进DataFrame中，新的列将根据我们的name属性对该列进行命名，如果我们没有给Series命名，DataFrame则会自动帮我们命名为**0**。



## #DataFrame

```python
In [87]:  data = {'name': ['BTC', 'ETH', 'EOS'], 'price':[50000, 4000, 150]}
In [88]: data = DataFrame(data)
In [89]: data
Out[89]:
  name  price
 BTC  50000
 ETH   4000
 EOS    150
 
In [95]: data.index
Out[95]: RangeIndex(start=0, stop=3, step=1)

In [96]: data.values
Out[96]:
array([['BTC', 50000],
       ['ETH', 4000],
       ['EOS', 150]], dtype=object)

In [97]: data.columns    #DataFrame的列标签
Out[97]: Index(['name', 'price'], dtype='object')
```

```
In [92]: data.name
Out[92]:
   0    BTC
   1    ETH
   2    EOS
Name: name, dtype: object

In [93]: data.price
Out[93]:
   0    50000
   1     4000
   2      150
Name: price, dtype: int64

In [94]: data.iloc[1]    #iloc获取该索引行数据
Out[94]:
name      ETH
price    4000
Name: 1, dtype: object
```

```
In [54]: data['rank'] = [1,2,3]       # 添加列数据                                                                    

In [55]: data                                                                                             
Out[55]: 
  name  price  rank
0  BTC  50000     1
1  ETH   4000     2
2  EOS    150     3

In [58]: data.loc[3] = ['ETC', 800, 0] # 添加行数据                                                                

In [59]: data                                                                                             
Out[59]: 
  name  price  rank
0  BTC  50000     1
1  ETH   4000     2
2  EOS    150     4
3  ETC    800     0
```

```
In [77]: data.drop(3)                  # 删除行数据                                                                   
Out[77]: 
  name  price  rank
0  BTC  50000     1
1  ETH   4000     2
2  EOS    150     4

In [78]: data                                                                                             
Out[78]: 
  name  price  rank
0  BTC  50000     1
1  ETH   4000     2
2  EOS    150     4
3  ETC    800     0

In [69]: data.drop(3, inplace=True)    # 删除行数据（没有inplace=True参数,data不会变）                                                                   

In [70]: data                                                                                             
Out[70]: 
  name  price  rank
0  BTC  50000     1
1  ETH   4000     2
2  EOS    150     4

In [79]: del data['rank']              # 删除列数据                                                                  

In [80]: data                                                                                             
Out[80]: 
  name  price
0  BTC  50000
1  ETH   4000
2  EOS    150
3  ETC    800
```

```
In [84]: data.loc[4] = ['haha', np.nan] #添加缺失值                                                                   

In [85]: data                                                                                             
Out[85]: 
   name    price
0   BTC  50000.0
1   ETH   4000.0
2   EOS    150.0
3   ETC    800.0
4  haha      NaN
```

```
In [90]: data.dropna(inplace=True)     # 删除缺失值                                                                    

In [91]: data                                                                                             
Out[91]: 
  name    price
0  BTC  50000.0
1  ETH   4000.0
2  EOS    150.0
3  ETC    800.0
```

```
In [101]: data.fillna(0, inplace=True) # 填充缺失值为0                                                                 

In [102]: data                                                                                            
Out[102]: 
   name    price
0   BTC  50000.0
1   ETH   4000.0
2   EOS    150.0
3   ETC    800.0
4  haha      0.0
```

#### pd函数

- `pd.concat()`

  - ```
    pd.concat(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, copy=True)
    ```

    - objs 需要连接的对象(list)，eg [df1, df2]
    - axis axis = 0, 表示在水平方向(row)进行连接 axis = 1, 表示在垂直方向(column)进行连接
    - join outer, 表示index全部需要; inner,表示只取index重合的部分

- `pd.describe()`

  - ```
    1、count：返回数组的个数；
    
    2、mean：返回数组的平均值，1 3 5 9的平均值为4.5；
    
    3、std：返回数组的标准差；
    
    4、min：返回数组的最小值；
    
    5、25%，50%，75%：返回数组的三个不同百分位置的数值，也就是统计学中的四分位数，其中50%对应的是中位数。
    
    6、max：返回列表的最大值。
    ```

  - 三个参数

    - ```
      percentiles：默认是返回四分位数，即25%，50%和75%，可以修改：describe(percentiles=[.75, 0.8])，则返回的是50%，75%，80%位置的数，可以根据需要进行相应的处理。
      
      2、include：默认只计算数值型特征的统计量，当参数为’all’时，显示所有类型的数据；当参数为numpy.number时，返回的是数值类型的数据；当参数为numpy.object，返回的是object类型的数据；当include=[‘category’]时，返回的是category；当include=[‘O’]时，返回统计的是字符串型的数据。
      
      3、exclude：include可以指定返回类型，而exclude则可以指定不返回某种类型，即返回除指定类型之外的数据。
      ```

  - 


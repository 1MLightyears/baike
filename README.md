[toc]

# 百度百科bot

### 简介

搜索百度百科并返回匹配条目的简介。

------

### 安装

```python
#pip install baike
```



------

### 简单上手

想要直接在百度百科搜索一个词条，可以从以下的方法中二选一：

1.

```python
from baike import Baike
ret=Baike('你要搜的内容').query()
#返回结果保存在ret里
```

2.

```python
from baike import getBaike
ret=getBaike('你要搜的内容')
#同上
```
------

### 更多功能

1. 通过指定变量`entries`为`True`，你可以显示多义词的义项列表：

   ```python
   >>>print(getBaike('Python',entries=True))
   Python
   -计算机程序设计语言
   -英文单词
   ```
   该变量默认为`False`，此时默认显示第一个搜索命中结果的内容简介。
   如果该词条不是一个多义词，返回空字符串。
   1. 1. 再指定变量`no`为整数，你可以显示第`no`个词条的内容简介：
   
      ```Python
      >>>print(getBaike('Python',entries=True,no=2))
      Python（英文单词）
      python发音：英 [ˈpaɪθən] 美 [ˈpaɪθɑ:n]中文释义：巨蛇，大蟒复数形式：pythons
      ```
      `no`不能等于0或1，否则返回空字符串。
      如果`no`$>$词条数，则会显示最后一个词条。
      如果`no`是负数，则会从后往前计数。类似的，如果`no`$<-$词条数，则会显示第二个词条。

------

### 依赖

需要requests和lxml。

```python
pip install requests lxml
```

Python 3.6.9 3.7.1 正常运行。

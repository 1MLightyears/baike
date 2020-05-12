[toc]

# 百毒百科bot

### 简介

搜索百度百科并返回匹配条目的简介。

------

### 用法

二选一

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

### 依赖

需要requests和lxml。

```python
pip install requests lxml
```

Python 3.7.1 正常运行。

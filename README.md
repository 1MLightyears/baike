[TOC]

# baike

![PyPI](https://img.shields.io/pypi/v/baike?style=plastic)![PyPI - Python Version](https://img.shields.io/pypi/pyversions/baike?style=plastic)

### 简介

`baike`是一个百度百科search bot。

在百度百科上搜索词条并返回匹配条目的简介，图片等。

------

### 安装

```shell
#pip install baike
```

------

### 简单上手

想要直接在百度百科搜索一个词条，可以从以下的方法中二选一：

1.

```python
>>>from baike import Baike
>>>ret=Baike('你要搜的内容').query()
#返回结果保存在ret里
```

2.

```python
>>>from baike import getBaike
>>>ret=getBaike('你要搜的内容')
#同上
#也可以直接print(getBaike('你要搜的内容'))来显示
```
------

### 更多功能

1. 通过指定变量`no`为`0`，你可以显示多义词的义项列表：

   ```python
   >>>print(getBaike('Python',no=0))
     Python
   1:计算机程序设计语言
   2:英文单词
   ```
   这个值默认为`1`，此时默认显示第一个搜索命中结果的内容简介。

2. 指定变量`no`为非0整数，你可以显示第`no`个义项的内容简介：

   ```Python
   >>>print(getBaike('Python',no=2))
   Python（英文单词）
   python发音：英 [ˈpaɪθən] 美 [ˈpaɪθɑ:n]中文释义：巨蛇，大蟒复数形式：pythons
   ```
   如果`no`>义项数，则会显示最后一个义项。
   如果`no`是负数，则会从后往前计数。类似的，如果`no`<(-义项数)，则会显示第一个义项。

3. 在内部实现中，`no`实际上是一个由两个元素组成的列表。第一个元素为一个整数，即上文中的“义项序号”；第二个元素为一个整数列表或空列表，指出需要显示的义项中的“段落序号”。如：

   ```Python
   >>>print(getBaike('Python',no=[1,[1]]))
   Python（计算机程序设计语言）
   1.Python简介及应用领域
   Python是一种解释型脚本语言，可以应用于以下领域：
   ```

   “段落序号”可以指定多个，将按顺序显示：

   ```Python
   >>>print(getBaike('Python',no=[1,[0,1,2]]))
   Python（计算机程序设计语言）
   Python是一种跨平台的计算机程序设计语言。 是一个高层次的结合了解释性、编译性、互动性和面向对象的脚本语言。最初被设计用于编写自动化脚本(shell)，随着版本的不断
   更新和语言新功能的添加，越多被用于独立的、大型项目的开发。
   1.Python简介及应用领域
   Python是一种解释型脚本语言，可以应用于以下领域：
   2.下载Python
   在您开始之前，在你的计算机将需要Python，但您可能不需要下载它。首先检查(在同级目录下在命令行窗口输入python)有没有安装Python。如果你看到了一个Python解释器的响
   应，那么就能在它的显示窗口中得到一个版本号。通常的版本都可以做到Python的向前兼容。
   如果您需要安装， 您不妨下载最近稳定的版本。 就是那个以没有被标记作为alpha或Beta发行的最高的版本。目前最稳定的版本是Python3.0以上
   如果你使用的操作系统是Windows：当前最稳定的Windows版本下载是"Python 3.8.3 for Windows"
   如果你使用的是Mac，MacOS 10.2 (Jaguar), 10.3 (Panther) and 10.4 (Tiger)已经集成安装了Python，但是你大概需要安装最近通用的构架(build)。
   对于Red Hat，安装python2和python2-devel包。
   对于Debian，安装python2.5和python2.5-dev包。
   ```

   请注意，`baike`不会对“段落序号”做任何检查，这意味着诸如`getBaike("Python",no=[1,[0,0,0,3,2,1]])`等等重复值和逆序值是完全合法的。

   0号段落即为该义项的简介段落，`[0]`也是“段落序号”的默认值：

   ```python
   >>>print(getBaike('Python',no=[1,[0]]))
   Python（计算机程序设计语言）
   Python是一种跨平台的计算机程序设计语言。 是一个高层次的结合了解释性、编译性、互动性和面向对象的脚本语言。最初被设计用于编写自动化脚本(shell)，随着版本的不断
   更新和语言新功能的添加，越多被用于独立的、大型项目的开发。
   ```

   如果“段落序号”为空列表`[]`，那么将显示段落目录：

   ```Python
   >>>print(getBaike('Python',no=[1,[]]))
   Python（计算机程序设计语言）
   【目录】
   0简介
   1Python简介及应用领域
   2下载Python
   3发展历程
   4风格
   5与MATLAB的对比
   6设计定位
   7执行
   8基本语法
   9帮助
   10CGI
   11特点
   12应用
   13工具功能
   14标准库
   15开发环境
   16解释器
   17著名应用
   18库导入
   19学习网站
   ```

   在“段落序号”内部，一样可以使用负数来索引段落。

   当“义项序号”为`0`时，“段落序号”将被忽略，但是仍然需要输入合法的值以避免报错。

4. 指定变量`timeout`为正整数，你可以设定搜索的超时时间，单位为秒：

   ```Python
   >>>ret=getBaike('Python',timeout=1)
   ```
   当搜索超时时，标准错误输出`stderr`会显示一条错误信息`超时错误:`，紧接着是引发超时错误的网页链接。

   你可以重定向标准错误输出至文件来实现日志功能。该变量默认为`5`。

   请注意，每次搜索对应2\~3个网页请求，而`timeout`值是对**单个请求**的时长所设的限制，因此一次搜索的总时长最长的花费可能会是`timeout`的2\~3倍。

5. 如果搜索没有结果，标准错误输出`stderr`会显示一条错误信息`没有匹配的搜索结果:`，紧接着是没有搜索结果的关键字。类似的，你可以重定向标准错误输出至文件来实现日志功能。

6. 指定变量`pic`为`True`，你可以自动下载这个词条的概要图：

   ```Python
   >>>ret=getBaike('Python',pic=True)
   ```

   如果该词条有概要图，那么就会下载到当前目录下，文件名格式为"<搜索关键词>\_<义项序号>\_<12位时间戳>.<图片格式>"。默认图片格式是jpg。

   该变量默认为`False`。

7. 当变量的值有误时，标准错误输出`stderr`会显示一条错误信息`参数不正确:`，紧接着是有误的参数名。要想更正，可以通过`setting()`方法设置正确的参数值，如果设置正确那么`setting()`将返回`0`，错误则是非`0`值。

   每个`Baike`搜索对象的设置都是独立的。如果希望将搜索设置设为默认值（如`no`参数等），可以使用`reset()`方法。

   如果使用`getBaike()`进行搜索，因为每次搜索都是独立的，因此每次搜索都会将从默认值开始。

------

### 已知问题

- [ ] 无法显示部分表格/列表

------

### 依赖

需要`requests`和`lxml`。若安装失败可以手动执行：

```bash
#pip install requests lxml
```

在Python 3.6.9, 3.7.1, 3.9.0 上正常运行。

在Windows10 1909 20H4， Ubuntu 18.04 LTS上正常运行。

在Termux上安装`lxml`可能存在问题，请尝试先安装`Cython `或先安装对应发行版的库文件。

`baike`仍处于pre-Alpha阶段，建议随时使用最新版以减少bug。

------

### 声明

`baike`只有收录/分类/组织的功能，对显示的信息**不**负任何法律责任，也**不**享有著作权，若信息源的信息发生变更，baike**没有**能力随时更新内容，因此使用者须自行对提供的信息的真实性、进行判断。
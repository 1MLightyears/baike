'''
百度百科bot
by 百万光年(1MLightyears@gmail.com)
https://github.com/1MLightyears/baike

搜索百度百科并返回匹配条目的简介。

具体用法请查看README.md。
'''

import requests as rq
from lxml import html
import re
from sys import stderr

class Baike(object):
    def __init__(self, *args,**kwargs):
        self.settings(*args,**kwargs)

    def settings(self,keyword:str=None,no:int=1,timeout=0):
        '''
        初始化搜索关键字和header。

        keyword(str):要搜索的关键字。
        no(int):当no为整数时，获取第no个义项；
                当no为0时，获取义项列表；
                负数的no意味着从最后一个义项开始倒数。
        timeout(int):请求的超时限制。超时后会报错'超时错误'并返回空字符串。
        '''


        if keyword != None:
            self.keyword = keyword
        else:
            self.keyword = ''

        if timeout > 0:
            self.timeout = timeout
        else:
            self.timeout = 5  #默认值

        self.header = {
                'Host': 'baike.baidu.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Accept-Encoding': 'gzip, deflate'
        }
        if isinstance(no,int):
            self.no = no
        else:
            self.no = 1


    def getDescription(self, url: str):
        """
        获取词条的内容简介。
        """
        try:
            ret = rq.get(url, headers=self.header, timeout=self.timeout)
        except:
            stderr.write('超时错误:' + url + '\n')
            return ''
        doc = html.fromstring(ret.text)

        #获取主标题，如果前面的搜索有结果，那默认这个词条一定有主标题
        title=doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h1/text()")[0]
        #如果有副标题，加上副标题
        subtitle = doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h2/text()")
        if subtitle != []:
            subtitle = subtitle[0]
        else:
            subtitle = ''
            #由于没有副标题的现象比较普遍，因此这里不考虑报错

        #获取description
        desclist = doc.xpath("//div[@class='lemma-summary']//text()")
        description=''
        for s in desclist:
            description += s

        #对description进行后期处理
        #删去\xa0
        description = re.sub(r'\xa0', '', description)
        #删去角标部分
        description = re.sub(r'\[[0-9\-]*?\]', '', description)
        #删去换行符
        description = re.sub(r'[\n\r]', '', description)

        #处理完毕，拼接结果
        text=title+subtitle+'\n'+description
        return text

    def getEntries(self, url: str,no:int=1):
        """
        获取义项列表。
        """
        try:
            ret = rq.get(url, headers=self.header,timeout=self.timeout)
        except:
            stderr.write('超时错误:' + url + '\n')
            return ''
        doc = html.fromstring(ret.text)

        #获取主标题，如果前面的搜索有结果，那默认这个词条一定有主标题
        title=doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h1/text()")[0]
        #获取义项列表
        entrylist = doc.xpath("//ul[@class='polysemantList-wrapper cmn-clearfix']//li/*")
        #如果义项列表是空的，说明这是个单义词，为它增加一个dummy义项"(这是一个单义词)"
        if entrylist == []:
            entrylist.append(html.HtmlElement())
            entrylist[0].text='(这是一个单义词)'
        #为能返回正确的url，对其他url添加头部
        for i in range(1,len(entrylist)):
             entrylist[i].attrib['href']="https://baike.baidu.com"+entrylist[i].attrib['href']
        #为使得对于列表的访问逻辑更合理，增加对于1的处理
        entrylist[0].attrib['href'] = url
        #对no进行处理
        if no != 0:
            if no > 0:
                no -= 1
            if no > len(entrylist)-1:
                no = len(entrylist) - 1
            elif no < -len(entrylist):
                no = -len(entrylist)
                #处理完毕，no指向的entrylist一定有
            return self.getDescription(entrylist[no].attrib['href'])
        elif no == 0:
            #如果处理后的no是0那么说明要求显示义项列表
            entries = ''
            i=0
            for i in range(len(entrylist)):
                entries += str(i+1)+':'+entrylist[i].text+'\n'

            #处理完毕，拼接结果
            text=title+'\n'+entries
            return text

    def query(self):
        '''
        搜索关键字
        '''

        if self.keyword == None:
            return ''

        # 获取搜索结果
        try:
            ret = rq.get('https://baike.baidu.com/search?word=' + self.keyword,headers=self.header,timeout=self.timeout)
        except:
            stderr.write('超时错误:' + 'https://baike.baidu.com/search?word=' + self.keyword + '\n')
            return ''
        ret.encoding='utf-8'
        doc = html.fromstring(ret.text)
        x = "//div[@class='searchResult']/dl[1]/dd[1]/a[@class='result-title']"
        ans = doc.xpath(x)
        if ans == []:
            stderr.write('没有匹配的搜索结果:'+self.keyword+'\n')
            return ''  #搜索没有结果
        url = ans[0].attrib['href']
        if url[0] == '/':
            url = 'https://baike.baidu.com' + url

        return self.getEntries(url,self.no)


    def __call__(self,*args,**kwargs):
        self.settings(*args,**kwargs)
        return self.query()

#提供一个预先定义好的对象getBaike方便直接调用
getBaike = Baike()
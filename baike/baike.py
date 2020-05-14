'''
百度百科bot
by 百万光年(1MLightyears@gmail.com)

搜索百度百科并返回匹配条目的简介。

具体用法请查看README.md。
'''

import requests as rq
from lxml import html
import re

class Baike(object):
    def __init__(self, *args,**kwargs):
        self.settings(*args,**kwargs)

    def settings(self,keyword:str=None,entries:bool=False,no:int=1):
        '''
        初始化搜索关键字和header。

        keyword(str):要搜索的关键字。
        entries(bool):True:在接下来的搜索中，获取多义项词条的义项列表;
                      False:在接下来的搜索中，获取第一个匹配的词条的内容简介;
        no(int):当entries=True时，直接获取第n个词条的内容简介
        '''
        self.keyword=''
        if keyword != None:
            self.keyword = keyword
        self.entries=entries
        self.header = {
                'Host': 'baike.baidu.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Accept-Encoding': 'gzip, deflate'
        }
        self.no=no

    def getDescription(self, url: str):
        """
        获取词条的内容简介。
        """
        ret = rq.get(url, headers=self.header)
        doc = html.fromstring(ret.text)

        #获取主标题，如果前面的搜索有结果，那默认这个词条一定有主标题
        title=doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h1/text()")[0]
        #如果有副标题，加上副标题
        subtitle = doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h2/text()")
        if subtitle != []:
            subtitle = subtitle[0]
        else:
            subtitle = ''

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
        获取多义项词条的义项列表。
        """
        ret = rq.get(url, headers=self.header)
        doc = html.fromstring(ret.text)

        #获取主标题，如果前面的搜索有结果，那默认这个词条一定有主标题
        title=doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h1/text()")[0]
        #获取义项列表
        entrylist = doc.xpath("//div[@class='polysemant-list polysemant-list-normal']//li/*")
        if entrylist == []:
            #说明这是个单义项词条
            return ''
        #对no进行处理
        if no > 0:
            no -= 1
        if (no != 0):
            if no > len(entrylist):
                no = len(entrylist) - 1
            elif no == -len(entrylist):
                no = -len(entrylist) + 1
            #处理完毕，no指向的entrylist一定有
            return self.getDescription("https://baike.baidu.com" +entrylist[no].attrib['href'])

        #如果处理后的no是0那么说明要求显示义项列表
        entries=''
        for s in entrylist:
            entries += '-'+s.text+'\n'

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
        ret = rq.get('https://baike.baidu.com/search?word=' + self.keyword,headers=self.header)
        ret.encoding='utf-8'
        doc = html.fromstring(ret.text)
        x = "//div[@class='searchResult']/dl[1]/dd[1]/a[@class='result-title']"
        ans = doc.xpath(x)
        if ans == []:
            return ''  #搜索没有结果
        url = ans[0].attrib['href']
        if url[0] == '/':
            url = 'https://baike.baidu.com' + url

        if self.entries:
            return self.getEntries(url,self.no)
        else:
            return self.getDescription(url)


    def __call__(self,*args,**kwargs):
        self.settings(*args,**kwargs)
        return self.query()

#提供一个预先定义好的对象getBaike方便直接调用
getBaike = Baike()

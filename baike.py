'''
百毒百科bot
by 百万光年(1MLightyears@gmail.com)

搜索百度百科并返回匹配条目的简介。

用法：二选一
1.
from baike import Baike
ret=Baike('你要搜的内容').query()
#返回结果保存在ret里

2.
from baike import getBaike
ret=getBaike('你要搜的内容')
#同上

'''

import requests as rq
from lxml import html
import re

class Baike(object):
    def __init__(self, keyword: str = None):
        '''
        初始化搜索关键字和header
        '''
        self.keyword = keyword
        self.header = {
                'Host': 'baike.baidu.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Accept-Encoding': 'gzip, deflate'
        }

    def query(self):
        '''
        百度百科搜索关键字，位于self.header
        '''

        if self.keyword == None:
            return ''

        # round 1 获取第一个搜索结果
        ret = rq.get('https://baike.baidu.com/search?word=' + self.keyword,headers=self.header)
        ret.encoding='utf-8'
        doc = html.fromstring(ret.text)
        x = "//div[@class='searchResult']/dl[1]/dd[1]/a"
        ans = doc.xpath(x)


        # round 2 获取简介部分
        url = ans[0].attrib['href']
        if url[0] == '/':
            url = 'https://baike.baidu.com' + url
        ret = rq.get(url, headers=self.header)
        doc = html.fromstring(ret.text)

        #获取主标题，默认这个词条一定有主标题
        title=doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h1/text()")[0]
        #如果有副标题，加上副标题
        subtitle = doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h2/text()")
        if subtitle != []:
            subtitle = subtitle[0]
        else:
            subtitle = ''
        #拼接成标题
        title=title+subtitle+'\n'

        #获取description
        ans = doc.xpath("//div[@class='lemma-summary']//text()")
        description=''
        for i in ans:
            description += i

        #对description进行后期处理
        #删去\xa0
        description = re.sub(r'\xa0', '', description)
        #删去角标部分
        description = re.sub(r'\[[0-9\-]*?\]', '', description)
        #删去换行符
        description = re.sub(r'[\n\r]', '', description)

        #处理完毕，拼接结果
        return (title+description)

    def __call__(self, keyword=None):
        if keyword:
            self.keyword=keyword
        return self.query()

#提供一个预先定义好的对象getBaike方便直接调用
getBaike=Baike()
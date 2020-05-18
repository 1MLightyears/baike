import requests as rq
from lxml import html
import re
from sys import stderr


class Baike(object):
    '''
    主对象部分。进行百科搜索。

    settings(self,keyword:str=None,no:int=1,timeout=5,pic:bool=False):
        对当前的搜索对象进行设置。
    query():以当前设置进行一次搜索。
    setting(keyword:str=None,no:int=1,timeout=5,pic:bool=False):
            设置参数。
    '''
    #private
    def __init__(self, *args,**kwargs):
        self.settings(*args,**kwargs)

    def __getSummaryPic(self, url: str):
        """
        保存某个义项的概要图。
        """
        try:
            ir = rq.get(url, stream=True)
            if ir.status_code == 200:
                with open(self.title+'_'+str(self.no)+'.'+url[-3:], 'wb') as f:
                    for chunk in ir:
                        f.write(chunk)
            return True#成功存图返回True
        except rq.exceptions.Timeout:
            stderr.write('超时错误:' + url + ';'+'HTTP状态码:'+str(ir.status_code)+'\n')
            return False#存图失败返回False

    def __getDescription(self, url: str):
        """
        获取词条的内容简介。
        """
        try:
            ret = rq.get(url, headers=self.__header, timeout=self.timeout)
        except rq.exceptions.Timeout:
            stderr.write('超时错误:' + url + ';'+'HTTP状态码:'+str(ret.status_code)+'\n')
            return ''
        doc = html.fromstring(ret.text)

        #如果有副标题，加上副标题
        self.subtitle = doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h2/text()")
        if self.subtitle != []:
            self.subtitle = self.subtitle[0]
        else:
            self.subtitle='' #由于没有副标题的现象比较普遍，因此这里不考虑报错

        #获取summary图
        if self.pic:
            img = doc.xpath("//div[@class='summary-pic']//img")
            if img != []:
                self.__getSummaryPic(img[0].attrib['src'])

        #获取description
        desclist = doc.xpath("//div[@class='lemma-summary']//text()")
        self.description=''
        for s in desclist:
            self.description += s

        #对description进行后期处理
        #删去\xa0
        self.description = re.sub(r'\xa0', '', self.description)
        #删去角标部分
        self.description = re.sub(r'\[[0-9\-]*?\]', '', self.description)
        #删去换行符
        self.description = re.sub(r'[\n\r]', '', self.description)

        #处理完毕，拼接结果
        text=self.title+self.subtitle+'\n'+self.description
        return text

    def __getEntries(self, url: str):
        """
        获取义项列表。
        """
        try:
            ret = rq.get(url, headers=self.__header,timeout=self.timeout)
        except rq.exceptions.Timeout:
            stderr.write('超时错误:' + url + ';'+'HTTP状态码:'+str(ret.status_code)+'\n')
            return ''
        doc = html.fromstring(ret.text)

        #获取主标题，如果前面的搜索有结果，那默认这个词条一定有主标题
        self.title=doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h1/text()")[0]
        #获取义项列表
        self.entrylist = doc.xpath("//ul[@class='polysemantList-wrapper cmn-clearfix']//li/*")
        #如果义项列表是空的，说明这是个单义词，为它增加一个dummy义项"(这是一个单义词)"
        if self.entrylist == []:
            self.entrylist=[html.HtmlElement()]
            self.entrylist[0].text = '(这是一个单义词)'

        #为能返回正确的url，对其他url添加头部
        for i in range(1,len(self.entrylist)):
             self.entrylist[i].attrib['href']="https://baike.baidu.com"+self.entrylist[i].attrib['href']
        #为使得对于列表的访问逻辑更合理，增加对于1的处理
        self.entrylist[0].attrib['href'] = url
        #对no进行处理
        if self.no != 0:
            if self.no > 0:
                self.no -= 1
            if self.no > len(self.entrylist)-1:
                self.no = len(self.entrylist) - 1
            elif self.no < -len(self.entrylist):
                self.no = -len(self.entrylist)
                #处理完毕，no指向的entrylist一定有
            return self.__getDescription(self.entrylist[self.no].attrib['href'])
        elif self.no == 0:
            #如果处理后的no是0那么说明要求显示义项列表
            entries = ''
            self.title=self.keyword
            for i in range(len(self.entrylist)):
                entries += str(i+1)+':'+self.entrylist[i].text+'\n'

            #处理完毕，拼接结果
            text=self.title+'\n'+entries
            return text

    #public
    def query(self):
        '''
        搜索关键字
        '''

        if self.keyword == None:
            return ''

        # 获取搜索结果
        try:
            ret = rq.get('https://baike.baidu.com/search?word=' + self.keyword,headers=self.__header,timeout=self.timeout)
        except rq.exceptions.Timeout:
            stderr.write('超时错误:' + 'https://baike.baidu.com/search?word=' + self.keyword + ';'+'HTTP状态码:'+str(ret.status_code)+'\n')
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

        return self.__getEntries(url)

    def settings(self,keyword:str=None,no:int=1,timeout=5,pic:bool=False):
        '''
        初始化搜索关键字和header。

        keyword(str):要搜索的关键字。默认为None是为了防止报错，这时返回空字符串。
        no(int):当no为整数时，获取第no个义项；
                当no为0时，获取义项列表；
                负数的no意味着从最后一个义项开始倒数。
                默认为1。
        timeout(int):请求的超时限制。超时后会报错'超时错误'并返回空字符串。默认为5(秒)。
        pic(bool):是否下载简介图片。默认为False。
        '''

        #用户设置部分
        #keyword
        if keyword != None:
            self.keyword = keyword
        else:
            self.keyword = ''

        #no
        if isinstance(no,int):
            self.no = no
        else:
            self.no = 1

        #timeout
        if timeout > 0:
            self.timeout = timeout
        else:
            self.timeout = 5  #默认值

        #pic
        self.pic = pic

        ### 自动获取部分
        #header
        #暂时使用Firefox的header
        self.__header = {
                'Host': 'baike.baidu.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Accept-Encoding': 'gzip, deflate'
        }
        #title
        self.title = ''

        #subtitle
        self.subtitle = ''

        #description
        self.description = ''

    def __call__(self,*args,**kwargs):
        self.settings(*args,**kwargs)
        return self.query()

#提供一个预先定义好的对象getBaike方便直接调用
getBaike = Baike()
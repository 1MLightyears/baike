import re
from sys import stderr
from typing import List

import requests as rq
from lxml import html


class Baike(object):
    '''
    主对象部分。进行百科搜索。

    setting(self,keyword:str=None,no:int=1,timeout=5,pic:bool=False):
        对当前的搜索对象进行设置。
    query():以当前设置进行一次搜索。
    setting(keyword:str=None,no:List=[1,[0]],timeout=5,pic:bool=False):
            设置参数。
    '''
    #private
    def __init__(self, *args, **kwargs):
        self.reset()
        self.setting(*args,**kwargs)

    def __regularize(self,i:int,j:int):
        """
        将i规范到-j~j-1之间，以便于列表索引。
        """
        if i >= j:
            i=j-1
        elif i<-j:
            i=-j
        return i

    def __getTitles(self, doc):
        """
        获取主副标题。
        doc(lxml.html):需要获取标题的页面
        """
        self.title=doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h1/text()")[0]
        self.subtitle = doc.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h2/text()")
        if self.subtitle != []:
            self.subtitle = self.subtitle[0]
        else:
            self.subtitle=''

    def __getSummaryPic(self, url: str):
        """
        保存某个义项的概要图。
        """
        #先获取到不带附加参数的url链接
        url = re.search(r'^(.*?)\?', url).group(1)
        try:
            ir = rq.get(url, stream=True)
            if ir.status_code == 200:
                with open(self.title + '_' + str(self.__setup['no']) + '.jpg', 'wb') as f:  #默认图片为jpg格式
                    for chunk in ir:
                        f.write(chunk)
            return True#成功存图返回True
        except rq.exceptions.Timeout:
            stderr.write('超时错误:' + url + ';'+'HTTP状态码:'+str(ir.status_code)+'\n')
            return False#存图失败返回False

    def __getParagraph(self, url: str):
        """
        获取词条的内容简介。
        """
        endl='ANewLine'
        try:
            ret = rq.get(url, headers=self.__header, timeout=self.__setup['timeout'])
        except rq.exceptions.Timeout:
            stderr.write('超时错误:' + url + ';'+'HTTP状态码:'+str(ret.status_code)+'\n')
            return ''
        doc = html.fromstring(ret.text)

        #换了一个新页面，重新获取一次标题副标题
        self.__getTitles(doc)

        #获取summary图
        if self.__setup['pic']:
            img = doc.xpath("//div[@class='summary-pic']//img")
            if img != []:
                self.__getSummaryPic(img[0].attrib["src"])

        self.text = ''

        #如果no的第二个参数是空列表，那么显示段落目录
        if self.__setup['no'][1] == []:
            self.text='【目录】'+endl+'0简介'+endl
            index = doc.xpath("//dt[@class='catalog-title level1']")
            for item in index:
                self.text+=item.text_content()+endl


        #处理词条文本，分成段落
        paralist = []
        divlist = doc.xpath("//div[@class='main-content']/div")
        for div in divlist:
            if 'lemma-summary' in list(div.attrib.values()):#是简介部分
                paralist.append(div.text_content())
            elif 'para-title level-2' in list(div.attrib.values()):
                paralist.append(str(len(paralist))+'.')#一个段落的标题
                for t in div.getchildren()[0].itertext():
                    #段落标题是一个<h2>，这个标签底下有一个<span>会影响分切出的段落标题，因此需要过滤掉
                    #这个<span>，它的text和页面标题一致。
                    if t != self.title:
                        paralist[len(paralist)-1]+=t+' '#拼接出适合阅读的标题
            elif ('para' in list(div.attrib.values()))and('style'not in list(div.attrib)):#前一个段落的内容,且不是图片
                paralist[len(paralist) - 1] += endl+div.text_content()#添加内容到列表的最后一个里
            elif 'album-list' in list(div.attrib.values()):#内容结束
                break

        #选出对应片段
        for i in self.__setup['no'][1]:
            self.text+=paralist[self.__regularize(i,len(paralist))]+endl

        #对description进行后期处理
        #删去\xa0
        self.text = re.sub(r'\xa0', '', self.text)
        #删去角标部分
        self.text = re.sub(r'\[[0-9\-]*?\]', '', self.text)
        #删去换行符
        self.text = re.sub(r'[\n\r]', '', self.text)
        #把换行标记ANewLine变成\n
        self.text = re.sub(endl,'\n', self.text)

        #处理完毕，拼接结果
        return self.title+self.subtitle+'\n'+self.text

    def __getEntries(self, url: str):
        """
        获取义项列表。
        """
        try:
            ret = rq.get(url, headers=self.__header,timeout=self.__setup['timeout'])
        except rq.exceptions.Timeout:
            stderr.write('超时错误:' + url + ';'+'HTTP状态码:'+str(ret.status_code)+'\n')
            return ''
        doc = html.fromstring(ret.text)

        #现在我们在第一个义项页面里
        self.__getTitles(doc)

        #获取义项列表
        self.entrylist = doc.xpath("//ul[@class='polysemantList-wrapper cmn-clearfix']//li/*")
        #如果义项列表是空的，说明这是个单义词，为其添加标题
        if self.entrylist == []:
            self.entrylist=[html.HtmlElement()]
            self.entrylist[0].text = self.title + '\n' + self.subtitle
        #为使得第i个索引指向第i个义项，需要添加一个dummy0号义项在entrylist里
        self.entrylist = [html.HtmlElement()] + self.entrylist

        #为能返回正确的url，对其他url添加头部
        for i in range(len(self.entrylist)):
            if self.entrylist[i].attrib.has_key('href'):
                self.entrylist[i].attrib['href'] = "https://baike.baidu.com" + self.entrylist[i].attrib['href']
            else:
                #没有href属性的是当前义项，为它加一个url
                self.entrylist[i].attrib['href'] = url

        #对no进行处理
        #如果no不是列表，把它变成列表
        if isinstance(self.__setup['no'], int):
            self.__setup['no'] = [self.__setup['no'], 1]
        #获取第no[0]号义项的内容
        if self.__setup['no'][0] != 0:
            return self.__getParagraph(self.entrylist[self.__regularize(self.__setup['no'][0],len(self.entrylist))].attrib['href'])
        elif self.__setup['no'][0] == 0:
            #如果no是0那么说明要求显示义项列表
            entries = ''
            self.title=self.__setup['keyword']
            for i in range(1,len(self.entrylist)):
                entries += str(i)+':'+self.entrylist[i].text+'\n'

            #处理完毕，拼接结果
            return self.title+'\n'+entries

    def __call__(self, *args, **kwargs):
        self.reset()
        if self.setting(*args,**kwargs)==0:
            return self.query()

    #public
    def query(self):
        '''
        搜索关键字
        '''

        if self.setting() != 0:
            return ''

        # 获取搜索结果
        try:
            ret = rq.get('https://baike.baidu.com/search?word=' + self.__setup['keyword'],headers=self.__header,timeout=self.__setup['timeout'])
        except rq.exceptions.Timeout:
            stderr.write('超时错误:' + 'https://baike.baidu.com/search?word=' + self.__setup['keyword'] + ';'+'HTTP状态码:'+str(ret.status_code)+'\n')
            return ''
        ret.encoding='utf-8'
        doc = html.fromstring(ret.text)
        x = "//div[@class='searchResult']/dl[1]/dd[1]/a[@class='result-title']"
        ans = doc.xpath(x)
        if ans == []:
            stderr.write('没有匹配的搜索结果:'+self.__setup['keyword']+'\n')
            return ''  #搜索没有结果
        url = ans[0].attrib['href']
        if url[0] == '/':
            url = 'https://baike.baidu.com' + url

        return self.__getEntries(url)

    def setting(self,*args,**kwargs):
        '''
        设置搜索关键字和header。

        keyword(str):要搜索的关键字。默认为None，这时返回空字符串。
        no(List of int):第一个参数：整数no1。
                            为整数时，获取第no1个义项；
                            为0时，获取义项列表；
                            负数的no1意味着从最后一个义项开始倒数。
                            默认为1。
                        第二个参数：列表no2.
                            为空(“[]”)时，获取目录；
                            为0时，获取简介段落；
                            为整数时，依次获取各段落并拼接。
                            默认为[0]。
        timeout(int):请求的超时限制。超时后会报错'超时错误'并返回空字符串。默认为5(秒)。
        pic(bool):是否下载简介图片。默认为False。

        如果设置合法，该函数返回0。如果设置不合法，该函数返回大于0的值，此时调用query()会报错。
        '''
        #用户设置部分
        for i, j in zip(self.__setup.keys(), args):
            self.__setup[i] = j
        self.__setup.update(kwargs)
        #检查各变量是否合法
        #keyword
        if not isinstance(self.__setup['keyword'],str):
            stderr.write('参数不正确:keyword必须是字符串\n')
            return 1

        #no
        if not (isinstance(self.__setup['no'], int) or (isinstance(self.__setup['no'], List)and(isinstance(self.__setup['no'][0],int))and([i for i in self.__setup['no'][1] if not isinstance(i,int)]==[]))):
            stderr.write('参数不正确:no必须是整数或列表\n')    #no是列表                                 #列表部分里没有一个元素不是整数（no里的每个元素都是整数）
            return 1

        #timeout
        if self.__setup['timeout'] <= 0:
            stderr.write('参数不正确:timeout必须大于0\n')
            return 1


        #pic
        if not isinstance(self.__setup['pic'],bool):
            stderr.write('参数不正确:pic必须是True或False\n')
            return 1
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
        self.text = ''

        return 0

    def reset(self):
        """
        提供默认设置。
        """
        self.__setup = {
            'keyword': '',
            'no': [1,[0]],
            'timeout': 5,
            'pic':False
            }


#提供一个预先定义好的对象getBaike方便直接调用
getBaike = Baike()
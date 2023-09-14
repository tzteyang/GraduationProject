# encoding:utf-8
import random
import time
import re
from html.parser import HTMLParser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
import undetected_chromedriver as uc
from utls.selenium_tool import selenium_entity
from web_page_preprocess import noisy_text_clean

# 格式化文本
tag_list = ["h1","h2","h3","h3","h4","p","div","hr","table","section"]
str_Arr = ""
class MyHTMLParser(HTMLParser):
    def pre_handle(self, content):
        global str_Arr
        # print("content", content)
        styleTagAndText = re.findall("(<style.*?>.*?</style>)", content)
        scriptTagAndText = re.findall("(<script.*?>.*?</script>)", content)
        re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
        re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
        # print(styleTagAndText)
        for i in styleTagAndText:
            # print("-----------------正则替换style-----------------")
            content = content.replace(i,"",10)
        for i in scriptTagAndText:
            # print("-----------------正则替换script-----------------")
            content = content.replace(i,"",10)
        content=re_script.sub('',content) #去掉SCRIPT
        content=re_style.sub('',content)#去掉style
        return content
    
    def handle_starttag(self, tag, attrs):
        global str_Arr
        # print("Encountered a start tag:", tag)
        # if tag in tag_list:
            # str_Arr += "<p>"
            
    def handle_data(self, data):
        global str_Arr
        # print("Encountered some data  :", data)
        # if '&' not in data and 'sp' not in data and data != ' ' and data != '​':
        if data != '​': # 不占位置的空格
            str_Arr += data.strip()
    def handle_endtag(self, tag):
        global str_Arr
        # print("Encountered an end tag :", tag)
        if tag in tag_list:
            str_Arr += "<SEP>"

    def get_str(self):
        global str_Arr
        # styleTagAndText = re.findall("(<style.*?>.*?</style>)", str_Arr)
        # scriptTagAndText = re.findall("(<script.*?>.*?</script>)", str_Arr)
        # for i in styleTagAndText:
        #     str_Arr = str_Arr.replace(i,"",1)
        # for i in scriptTagAndText:
        #     str_Arr = str_Arr.replace(i,"",1)
        str_temp = str_Arr.replace("\n", "").replace("\t", "").replace("\"","“").replace("　", "").replace("<br><br><br><br><br><br>", "<br><br>").replace("<br><br><br><br><br>", "<br><br>").replace("<br><br><br><br>", "<br><br>").replace("<br><br><br>", "<br><br>")
        str_Arr = ""
        return str_temp


# chrome初始化
def chrome_init(self,url):
    self.page = 1   # 当前页面
    chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument(f'--proxy-server=tunnel3.qg.net:15997')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-service-autorun')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--password-store=basic')
    chrome_options.add_argument('--no-sandbox')
    self.url = url
    self.browser = uc.Chrome(version_main=111, options=chrome_options)


# 格式化content
def format_content(content_list):
    content = etree.tostring(content_list, encoding="utf-8").decode('utf-8')
    parser = MyHTMLParser()
    parser.feed(parser.pre_handle(content))
    content = parser.get_str()
    return content

        
class GetInfo():
    def __init__(self,url):
        self.url = url
        # self.headless = kwargs.get('headless')
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('detach', True)  # 不自动关闭浏览器
        self.options.add_argument('--incognito')
        self.options.add_argument("--disable-extensions")
        # self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--no-sandbox")
        self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        

        self.browser = webdriver.Chrome(options=self.options)
        # self.url = url
        # chrome_init(self, self.url)

    def get_page_content(self):
            
        if self.url != '' :
            print('url:',self.url)
            try:
                self.browser.get(self.url)
                time.sleep(random.uniform(1, 2))
                xml = etree.HTML(self.browser.page_source)
                    
                content_list = xml.xpath('//body')[0]
                content = format_content(content_list)
                
                self.browser.quit()
                content = re.sub('(<SEP>)+', '<SEP>', content) # 防止< >造成的影响, ()包括内容代表整体匹配
                return content
                    
            except Exception as e:

                print('e',e)
                self.browser.quit()
                return False
            
        self.browser.quit()
        return True

    
if __name__ == '__main__':
    url = 'https://mp.weixin.qq.com/s?__biz=MzI5Mjk2MTI1Nw==&mid=2247576230&idx=1&sn=74310ce3be129b7688a1d88f4b055cc4&chksm=ec7a8420db0d0d36ba32d6ab53a203d2e48b4b052839c70c8f206a9f34af249982b3751e0d0d&scene=27'
    
    res =  GetInfo(url).get_page_content()
    # print(res)
    noisy_text_clean(res, '严钧')
    # [ print(len(str)) for str in res.split('<SEP>')]
    # res = re.sub() 
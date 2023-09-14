from lxml import etree
import re
import time
import random
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ua = UserAgent()
# print(ua)
class SeleniumInit():
    """
    :selenium初始化
    :url: '待爬取的url地址'
    """
    # 初始化

    def __init__(self, **kwargs):
        self.url = kwargs.get("url")
        self.page = 1   # 当前页面
        self.latest_news = []
        chrome_options = uc.ChromeOptions()
        # chrome_options.add_argument(f'--proxy-server=tunnel3.qg.net:15997')
        # chrome_options.add_argument(f'--headless')
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
        # self.browser = uc.Chrome(version_main=110, options=chrome_options)

        flg = False
        
        try:
            self.browser = uc.Chrome(version_main=111, options=chrome_options)
        except Exception as e:
            print(e)
            time.sleep(10)
            cnt = 1
            while cnt < 10:
                try:
                    self.browser = uc.Chrome(version_main=111, options=chrome_options)
                except Exception as e:
                    print(e)
                    cnt += 1
                else:
                    cnt = 10
                    flg = True
        else:
            flg = True
        
        if flg is False:
            self.browser = None

        # self.browser.implicitly_wait(10)
        
    # def __init__(self,**kwargs):
    #     self.url = kwargs.get("url")
    #     self.page = 1   # 当前页面
    #     chrome_options = Options()
    #     chrome_options.add_argument('--headless')  # 无头模式
    #     # chrome_options.add_argument(f'--proxy-server=tunnel3.qg.net:11476')
    #     chrome_options.add_argument('--no-sandbox')
    #     chrome_options.add_argument('--disable-dev-shm-usage')
    #     chrome_options.add_argument('--disable-gpu')

    #     # 反爬，避免网站检测爬虫
    #     # chrome_options.add_experimental_option('useAutomationExtension', False)
    #     chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    #     # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    #     # 参数设置
    #     chrome_options.add_argument('--window-size=1300,1000')  # 设置窗口大小, 窗口大小会有影响.
    #     # chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48')
    #     chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36')           
    #     prefs = {"profile.managed_default_content_settings.images": 2,
    #              'permissions.default.stylesheet': 2, 'download.prompt_for_download': True, 'safebrowsing': True}
    #     # 禁止加载图片和css
    #     # chrome_options.add_experimental_option("prefs", prefs)
    #     # chrome_options.add_argument('blink-settings=imagesEnabled=false')
    #     # chrome_options.add_argument('--disable-gpu')
    #     self.browser = webdriver.Chrome(options=chrome_options)

    #     # 设置浏览器参数，webdriver：undefined，模拟现实浏览器
    #     self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    #         'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    #     })

    def page_parse(self, **kwargs):
        '''
        :解析url
        "return xml文本
        '''
        if kwargs:
            self.browser.get(kwargs.get('url'))
        time.sleep(random.uniform(1, 2))
        xml = etree.HTML(self.browser.page_source)
        return xml
 
    def element_format(self, td_tmp_list):
        '''
        :清洗element的冗余标签
        :现有功能：清楚所有标签
        '''
        res_list = []  # 总数据
        line_list = []  # 一行的数据
        slice_num = 0
        for item in td_tmp_list:
            # <td style="text-align:center;padding-top: 0px;"><a target="_blank" href="//www.bse.cn/newshare/listofissues_detail.html?id=2">833819</a></td>
            content = re.sub(r'<.+?>', '', etree.tostring(item,
                             encoding="utf-8").decode('utf-8'))
            slice_num += 1
            line_list.append(content)
            if slice_num % 10 == 0:
                res_list.append(line_list)
                line_list = []
                slice_num = 0
        return res_list

    def close_browser(self):
        '''
        :关闭browser
        '''
        self.browser.quit()

import requests
import lxml.html
import re
import time
import os
import random

from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait


REQUEST_URL0 = "mm.chinasareview.com"
REQUEST_URL1 = "http://www.meizitu.com/a/sexy_{0}.html"

PICTURE_PATH = "f:/meizitu"

# user_agent列表，每次执行requests请求都随机使用该列表中的user_agent，避免服务器反爬
user_agent_list = [
    # Windows / Firefox 58
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:58.0) Gecko/20100101 Firefox/58.0",
    # Linux / Firefox 58
    "Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0",
    # Mac OS X / Safari 11.0.2
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_2) AppleWebKit/603.1.13 (KHTML, like Gecko) Version/11.0.2 Safari/603.1.13",
    # Windows / IE 11
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    # Windows / Edge 16
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/16.16299.15.0",
    # Windows / Chrome 63
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    # Android Phone / Chrome 63
    "Mozilla/5.0 (Linux; Android 7.0; SM-G935P Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36",
    # Android Tablet / Chrome 63
    "Mozilla/5.0 (Linux; Android 4.4.4; Lenovo TAB 2 A10-70L Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Safari/537.36",
    # iPhone / Safari 11.1.1
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/11.1.1 Mobile/14E304 Safari/602.1",
    # iPad / Safari 11.1.1
    "Mozilla/5.0 (iPad; CPU OS 11_1_1 like Mac OS X) AppleWebKit/603.3.3 (KHTML, like Gecko) Version/11.1.1 Mobile/14G5037b Safari/602.1"]

# requests请求头
requests_header = {
    "Accept": "text/html,application/xhtml+xml,aplication/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,en-US;q=0.5",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    # "Host": "",
    # "Referer": "",
    "User-Agent": "",
    "Cookie": "__jsluid=348e7c7f1f7112204a6748ce0de5386a",
    "If-Modified-Since": "Sat, 01 Jul 2017 09:58:53 GMT",
    "If-None-Match": "34f136a550f2d21:108f",
}

# 使用requests下载html页面


def download_page_html(url):
    phtml = None

    try:
        requests_header["User-Agent"] = random.choice(user_agent_list) # 选择一个随机的User-Agent
        # print(requests_header)
        page = requests.get(url=url, headers=requests_header) # 请求指定的页面
        # print(page.encoding)
        page.encoding = "gb2312" # 转换页面的编码为gb2312(避免中文乱码)
        phtml = page.text # 提取请求结果中包含的html文本
        # print("requests success")
        page.close() # 关闭requests请求
    except requests.exceptions.RequestException as e:
        print("requests error:", e)
        phtml = None
    finally:
        return phtml

# 下载指定链接的图片文件


def download_picture(url, dir):
    try:
        picdir = "{0}/{1}".format(PICTURE_PATH, dir) # 构造图片保存路径
        # print(picdir)
        if os.path.exists(picdir) != True:
            os.makedirs(picdir) # 如果指定的文件夹不存在就递归创建

        pic_name = url.split("/")[-1] # 用图片链接中最后一个/后面的部分作为保存的图片名
        pic_full_name = "{0}/{1}".format(picdir, pic_name)

        # print("save picture to :", pic_full_name)

        requests_header["User-Agent"] = random.choice(user_agent_list) # 选择一个随机的User-Agent

        response = requests.get(url, headers=requests_header)  # 获取的文本实际上是图片的二进制文本
        imgdata = response.content  # 将他拷贝到本地文件 w 写  b 二进制  wb代表写入二进制文本
        if len(imgdata) > (5*1024):  # 只保存大于5k的图片
            with open(pic_full_name, 'wb') as f:
                f.write(imgdata) # 把图片数据写入文件。with语句会自动关闭f
            print("save picture to :", pic_full_name)
        else:
            print("picture size too small")
        response.close()
    except:
        print("download piccture {0} error".format(url))


# 获取所有需要爬取的页面数
def get_page_list_num(tree):

    page_list_num = 0

    try:
        # 使用xpath选择器选择html中指定的元素。
        gotolast = tree.xpath(
            "/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/div/ul/li[18]/a/@href")[0]  # sexy_33.html
        # print(gotolast)
        gotolast = str(gotolast)
        # print(gotolast)
        gotolast = re.sub(r"\D", "", gotolast)  # 把非数字字符串替换为空
        page_list_num = int(gotolast)  # 转化为整数
        print("max_page_number:", page_list_num)
    except:
        print("get page number error")
        page_list_num = 0
    finally:
        return page_list_num


def get_pagealbum_list(tree):  # 获取页面中的图片集列表
    pagealbum_list = []
    pagealbum_list = tree.xpath(
        "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/ul/li/div/div/a/@href")
    return pagealbum_list


def get_albumphoto_list(tree):  # 获取图集中的图片列表
    albumphoto_list = []
    albumphoto_list = tree.xpath(
        "/html/body/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/p/img/@src")
    return albumphoto_list


def get_albumphoto_title(tree):  # 获取图集中的标题
    albumphoto_title = None
    albumphoto_title = tree.xpath(
        "/html/body/div[2]/div[2]/div[2]/div[1]/div[1]/div[1]/h2/a/text()")[0]
    # print(albumphoto_title)
    return albumphoto_title


requests_url = REQUEST_URL1.format(1)
# print("requests_url :", requests_url)
# print(requests_header)

page_list_num = 0
page_list_idx = 1
webspider_sleep = 0
web_driver = None


def web_driver_init():
    global web_driver
    if web_driver == None:
        options = Options()
        options.add_argument('-headless')  # 无头参数
        # 配了环境变量第一个参数就可以省了，不然传绝对路径
        web_driver = Firefox(firefox_options=options)
        web_driver.implicitly_wait(20)


def web_driver_page(url):
    htmlpage = None
    try:
        web_driver.get(url)
        htmlpage = web_driver.page_source
    except:
        print("get webpage {0} error".format(url))
    finally:
        return htmlpage


def web_driver_exit():
    if web_driver != None:
        web_driver.close()


def meizitu_webspider():
    global page_list_num
    global page_list_idx
    global requests_url
    global webspider_sleep

    print("requests_url :", requests_url)
    page_html_list = download_page_html(requests_url)  # 下载当前页面
    if(page_html_list != None):
        # print(page_html_list)
        tree = lxml.html.fromstring(page_html_list)
        if page_list_num == 0:  # 计算当前共有多少个页面需要处理
            page_list_num = get_page_list_num(tree)

        pagealbum_list = get_pagealbum_list(tree)  # 获取当前页面中图集列表
        # print(pagealbum_list)
        for lst in pagealbum_list:  # 以此遍历当前页面中的每个图集
            print("album_list:", lst)
            # 图集使用的js异步加载图片，所以这里要用selenium加载动态页面
            albumphoto_page = web_driver_page(lst)
            # print(albumphoto_page)
            if albumphoto_page != None:
                tree0 = lxml.html.fromstring(albumphoto_page)

                albumphoto_title = get_albumphoto_title(tree0)  # 获取图集标题
                print("Title:", albumphoto_title)

                albumphoto_list = get_albumphoto_list(tree0)  # 获取图集中的图片列表
                for plst in albumphoto_list:
                    print("imgsrc:", plst)

                    download_picture(plst, albumphoto_title)  # 下载图片

                    webspider_sleep = random.randint(1, 5)  # 延时一个随机值，避免被服务器反爬
                    print("waiting {0} seconds".format(webspider_sleep))
                    time.sleep(webspider_sleep)

        if page_list_idx < page_list_num:  # 递归处理下一个页面
            page_list_idx = page_list_idx + 1
            requests_url = REQUEST_URL1.format(page_list_idx)
            meizitu_webspider()
        else:
            return 0


if __name__ == "__main__":
    web_driver_init()  # 初始化selenium
    meizitu_webspider()
    web_driver_exit()  # 退出selenium

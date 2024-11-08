import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import warnings


warnings.filterwarnings('ignore')
pd.set_option("display.max_columns",None)


def get_code(display_name):
    """
    Get security code by display_name
    :param display_name: e.g. 平安银行
    :return:
    """
    if not os.path.exists('./ALL_SECURITIES'):
        print("ALL_SECURITIES: file does not exist")
    else:
        file = open('ALL_SECURITIES', 'r', encoding='UTF-8')
        for line in file:
            if display_name in line:
                code = line.split(' ')[0]
                file.close()
                return code[:6]
        # if not find
        file.close()
        return None


def run():

    name = input("请输入上市公司名称（股票简称）: ")
    code = get_code(name)
    print(name, "的股票代码为：", code)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"') #防止403 Nginx forbidden.
    driver = webdriver.Chrome(chrome_options=options)
    url = "https://gushitong.baidu.com/stock/ab-" + code + "?mainTab=%E8%B4%A2%E5%8A%A1&sheet=%E5%88%A9%E6%B6%A6%E5%88%86%E9%85%8D%E8%A1%A8"
    print(url)
    driver.get(url)
    time.sleep(3)
    html = driver.execute_script('return document.documentElement.outerHTML')
    bsObj = BeautifulSoup(html, 'html.parser')

    content = bsObj.find("div", {"class": "report-title small-screen"})
    titles = []
    for i in content.findAll("div"):
        titles.append(i.text)
    print(titles)
    content = bsObj.findAll("div", {"class": "report-content-col"})[0]
    price = []
    for i in content.findAll("div", {"class": "price"}):
        price.append(i.text)
    print(price)
    same = []
    for i in content.findAll("div", {"class": "same"}):
        same.append(i.text)
    print(same)

    df = pd.DataFrame([titles,price,same]).T
    df.columns = ["title","price","same"]
    df.style.set_properties(**{'text-align': 'left'})
    print(df)


def run2():

    names = input("请输入上市公司名称（股票简称）列表，不同名称以空格隔开: ")
    names = names.split()

    if len(names)==0: return None

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument(
        'user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"')  # 防止403 Nginx forbidden.
    driver = webdriver.Chrome(chrome_options=options)

    result = pd.DataFrame()
    for name in names:
        code = get_code(name)
        print(name, "的股票代码为：", code)

        url = "https://gushitong.baidu.com/stock/ab-" + code + "?mainTab=%E8%B4%A2%E5%8A%A1&sheet=%E5%88%A9%E6%B6%A6%E5%88%86%E9%85%8D%E8%A1%A8"
        print(url)
        driver.get(url)
        time.sleep(3)
        html = driver.execute_script('return document.documentElement.outerHTML')
        bsObj = BeautifulSoup(html, 'html.parser')

        content = bsObj.find("div", {"class": "report-title small-screen"})
        titles = []
        for i in content.findAll("div"):
            titles.append(i.text)
        # print(titles)
        content = bsObj.findAll("div", {"class": "report-content-col"})[0]
        price = []
        for i in content.findAll("div", {"class": "price"}):
            price.append(i.text)
        # print(price)
        same = []
        for i in content.findAll("div", {"class": "same"}):
            same.append(i.text)
        # print(same)

        df = pd.DataFrame([titles, price, same]).T
        df.columns = ["财务指标","金额（"+name+"）","比率（"+name+"）"]
        df.set_index("财务指标", inplace=True)
        result = pd.concat([result,df],axis=1)

    print(result)


run2()


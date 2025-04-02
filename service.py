import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import warnings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    url = "https://gushitong.baidu.com/stock/ab-" + code + "?mainTab=%E8%B4%A2%E5%8A%A1&sheet=%E5%88%A9%E6%B6%A6%E5%88%86%E9%85%8D%E8%A1%A8"
    print(url)

    options = webdriver.ChromeOptions()
    # options.add_argument('headless') #headless访问可能会被认为是爬虫程序
    # options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"') #防止403 Nginx forbidden.
    options.add_argument("--disable-blink-features=AutomationControlled")  # 让 Selenium 看起来更像正常用户
    driver = webdriver.Chrome(options=options)
    # 执行 JavaScript 让 Selenium 伪装成真实用户
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """
    })

    # 请求目标网址
    driver.get(url)
    # 等待 .report-table-list-container 元素加载完成
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.report-table-list-container'))
    )
    # 获取图表容器
    container_html = driver.execute_script("""
        var container = document.querySelector('.report-table-list-container');
        return container ? container.innerHTML : "未找到容器";
    """)
    # print(container_html)

    bsObj = BeautifulSoup(container_html, 'html.parser')

    level1 = []
    content1 = bsObj.findAll("div", {"class": "report-row level-title"})
    for i in range(len(content1)-1): #剔除每股收益的两个指标，因其不在利润表内
        report_col_content = content1[i].findAll("div", {"class": "report-col-content"})
        title = report_col_content[0].find('div', class_='cos-line-clamp-1').text.strip()
        amount = report_col_content[1].find('div', class_='cos-line-clamp-1').text.strip()
        growth = report_col_content[1].find_all('div', class_='harmony-os-medium')[-1].text.strip()
        level1.append((i,title,amount,growth))
    print(level1)

    level2 = []
    content2 = bsObj.findAll("div", {"style": "display: block;"})
    for i in range(len(content2)-1): #剔除每股收益的两个指标，因其不在利润表内
        content2x = content2[i].findAll("div", {"class": "report-row level2"})
        for j in range(len(content2x)):
            report_col_content = content2x[j].findAll("div", {"class": "report-col-content"})
            title = report_col_content[0].find('div', class_='cos-line-clamp-1').text.strip()
            amount = report_col_content[1].find('div', class_='cos-line-clamp-1').text.strip()
            growth = report_col_content[1].find_all('div', class_='harmony-os-medium')[-1].text.strip()
            level2.append((i,title,amount,growth))
    print(level2)

    data = level1+level2
    data.sort(key=lambda x: x[0])
    new_data = [(item[1], item[2], item[3]) for item in data] #去掉元组首元素，即分组信息
    df = pd.DataFrame(new_data, columns=["指标", "金额(" + name + ")", "变动(" + name + ")"])
    df.set_index("指标", inplace=True)
    #df.style.set_properties(**{'text-align': 'left'})

    return df


def runBatch(names=None):
    """
    利润分配表
    :return:
    """
    if names is None:
        names = input("请输入上市公司名称（股票简称）列表，不同名称以空格隔开: ")
        names = names.split()
        if len(names)==0: return None

    options = webdriver.ChromeOptions()
    # options.add_argument('headless') #headless访问可能会被认为是爬虫程序
    # options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"') #防止403 Nginx forbidden.
    options.add_argument("--disable-blink-features=AutomationControlled")  # 让 Selenium 看起来更像正常用户
    driver = webdriver.Chrome(options=options)
    # 执行 JavaScript 让 Selenium 伪装成真实用户
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """
    })

    result = pd.DataFrame()
    for name in names:
        code = get_code(name)
        print(name, "的股票代码为：", code)
        url = "https://gushitong.baidu.com/stock/ab-" + code + "?mainTab=%E8%B4%A2%E5%8A%A1&sheet=%E5%88%A9%E6%B6%A6%E5%88%86%E9%85%8D%E8%A1%A8"
        print(url)

        # 请求目标网址
        driver.get(url)
        # 等待 .report-table-list-container 元素加载完成
        WebDriverWait(driver, 30).until( #根据网速进行调整
            EC.presence_of_element_located((By.CSS_SELECTOR, '.report-table-list-container'))
        )
        # 获取图表容器
        container_html = driver.execute_script("""
                    var container = document.querySelector('.report-table-list-container');
                    return container ? container.innerHTML : "未找到容器";
                """)
        # print(container_html)

        bsObj = BeautifulSoup(container_html, 'html.parser')

        level1 = []
        content1 = bsObj.findAll("div", {"class": "report-row level-title"})
        for i in range(len(content1) - 1):  # 剔除每股收益的两个指标，因其不在利润表内
            report_col_content = content1[i].findAll("div", {"class": "report-col-content"})
            title = report_col_content[0].find('div', class_='cos-line-clamp-1').text.strip()
            amount = report_col_content[1].find('div', class_='cos-line-clamp-1').text.strip()
            growth = report_col_content[1].find_all('div', class_='harmony-os-medium')[-1].text.strip()
            level1.append((i, title, amount, growth))
        print(level1)

        level2 = []
        content2 = bsObj.findAll("div", {"style": "display: block;"})
        for i in range(len(content2) - 1):  # 剔除每股收益的两个指标，因其不在利润表内
            content2x = content2[i].findAll("div", {"class": "report-row level2"})
            for j in range(len(content2x)):
                report_col_content = content2x[j].findAll("div", {"class": "report-col-content"})
                title = report_col_content[0].find('div', class_='cos-line-clamp-1').text.strip()
                amount = report_col_content[1].find('div', class_='cos-line-clamp-1').text.strip()
                growth = report_col_content[1].find_all('div', class_='harmony-os-medium')[-1].text.strip()
                level2.append((i, title, amount, growth))
        print(level2)

        data = level1 + level2
        data.sort(key=lambda x: x[0])
        new_data = [(item[1], item[2], item[3]) for item in data]  # 去掉元组首元素，即分组信息
        df = pd.DataFrame(new_data, columns=["指标", "金额(" + name + ")", "变动(" + name + ")"])
        df.set_index("指标", inplace=True)
        # df.style.set_properties(**{'text-align': 'left'})

        result = pd.concat([result,df],axis=1)

    # print(result)
    result.to_csv('result.csv', index=True, encoding='utf-8')


def test():
    # 2/4/2025
    top15 = ['工商银行'
        ,'建设银行'
        ,'农业银行'
        ,'中国银行'
        ,'邮储银行'
        ,'交通银行'
        ,'招商银行'
        ,'兴业银行'
        ,'浦发银行'
        ,'中信银行'
        ,'民生银行'
        ,'光大银行'
        ,'华夏银行'
        ,'平安银行']
    runBatch(top15)

#!/usr/bin/python
# coding:utf-8

"""
Author: Andy Tian
Contact: tianjunning@126.com
Software: PyCharm
Filename: dianping_spider.py
Time: 2019/3/24 13:21
"""
import time
import requests
from lxml import etree
import re
from redis import Redis
from settings import UserAgent, Cookies, hcf


# 获取店铺的url列表
def get_shop_url_list():
    url = 'https://www.dianping.com/beijing/ch10'
    headres = {
        'User-Agent': UserAgent,
        "Cookies": Cookies
    }
    resp = requests.get(url=url, headers=headres)
    Html = etree.HTML(resp.text)
    shop_url_list = Html.xpath('//div[@class="tit"]/a[1]/@href')
    return shop_url_list


def get_msgs(url):
    headres = {
        'User-Agent': UserAgent,
        'Cookie': Cookies,
        'referer': '{}'.format(url),
    }
    htmlstr = requests.get(url, headers=headres).text
    css_url = "http:" + re.findall(r'(//s3plus.meituan.net.*\.css?)">', htmlstr)[0]
    code_list = list(set(re.findall(r'class="(\w*?)"><', htmlstr)))
    return htmlstr, css_url, code_list


def get_comment_url_list(url):
    headres = {
        'User-Agent': UserAgent,
        'Cookie': Cookies}
    resp = requests.get(url=url + "/review_all", headers=headres)
    HTML = etree.HTML(resp.text)
    page_num = HTML.xpath('string(//div[@class="reviews-pages"]//a[last()-1]/text())')
    comment_url_list = []
    for page in range(1, int(page_num) + 1):
        comment_url_list.append("{}/review_all/p{}".format(url, page))
    return comment_url_list


# 通过css_url可以获取到css_info的信息 包括编码和gsv的关系 以及 编码和坐标的关系
def get_css_info(css_url):
    headres = {
        'User-Agent': UserAgent,
        'Cookie': Cookies}
    css_info = requests.get(url=css_url, headers=headres).text
    svg_url_list = re.findall(r'//s3plus.meituan.*?\.svg', css_info)
    label_list = re.findall(r'\w{1,4}\[class\^="\w{2,3}"\]', css_info)
    coor_list = list(set(re.findall(r"\..{5,6}{back.*?px;}", css_info)))

    # 不同开头的编码对应不同的 svg_url
    code_svginfo, code_svginfo_1 = {}, {}
    for label, svg_url in zip(label_list, svg_url_list):
        key = re.findall(r'.*\"(\w*)"', label)[0]
        resp = requests.get(url='http:' + svg_url, headers=headres)
        # code_svginfo[key] = resp
        code_svginfo_1[key] = resp.text

    # 不同的编码对应不同的坐标设置
    code_coor = {}
    for coor in coor_list:
        key = re.findall(r'(.*?){.*}', coor.lstrip("."))[0]
        value = re.findall(r'.*?:-(.*?)px;}', coor)[0].replace('.0', '').replace("px -", ',')
        value_x = int(value.split(",")[0])
        value_y = int(value.split(",")[1])
        code_coor[key] = (value_x, value_y)
    return code_svginfo_1, code_coor


def get_word(svginfo=None, code=None, coor=None, code_coor=None):
    if code_coor:
        coor = code_coor[code]
    HTML = etree.HTML(svginfo.encode())
    if HTML.xpath("//defs"):
        y_reffer_list = [int(x.replace("M0 ", '').replace(" H600", '')) for x in HTML.xpath('//path/@d')]
        y_reffer_list.append(int(coor[1]))
        reffer_y_index = sorted(y_reffer_list).index(int(coor[1])) + 1
        wordstr = \
            re.findall(r'<textPath xlink:href="#{}" textLength="\d\d\d">(.*?)</textPath>'.format(reffer_y_index),
                       svginfo)[
                0]
        length_list = [int(x) for x in re.findall(r'textLength="(\d\d\d)">', svginfo)]
        # div = 被除的这个数是length_list一组数的最大公约数
        div = hcf(length_list)
        word = wordstr[int(coor[0]) // div]
    else:
        y_reffer_list = [int(x) for x in HTML.xpath("//text/@y")]
        # div = hcf(y_reffer_list)
        y_reffer_list.append(int(coor[1]))
        y_reffer = y_reffer_list[sorted(y_reffer_list).index(int(coor[1]))]
        x_reffer_str = HTML.xpath("//text[@y='{}']/text()".format(y_reffer))[0]
        # div =  int(HTML.xpath('//text[@y={}]/@x'.format(y_reffer))[0].split(" ")[0])
        word = x_reffer_str[int(coor[0]) // 14]
    return word


def get_info(html):
    html = re.sub(r'<img class="emoji-img" src=.*? alt=""/>', '', html).replace("<br />", ',').replace("\n",
                                                                                                       '').replace("\t",
                                                                                                                   '')
    HTML = etree.HTML(html)
    info, score = {}, {}
    info['shop_name'] = HTML.xpath('string(//h1[@class="shop-name"]/text())')
    info['address'] = HTML.xpath('string(//div[@class="address-info"]/text())').split(":")[1].strip()
    info['teleNo'] = HTML.xpath('string(//div[@class="phone-info"])').split(":")[1].strip()
    info['reviewCount'] = HTML.xpath('string(//span[@class="reviews"]/text())')[:-3]
    info['avgPrice'] = HTML.xpath('string(//span[@class="price"]/text())').split("：")[1]
    info['good_tag'] = [x.split("(")[0].strip() for x in HTML.xpath('//div[@class="content"]/span/a/text()')]
    score['taste_score'] = \
        HTML.xpath('string(//div[@class="rank-info"]//span[@class="score"]/span[1]/text())').split("：")[1]
    score['enver_score'] = \
        HTML.xpath('string(//div[@class="rank-info"]//span[@class="score"]/span[2]/text())').split("：")[1]
    score['serve_score'] = \
        HTML.xpath('string(//div[@class="rank-info"]//span[@class="score"]/span[3]/text())').split("：")[1]
    info['score'] = score
    return info


def get_comment(html):
    html = re.sub(r'<img class="emoji-img" src=.*? alt=""/>', '', html).replace("<br />", ',').replace("\n",
                                                                                                       '').replace("\t",
                                                                                                                   '')
    HTML = etree.HTML(html)
    name_com = []
    names = [x.strip() for x in HTML.xpath('//div[@class="reviews-items"]//a[@class="name"]/text()')]
    comments = [x.strip() for x in HTML.xpath('//div[@class="review-words Hide"]/text()')[::2]]
    for name, com in zip(names, comments):
        n_c = {}
        n_c[name] = com
        name_com.append(n_c)
    return name_com


def main():
    # 做数据库连接
    redis = Redis(host='localhost', port=6379, decode_responses=True)
    loop = 0
    for url in get_shop_url_list():
        # 如果是第一次连接数据库,先将数据库信息清零
        if loop == 0:
            redis.flushall()
            loop += 1
        # 评论的url列表
        loop_in = 0
        name_com_list = []
        comment_url_list = get_comment_url_list(url)
        for url in comment_url_list:
            htmlstr, cssurl, code_list = get_msgs(url)
            # 店铺首页的html源码  str
            # cssurl 提取的样式的地址(包含坐标) str
            # code_list  code的列表 list
            if redis.exists(cssurl):
                for code in code_list:
                    if len(code) == 5 or len(code) == 6:
                        k = code[:-3]
                        svginfo = redis.get(k)
                        coorstr = redis.get("{}".format(code))
                        coor = tuple(int(x) for x in coorstr.split(","))
                        word = get_word(svginfo=svginfo, code=code, coor=coor)
                        patten = re.compile(r'<\w{1,4} class="%s"></\w{1,4}>' % code)
                        htmlstr = re.sub(patten, word, htmlstr)

            if not redis.exists(cssurl):
                redis.set(cssurl, "a")
                code_svginfo, code_coor = get_css_info(cssurl)
                # code_svginfo 字典类型,k为代码前三位,v为包含svg信息的response
                # code_coor  字典类型,k为代码,v为代码对应的坐标
                for k, v in code_svginfo.items():
                    redis.set(k, v)
                for code, coor in code_coor.items():
                    redis.set('{}'.format(code), str(coor[0]) + "," + str(coor[1]))
                for code in code_list:
                    if len(code) == 5 or len(code) == 6:
                        k = code[:-3]
                        svginfo = code_svginfo[k]
                        word = get_word(svginfo=svginfo, code=code, code_coor=code_coor, coor=None)
                        patten = re.compile(r'<\w{1,4} class="%s"></\w{1,4}>' % code)
                        htmlstr = re.sub(patten, word, htmlstr)

            if loop_in == 0:
                info = get_info(htmlstr)
                loop_in += 1

            n_com_list = get_comment(htmlstr)
            name_com_list += n_com_list
            info['user_com'] = name_com_list
            time.sleep(2)
        time.sleep(5)


if __name__ == "__main__":
    main()

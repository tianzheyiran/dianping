#!/usr/bin/python
# coding:utf-8

"""
Author: Andy Tian
Contact: tianjunning@126.com
Software: PyCharm
Filename: settings.py
Time: 2019/3/13 23:55
"""

UserAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36'
Cookies = '_hc.v=98490d0f-353e-5877-da3b-8141fe8f4414.1552360560; _lxsdk_cuid=1696fffead48e-0041f73916061d-6b111b7e-144000-1696fffead5c8; _lxsdk=1696fffead48e-0041f73916061d-6b111b7e-144000-1696fffead5c8; s_ViewType=10; aburl=1; Hm_lvt_4c4fc10949f0d691f3a2cc4ca5065397=1552368064; cy=2; cye=beijing; _dp.ac.v=6fc1b89d-2a21-479b-b2c2-c4686e78a7f7; ua=%E5%A4%A9%E8%BE%84%E7%BE%BF%E5%86%89; ctu=0f25cd7ad54b105fc1f422312db6baa2dd8369ca5d2f3caaecefc407f693c91c; uamo=15321318603; dper=c9a75c8481b5d501bb41f26404b1a6690574135aebbbe9777f06c3688f777b468ec67a40adccecec6bfd5ebfacb4fbf2b70db1b32d6b0878181e595377c34c6c229b507b7329dac4d719dc3b233c717139d3129e12f2c037efb6fb03dd6bbd4b; ll=7fd06e815b796be3df069dec7836c3df; _lx_utm=utm_source%3Dwww.sogou%26utm_medium%3Dorganic; _lxsdk_s=169af16f0ce-600-0f1-973%7C%7C41'


def hcf(array):
    min_num = min(array)
    min_num_hcf = []
    for i in range(1, min_num + 1):
        if min_num % i == 0:
            min_num_hcf.append(i)

    for j in array:
        for k in min_num_hcf:
            if j % k != 0:
                min_num_hcf.remove(k)

    return max(min_num_hcf)


if __name__ == "__main__":
    array = [121, 132, 143, 220, 330]
    num = hcf(array)
    print(num)

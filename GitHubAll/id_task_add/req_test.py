# -*- coding: utf-8 -*-
# @Time    : 2023-11-22 14:55
# @Author  : Liu
# @Site    : 
# @File    : req_test.py
# @Software: PyCharm

import requests

headers = {
    'authority': 'github.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'cookie': '_octo=GH1.1.1152434039.1699942516; preferred_color_mode=light; tz=Asia%2FShanghai; _device_id=7ce4064b9aa0a6c8c426d140c9e49702; saved_user_sessions=73265739%3AYDIzQx29jPfgOzYDQ5d6Dx4-ctZA0UPa0X7Vbylu3N_26aYM; user_session=YDIzQx29jPfgOzYDQ5d6Dx4-ctZA0UPa0X7Vbylu3N_26aYM; __Host-user_session_same_site=YDIzQx29jPfgOzYDQ5d6Dx4-ctZA0UPa0X7Vbylu3N_26aYM; tz=Asia%2FShanghai; color_mode=%7B%22color_mode%22%3A%22auto%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark%22%2C%22color_mode%22%3A%22dark%22%7D%7D; logged_in=yes; dotcom_user=liulijun-king; has_recent_activity=1; _gh_sess=h9BlXD1l9FuPx%2BUB%2Fv6UX3UzUZ3UlXgKPqre4bXKZLd4P4Uha5MsSo0F6ZEQSTtwlRFHZsQrdpPR2ODZo69Hvp2%2FmDHUfvuuiM89UR4iO1POWj4qUJ5QgNr9I049SLHiN%2FW420Md5Sl155LIUTF0fw0jFp9%2BpA2F1Z%2F6GnO%2BzqAf9w6ZwRFr4GXaFQK94LG9Sn9%2FWNfx4t1C6mLG78dBYVxXYg7BSLLRjjc4EryGPejCQqtIpF5tDqedFd1ITDqCHml4AzRQPYd5DM%2FtseFYov%2FWSZ62IkxfoQWPMA9%2F3VxhuoO3GiQKZ9jxba3F%2F3%2FTtqzGfiHt%2BIumQ87J5lNGloGaFyDvTd9aRcgJEpNaULkkec%2B13A6c1bzX613Z2VgFwNkA6uDdryVLcs7OXtKT4j5HQCXmt97lqWdLdsV6MPcQ%2B%2FuIVWg4g6h3S1wsyp6FyASlYrU%2FM5RQ3DIuFgiWOBQ3VeqU7TbTfb%2FOmPWP5Yt%2BkLD9cz1QM9YlKV0xNQqztIK30v%2FS6u%2FAmJidm6NtH5DM%2FFB3kgC8pNx3lJBdLndwdHGopM30ExqV6h9q13i5etcolTy%2BrCmFdDbz4dQbWE4%2FSveh6myqH%2FTL7x2Cs2q5YNi9qHqDiv00MP9UvhWphMRPqPNCl6%2Fbc1TPDrROl4UBC6VznTgY24nO4XjdFCRIsZ9gvN65qg%2BsXWZ7Wp6zrwHxy4DTtGp%2FIlO%2BRhpQurm5%2F9KIv8W%2FWxOTYoIsky3F88v9RFz5oXz1%2FedZyx1axn33jtbNxAVf3p0DVOfVY%2FlR3itSJeysabFhwhbyEr9oEoT1%2FqP8bkbbBssJCmjW4rfk92xBh58MLXcPU1qh3IcW5qFkDiW85hbsV6dxuC0bLGnYB%2F8DINS8jp5zL601k5zveqW2aD%2BjXFVQyegG%2BZoKUxM6GZJ08rs9OaBh%2FrFhIpKz9JMSrit%2FNE3fzY7nJnbmVnNdUuHhEpGI4%2FPnMHjqInBizWxbNd2ykRTpEdbKjiNhtfimLQ522UYLkEh5T7PlEHiCKf%2FZrbZnMAChmg%3D%3D--txEO1tevLBuXTEgH--wGCeu9tZ4NzZNnRDC%2F9j2w%3D%3D',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

response = requests.get('https://github.com/cafebazaar', headers=headers, proxies={
    "http": "http://shengmingxing_zxcj-zone-custom:zxc_2023@679e234e86e0ed04.na.ipidea.online:2333",
    'https': "http://shengmingxing_zxcj-zone-custom:zxc_2023@679e234e86e0ed04.na.ipidea.online:2333"})
print(response.content.decode())

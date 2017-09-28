#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request
import re
import bs4
import hashlib
import mongo
import time


maxcount = 100000  # 数据数量
#2,3,4,5/channel?cat=5
home = ['https://baijia.baidu.com','https://baijia.baidu.com','https://baijia.baidu.com/channel?cat=1','https://baijia.baidu.com/channel?cat=2','https://baijia.baidu.com/channel?cat=3','https://baijia.baidu.com/channel?cat=4','https://baijia.baidu.com/channel?cat=5']  # 起始位置

url_set = set()
url_old = set()
request_headers = {
"Accept-Language": "en-US,en;q=0.5",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Referer": "http://www.baidu.com",
"Connection": "keep-alive"
}

def getnews():
    for homeurl in home:
        request = urllib.request.Request(homeurl, headers=request_headers)
        html = urllib.request.urlopen(request, timeout=5).read().decode('utf8')
        print(home)
        #print(html)
        soup = bs4.BeautifulSoup(html, 'html.parser')
        #links = soup.find_all(href=re.compile("id="),target="_blank")
        links = soup.find_all(href=re.compile("id="), target="_blank")
        for link in links:
            url_set.add(link.get('href'))
            #print(link)
            #print(url_set)

        count = 0
        while len(url_set) != 0:
            try:
                url = url_set.pop()
                url_old.add(url)
                #base = "https://baijia.baidu.com"
                base = "https://baijia.baidu.com"
                request = urllib.request.Request(base+url, headers=request_headers)
                html = urllib.request.urlopen(request, timeout=5).read().decode('utf8')
                #print(html)
                soup = bs4.BeautifulSoup(html, 'html.parser')
                links = soup.find_all(href=re.compile("id="),target="_blank")

                # 获取URL
                for link in links:
                    if link['href'] not in url_old:
                        url_set.add(link.get('href'))
                url = (base+url).strip()
                id = hashlib.md5(url.encode("utf-8")).hexdigest()
                title = soup.find("h1", attrs={"class": "title"}).get_text()
                print(url+","+title.strip())
                pubtime = soup.find("span", attrs={'class': 'time'}).get_text()
                #transinto timestamp
                pubDate = time.mktime(time.strptime(pubtime, '%Y-%m-%d %H:%M'))
                #print(pubDate.strip())
                content = soup.find("section", attrs={'class': 'news-content'}).get_text()
                #print(url)
                newsdata = {"id": id, "content": content, "title": title, "pubDate": pubDate, "url": url}
                #print(id)
                #print(pubDate)
                if mongo.selectByTitle(title):
                    mongo.insert_one_news(newsdata)

            except Exception as e:
                print(e)
                continue
            else:
                print(title)
                count += 1
            finally:
                # 判断数据是否收集完成
                if count == maxcount:
                    break
getnews()

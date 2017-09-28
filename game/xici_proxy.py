#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-9-4 下午8:24
# @Author  : ai-i-luru@interns.chuangxin.com

#xicidaili
import urllib2
import re
import threading
import time

rawProxyList = []
checkedProxyList = []
request_headers = {
"Accept-Language": "en-US,en;q=0.5",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Referer": "http://www.baidu.com",
"Connection": "keep-alive"
}
# 抓取代理网站
targets = []
for i in range(1, 7):
    target = r"http://www.xici.net.co/nn/%d" % i
    targets.append(target)
# print targets

# 正则
p = re.compile(r'<tr class=".+?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>.+?(\d{2,4})</td>.+?<td>(.{4,5})</td>',
               re.DOTALL)


# 获取代理的类
class ProxyGet(threading.Thread):
    def __init__(self, target):
        threading.Thread.__init__(self)
        self.target = target

    def getProxy(self):
        print "目标网站：" + self.target
        request = urllib2.Request(self.target, headers=request_headers)
        req = urllib2.urlopen(request, timeout=5)
        result = req.read()
        matchs = p.findall(result)
        for row in matchs:
            ip = row[0]
            port = row[1]
            agent = row[2]
            addr = agent + '://' + ip + ':' + port
            proxy = [ip, port, addr]
            rawProxyList.append(proxy)

    def run(self):
        self.getProxy()

        # 检验代理类


class ProxyCheck(threading.Thread):
    def __init__(self, proxyList):
        threading.Thread.__init__(self)
        self.proxyList = proxyList
        self.timeout = 5
        self.testUrl = "http://www.baidu.com/"
        self.testStr = "030173"

    def checkProxy(self):
        cookies = urllib2.HTTPCookieProcessor()
        for proxy in self.proxyList:
            proxyHandler = urllib2.ProxyHandler({"http": r'http://%s:%s' % (proxy[0], proxy[1])})
            opener = urllib2.build_opener(cookies, proxyHandler)
            opener.addheaders = [('User-Agent',
                                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36')]
            t1 = time.time()
            try:
                req = opener.open(self.testUrl, timeout=self.timeout)
                result = req.read()
                timeused = time.time() - t1
                pos = result.find(self.testStr)

                if pos > 1:
                    checkedProxyList.append((proxy[0], proxy[1], proxy[2], timeused))
                else:
                    continue
            except Exception, e:
                continue

    def run(self):
        self.checkProxy()


if __name__ == "__main__":
    getThreads = []
    checkThreads = []

# 对每个目标网站开启一个线程负责抓取代理
for i in range(len(targets)):
    t = ProxyGet(targets[i])
    getThreads.append(t)

for i in range(len(getThreads)):
    getThreads[i].start()

for i in range(len(getThreads)):
    getThreads[i].join()

print '.' * 10 + "总共抓取了%s个代理" % len(rawProxyList) + '.' * 10

# 开启20个线程负责校验，将抓取到的代理分成20份，每个线程校验一份
for i in range(20):
    t = ProxyCheck(rawProxyList[((len(rawProxyList) + 19) / 20) * i:((len(rawProxyList) + 19) / 20) * (i + 1)])
    checkThreads.append(t)

for i in range(len(checkThreads)):
    checkThreads[i].start()

for i in range(len(checkThreads)):
    checkThreads[i].join()

print '.' * 10 + "总共有%s个代理通过校验" % len(checkedProxyList) + '.' * 10

# 持久化
data = []
f = open("proxy_list.txt", 'w+')
for proxy in sorted(checkedProxyList, cmp=lambda x, y: cmp(x[3], y[3])):
    print "checked proxy is: %s:%s\t%s\t%s" % (proxy[0], proxy[1], proxy[2], proxy[3])
    f.write("%s:%s\t%s\t%s\n" % (proxy[0], proxy[1], proxy[2], proxy[3]))
    data.append(proxy[2])
f.close()
print data

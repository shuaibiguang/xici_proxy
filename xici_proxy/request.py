from fake_useragent import UserAgent
import requests
import http.cookiejar as cookielib
from lxml import etree
import re
import pymysql.cursors
from urllib import parse

class db:
    host = "localhost"
    user = "root"
    password = ''
    db = "ip_proxy"
    
    def __init__(self):
        self.connection = pymysql.connect(host=self.host, user=self.user,password=self.password,db=self.db,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

    # 再插入之前首先验证数据是否存在
    def is_exist(self,ip):
        with self.connection.cursor() as cursor:
            sql = """
            select * from ip_list where ip = %s
            """
            cursor.execute(sql, ip)
            result = cursor.fetchall()
            if len(result) == 0:
                return True
            else:
                return False

    #插入数据
    def save_ip(self,ip,port,type):
        if self.is_exist(ip):
            with self.connection.cursor() as cursor:
                sql = """
                insert into ip_list (ip,port,type) values (%s,%s,%s)
                """
                cursor.execute(sql,(ip,port,type))
                self.connection.commit()
                print ("插入成功,ip:"+ip)
        

class paqu:
    ua = UserAgent()
    db = db()
    headers = {
        "HOST":"www.xicidaili.com",
        "Referer":"http://www.xicidaili.com",
        "User-Agent":ua.random
    }

    session = requests.session()
    session.cookie = cookielib.LWPCookieJar(filename="cookors.txt")

    try:
        session.cookies.load(ignore_discard=True)
    except:
        print ('未能加载cookir')


    def main(self,url = "http://www.xicidaili.com/nn/"):
        html = self.session.get(url,headers=self.headers).content
        dom = etree.HTML(html)
        ip_list = dom.xpath('//table[@id="ip_list"]')
        trs = ip_list[0].xpath('tr')
        for tr in trs:
            tds = tr.xpath('td')
            if (len(tds) > 0):
                ip = tds[1].xpath('text()')[0]
                prot = tds[2].xpath('text()')[0]
                http_type = tds[5].xpath('text()')[0]
                seep = tds[6].xpath('div/div/@style')[0]
                # 正则处理下载速度，如果低于70%pass掉
                se = re.findall(".*:(\d+)%",seep)
                if se:
                    seep = se[0]
                    if int(seep) > 70:
                        # 开始入库
                        self.db.save_ip(ip,prot,http_type)
        next_page = dom.xpath('//a[@class="next_page"]/@href')
        if next_page:
            page_url = parse.urljoin(url, next_page[0])
            return self.main(page_url)

p = paqu()
p.main()






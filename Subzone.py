'''
Created on 2017-12-13

@author: Administrator
'''

# -*- coding:utf-8 -*-

import threading
import queue
import time
import requests
from bs4 import BeautifulSoup
import logging
from HouseFetcher import HouseFetcher
import os


headers = {
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'zh-CN,zh',
'Connection':'keep-alive',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
'Upgrade-Insecure-Requests':'1'
}


href_exit='exit'

class Subzone:
    def __init__(self, zone, subzone, url, house_queue):
        self.zone=zone
        self.subzone=subzone
        self.href_queue=queue.Queue()
        self.house_queue=house_queue
        self.session_discover = requests.Session()
        self.session_discover.headers.update(headers)
        self.url=url
        self.host='https://nj.lianjia.com'
        
        #make directory for zone and subzone
        if not os.path.exists(zone):
            os.mkdir(zone)
        
        subzonedir=r'%s\%s'%(zone, subzone)
        if not os.path.exists(subzonedir):
            os.mkdir(subzonedir)
        
    def startwork(self):
        # excel writer
        #filename = '%s-%s'%(self.zone, self.subzone)
        #persister = ExcelPersister(filename, self.house_queue)
        #persister.startwork()
        
        discover_thread = threading.Thread(target=self.discoverhouselink, name='discover house linkage thread')
        discover_thread.start();
        
        threads=[]
        for i in range(1, 7):
            detail_thread=threading.Thread(target=self.gethousedetail, name='house detail fetch thread %d'%i)
            threads.append(detail_thread)
            i = i+1
        
        #start detail thread
        for t in threads:
            t.start();
        
        discover_thread.join();
        
        for t in threads:
            t.join();

        #persister.stopwork();
    
    def discoverhouselink(self):
        try:
            r=self.session_discover.get(self.url, verify=False);
            firstpage = r.text
            self.houselinkfrompage(firstpage)
            
            totalpage=self.totalpage(firstpage)
            i = 2
            while i <= totalpage:
                url = self.url + 'pg%d'%i
                time.sleep(1)
                
                try:
                    r=self.session_discover.get(url, verify=False)
                    self.houselinkfrompage(r.text)
                except BaseException as ex:
                    logging.error('catch an exception with [%s] %s'%(url,ex))
                    
                i=i+1
        except BaseException as ex:
            logging.error('catch an exception %s'%ex)
        self.href_queue.put(href_exit) #put a dummy href for exit
    
    def houselinkfrompage(self, page):
        bf=BeautifulSoup(page, 'html.parser')
        selllisttag=bf.find(name='ul', attrs={'class':'sellListContent'})
        titletags=selllisttag.find_all(name='div', attrs={'class':'title'})
        for titletag in titletags:
            atag=titletag.find(name='a')
            link=atag['href']
            logging.debug("get a house linkage:%s"%link)
            self.href_queue.put(link)
    
    def totalpage(self, page):
        bf=BeautifulSoup(page, 'html.parser')
        pagesdivtag=bf.find(name='div', attrs={'class':'page-box house-lst-page-box'})
        pagedata=pagesdivtag['page-data']
        pagedic=eval(pagedata) #convert string to dictionary
        totalpage=pagedic['totalPage']
        return totalpage
    
    def gethousedetail(self):
        path='%s\\%s'%(self.zone, self.subzone)
        s = requests.Session()
        
        while True:
            href=self.href_queue.get()
            if href==href_exit:               #no more task
                self.href_queue.put(href_exit)
                return

            #deal with the house detail
            try:
                fetch = HouseFetcher(self.subzone, href, s, path)
                housedetail=fetch.dowork()
                if housedetail is None:
                    logging.error("can not get the detail for url %s"%href)
                else:
                    housedetail.url=href
                    self.house_queue.put(housedetail)
                    #logging.warn('[%s] get a house %s'%())
            except BaseException as ex:
                logging.error('catch an exception %s'%ex)
            finally:
                time.sleep(1)
               
    
if __name__ == '__main__':
    begin = time.time()
    subzone=Subzone('gulou', 'caochangmendajie', 'https://nj.lianjia.com/ershoufang/caochangmendajie/')
    subzone.startwork()
    end = time.time()
    input("all search is done and take %d second!"%(end-begin))
    
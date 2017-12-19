'''
Created on 2017-12-15

@author: Administrator
'''

# -*- coding:utf-8 -*-

import threading
import Subzone
import requests
import logging
import queue
import ExcelPersister
from bs4 import BeautifulSoup

#import requests.urllib3.exceptions.InsecureRequestWarning
requests.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)

#config the log
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='housescrapper.log',
                filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class Zone:
    def __init__(self, zone, zone_url):
        self.zone = zone
        self.url = zone_url
        self.host='https://nj.lianjia.com'
        self.house_queue=queue.Queue()
        
    def scrapysubzone(self):
        zone_session = requests.Session()
        zone_session.headers.update(Subzone.headers)
        
        persister = ExcelPersister.ExcelPersister(self.zone, self.house_queue)
        persister.startwork()
        
        try:
            zone_response = zone_session.get(self.url, verify=False)
            subzones = self.getsubzones(zone_response.text)
            logging.debug('get subzones %s'%subzones)
            threads=[]
            for (key, value) in subzones.items():
                subzone=Subzone.Subzone(self.zone, key, value, self.house_queue)
                t=threading.Thread(target=subzone.startwork, name='subzone_%s'%key)
                threads.append(t)
                t.start()
                t.join()
                logging.debug('finish scrap the house in %s %s'%(self.zone, key))
                
        except BaseException as e:
            logging.error('catch an exception %s'%e)
        
        persister.stopwork()
    
    def getsubzones(self, text):
        subzones = {}
        bs = BeautifulSoup(text, 'html.parser')
        #logging.debug('text is %s'%text)
        secondhandtags = bs.find(name='div', attrs={'data-role':'ershoufang'})
        subtags=secondhandtags.find_all(name='div')
        hrefs = subtags[1].find_all(name='a');
        for tag in hrefs:
            subzones[tag.text.strip()] = self.host + tag['href']
        return subzones

if __name__ == '__main__':
    zone = Zone('秦淮', 'https://nj.lianjia.com/ershoufang/qinhuai/')
    zone.scrapysubzone()
    #merge = Excelmerge.Excelmerge('鼓楼')
    #merge.merge()
   
            
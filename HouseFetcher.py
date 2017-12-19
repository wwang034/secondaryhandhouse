'''
Created on 2017-12-10

@author: Administrator
'''
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import requests
import logging
import os
import time
from House import House
from ExcelPersister import ExcelPersister


headers = {
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'zh-CN,zh',
'Connection':'keep-alive',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
'Upgrade-Insecure-Requests':'1'
}

class HouseFetcher(object):
    def __init__(self, subzone, url, session, path):
        self.url = url
        self.session = session
        self.path = path
        self.subzone = subzone
        
    def saveimg(self, housedetail, houseobj):
        bf=BeautifulSoup(housedetail, 'html.parser')
        
        #title for the directory name
        titleTag = bf.find(name='title')
        title=titleTag.text
        
        picUlTag=bf.find(name='ul', attrs={'class':'smallpic'})
        picTags = picUlTag.find_all(name='li')
            
        #make a directory with name same as title
        try:
            dir= self.path + '\\' + title+'\\'
            houseobj.imgpath=dir
            if not os.path.exists(dir): 
                os.mkdir(dir)
                
            self.session.headers.update({'Host':'image1.ljcdn.com'})
            for tag in picTags: #save the picture
                imgsrc=tag['data-src']
                
                #find image name
                imgname=''
                if hasattr(tag, 'data-desc'):
                    imgname=tag['data-desc']+'.jpg'
                
                if imgname=='':
                    imgname=imgsrc[imgsrc.rfind('/')+1:] 
                
                # fetch the image
                imgResponse = self.session.get(imgsrc, verify=False)
                       
                # write the image
                fd=open(dir+imgname, 'wb')
                fd.write(imgResponse.content)
                fd.close()
                    
                #time.sleep()
        except BaseException as ex:
            logging.error('catch an exception: %s'%str(ex))
            return False
        
        return True
    
    def savedetail(self, housedetail, houseobj):
        text = housedetail
        
        try:
            bf=BeautifulSoup(text, 'html.parser')
            
            houseobj.subzone=self.subzone
            
            #total price
            totalpricetag=bf.find(name='span', attrs={'class':'total'})
            if totalpricetag is not None:
                totalprice=totalpricetag.text;
                houseobj.totalprice = totalprice
            
            #unit price
            unitpricetag=bf.find(name='span', attrs={'class':'unitPriceValue'})
            if unitpricetag is not None:
                unitprice=unitpricetag.text;
                houseobj.unitprice=unitprice
            
            #room info
            roomtag=bf.find(name='div', attrs={'class':'room'})
            if roomtag is not None:
                roommaininfotag=roomtag.find(name='div', attrs={'class':'mainInfo'})
                if roommaininfotag is not None:
                    roommaininfo=roommaininfotag.text
                    houseobj.roommaininfo=roommaininfo
            
            #subinfo
                roomsubinfotag=roomtag.find(name='div', attrs={'class':'subInfo'})
                if roomsubinfotag is not None:
                    roomsubinfo=roomsubinfotag.text
                    houseobj.roomsubinfo=roomsubinfo
            
            #type
            typetag=bf.find(name='div', attrs={'class':'type'})
            #main info
            if typetag is not None:
                typemaininfotag=typetag.find(name='div', attrs={'class':'mainInfo'})
                if typemaininfotag is not None:
                    typemaininfo=typemaininfotag.text
                    houseobj.typemaininfo=typemaininfo
            
            #subinfo
                typesubinfotag=typetag.find(name='div', attrs={'class':'subInfo'})
                if typesubinfotag is not None:
                    typesubinfo=typesubinfotag.text
                    houseobj.typesubinfo=typesubinfo
            
            #area and build time
            areaandtimetag=bf.find(name='div', attrs={'class':'area'})
            if areaandtimetag is not None:
                areatag=areaandtimetag.find(name='div', attrs={'class':'mainInfo'})
                if areatag is not None:
                    area=areatag.text
                    houseobj.area=area
            
                buildTimeTag=areaandtimetag.find(name='div', attrs={'class':'subInfo'})
                if buildTimeTag is not None:
                    buildTime=buildTimeTag.text
                    houseobj.buildtime=buildTime
            
            #title for the house
            titleTag = bf.find(name='title')
            if titleTag is not None:
                title=titleTag.text
            #print('title is %s'%title)
                houseobj.subject=title
            
            #broker and phone
            brokertag=bf.find(name='div', attrs={'class':'brokerInfo clear'})
            if brokertag is not None:
                brokercontacttag=brokertag.find(name='a', attrs={'class':'name LOGCLICK'})
                if brokercontacttag is not None:
                    houseobj.brokername=brokercontacttag.text
            
                phonetag=brokertag.find(name='div', attrs={'class':'phone'})
                if phonetag is not None:
                    phone=phonetag.text
                    houseobj.brokerphone=phone
            
            #transaction detail
            transactiontag=bf.find(name='div', attrs={'class':'transaction'})
            if transactiontag is not None:
                transdetailtags=transactiontag.find_all(name='li')
                if len(transdetailtags) == 8:
                    #print('sell begin time is %s'%transdetailtags[0].text)
                    houseobj.beginsell=transdetailtags[0].text.strip()[4:]
                    #print('transaction type is %s'%transdetailtags[1].text)
                    houseobj.transactiontype=transdetailtags[1].text.strip()[4:]
                    #print('last sell time is %s'%transdetailtags[2].text)
                    houseobj.lastselltime=transdetailtags[2].text.strip()[4:]
                    #print('usage of house is %s'%transdetailtags[3].text)
                    houseobj.usage=transdetailtags[3].text.strip()[4:]
                    #print('house year is %s'%transdetailtags[4].text)
                    houseobj.year=transdetailtags[4].text.strip()[4:]
                    #print('belonging right is %s'%transdetailtags[5].text)
                    houseobj.right=transdetailtags[5].text.strip()[4:]
                    #print('mortage info is %s'%transdetailtags[6].text)
                    houseobj.mortage=transdetailtags[6].text.strip()[4:]
                    #print('attachment of house %s'%transdetailtags[7].text)
                    houseobj.attachment=transdetailtags[7].text.strip()[4:]
                else:
                    logging.warn('transaction detail tags\' count is not 8 but %d'%len(transdetailtags))
                
            #more detail
            moredetailtag=bf.find(name='div', attrs={'class':'introContent showbasemore'})
            if moredetailtag is not None:
                baseattrstag=moredetailtag.find_all(name='div', attrs={'class':'baseattribute clear'})
                if baseattrstag is not None:
                    for tag in baseattrstag:
                        nametag=tag.find(name='div', attrs={'class':'name'})
                        contenttag=tag.find(name='div', attrs={'class':'content'})
                        
                        #print('[%s]:%s'%(nametag.text, contenttag.text))
                        
                        if nametag.text=='核心卖点':
                            #print('key sell points is %s'%(contenttag.text))
                            houseobj.sellpoint=contenttag.text.strip()
                        elif nametag.text=='户型介绍':
                            #print('house type introduction is %s'%(contenttag.text))
                            houseobj.introduction=contenttag.text.strip()
                        elif nametag.text=='税费解析':
                            #print('tax illustration is %s'%(contenttag.text))
                            houseobj.taxillustration=contenttag.text.strip()
                        elif nametag.text=='小区介绍':
                            #print('area introduction is %s'%(contenttag.text))
                            houseobj.areaintroduction=contenttag.text.strip()
        except BaseException as ex:
            logging.error('catch an exception: %s'%str(ex))
            return False
        
        return True
        
    def dowork(self):
        house=House()
        try:
            self.session.headers.update({'Host':'nj.lianjia.com'})
            r = self.session.get(self.url, verify=False)
            if not self.savedetail(r.text, house):
                logging.warn("Can not save the detail info with url %s"%self.url);
                return None
            
            if not self.saveimg(r.text, house):
                logging.warn("Can not save the image with url %s"%self.url);
                return None
            
            return house
        except BaseException as ex:
            logging.error('catch an exception: %s'%str(ex))
        
        return None
            
if __name__=='__main__':
    persister = ExcelPersister()
    persister.startwork()
    
    s = requests.Session()
    s.headers.update(headers)
    #url = 'https://nj.lianjia.com/ershoufang/103101164368.html'
    url = 'https://nj.lianjia.com/ershoufang/103101921226.html'
    detail = HouseFetcher(url, s)
    house = detail.dowork()
    
    if house != None:
        persister.addHouse(house)
        persister.stopwork()
    
    input("the work is done")
    
    
    

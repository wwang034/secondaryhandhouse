'''
Created on 2017-12-12

@author: Administrator
'''

# -*- coding:utf-8 -*-

import threading
import xlwt
import logging
import time

#count = 0

class ExcelPersister:
    def __init__(self, zone, queue):
        self.queue=queue
        self.started=False
        self.workbook = xlwt.Workbook(encoding = 'utf-8')
        
        self.summary_sheet = self.workbook.add_sheet('%s'%zone)
        self.summary_sheet_row=0
        
        #write summary head
        self.writeexcelhead(self.summary_sheet)
        self.summary_sheet_row=1
        
        self.sub_sheet={}
        self.sub_sheet_row={}
        
        self.filename = zone
    
    def addHouse(self, house):
        self.queue.put(house)
    
    def startwork(self):
        self.t = threading.Thread(target=self.dowork, name='ExcelPersister-%s'%self.filename)
        self.t.start()
        
    def stopwork(self):
        self.started=False
        self.t.join()
        
    def writetoexcel(self, house):
        #global count
        subzone=house.subzone
        if not self.sub_sheet.__contains__(house.subzone):
            self.sub_sheet[subzone]=self.workbook.add_sheet(house.subzone)
            self.writeexcelhead(self.sub_sheet[subzone])
            self.sub_sheet_row[subzone]=1
        
        self.persistHouse(house, self.summary_sheet, self.summary_sheet_row)
        self.summary_sheet_row=self.summary_sheet_row+1
        
        self.persistHouse(house, self.sub_sheet[subzone], self.sub_sheet_row[subzone])
        self.sub_sheet_row[subzone]=self.sub_sheet_row[subzone]+1
        
        #count=count+1
        #if count == 10:
            #self.workbook.save('%s.xls'%self.filename)
    
    def dowork(self):
        self.started = True
        while self.started:
            if self.queue.empty():
                time.sleep(0.5)
            else:
                house = self.queue.get()
                self.writetoexcel(house)
        
        # deal with the remain work
        while not self.queue.empty():
            house = self.queue.get()
            self.writetoexcel(house)
        
        # save the excel file
        self.workbook.save('%s.xls'%self.filename)
                
    def writeexcelhead(self, sheet):
        sheet.write(0, 0, '房源')
        sheet.write(0, 1, '总价')
        sheet.write(0, 2, '单价')
        sheet.write(0, 3, '户型')
        sheet.write(0, 4, '楼层')
        sheet.write(0, 5, '朝向')
        sheet.write(0, 6, '装修')
        sheet.write(0, 7, '面积')
        sheet.write(0, 8, '修建时间')
        sheet.write(0, 9, '经纪人')
        sheet.write(0, 10, '联系电话')
        sheet.write(0, 11, '挂牌时间')
        sheet.write(0, 12, '交易权属')
        sheet.write(0, 13, '上次交易')
        sheet.write(0, 14, '房屋用途')
        sheet.write(0, 15, '房屋年限')
        sheet.write(0, 16, '产权所属')
        sheet.write(0, 17, '抵押信息')
        sheet.write(0, 18, '核心卖点')
        sheet.write(0, 19, '户型介绍')
        sheet.write(0, 20, '税费解析')
        sheet.write(0, 21, '图片链接')
        sheet.write(0, 22, '版块')
        
    def persistHouse(self, house, sheet, row):
        #TODO, add waring message, when same field are missing
        subject = house.subject or ' '
        hyperlink='HYPERLINK("%s";"%s")'%(house.url, subject)
        sheet.write(row, 0, xlwt.Formula(hyperlink))
        sheet.write(row, 1, house.totalprice or ' ')
        sheet.write(row, 2, house.unitprice or ' ')
        
        if hasattr(house, 'roommaininfo'):
            sheet.write(row, 3, house.roommaininfo)
        else:
            logging.warn('No room main info: %s'%house.url)
        
        if hasattr(house, 'roomsubinfo'):
            sheet.write(row, 4, house.roomsubinfo)
        else:
            logging.warn('No room subinfo info: %s'%house.url)
        
        if hasattr(house, 'typemaininfo'):
            sheet.write(row, 5, house.typemaininfo)
        else:
            logging.warn('No type main info: %s'%house.url)
        
        if hasattr(house, 'typesubinfo'):
            sheet.write(row, 6, house.typesubinfo)
        else:
            logging.warn('No type sub info: %s'%house.url)
        
        if hasattr(house, 'area'):
            sheet.write(row, 7, house.area)
        else:
            logging.warn('No area: %s'%house.url)
        
        if hasattr(house, 'buildtime'):
            sheet.write(row, 8, house.buildtime)
        else:
            logging.warn('No build time: %s'%house.url)
            
        if hasattr(house, 'brokername'):
            sheet.write(row, 9, house.brokername)
        else:
            logging.warn('No brokername: %s'%house.url)
        
        if hasattr(house, 'brokerphone'):
            sheet.write(row, 10, house.brokerphone)
        else:
            logging.warn('No broker phone: %s'%house.url)
            
        if hasattr(house, 'beginsell'):
            sheet.write(row, 11, house.beginsell)
        else:
            logging.warn('No begin sell time: %s'%house.url)
            
        if hasattr(house, 'transactiontype'):
            sheet.write(row, 12, house.transactiontype)
        else:
            logging.warn('No transactiontype: %s'%house.url)
        
        if hasattr(house, 'lastselltime'):
            sheet.write(row, 13, house.lastselltime)
        else:
            logging.warn('No lastselltime: %s'%house.url)
        
        if hasattr(house, 'usage'):
            sheet.write(row, 14, house.usage)
        else:
            logging.warn('No usage: %s'%house.url)
        
        if hasattr(house, 'year'):
            sheet.write(row, 15, house.year)
        else:
            logging.warn('No year: %s'%house.url)
        
        if hasattr(house, 'right'):
            sheet.write(row, 16, house.right)
        else:
            logging.warn('No right: %s'%house.url)
        
        if hasattr(house, 'mortage'):
            sheet.write(row, 17, house.mortage)
        else:
            logging.warn('No mortage: %s'%house.url)
        
        if hasattr(house, 'sellpoint'):
            sheet.write(row, 18, house.sellpoint)
        else:
            logging.warn('No sell point: %s'%house.url)
        
        if hasattr(house, 'introduction'):
            sheet.write(row, 19, house.introduction)
        else:
            logging.warn('No introduction: %s'%house.url)
        
        if hasattr(house, 'taxillustration'):
            sheet.write(row, 20, house.taxillustration)
        else:
            logging.warn('No tax info: %s'%house.url)
    
        if hasattr(house, 'imgpath'):
            hyperlink = 'HYPERLINK("%s";"%s")'%(house.imgpath, 'image')
            sheet.write(row, 21, xlwt.Formula(hyperlink))
        else:
            logging.warn('No img path: %s'%house.url)
        
        sheet.write(row, 22, house.subzone)
        logging.debug("[%s] add an house [%s]"%(sheet, house)) 
                
if __name__=='__main__':
    persister=ExcelPersister()
    persister.stopwork()    

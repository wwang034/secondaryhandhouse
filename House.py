'''
Created on 2017-12-12

@author: Administrator
'''

class House:
    def __init__(self):
        self.subject = None
        self.totalprice = None
        self.unitprice = None
        self.url = None
        self.subzone = None
        
    def __str__(self):
        return '[%s %s: %s, %s, %s]'%(self.subzone, self.subject, self.totalprice, self.unitprice, self.url)


'''
Created on 2017-12-18

@author: Administrator
'''

# -*- coding:utf-8 -*-

from Zone import Zone
import logging

zonelist={
      #'鼓楼':'https://nj.lianjia.com/ershoufang/gulou/',
      #'建邺':'https://nj.lianjia.com/ershoufang/jianye/',
      #'秦淮':'https://nj.lianjia.com/ershoufang/qinhuai/',
      #'玄武':'https://nj.lianjia.com/ershoufang/xuanwu/',
      '雨花台':'https://nj.lianjia.com/ershoufang/yuhuatai/',
      #'栖霞':'https://nj.lianjia.com/ershoufang/qixia/',
      #'江宁':'https://nj.lianjia.com/ershoufang/jiangning/',
      #'浦口':'https://nj.lianjia.com/ershoufang/pukou/'
      }

if __name__ == '__main__':
    for k, v in zonelist.items():
        zone = Zone(k, v)
        zone.scrapysubzone()
        logging.debug('finish scrap zone %s with url %s'%(k, v))
    
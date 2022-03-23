# -*- coding:UTF-8 -*-
#!/usr/bin/env python
# @Time  : 2019.11.21
# @author  : jiao ren
# @email : renjiao.jiao@qq.com

from vaex_api import Vaex
import time,json
import random
import threading
import datetime

SYMBOL = "HSPCUSDT"
vaex = Vaex(symbol=SYMBOL)
# 请在这里配置api key和api secret
vaex.auth(key="", secret="")

# 分别获得买的挂单价格序列buyprice，买的挂单量序列buyvolume，卖的挂单价格序列sellprice，卖的挂单量序列sellvolume
#  return buyprice, buyvolume, sellprice, sellvolume
def getDepth(level = 100):
    # 获取L20,L100,full 水平的深度盘口数据
    DepthData = vaex.get_depth(limit=level)
    # 分离出买卖价格序列和买卖量的序列
    sellprice, sellvolume = [], []
    buyprice, buyvolume = [], []
    if ('asks' in DepthData) and ('bids' in DepthData):
        for order in DepthData['asks']:
            sellprice.append(order[0])
            sellvolume.append(order[1])
        for order in DepthData['bids']:
            buyprice.append(order[0])
            buyvolume.append(order[1])
    # 分别获得买的挂单价格序列buyprice，买的挂单量序列buyvolume，卖的挂单价格序列sellprice，卖的挂单量序列sellvolume
    return buyprice, buyvolume, sellprice, sellvolume

#self交易量的区间和频率： 在买一卖一随机取价和区间，两秒后进行撤销
def self_trade():
    while True:
        try:
            #print('1self_trade')
            buyprice, buyvolume, sellprice, sellvolume = getDepth()
            #print(buyprice, buyvolume, sellprice, sellvolume)
            #print('self_trade')
            direction = random.randint(0, 1)
            tradeprice = round(random.uniform(float(buyprice[0]), float(sellprice[0])), 3)
            tradeVolume = round(random.uniform(self_tradeMin, self_tradeMax), 1)
            '''if self_trade_price_max!=0 and tradeprice > self_trade_price_max:
                tradeprice = self_trade_price_max
            if self_trade_price_min!=0 and tradeprice < self_trade_price_min:
                tradeprice = self_trade_price_min'''
            result = vaex.trade(price=tradeprice, amount=tradeVolume, direction=direction)
            if 'symbol' in result:
                print('\nself交易  价格' + str(tradeprice) + '  ' + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' 下单量' + str(tradeVolume))
                time.sleep(self_tradeFrequence) #两秒后进行反向交易
                result = vaex.trade(price=tradeprice, amount=tradeVolume, direction=1-direction)
                #打印结果值
                if 'symbol' in result:
                    if direction:
                        print('self交易:  self卖回成功')
                    else:
                        print('self交易:  self买回成功')
                else:
                    if direction:
                        print('self交易:  self卖回失败')
                    else:
                        print('self交易:  self买回失败')
            else:
                print("Trade fail....")
        except: continue


#在买一和买十，卖一和卖十之间随机取价和区间，每6秒下单一次
def addentrust():
    while True:
        try:
            buyprice, buyvolume, sellprice, sellvolume = getDepth()
            #在买一和买十，卖一和卖十之间随机取价和区间
            direction = random.randint(0, 1) #随机取方向
            flagDirec=""
            if direction: #如果随机数为1，挂买单
                if len(buyprice) > 10:
                    tradeprice = round(random.uniform(float(buyprice[9]), float(buyprice[0])), 3) #随机取价格
                    tradeVolume = round(random.uniform(cross_tradeMin, cross_tradeMax), 1) #随机取量
                else:
                    tradeprice = round(random.uniform(float(buyprice[-1]), float(buyprice[0])), 3)
                    tradeVolume = round(random.uniform(cross_tradeMin, cross_tradeMax), 1)
                flagDirec='买'
            else:
                if len(sellprice) > 10:
                    tradeprice = round(random.uniform(float(sellprice[0]), float(sellprice[9])), 3)
                    tradeVolume = round(random.uniform(cross_tradeMin, cross_tradeMax), 1)
                else:
                    tradeprice = round(random.uniform(float(sellprice[0]), float(sellprice[-1])), 3)
                    tradeVolume = round(random.uniform(cross_tradeMin, cross_tradeMax), 1)
                flagDirec = '卖'

            if cross_trade_price_max!=0 and tradeprice > cross_trade_price_max:
                tradeprice = cross_trade_price_max
            if cross_trade_price_min!=0 and tradeprice < cross_trade_price_min:
                tradeprice = cross_trade_price_min
            result = vaex.trade(price=tradeprice, amount=tradeVolume, direction=direction)
            if 'symbol' in result:
                print('\ncross交易订单:  价格' + str(tradeprice) + '  ' + datetime.datetime.now().strftime(
                "%Y/%m/%d %H:%M:%S") + ' 下单量' + str(tradeVolume) + ' 方向:' + flagDirec)
            else:
                print("Trade fail")

            time.sleep(cross_tradeFrequence) #每6秒下单一次
        except: continue


#延迟一分钟后，陆续撤单（撤单顺序随机）
def adjustable_cancel():
    while True:
        try:
            result = vaex.get_open_order()
            if 'list' in result and len(result['list'])>0:
                order_list = result['list']
                index = random.randint(0, len(order_list) - 1)
                result = vaex.cancel_order(order_list[index]['orderId'])
                print(result)
                if 'symbol' in result:
                    interval = 12 * adjustable_time / len(order_list)
                    print('撤销订单:' + str(order_list[index]['orderId']) + '  委托单个数：'+ str(len(order_list)) + ' 撤单间隔：'+ str(round(interval,2)) +'s')
                time.sleep(interval)  # 120s/每次撤单的延时时间为未成交单量,相当于恒定未成交单量的速度下，两分钟可以撤销完
        except: continue


# 撤单时间间隔，越小越快
adjustable_time=10

#self交易量的区间和频率： 在买一卖一随机取价和区间，n秒后进行反向操作
self_tradeFrequence=5  #5秒后反向交易，这个值越小交易越快
self_tradeMin=20
self_tradeMax=50


#cross交易量的区间和频率： 在买一和买十，卖一和卖十之间随机取价和区间，每n秒下单一次
cross_tradeFrequence = 5 #这个值越小交易越快
cross_tradeMin=2
cross_tradeMax=5

#新增：cross交易价格的上下限时，为0表示不设置
cross_trade_price_max=0
cross_trade_price_min=0


print('self交易')
selfTrade_thread = threading.Thread(target=self_trade)
selfTrade_thread.start()


print('cross下单交易开始')
addentrust_thread = threading.Thread(target=addentrust)
addentrust_thread.start()


time.sleep(60) #60秒后陆续撤单

print('cross撤单交易开始')
cancel_thread = threading.Thread(target=adjustable_cancel)
cancel_thread.start()




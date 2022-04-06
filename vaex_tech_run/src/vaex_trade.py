# -*- coding:UTF-8 -*-
#!/usr/bin/env python

import time
import asyncio
import websockets
import traceback

import logging
logging.basicConfig(level=logging.INFO,
                    format = '%(asctime)s - %(levelname)s - %(message)s')

from vaex_api import Vaex
from default_config import config
import utils
import vaex_func_trade

def cancel_pool(vaex):
    while True:
        try:
            vaex_func_trade.adjustable_cancel(vaex)
        except Exception as e:
            traceback.print_exc()
        time.sleep(2)

def save_trades_pool(vaex):
    while True:
        try:
            vaex_func_trade.save_trades(vaex, config['trade_data_dir'])
        except Exception as e:
            traceback.print_exc()
        time.sleep(60 * 10) # 每10分钟获取最新订单信息并存储

def print_trade_pool():
    while True:
        try:
            end_day = utils.get_now_time_str(time_format='%Y%m%d')
            end_time = f'{end_day}{config["report_hour"]:02d}0000'
            if utils.get_now_time_str() < end_time:
                if config['debug']:
                    time.sleep(10)
                else:
                    time.sleep(60 * 60) # 每60分钟尝试输出报告
                continue
            start_time = f'{utils.cal_date(end_day, -1)}{config["report_hour"]:02d}0000'
            vaex_func_trade.print_trade_report(
                input_dir = config['trade_data_dir'],
                output_dir = config['trade_report_dir'],
                start_time=start_time, end_time=end_time)
        except Exception as e:
            traceback.print_exc()
        if config['debug']:
            time.sleep(10)
        else:
            time.sleep(60 * 60)

def print_cancel_pool():
    while True:
        try:
            end_day = utils.get_now_time_str(time_format='%Y%m%d')
            end_time = f'{end_day}{config["report_hour"]:02d}0000'
            if utils.get_now_time_str() < end_time:
                if config['debug']:
                    time.sleep(10)
                else:
                    time.sleep(60 * 60) # 每60分钟尝试输出报告
                continue
            start_time = f'{utils.cal_date(end_day, -1)}{config["report_hour"]:02d}0000'
            vaex_func_trade.print_cancel_report(
                input_dir = config['cancel_data_dir'],
                output_dir = config['cancel_report_dir'],
                start_time=start_time, end_time=end_time)
        except Exception as e:
            traceback.print_exc()
        if config['debug']:
            time.sleep(10)
        else:
            time.sleep(60 * 60)

def wave_trade_pool(vaex):
    while True:
        try:
            # 自动波动交易
            if config['wave_trade_auto_on']:
                start_day = utils.get_now_time_str(time_format='%Y%m%d%')
                # generate auto config
                wave_num = utils.random_num(
                    min_val = config['wave_trade_auto_min_action_num'],
                    max_val = config['wave_trade_auto_max_action_num']+1,
                    num = 1,
                    sigma = 1)[0]
                now_time = utils.get_now_time_str(time_format='%Y%m%d%H%M%S')
                end_time = f"{start_day}235959"
                wave_times = utils.random_num(
                    min_val = int(now_time),
                    max_val = int(end_time),
                    num = wave_num,
                    sigma = 1)
                wave_percentages = utils.random_num(
                    min_val = config['wave_trade_auto_min_percentage'],
                    max_val = config['wave_trade_auto_max_percentage'],
                    num = wave_num,
                    sigma = 10000)
                while True:
                    now_day = utils.get_now_time_str(time_format='%Y%m%d%')
                    if now_day > start_day:
                        break
                    now_time = utils.get_now_time_str(time_format='%Y%m%d%H%M%S')
                    for index, start_time in enumerate(wave_times):
                        print(start_time)
                        print(now_time)
                        if now_time > start_time and int(now_time)-int(start_time) < 60:
                            # time check pass
                            print('ok')
                            wave_percentage = wave_percentages[index]
                            duration_time = utils.random_num(1, 60)
                            action_num = utils.random_num(1, 3)
                            vaex_func_trade.target_trade_allocation(vaex, wave_percentage, duration_time, action_num)
                            time.sleep(61)
                    time.sleep(10)
            elif config['wave_trade_manual_on']:
                # 手动配置的波动交易
                assert len(config['wave_trade_start_times']) == len(config['wave_trade_percentages'])
                assert len(config['wave_trade_start_times']) == len(config['wave_trade_duration_times'])
                assert len(config['wave_trade_start_times']) == len(config['wave_trade_action_nums'])
                now_time = utils.get_now_time_str(time_format='%Y%m%d%H%M%S')
                for index, start_time in enumerate(config['wave_trade_start_times']):
                    start_time = utils.time_format_change(start_time, config['wave_trade_time_format'])
                    if config['wave_trade_repeat_evenyday']:
                        start_time = f"{utils.get_now_time_str(time_format='%Y%m%d')}{start_time[-6:]}"
                    print(start_time)
                    print(now_time)
                    if now_time > start_time and int(now_time)-int(start_time) < 60:
                        # time check pass
                        # print('ok')
                        wave_percentage = config['wave_trade_percentages'][index]
                        duration_time = config['wave_trade_duration_times'][index]
                        action_num = config['wave_trade_action_nums'][index]
                        vaex_func_trade.target_trade_allocation(vaex, wave_percentage, duration_time, action_num)
                        time.sleep(61)
        except Exception as e:
            traceback.print_exc()
        time.sleep(10)

# async func
def func(vaex, target_func):
    while True:
        try:
            logging.info("Start main func...")
            async def main_logic():
                async with websockets.connect(config['web_addr'], ping_interval=None) as websocket:
                    await target_func(vaex, websocket)
            asyncio.get_event_loop().run_until_complete(main_logic())
        except Exception as e:
            traceback.print_exc()
            logging.warninga("Main func failed, restart")


vaex = Vaex(symbol=config['symbol'])
vaex.auth(key=config['key'], secret=config['secret'])
if __name__ == '__main__':
    import multiprocessing
    multiprocessing.set_start_method('spawn')
    pool = multiprocessing.Pool(processes = 7)
    pool.apply_async(func, (vaex, vaex_func_trade.self_trade,))
    pool.apply_async(func, (vaex, vaex_func_trade.cross_trade,))
    pool.apply_async(cancel_pool, (vaex,))
    pool.apply_async(save_trades_pool, (vaex,))
    pool.apply_async(print_trade_pool)
    pool.apply_async(print_cancel_pool)
    pool.apply_async(wave_trade_pool, (vaex,))
    pool.close()
    pool.join()

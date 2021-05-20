from ws_connect import *
from bot_class_trend import Input, CheckBot
import json
from bin_api_f import Binance
import logging

logging.basicConfig(level = logging.DEBUG, filename = 'mylog.log')

bot_api = Binance(
    API_KEY='YOUR API KEY',
    API_SECRET='YOUR SECRET KEY'
	)

# start websocket
start()

inpt = Input(shd=3, tp=39, st=42, offset=5)

deal_order_list = []
limit_order_d = {}
deal_list = []
result = ''
res_tp, res_st = 0, 0

while True:
		# update data from message
	from ws_connect import msg
	if prev_msg == msg:
		continue
	prev_msg = msg

	bot = CheckBot(msg)
	bot.set_input(inpt)

		# ищем сигнал {'LONG':price}
	ss = bot.search_signal()
	if ss != None:
		logging.info(str(ss))
		try:
			orderId = bot_api.futuresopenOrder(symbol='BTCUSDT')
			for i in orderId:
				if i['orderId'] not in deal_order_list:
					bot_api.futuresCancelOrder(symbol='BTCUSDT',orderId=i['orderId'])
		except:
			print('no order')

		print(ss)
		positionSide = list(ss)[0]
		price = ss[positionSide]
		side = 'BUY' if positionSide == 'LONG' else 'SELL'
		k = 1 if positionSide == 'LONG' else -1

		try:
			limit_order = (bot_api.futuresCreateOrder(
					symbol='BTCUSDT',
					side=side,
					positionSide=positionSide,
					type='STOP',
					timeInForce='GTC',
					quantity=0.002,
					price=price,
					stopPrice=price+(1*k)
					))
			limit_order_d = {'pos_side':positionSide, 'side':side, 'price':price, 'limitId':limit_order['orderId']}
			print('new order')
			logging.info(str(limit_order_d))
		except:
			print('new order error')
		print(res_st, res_tp)
		logging.info(str(res_tp)+' '+str(res_st))
		continue

		# проверяем открытие позиции по лимитке/получаем данные по позиции, записываем данные в список
	if limit_order_d:
		if limit_order_d['pos_side'] == 'LONG' and limit_order_d['price'] < bot.h and limit_order_d['price'] > bot.c:
			try:
				limitId = bot_api.futuresOrderInfo(symbol='BTCUSDT', orderId=limit_order_d['limitId'])
				if limitId['status'] == 'FILLED':
					print('position open')
					d = {'pos_side':limit_order_d['pos_side'],'tp_Id':0, 'st_Id':0, 'tp':0, 'st':0, 'price':float(limitId['price'])}
					limit_order_d = {}
					if d not in deal_list:
						deal_list.append(d)
						logging.info(str(d))
			except:
				print('no check FILLED')
				
		elif limit_order_d['pos_side'] == 'SHORT' and limit_order_d['price'] > bot.l and limit_order_d['price'] < bot.c: 
			try:
				limitId = bot_api.futuresOrderInfo(symbol='BTCUSDT', orderId=limit_order_d['limitId'])
				if limitId['status'] == 'FILLED':
					print('position open')
					d = {'pos_side':limit_order_d['pos_side'], 'tp_Id':0, 'st_Id':0, 'tp':0, 'st':0, 'price':float(limitId['price'])}
					limit_order_d = {}
					if d not in deal_list:
						deal_list.append(d)
						logging.info(str(d))
			except:
				print('no check FILLED')

	if deal_list:
		for i in deal_list:
			if i['tp'] + i['st'] == 0:
				if i['pos_side'] == 'LONG':
					try:
						tp = (bot_api.futuresCreateOrder(
						symbol='BTCUSDT',
						side='SELL',
						positionSide='LONG',
						type='TAKE_PROFIT',
						timeInForce='GTC',
						quantity=0.002,
						price=i['price']+39,
						stopPrice=i['price']+38
						))
						i['tp'] = float(tp['price'])
						i['tp_Id'] = int(tp['orderId'])
						deal_order_list.append(int(tp['orderId']))
						
					except:
						print('TP error')
					try:
						st = (bot_api.futuresCreateOrder(
						symbol='BTCUSDT',
						side='SELL',
						positionSide='LONG',
						type='STOP',
						timeInForce='GTC',
						quantity=0.002,
						price=i['price']-40,
						stopPrice=i['price']-40
						))
						i['st'] = float(st['price'])
						i['st_Id'] = int(st['orderId'])
						deal_order_list.append(int(st['orderId']))
					except:
						print('ST error')
					print('TP, ST')

				else:
					try:
						tp = (bot_api.futuresCreateOrder(
						symbol='BTCUSDT',
						side='BUY',
						positionSide='SHORT',
						type='TAKE_PROFIT',
						timeInForce='GTC',
						quantity=0.002,
						price=i['price']-39,
						stopPrice=i['price']-38
						))
						i['tp'] = float(tp['price'])
						i['tp_Id'] = int(tp['orderId'])
						deal_order_list.append(int(tp['orderId']))
					except:
						print('TP error')
					try:
						st = (bot_api.futuresCreateOrder(
						symbol='BTCUSDT',
						side='BUY',
						positionSide='SHORT',
						type='STOP',
						timeInForce='GTC',
						quantity=0.002,
						price=i['price']+40,
						stopPrice=i['price']+40
						))
						i['st'] = float(st['price'])
						i['st_Id'] = int(st['orderId'])
						deal_order_list.append(int(st['orderId']))
					except:
						print('ST error')
					print('TP, ST')

			else:
				if i['pos_side'] == 'LONG':
					if i['tp']<bot.c or i['st']>bot.c:
						stop_Id = bot_api.futuresOrderInfo(symbol='BTCUSDT', orderId=i['st_Id'])
						tp_Id = bot_api.futuresOrderInfo(symbol='BTCUSDT', orderId=i['tp_Id'])
						if stop_Id['status'] == 'FILLED' or tp_Id['status'] == 'FILLED':
							deal_order_list.remove(i['st_Id'])
							deal_order_list.remove(i['tp_Id'])
							Id = bot_api.futuresopenOrder(symbol='BTCUSDT')
							for j in Id:
								if j['orderId'] not in deal_order_list:
									bot_api.futuresCancelOrder(symbol='BTCUSDT',orderId=j['orderId'])
							deal_list.remove(i)
							print(deal_list)
							result = 'st' if stop_Id['status'] == 'FILLED' else 'tp'
							print(result)
							logging.info(str(result))

				else:
					if i['tp']>bot.c or i['st']<bot.c:
						stop_Id = bot_api.futuresOrderInfo(symbol='BTCUSDT', orderId=i['st_Id'])
						tp_Id = bot_api.futuresOrderInfo(symbol='BTCUSDT', orderId=i['tp_Id'])
						if stop_Id['status'] == 'FILLED' or tp_Id['status'] == 'FILLED':
							deal_order_list.remove(i['st_Id'])
							deal_order_list.remove(i['tp_Id'])
							Id = bot_api.futuresopenOrder(symbol='BTCUSDT')
							for j in Id:
								if j['orderId'] not in deal_order_list:
									bot_api.futuresCancelOrder(symbol='BTCUSDT',orderId=j['orderId'])
							deal_list.remove(i)
							print(deal_list)
							result = 'st' if stop_Id['status'] == 'FILLED' else 'tp'
							print(result)
							logging.info(str(result))

			if result == 'tp':
				res_tp = res_tp + 1
			elif result == 'st':
				res_st = res_st + 1


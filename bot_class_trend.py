import json

class Input(object):
	def __init__(self, **kwargs):
		self.shd = kwargs['shd']
		self.tp = kwargs['tp']
		self.st = kwargs['st']
		self.offset = kwargs['offset']
		
class CheckBot(object):
	def __init__(self, obj):
		data = json.loads(obj)['data']
		self.time_event = data['E']
		self.o = float(data['k']['o'])
		self.c = float(data['k']['c'])
		self.h = float(data['k']['h'])
		self.l = float(data['k']['l'])
		self.x = data['k']['x']
		if self.o < self.c:
			self.dir = 'up'
			self.shd = round(self.h - self.c)
		else:
			self.dir = 'down'
			self.shd = round(self.c - self.l)

	def set_input(self, inpt):
		self.shadow = inpt.shd
		self.tp = inpt.tp
		self.st = inpt.st
		self.offset = inpt.offset

	def search_signal(self):
		if self.x == True:
			print(self.o,self.c,self.h,self.l, self.shd)
			if self.shd <= 3:
				if self.dir == 'up':
					deal_up = self.c+5
					signal = {'LONG':deal_up}
					print('signal')
					return signal
				else:
					deal_down = self.c-5
					signal = {'SHORT':deal_down}
					print('signal')
					return signal

	def signal_true(self, signal):
		if signal.get('LONG') != None:
			if self.c > signal['LONG']:
				return signal
		else:
			if self.c < signal['SHORT']:
				return signal

	def check (self, deal_l):
		for i in deal_l:
			if i.get('LONG') != None:
				if i['LONG']+self.tp < self.c:
					retrn = ['** TP **', self.c, i]
					return retrn
				elif i['LONG']-self.st > self.c:
					retrn = ['** ST **', self.c, i]
					return retrn
			else:
				if i['SHORT']-self.tp > self.c:
					retrn = ['** TP **', self.c, i]
					return retrn
				elif i['SHORT']+self.st < self.c:
					retrn = ['** ST **', self.c, i]
					return retrn

		
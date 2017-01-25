import pandas as pd
import numpy as np
import math
'''数据预读取'''
port = 0.8
flowFile = '../data/flowFreq_2-6-'+str(port)+'.csv'
putFile = '../data/putSpeed.csv'
flowData = pd.read_csv(flowFile)	#到达机场的人流数据
putData = pd.read_csv(putFile)	#机场三个环节的速度数据


'''常量定义'''
Dseconds = 86400  #一天的秒数
dcRatio = 0.09  #double check的比例

# va = putData['ID Check Process Time'][0]
# vm = putData['Milimeter Wave Scan times'][0]
# vx = putData['X-Ray Scan Time'][0]

'''类定义'''
class Pos:
	def __init__(self,x,y):
		self.x = x
		self.y = y
class ZoneA:
	def __init__(self):
		self.queueA = []
class ZoneB:
	def __init__(self):
		self.queueB = []
		self.tp = 0

class ZoneD:
	pass
class CheckPoint:
	pass
class Passenger:
	'''
	
	'''
	def __init__(self,qid,state,id,nationality,attr,dCheck,isDanger,va,vb,vm,vd):
		'''
		zone:'A1','A2','B1','B2','D'
		id:乘客编号
		nationality 乘客国籍 0.America 1.Chinese
		attr:0. pre-check  1.regular-check 2.fast-check
		isDanger: 0.不是恐怖分子  1.是恐怖分子
		va:IDcheck时间
		vb:放包时间
		vm:milimeter时间
		vd：double check时间
		state:0.在等IDcheck 1.正在IDcheck 2.在等放包 3. 正在放包 
		4.放完包了正在milimeter 5.正常结束安检  6.正在double check 7.double check结束 -1. 是个危险分子
		'''
		self.qid = qid
		self.id = id
		self.nationality = nationality
		self.attr = attr
		self.state = state
		self.dCheck = dCheck
		self.isDanger = isDanger
		self.va = va
		self.vb = vb
		self.vm = vm
		self.vd = vd
		self.waitTime = 0
		self.baseTime = 0
		self.delta = 1

	def update(self,front_id,front_state):
		if self.state == 0:#若在等IDcheck
			if front_id==-1:#前面没有人,若有人则不变
				self.state = 1#转换为正在IDcheck
				self.baseTime = self.waitTime
			elif front_id > 0:
				if front_state == 2:#前面的人已经等放包了
					self.state = 1
			elif front_id == -2:
				print('bug!')

			self.waitTime+=self.delta

		elif self.state == 1:#若正在IDcheck
			time_delta = self.waitTime-self.baseTime
			if time_delta >= self.va:#已经达到idcheck完成时间，否则不变
				self.state = 2 #转换为正在等待放包
			self.waitTime+=self.delta

		elif self.state == 2:#正在等放包
			if front_id == -1:#前面没人
				self.state = 3
			else:
				if front_state == 4:
					self.state = 3
					self.baseTime = self.waitTime
			self.waitTime+=self.delta

		elif self.state == 3:#正在放包
			time_delta = self.waitTime-self.baseTime
			if time_delta>=self.vb:
				self.state = 4
				self.baseTime = self.waitTime
			self.waitTime+=self.delta

		elif self.state == 4:#正在milimeter
			time_delta = self.waitTime-self.baseTime
			if time_delta>=self.vm:
				if self.dCheck == 0:#是否需要double-check
					self.state = 5
				else:
					self.state = 6
					self.baseTime = self.waitTime
					self.waitTime+=1
			else:
				self.waitTime+=self.delta
		elif self.state == 6:
			time_delta = self.waitTime-self.baseTime
			if time_delta >= self.vd:
				if self.isDanger==1:
					self.state = -1
				else:
					self.state = 7
			else:
				self.waitTime+=self.delta
		return self.state


		self.waitTime+=self.delta

class PassengerManager:
	def __init__(self,constantGiver,id_size):
		self.queue = ['p','p','p','f','r','r','r','r']
		self.zoneBs=[]
		self.waitingPassengers = []  #当还没过完安检的passenger列表
		self.finishedPassengers = [] #当前已经完成的passenger列表
		self.front_ids = [-2]*id_size #front_id[i] 表示id为i的乘客的前一名乘客的id值，前面没有人则为-1,初始化 不存在的都为-2，规模为50000
		self.states = [-1]*id_size  #所有乘客的状态，states[i]代表id为i的乘客的状态，-1代表不存在乘客
		self.curMaxId = 0
		self.cg = constantGiver
		entranceSeries = self.cg.getEntrance(0)
		entryNum = len(entranceSeries)
		for i in range(entryNum):
			num = entranceSeries[i]
			if self.queue[i] == 'p':		#处理preCheck
				preId = -1
				for j in range(num):
					self.qid = i
					self.attr = 0
					self.va = self.cg.getVa()
					self.vb = self.cg.getVb(self.attr)
					self.vm = self.cg.getVm()
					self.nationality = self.cg.getNationality('Chinese')
					self.isDanger = self.cg.getDanger(self.attr)

					if self.isDanger == 1:
						self.dCheck = 1
					else:
						self.dCheck = self.cg.getDcheck()

					self.vd = self.cg.getVd()
					self.id = self.curMaxId
					self.waitingPassengers.append(Passenger(self.qid,0,self.id,self.nationality,self.attr,self.dCheck,self.isDanger,self.va,self.vb,self.vm,self.vd))
					self.front_ids[self.id] = preId #更新front_ids
					self.states[self.id] = 0
					preId = self.id
					self.curMaxId +=1 

			elif self.queue[i] == 'r':	#处理regularCheck
				preId = -1
				for j in range(num):
					self.qid = i
					self.attr = 1
					self.va =self.cg.getVa()
					self.vb = self.cg.getVb(self.attr)
					self.vm = self.cg.getVm()
					self.nationality = self.cg.getNationality('Chinese')
					self.isDanger =self.cg.getDanger(self.attr)
					if self.isDanger == 1:
						self.dCheck = 1
					else:
						self.dCheck = self.cg.getDcheck()
					self.vd = self.cg.getVd()
					self.id = self.curMaxId
					self.curMaxId+=1
					self.waitingPassengers.append(Passenger(self.qid,0,self.id,self.nationality,self.attr,self.dCheck,self.isDanger,self.va,self.vb,self.vm,self.vd))
					self.front_ids[self.id] = preId
					self.states[self.id] = 0
					preId = self.id

			elif self.queue[i] == 'f':#处理fast-check
				preId = -1
				for j in range(num):
					self.qid = i
					self.attr = 2
					self.va =self.cg.getVa()
					self.vb = self.cg.getVb(self.attr)
					self.vm = self.cg.getVm()
					self.nationality = self.cg.getNationality('Chinese')
					self.isDanger =self.cg.getDanger(self.attr)
					if self.isDanger == 1:
						self.dCheck = 1
					else:
						self.dCheck = self.cg.getDcheck()
					self.vd = self.cg.getVd()
					self.id = self.curMaxId
					self.curMaxId+=1
					self.waitingPassengers.append(Passenger(self.qid,0,self.id,self.nationality,self.attr,self.dCheck,self.isDanger,self.va,self.vb,self.vm,self.vd))
					self.front_ids[self.id] = preId
					self.states[self.id] = 0
					preId = self.id
	def findFastest():
		pass
	def update(self,timeStamp):
		entranceSeries = self.cg.getEntrance(timeStamp)
		deleteIndex = []
		i = 0
		while i <len(self.waitingPassengers):
			id = self.waitingPassengers[i].id
			front_id = self.front_ids[id]

			front_state = self.states[front_id]
			state = self.waitingPassengers[i].update(front_id,front_state)

			self.states[id] = state

			if state == -1:#是个危险分子
				print('dangerous!')
				del self.waitingPassengers[i]
				i-=1
			elif state == 5 or state == 7:
				self.finishedPassengers.append(self.waitingPassengers[i])
				del self.waitingPassengers[i]
				i-=1
			i+=1

		#增添新的乘客
		for i in range(len(entranceSeries)):
			num = entranceSeries[i]
			if self.queue[i] == 'p':		#处理preCheck
				preId = -1
				for j in range(num):
					self.qid = i
					self.attr = 0
					self.va = self.cg.getVa()
					self.vb = self.cg.getVb(self.attr)
					self.vm = self.cg.getVm()
					self.nationality = self.cg.getNationality('American')
					self.isDanger = self.cg.getDanger(self.attr)

					if self.isDanger == 1:
						self.dCheck = 1
					else:
						self.dCheck = self.cg.getDcheck()

					self.vd = self.cg.getVd()
					self.id = self.curMaxId
					self.curMaxId+=1
					self.waitingPassengers.append(Passenger(self.qid,0,self.id,self.nationality,self.attr,self.isDanger,self.dCheck,self.va,self.vb,self.vm,self.vd))
					self.front_ids[self.id] = preId
					self.states[self.id] = 0
					preId = self.id

			elif self.queue[i] == 'r':	#处理regularCheck
				preId = -1
				for j in range(num):
					self.qid = i
					self.attr = 1
					self.va = self.cg.getVa()
					self.vb = self.cg.getVb(self.attr)
					self.vm = self.cg.getVm()
					self.nationality = self.cg.getNationality('American')
					self.isDanger = self.cg.getDanger(self.attr)

					if self.isDanger == 1:
						self.dCheck = 1
					else:
						self.dCheck = self.cg.getDcheck()

					self.vd = self.cg.getVd()
					self.id = self.curMaxId
					self.curMaxId+=1
					self.waitingPassengers.append(Passenger(self.qid,0,self.id,self.nationality,self.attr,self.dCheck,self.isDanger,self.va,self.vb,self.vm,self.vd))
					self.front_ids[self.id] = preId
					self.states[self.id] = 0
					preId = self.id

			elif self.queue[i] == 'f':#处理fast-check
				preId = -1
				for j in range(num):
					self.qid = i
					self.attr = 2
					self.va =self.cg.getVa()
					self.vb = self.cg.getVb(self.attr)
					self.vm = self.cg.getVm()
					self.nationality = self.cg.getNationality('American')
					self.isDanger =self.cg.getDanger(self.attr)
					if self.isDanger == 1:
						self.dCheck = 1
					else:
						self.dCheck = self.cg.getDcheck()
					self.vd = self.cg.getVd()
					self.id = self.curMaxId
					self.curMaxId+=1
					self.waitingPassengers.append(Passenger(self.qid,0,self.id,self.nationality,self.attr,self.dCheck,self.isDanger,self.va,self.vb,self.vm,self.vd))
					self.front_ids[self.id] = preId
					self.states[self.id] = 0
					preId = self.id

	def calWaitInTimes(self):
		tmp = []
		for i in range(len(self.finishedPassengers)):
			tmp.append(self.finishedPassengers[i].waitTime)
		self.waitInTimeList = pd.Series(tmp)
	def getWaitVar(self):
		return self.waitInTimeList.std()

class ConstantGiver:
	def __init__(self,flowData,putData):
		self.random_size = 500000    #设置random出的各个环节的速度的size
		self.preDangerRatio = 0.0001  #pre-check中危险分子比例
		self.fastDangerRatio = 0.0002 #fast-check中危险分子比例
		self.reguDangerRatio = 0.0001  #regular-check中危险分子比例
		self.douCheckRatio = 0.09  #人群中precheck的比例
		self.preCheckRatio = 0.45 #

		self.flowData = flowData
		self.putData = putData
		self.tot_timeStamps = flowData.shape[0]   #暂时一秒更新一次所有状态
		self.vaMean = putData.iloc[0,1]
		self.vmMean = putData.iloc[0,2]
		self.vdMean = putData.iloc[0,4]
		self.vpbMean = putData.iloc[0,5]
		self.vrbMean = putData.iloc[0,6]
		self.vfbMean = putData.iloc[0,7]
	
		self.vaStd = putData.iloc[1,1]
		self.vmStd = putData.iloc[1,2]
		self.vdStd = putData.iloc[1,4]
		self.vpbStd = putData.iloc[1,5]
		self.vrbStd = putData.iloc[1,6]
		self.vfbStd = putData.iloc[1,7]

		self.vaList = (np.random.normal(self.vaMean,self.vaStd,self.random_size)).tolist()
		self.vmList =  (np.random.normal(self.vmMean,self.vmStd,self.random_size)).tolist()
		self.vdList =  (np.random.normal(self.vdMean,self.vdStd,self.random_size)).tolist()
		self.vpbList = (np.random.normal(self.vpbMean,self.vpbStd,self.random_size)).tolist()
		self.vrbList = (np.random.normal(self.vrbMean,self.vrbStd,self.random_size)).tolist()
		self.vfbList = (np.random.normal(self.vfbMean,self.vfbStd,self.random_size)).tolist()

	def getEntrance(self,timeStamp): #分别取出timeStamp时刻到6个通道的人数
		return flowData.iloc[timeStamp,:]
	def getDcheck(self):
		p = np.random.random_sample()
		if self.douCheckRatio>p:
			return 1
		else:
			return 0

	def getDanger(self,attr):
		ratio = np.random.random_sample()
		if attr == 0:#pre-check
			if self.preDangerRatio>ratio:
				return 1
			else:
				return 0
		elif attr == 1:#regular-check
			if self.reguDangerRatio>ratio:
				return 1
			else:
				return 0
		elif attr == 2:#'fast-check'
			if self.fastDangerRatio>ratio:
				return 1
			else:
				return 0

	def getNationality(self,nation):
		if nation == 'American':
			return 0
		elif nation == 'Chinese':
			return 1
		else:
			print('bug!')

	def getVa(self):
		va =-1
		while va<0:
			va = self.vaList.pop()
		return va

	def getVb(self,attr):
		vb =-1
		if attr == 0: #pre-check
			while vb<0:
				vb = self.vpbList.pop()
		elif attr == 1: #regu-check
			while vb<0:
				vb = self.vrbList.pop()
		else:
			while vb<0:
				vb = self.vfbList.pop()
		return vb

	def getVm(self):
		vm =-1
		while vm<0:
			vm = self.vmList.pop()
		return vm

	def getVd(self):
		vd =-1
		while vd<0:
			vd = self.vdList.pop()
		return vd
'''函数定义'''
def dist(p1,p2):
	return abs(p1.x-p2.x)+abs(p1.y-p2.y)

class TimeController:
	def __init__(self,flowData,putData,time_scale,rand_size):
		cg = ConstantGiver(flowData,putData)
		self.pm = PassengerManager(cg,rand_size)
	def updateAll(self,timeStamp):
		self.pm.update(timeStamp)
	def getWaitInTimeVar(self):
		self.pm.calWaitInTimes()
		return self.pm.getWaitVar()
	def getThroughPut(self):
		population = len(self.pm.finishedPassengers)
		return time_scale*18/population

	
if __name__ == '__main__':
	# print(constantGiver.getVa())
	# print(constantGiver.getVb())
	# print(constantGiver.getVm())
	# print(constantGiver.getVd())
	time_scale = 86400
	tc = TimeController(flowData,putData,time_scale,500000)
	for i in range(time_scale):
		tc.updateAll(i)
	print(len(tc.pm.finishedPassengers))
	print(tc.getWaitInTimeVar())
	print(tc.getThroughPut())

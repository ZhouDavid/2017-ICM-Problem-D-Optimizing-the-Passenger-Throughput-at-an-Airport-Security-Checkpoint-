import pandas as pd
import numpy as np
import math
totNum = 8

filePath = '../data/flowFreq_2-6.csv'
outPath = '../data/flowFreq_'

originFlow = pd.read_csv(filePath)
for preNum in range(3,totNum):
	regNum = totNum - preNum
	attrList = []
	for j in range(preNum):
		attrList.append('preCheck')
	for j in range(regNum):
		attrList.append('regCheck')
	dataFlow = pd.DataFrame()
	for i in range(originFlow.shape[0]):
		sum1 = 0
		sum2 = 0
		line = []
		for j in range(2):
			sum1+=originFlow.iloc[i,j]
		val = math.ceil(sum1/preNum)
		for j in range(preNum):
			line.append(val)
		for j in range(2,totNum):
			sum2+=originFlow.iloc[i,j]
		val = math.floor(sum2/regNum)
		for j in range(regNum):
			line.append(val)
		line2 = []
		line2.append(line)
		s = pd.DataFrame(line2)
		dataFlow = dataFlow.append(s,ignore_index = True)			
	dataFlow.to_csv(outPath+str(preNum)+'-'+str(regNum)+'.csv',index = False)



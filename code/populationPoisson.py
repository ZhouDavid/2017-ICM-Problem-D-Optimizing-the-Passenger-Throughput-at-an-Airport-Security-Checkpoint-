import pandas as pd
import numpy as np
import math

filename= '../data/dealed_time.csv'
time_delta = 10
Dseconds = 86400  #一天的秒数
ID_speed = 0	#ID check 速度：秒/每人
MM_speed = 0	#Milimiter scan 速度：秒/每人
Xray_speed = 0	#X-Ray scan 速度：秒/每人
def strategy(df,pre_num,pre_mean,regu_mean,size):
	for i in range(df.shape[1]):
		if i < pre_num:
			df.iloc[:,i] = np.random.poisson(pre_mean,size)
		else:
			df.iloc[:,i] = np.random.poisson(regu_mean,size)
	return df
def ceil2delta(time,time_delta):
	while time%time_delta:
		time+=1
	return time
def range_index(number,List):
	for i in range(len(List)):
		if number<List[i]:
			return i
def list_initialize(size,number):
	List = []
	for i in range(size):
		List.append(number)
	return List
if __name__ == '__main__':
	data = pd.read_csv(filename)

	# #求各环节速度
	# ID1_Series = data['ID Check Process Time 1'].dropna(how='any')
	# ID2_Series = data['ID Check Process Time 2'].dropna(how='any')
	# ID_Series = ID1_Series.append(ID2_Series)
	# MM_Series = data['Milimeter Wave Scan times'].dropna(how='any')
	# Xray_Series = data['X-Ray Scan Time'].dropna(how='any')
	# DoubleCheck = data['Time to get scanned property'].dropna(how = 'any')

	# ID_speed = ID_Series.mean()
	# ID_var = ID_Series.std()
	# MM_speed = MM_Series.mean()
	# MM_var = MM_Series.std()
	# Xray_speed = Xray_Series.mean()
	# Xray_var = Xray_Series.std()
	# Double_speed = DoubleCheck.mean()
	# Double_var = DoubleCheck.std()

	# file = open('../data/putSpeed.csv','w')
	# content = [',ID,MM,Xray,Double\n','mean,'+str(ID_speed)+','+str(MM_speed)+','+str(Xray_speed)+','+str(Double_speed)+'\n',\
	# 'std,'+str(ID_var)+','+str(MM_var)+','+str(Xray_var)+','+str(Double_var)]
	# file.writelines(content)

	#求乘客每time_delta到达机场的人数分布（泊松过程）
	attrList = ['pre-check1','pre-check2','regular-check1','regular-check2','regular-check3','regular-check4','regular-check5','regular-check6']
	output = pd.DataFrame(columns = attrList)
	time_start = 0
	tot_time1 = data.iloc[:,0].sum()#得到pre-check总时间
	tot_time2 = data.iloc[:,1].sum()#得到regular-check总时间
	tmax1 = ceil2delta(math.ceil(tot_time1),time_delta)#pre-check总时间取被time_delta整除的上整
	tmax2 = ceil2delta(math.ceil(tot_time2),time_delta)#regular-check总时间取被time_delta整除的上整
	tmax = max([tmax1,tmax2])
	preList = list(range(time_delta,tmax1+time_delta,time_delta))
	reguList = list(range(time_delta,tmax2+time_delta,time_delta))
	preCountList = list_initialize(len(preList),0)
	reguCountList = list_initialize(len(reguList),0)
	#print(len(preCountList),len(reguCountList))
	for j in range(2):
		time = 0
		for i in range(data.shape[0]):
			if j==0:
				time +=data.iloc[i,j]
				index = range_index(time,preList)
				tmp = preCountList[index]
				tmp += 1
				preCountList[index]=tmp
			else:
				if pd.isnull(data.iloc[i,j]):
					break
				else:
					time +=data.iloc[i,j]
					index = range_index(time,reguList)
					tmp = reguCountList[index]
					tmp += 1
					reguCountList[index] = tmp
	#两列对齐，pre剩余用nan补全
	delta = len(reguCountList)-len(preCountList)
	for i in range(delta):
		preCountList.append(np.nan)

	output['pre-check'] = preCountList
	output['regular-check'] = reguCountList

	port = 1.0
	pre_mean = output['pre-check'].mean()*port
	regu_mean = output['regular-check'].mean()*port
	print(pre_mean*0.45+regu_mean*0.55)
	size = math.floor(Dseconds/time_delta)
	popuFreq = pd.DataFrame(columns = attrList)
    
	flowFreq26 = strategy(popuFreq,2,pre_mean,regu_mean,size) 
	flowFreq26.to_csv('../data/flowFreq_2-6'+'-'+str(port)+'.csv',index = False)
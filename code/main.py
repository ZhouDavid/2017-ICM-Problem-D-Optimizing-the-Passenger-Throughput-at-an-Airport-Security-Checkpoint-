import pandas as pd
import numpy as np
import math
from datetime import time
def str2seconds(stime):
	minutes = int(stime[0:2])
	seconds = int(stime[3:5])
	mseconds = int(stime[6:7])
	tot_seconds = minutes*60+seconds+0.1*mseconds
	return tot_seconds

def parseSeconds(stime):
	if len(stime)==4:
		seconds = int(stime[2:4])*60
	else:
		seconds = int(stime[3:5])+int(stime[6:7])*0.1
	return seconds

time = pd.read_csv('time.csv')
columnName1 = ['TSA Pre-Check Arrival Times','Regular Pax Arrival Times','ID Check Process Time 1',\
'ID Check Process Time 2','Milimeter Wave Scan times','X-Ray Scan Time','X-Ray Scan Time','Time to get scanned property']
columnName2 = ['Pre-Check Arrival time','regular arrival time','ID check time','human scan time','bag scan time','double-check time']
k = 0
data1 = pd.DataFrame(columns = columnName1)
data2 = pd.DataFrame(columns = columnName2)
for j in range(len(columnName1)):
	SeriesList = []
	if j==0 or j==1 or j==4 or j==5 or j==6:
		for i in range(1,len(time[columnName1[j]])):
			if pd.isnull(time[columnName1[j]][i]):
				SeriesList.append(np.nan)
			else:
				seconds1 = str2seconds(time[columnName1[j]][i-1])
				seconds2 = str2seconds(time[columnName1[j]][i])
				SeriesList.append(seconds2-seconds1)
	else:
		for i in range(len(time[columnName1[j]])):
			if pd.isnull(time[columnName1[j]][i]):
				SeriesList.append(np.nan)
			else:
				SeriesList.append(parseSeconds(time[columnName1[j]][i]))
		SeriesList = SeriesList[0:len(SeriesList)-1]
	data1[columnName1[j]] = SeriesList
data1.describe().to_csv('data_describe.csv',index=True)
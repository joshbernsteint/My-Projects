#Made by Joshua Bernstein
# Ideal Conditions: 
# Temperature: 60-76
# Humidity >= 95%
# Dew Point >= 60 Degrees
# Least Time to Germinate: 6 hrs


#Time has the highest weight of the variables, if the time is in the ideal condition, then +20 points will be added (<=6)
#If the temperature is in the ideal condition, then +15 points will be added 60 <-> 76 and <80
#If the Humidity is in the ideal condition, then +10 points will be added >= 0.95
#If the Dew Point is in the ideal condition, then +7 points will be added >= 60


import matplotlib.pyplot as plt #Used to create the graph
import csv #Used to read data

temp = 0
humidity = 0
dewPoint = 0
accumTime = 0
timeOutsideIdeal = 0 # We will assume that after 10 hours outside of ideal conditions, the fungal disease will start to die
risk = 0

class day:
    '''Used to store the information for one day'''
    def __init__(self,name):
        self.label = name
        self.times = []
    def addTime(self,tLst):
        '''Adds a time block to the list'''
        self.times.append(tLst)
    def getLst(self):
        '''Returns a list of all time blocks and their corresponding variables'''
        return self.times
    def print(self):
        '''Prints out full class, used solely for debugging'''
        print(f'Date: {self.label}')
        for i in range(len(self.times)):
            print(f'Time Reading #{i+1}:\t{self.times[i]}')


def createGraph(x,y):
    '''Creates a graph with x-axis x and y-axis y'''
    plt.plot(x,y)
    plt.xlabel("Hours (hr)")
    plt.ylabel("Risk Percentage (%)")
    plt.title("Risk Percentage of Common rust (6/1/2022 to 6/4/2022)")
    plt.axis([0,100,0,0.75])
    plt.xscale('linear')
    plt.grid(True)
    plt.show()


days = []
with open("Days.csv",'r') as csv_file:
    file_content = csv.reader(csv_file) #Converts the file into a list of lines
    index = 0
    for row in file_content:#Loops through each line
        if index == 0:
            inner = 0
            for col in row:#Creates a list of days
                if col != "" and inner == 0:
                    days.append(day(col[3:]))
                elif col != "":
                    days.append(day(col))
                inner +=1
        elif index > 1:#Adds each time block to the appropriate day
            innerIndex = 0
            days[0].addTime(row[0:4])
            days[1].addTime(row[5:9])
            days[2].addTime(row[10:14])
            days[3].addTime(row[15:19])
        index += 1


def isIdeal(temperature,humid,d_p):
    '''Returns whether or not the variables are in the ideal condition'''
    score = 0
    if 60 <= temperature <= 76:
        score += 15
    if humid >= 0.95:
        score += 10
    if d_p >= 60:
        score += 7
    
    if score == 32:
        return True
    return False


hourCount = 0
timeLst = []
riskLst = []
for d in days:
    temporary = d.getLst()
    for col in temporary:
        temp = int(col[1])
        humidity = int(col[3])/100
        dewPoint = int(col[2])

        if isIdeal(temp,humidity,dewPoint):#If the climate is ideal
            accumTime += 1
            timeOutsideIdeal = 0
        else:# If the weather is not ideal
            timeOutsideIdeal += 1
            if timeOutsideIdeal >= 10:
                accumTime = 0
        risk = 0#Intializes the risk to 0
        if timeOutsideIdeal < 20:#If the weather has not been ideal for less than 20 hours
            if 0 <= accumTime <= 2:
                risk = 0.25
            elif 2 <= accumTime <= 6:
                risk = 0.5
            elif 6 <= accumTime <= 10:
                risk = 0.75
            else:
                risk = 0.95
        else:#If the weather has not been ideal for 20 hours or more
            risk = 0.1
        

        timeLst.append(hourCount)
        riskLst.append(risk)
        hourCount +=1

createGraph(timeLst,riskLst)
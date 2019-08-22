import matplotlib.pyplot as plt
import pandas as pd
import random
import simpy
import math
import numpy as np
np.set_printoptions(precision=4)
np.set_printoptions(suppress=True)


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)



#def PrintCustomers(customers):
#    print("%s    %s      %s     %s     %s     %s" % ("name", "timeOfArrival", "waitTime", "startTime", "serviceTime", "departureTime"))
#    for customer in customers:
#        customer.Print()

def CustomersToArray(customers):
    arr = np.empty([0,6])
    for customer in customers:
        row = np.array([customer.name, customer.timeOfArrival, customer.waitTime, customer.startTime, customer.serviceTime, customer.departureTime])
        arr = np.vstack((arr,row))
    return arr

def ArrayToDataFrame(arr):
    return pd.DataFrame(arr, columns=["id","timeOfArrival","waitTime","startTime","serviceTime","departureTime"])

def CustomersToDataFrame(customers):
    arr = CustomersToArray(customers)
    df = ArrayToDataFrame(arr)
    return df

class Customer():
    def __init__(self, simu, name, timeOfArrival, waitTime, startTime, serviceTime, departureTime):
        self.simu = simu
        self.name = name
        self.timeOfArrival = timeOfArrival
        self.waitTime = waitTime
        self.startTime = startTime
        self.serviceTime = serviceTime
        self.departureTime = departureTime

    def Arrival(self, env):
        with self.simu.servers.request() as request:
            yield request
            yield env.process(self.simu.Serve(self))

    #def Print(self):
    #    print("%s          %8.4f      %8.4f      %8.4f        %8.4f          %8.4f" % (self.name, self.timeOfArrival, self.waitTime, self.startTime, self.serviceTime, self.departureTime))



class Simu:
    def __init__(self, numServers, serviceTime, arrivalTime, duration):
        self.numServers = numServers          # Number of agents taking chats
        self.serviceTime = serviceTime         # AHT (Average Handle Time = Number of seconds it takes to help a customer, once the chat has begun)
        self.arrivalTime = arrivalTime         # AAT (Average Arrival Time = Number of seconds between customer's arrivals)
        self.duration = duration           # Simulation time in Seconds

        self.queueSize = 0
        self.customers = []
        self.statesQueueSize = []

        # Create an environment and start the Queue process
        self.env = simpy.Environment()
        self.servers = simpy.Resource(self.env, self.numServers)

        self.env.process(self.State())
        self.env.process(self.Queue())

    def RunSimu(self):
        self.env.run(until=self.duration)

    def State(self):
        while True:
            self.statesQueueSize.append(self.queueSize)
            yield self.env.timeout(1)

    def Queue(self):
        i = 0

        #Create more customers while the simulation is running
        while True:
            arrivalTime = random.expovariate(1.0/self.arrivalTime)
            yield self.env.timeout(arrivalTime)
            i += 1
            customer = Customer(self, name=i, timeOfArrival=self.env.now, waitTime=None, startTime=None, serviceTime=None, departureTime=None)
            self.queueSize += 1
            self.env.process(customer.Arrival(self.env))

    def Serve(self, customer):
        customer.waitTime = self.env.now - customer.timeOfArrival
        customer.startTime = self.env.now

        #customer.serviceTime = random.normalvariate(self.serviceTime,)
        #customer.serviceTime = random.expovariate(1.0/self.serviceTime)

        mu = self.serviceTime
        std = 553.867816
        mu2 = math.log(mu)-0.5*math.log(math.pow(std/mu,2)+1)
        std2 = 0.716256793
        customer.serviceTime = random.lognormvariate(mu2,std2)
        yield self.env.timeout(customer.serviceTime)

        self.queueSize -= 1

        customer.departureTime = self.env.now
        self.customers.append(customer)

    def PrintResults(self):
        #print("")

        df = CustomersToDataFrame(self.customers)
        #print(df)

        #print(hist)


# Model Variables
NumberOfAgents = 5
#ServiceTime = 676.5
ServiceTime = 676.5
ArrivalTime = 115
Duration = 3600
NumberOfSimulations = 1


figA, (axA0, axA1, axA2) = plt.subplots(nrows=3, ncols=1) # two axes on figure
figA.set_figheight=12

# RunSimulations
simulations = []
for i in range(NumberOfSimulations):
    sim = Simu(NumberOfAgents, ServiceTime, ArrivalTime, Duration)
    sim.RunSimu()
    simulations.append(sim)

# Get Summary Data
i = 0
custArr = np.empty([0,7])
queueSizeArr = np.empty([Duration,0])
for x in simulations:
    custArr_u = CustomersToArray(x.customers)
    custArr = np.vstack((custArr,np.hstack((np.array(np.zeros(len(x.customers))+i)[np.newaxis].T, custArr_u))))
    queueSizeArr = np.hstack((queueSizeArr, np.asarray(x.statesQueueSize)[np.newaxis].T))

    custData = pd.DataFrame(custArr_u, columns=["custId","timeOfArrival","waitTime","startTime","serviceTime","departureTime"])

    axA0.set_title('Histogram of Waittimes')
    bins = [x/2 for x in range(0,100,1)]
    axA0.hist(custData['waitTime'], bins=bins, density=True, alpha=0.5)
    axA1.set_title('Queue Size by Time')
    axA1.plot(x.statesQueueSize)

    i += 1

customerData = pd.DataFrame(custArr, columns=["simId","custId","timeOfArrival","waitTime","startTime","serviceTime","departureTime"])
print(customerData.describe())

queueSizeData = pd.DataFrame(queueSizeArr)
print(queueSizeData.describe())

#print(customerData)

# Get Average Queue Sizes by State
tmp = np.zeros([Duration,1])
for i in range(0,len(tmp)):
    tmp[i] = sum(queueSizeArr[i])/len(queueSizeArr[i])

axA2.set_title('Average Queue Size')
axA2.plot(tmp, marker='o')

#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

import TraceAnalysis

class TraceAnalysisJitter(TraceAnalysis.TraceAnalysis):
    name = 'jitter'
    ''' initialization of the data structure used for the jitter analysis'''
    def __init__(self,si):
        self.si = si
        nbProc = len(si.procNames)
        self.value = 0
        self.taskActivationTime = {}
        self.jitterTime = {}
        self.readyTasksbyId = {}
        self.handlers = {
            'READY_AND_NEW': self.handleReadyAndNew,
            'READY': self.handleReady,
            'RUNNING': self.handleRunning
        }
    
    def handleEvent(self, event):
        procId = event['id']
        type = event['type']
        if type == 'proc':
            time = event['ts']
            stateName = event['stateName']
            stateName in self.handlers and self.handlers[stateName](time, procId)

    def handleReadyAndNew(self, time, procId):
        if not procId in self.taskActivationTime:
            self.taskActivationTime[procId] = []

        self.taskActivationTime[procId].append(time)
        if not procId in self.readyTasksbyId:
            self.readyTasksbyId[procId] = 0 

    def handleRunning(self, time, procId):
        if self.readyTasksbyId[procId] == 0:
            if not procId in self.jitterTime:
                self.jitterTime[procId] = []
            self.jitterTime[procId].append(time - self.taskActivationTime[procId].pop(0))
        else:
              self.readyTasksbyId[procId] -= 1  

    def handleReady(self, time, procId):
        self.readyTasksbyId[procId] += 1
    
    ''' handle event activation/running of tasks to perform jitter analysis'''
    def stop(self):
        for procId in self.jitterTime:
            time = sum(self.jitterTime[procId]) / len(self.jitterTime[procId])
            print('Proc {0} ===> jitter is {1}'.format(self.si.procNames[procId], time))
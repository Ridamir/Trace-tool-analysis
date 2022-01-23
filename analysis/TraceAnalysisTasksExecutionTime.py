#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

import TraceAnalysis
import json
from functools import reduce 

class TraceAnalysisTasksExecutionTime(TraceAnalysis.TraceAnalysis):
    name = 'tasksExecutionTime'

    def __init__(self, si):
        pass

    def calculate_job_time(self, acc, job_life_cycle):
        if acc is None:
            return (job_life_cycle, 0)
        if job_life_cycle["state"] == "SUSPENDED" or job_life_cycle["state"] == "WAITING":
            if acc[0]["state"] == "RUNNING":
                execution_time = acc[1] + job_life_cycle["time"] - acc[0]["time"]
                return (job_life_cycle, execution_time)
        return (job_life_cycle, acc[1])

    def calculate_jobs_time(self, acc, jobs_execution_time):
        return acc + jobs_execution_time[1]


    def stop(self):
        with open("tasks.json") as jsonFile:
            jsonObject = json.load(jsonFile)
        tasks_id = jsonObject.keys()
        for task_id in tasks_id:
            execution_time = 0
            jobs_life_cycles = jsonObject[task_id]["jobs_life_cycles"]
            jobs_execution_time = list(map(lambda x : reduce(self.calculate_job_time, x, None), jobs_life_cycles))
            sorted_list = sorted(jobs_execution_time, key = lambda x : x[1])
            result = reduce(self.calculate_jobs_time, jobs_execution_time, 0)
            print("The total execution time of task id", task_id, "is: ",result)
            #print(result)
            if len(sorted_list) > 0:
                print("Metrics for that task id", task_id,"are:")
                print("     - Min time execution: ", sorted_list[0][1])
                print("     - Max time execution: ", sorted_list[-1][1])
                print("     - Avg time execution: ", result/len(sorted_list))
            

    
#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

import TraceAnalysis
import json

class PreprocessingData(TraceAnalysis.TraceAnalysis):
    name = 'preprocessing'

    def __init__(self, si):
        self.tasks = {}
        self.resources = {}
        self.events = {}
        self.messages = {}
        self.alarms = {}

    def handleEvent(self, event):
        eventHandlers = {
            'proc': lambda: self.tasks.setdefault(event['id'], Task(event['id'])) \
                                      .add_job_state(JobState(event["procName"], event['ts'], event["stateName"])) ,
            'resource': lambda: self.resources.setdefault(event['resourceName'], Ressource(event['resourceName'])) \
                                              .add_resource_state(ResourceState(event['ts'], event["stateName"], event["procName"])) ,
            'event_set': lambda: self.events.setdefault(event['evtName'], Event(event['evtName'])) \
                                            .add_event_state(EventState(event["ts"], event["type"], event["procName"], event["evtName"])) ,
            'event_reset': lambda: self.events.setdefault(event['evtName'], Event(event['evtName'])) \
                                              .add_event_state(EventState(event["ts"], event["type"], event["procName"], event["evtName"])) ,
            'message_send': lambda: self.messages.setdefault(event['id'], Message(event['id'])) \
                                                 .add_message_state(MessageState(event['ts'], event["type"], event["msgName"], event["kind"])) ,
            'message_receive': lambda: self.messages.setdefault(event['id'], Message(event['id'])) \
                                                    .add_message_state(MessageState(event['ts'], event["type"], event["msgName"], event["kind"])) ,
            'timeobj_expire': lambda: self.alarms.setdefault(event['id'], Alarm(event['id'])) \
                                                 .add_alarm_state(AlarmState(event['ts'], event["type"], event["id"], event["toName"])) ,
        }
        event['type'] in eventHandlers and eventHandlers[event['type']]()

    def stop(self):
        ''' tasks '''
        json_tasks = json.dumps(self.tasks, default=lambda x: x.__dict__, indent = 4)
        with open("tasks.json", "w") as outfile:
            outfile.write(json_tasks)  
        ''' resources '''
        json_resources = json.dumps(self.resources, default=lambda x: x.__dict__, indent = 4)
        with open("resources.json", "w") as outfile:
            outfile.write(json_resources)
        ''' messages '''
        json_messages = json.dumps(self.messages, default=lambda x: x.__dict__, indent = 4)
        with open("messages.json", "w") as outfile:
            outfile.write(json_messages)
        ''' alarms '''
        json_alarms = json.dumps(self.alarms, default=lambda x: x.__dict__, indent = 4)
        with open("alarms.json", "w") as outfile:
            outfile.write(json_alarms)            
        ''' events '''
        json_events = json.dumps(self.events, default=lambda x: x.__dict__, indent = 4)
        with open("events.json", "w") as outfile:
            outfile.write(json_events)      


class JobState: 

    def __init__(self, procName, time, state):
        self.__dict__.update({k: v for k, v in locals().items() if k != 'self'})


class ResourceState: 

    def __init__(self, time, state, procName):
        self.__dict__.update({k: v for k, v in locals().items() if k != 'self'})


class EventState: 

    def __init__(self, time, state, procName, evtName):
        self.__dict__.update({k: v for k, v in locals().items() if k != 'self'})


class MessageState:

    def __init__(self, time, state, msgName, kind):
        self.__dict__.update({k: v for k, v in locals().items() if k != 'self'})


class AlarmState: 

    def __init__(self, time, state, id, name):
        self.__dict__.update({k: v for k, v in locals().items() if k != 'self'})


class Task:

    def __init__(self, id):
        self.id = id
        self.jobs_life_cycles = []
           
    def add_job_state(self, job_state):       
        handlers = {
            'READY_AND_NEW': lambda: self.jobs_life_cycles.append([job_state]),
            'READY': lambda: self.__append_if_exist(job_state, self.__get_first_running_or_waiting_job),
            'RUNNING': lambda: self.__append_if_exist(job_state, self.__get_first_ready_job),
            'SUSPENDED': lambda: self.__append_if_exist(job_state, self.__get_first_running_job),
            'WAITING' : lambda: self.__append_if_exist(job_state, self.__get_first_running_job),
        }
        job_state.state in handlers and handlers[job_state.state]()

    def __append_if_exist(self, job_state, get_job):
        job_life_cycle = get_job()
        job_life_cycle and job_life_cycle.append(job_state)
           
    def __get_first_job_by_predicate(self, predicate):
        return next(filter(lambda job_life_cycle: predicate(job_life_cycle[-1].state), self.jobs_life_cycles), None)    # filter return table 
                                                                                                                        # and next return the first element         
    def __get_first_ready_job(self):     
        return self.__get_first_job_by_predicate(lambda state: state == "READY_AND_NEW" or state == "READY")       

    def __get_first_running_job(self):
        return self.__get_first_job_by_predicate(lambda state: state == "RUNNING")

    def __get_first_running_or_waiting_job(self):
        return self.__get_first_job_by_predicate(lambda state: state == "RUNNING" or state == "WAITING") 


class Ressource: 

    def __init__(self, resourceName):
        self.resourceName = resourceName
        self.resources_life_cycles = []

    def add_resource_state(self, ressource_state): 
        self.resources_life_cycles.append(ressource_state)


class Event:

    def __init__(self, evtName):
        self.evtName = evtName
        self.events_life_cycles =[]

    def add_event_state(self, event_state):
        self.events_life_cycles.append(event_state)


class Message:

    def __init__(self, id):
        self.id = id
        self.messages_life_cycles =[]

    def add_message_state(self, message_state):
        self.messages_life_cycles.append(message_state)
        

class Alarm:

    def __init__(self, id):
        self.id = id
        self.alarms_life_cycles =[]

    def add_alarm_state(self, alarm_state):
        self.alarms_life_cycles.append(alarm_state)

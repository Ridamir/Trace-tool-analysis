#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

import TraceAnalysis
import json

class TraceAnalysisEventConsistency(TraceAnalysis.TraceAnalysis):
    name = 'eventConsistency'

    def __init__(self, si):
        self.inconsistent_event = []
        
    def check_event_consistency(self):
        with open("events.json") as jsonFile:
            jsonObject = json.load(jsonFile)
        events_name = jsonObject.keys()
        for event_name in events_name:
            events_life_cycles = jsonObject[event_name]["events_life_cycles"]
            last_state = None
            for event_life_cycles in events_life_cycles:
                state = event_life_cycles["state"]
                if last_state == state:
                    self.inconsistent_event.append(event_name)
                    break
                last_state = state
        if len(self.inconsistent_event) == 0:
            print("There is no inconsistency in events")
        else:
            print("There is inconsistency in events: ", self.inconsistent_event)

    def stop(self):
        self.check_event_consistency()
        
        

 


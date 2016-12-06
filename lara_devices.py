#!/usr/bin/env python
# -*- coding: utf-8 -*-

#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: LARA_Device
# FILENAME: lara_device.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# VERSION: 0.0.3
#
# CREATION_DATE: 2013/06/03
# LASTMODIFICATION_DATE: 2014/09/17
#
# BRIEF_DESCRIPTION: Device classes for LARA
# DETAILED_DESCRIPTION:
#
# ____________________________________________________________________________
#
#   Copyright:
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This file is provided "AS IS" with NO WARRANTY OF ANY KIND,
#   INCLUDING THE WARRANTIES OF DESIGN, MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE.
#
#   For further Information see COPYING file that comes with this distribution.
#_______________________________________________________________________________

import lara_material as lam

import logging
import itertools

class LA_Device(object):
    """LARA Device class
    """
    #: Doc comment for class attribute Foo.bar.
    #: It can have multiple lines.
    
    #: Doc comment for init
    def __init__(self, device_name="", ext_nests=[], int_nests=[] ) :
        self.device_name = device_name;
        
        self.external_nests_list = []
        self.external_stack_occupied = []
        self.external_stack_reference = []
        
        self.internal_nests_list = []
        self.internal_stack_occupied = []
        self.internal_stack_reference = []
            
        for ext_nest in ext_nests:
            for stacks in range(ext_nest["stacks_num"]):
                ext_nest["curr_max_nests"] = 1 
                self.external_nests_list.append( ext_nest )
                self.external_stack_occupied.append(set())  
                self.external_stack_reference.append(set(range(1,2)))   # set 1 free nest by default
                
        for int_nest in int_nests:
            for stacks in range(int_nest["stacks_num"]):
                int_nest["curr_max_nests"] = 1
                self.internal_nests_list.append( int_nest )
                self.internal_stack_occupied.append(set())
                self.internal_stack_reference.append(set(range(1,2))) # set 1 free nest by default
        
        #self.device_class
        
    def totalExtNests(self, stack_num):
        return(self.external_nests_list[stack_num-1]["nests_num"])
    
    def loadNest(self, nest_location, ext_int):
        stack_index = nest_location[0]-1
        #print(nest_location)
        #print(self.external_nests_list)
        
        if ext_int == "ext": 
            if nest_location[1] < self.external_nests_list[stack_index]["nests_num"]:
                self.external_stack_occupied[stack_index].add(nest_location[1])
                self.external_stack_reference[stack_index].add(nest_location[1])
                if self.external_nests_list[stack_index]["curr_max_nests"] < nest_location[1] :
                    logging.warning("check, if max nest number can be reached !")
                    self.external_nests_list[stack_index]["curr_max_nests"] = nest_location[1] 
            else :
                logging.error("no further free external nests available")
        else :
            if nest_location[1] < self.internal_nests_list[stack_index]["nests_num"]:
                self.internal_stack_occupied[stack_index].add(nest_location[1])
                self.internal_stack_reference[stack_index].add(nest_location[1])
                if self.internal_nests_list[stack_index]["curr_max_nests"] < nest_location[1] :
                    logging.warning("check, if max nest number can be reached !")
                    self.internal_nests_list[stack_index]["curr_max_nests"] = nest_location[1] 
            else :
                logging.error("no further free nests available")
            
    def rmNest(self, nest_location,ext_int):
        stack_index = nest_location[0]-1
        logging.warning("nest removal without checking")
        if ext_int == "ext":
            self.external_stack_occupied[stack_index].discard(nest_location[1])
        else :
            self.internal_stack_occupied[stack_index].discard(nest_location[1])
            
    def mvExtNest(self, source_nest_location, target_nest_location):
        stack_index = source_nest_location[0]-1
        self.loadExtNest(target_nest_location)
        self.external_stack_occupied[stack_index].discard(source_nest_location[1])
        
    def firstFreeNest(self, stack_num,ext_int):
        stack_index = stack_num - 1 
        if ext_int == "ext":
            free_locs = self.external_stack_reference[stack_index] - self.external_stack_occupied[stack_index]
            if len(free_locs) > 0:
                return(free_locs.pop())
            elif  len(self.external_stack_reference[stack_index]) < self.external_nests_list[stack_index]["nests_num"] :
                self.external_nests_list[stack_index]["curr_max_nests"] += 1
                curr_max_nests = self.external_nests_list[stack_index]["curr_max_nests"]
                self.external_stack_reference[stack_index].add(curr_max_nests)  # add one more nest to occupy
                logging.debug("ld - fFN: curr max nests %s" %curr_max_nests)
                return(curr_max_nests)
            else:
                logging.error("no external positions available in stack, missing element proper error handling")
        else :
            free_locs = self.internal_stack_reference[stack_index] - self.internal_stack_occupied[stack_index]
            if len(free_locs) > 0:
                return(free_locs.pop())
            elif  len(self.internal_stack_reference[stack_index]) < self.internal_nests_list[stack_index]["nests_num"] :
                self.internal_nests_list[stack_index]["curr_max_nests"] += 1
                curr_max_nests = self.internal_nests_list[stack_index]["curr_max_nests"]
                self.internal_stack_reference[stack_index].add(curr_max_nests)  # add one more nest to occupy
                return(curr_max_nests)
            else:
                logging.error("no internal positions available in stack, missing element proper error handling")

    def testOccupied(self, nest_location):
        pass
        
    def name(self):
        return(str(self.device_name))
        
class Dispenser(LA_Device):
    def __init__(self, device_name="", ext_nests=[], int_nests=[]):
        super(Dispenser, self).__init__(device_name, ext_nests, int_nests)
        
class PlateHotel(LA_Device):
    def __init__(self, device_name="", ext_nests=[], int_nests=[]):
        super(PlateHotel, self).__init__(device_name, ext_nests, int_nests)        
       
class Incubator(LA_Device):
    def __init__(self, device_name="", ext_nests=[], int_nests=[]):
        super(Incubator, self).__init__(device_name, ext_nests, int_nests)    
        
class PlateCarousel(LA_Device):
    def __init__(self, device_name="", ext_nests=[], int_nests=[]):
        super(PlateCarousel, self).__init__(device_name, ext_nests, int_nests)    
        
class BarcodeReader(LA_Device):
    """Docstring for class LA_Device"""

    #: Doc comment for class attribute Foo.bar.
    #: It can have multiple lines.
    
    #: Doc comment for init
    def __init__(self, device_name="", ext_nests=[], int_nests=[]):
        super(BarCodeReader, self).__init__(device_name, ext_nests, int_nests)
      
class LabAutomationSystem(dict):
    # structure: device_name - device )
    def __init__(self, iterable=(), **kwargs):
        # filling with parameter given container info
        self.update(iterable, **kwargs)
    
    def update(self, iterable=(), **kwargs):
        if hasattr(iterable, 'iteritems'):
            iterable = iterable.iteritems()
        for (key, value) in itertools.chain(iterable, kwargs.iteritems()):
            if key not in self:
                self[key] = value
                
    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, dict.__repr__(self))
        
    def setDefaultDevices(self):
        logging.info("automation system needs to be moved into lml file")
        self["Carousel"] = PlateHotel("Carousel", ext_nests=[{"stacks_num": 4, "nests_num":25,"stack_hight":35,"orientation":'l', "plates_per_nest":1},
                                                         {"stacks_num": 4, "nests_num":15,"stack_hight":45,"orientation":'l', "plates_per_nest":1},
                                                         {"stacks_num": 1, "nests_num":8,"stack_hight":45,"orientation":'l', "plates_per_nest":1} ])
        self["Combi"] =  Dispenser("Combi", ext_nests=[{"stacks_num": 1,"nests_num":1,"stack_hight":45,"orientation":'l', "plates_per_nest":1}])
        self["Bravo"] =  Dispenser("Bravo", ext_nests=[{"stacks_num": 1,"nests_num":9,"stack_hight":45,"orientation":'l', "plates_per_nest":1}])
        self["CombiHotel"] = PlateHotel("CombiHotel", ext_nests=[{"stacks_num": 1, "nests_num":6,"stack_hight":35,"orientation":"pl", "plates_per_nest":1} ]) 
        self["BufferNestsLBravo"] = PlateHotel("BufferNestsLBravo", ext_nests=[{"stacks_num": 1, "nests_num":6,"stack_hight":35,"orientation":"pl", "plates_per_nest":1} ]) 
        self["BufferNestsRBravo"] = PlateHotel("BufferNestsRBravo", ext_nests=[{"stacks_num": 1, "nests_num":6,"stack_hight":35,"orientation":"pl", "plates_per_nest":1} ]) 
        self["Tip_Storage"] = PlateHotel("Tip_Storage", ext_nests=[{"stacks_num": 1, "nests_num":6,"stack_hight":45,"orientation":"pl", "plates_per_nest":1} ]) 
        self["Cytomat1550_1"] = PlateHotel("Cytomat1550_1", ext_nests=[{"stacks_num": 1, "nests_num":1,"stack_hight":45,"orientation":'p', "plates_per_nest":1}],
                                                               int_nests=[{"stacks_num": 1, "nests_num":20,"stack_hight":30,"orientation":'p', "plates_per_nest":1},
                                                                          {"stacks_num": 1, "nests_num":10,"stack_hight":45,"orientation":'p', "plates_per_nest":1} ])
        self["Cytomat1550_2"] = PlateHotel("Cytomat1550_2", ext_nests=[{"stacks_num": 1, "nests_num":1,"stack_hight":45,"orientation":'p', "plates_per_nest":1}],
                                                               int_nests=[{"stacks_num": 1, "nests_num":20,"stack_hight":30,"orientation":'p', "plates_per_nest":1},
                                                                          {"stacks_num": 1, "nests_num":10,"stack_hight":45,"orientation":'p', "plates_per_nest":1} ])
        self["Cytomat470"] = PlateHotel("Cytomat470", ext_nests=[{"stacks_num": 1, "nests_num":1,"stack_hight":45,"orientation":'p', "plates_per_nest":1}],
                                                           int_nests=[{"stacks_num": 1, "nests_num":20,"stack_hight":30,"orientation":'p', "plates_per_nest":1},
                                                                      {"stacks_num": 1, "nests_num":10,"stack_hight":45,"orientation":'p', "plates_per_nest":1} ])
        self["Cytomat_2"] = PlateHotel("Cytomat_2", ext_nests=[{"stacks_num": 1, "nests_num":1,"stack_hight":45,"orientation":'p', "plates_per_nest":1}],
                                                          int_nests=[{"stacks_num": 1, "nests_num":20,"stack_hight":30,"orientation":'p', "plates_per_nest":1},
                                                                     {"stacks_num": 1, "nests_num":10,"stack_hight":45,"orientation":'p', "plates_per_nest":1} ])
        self["Omega"] =  Dispenser("Omega", ext_nests=[{"stacks_num": 1,"nests_num":1,"stack_hight":45,"orientation":'l', "plates_per_nest":1}])
        self["Varioskan"] =  Dispenser("Varioskan", ext_nests=[{"stacks_num": 1,"nests_num":1,"stack_hight":45,"orientation":'l', "plates_per_nest":1}])
        self["Rotanta"] = PlateHotel("Rotanta", ext_nests=[{"stacks_num": 1, "nests_num":4,"stack_hight":35,"orientation":"l", "plates_per_nest":1} ]) 
        self["Tool_Hotel"] =  Dispenser("Tool_Hotel", ext_nests=[{"stacks_num": 1,"nests_num":1,"stack_hight":45,"orientation":'l', "plates_per_nest":1}])

    def loadDevices(self, exp_lml_tree):
        for device in exp_lml_tree.findall( 'AutomationSystem/Devices' ):
            logging.debug("reading lml file automation system %s" % device)

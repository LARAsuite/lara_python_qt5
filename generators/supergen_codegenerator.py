#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: LA_CodeGenerator
# FILENAME: supergen_codegenerator.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# CREATION_DATE: 2013/11/25
# LASTMODIFICATION_DATE: 2016/06/02
#
# BRIEF_DESCRIPTION: super codegenerator class for LARA
# DETAILED_DESCRIPTION: This is a new two Phase compiler - phase 1 determines the language and assembles the modules, 
#                       phase 2 interpretes the modules
#
# ____________________________________________________________________________
"""

__version__ = "0.0.3"

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

import sys
import logging
import datetime

import singledispatch  # will be included in python 3.4 functools library; for python < 3.3 plese use pip install singledispatch

import lara_process as lap
import lara_material as lam

from lara_codegenerator import LA_CodeGenerator
from lara_lml_generator import LA_LMLGenerator
from epMotion_codegenerator import LA_GenerateEPMotionCode

class SuperGen(LA_CodeGenerator):
    """Phase 1 meta generator"""
    def __init__(self, parse_obj, mode=None):
        super(SuperGen,self).__init__(parse_obj)
        
        self.experiment = parse_obj
        
        if mode == lap.ProcessStep.lml :
            self.lml_gen = LA_LMLGenerator(experiment=parse_obj)
            self.traverse4lml()
            self.lml_gen.saveExpXMLFile()
        
        else: 
            self.mode = lap.ProcessStep.sila   # default process mode 
            self.v11_obj_list = []
            self.epmotion_obj_list = []
            self.momentum_obj_list = []
            self.tecan_obj_list = []
    
            self.generate = singledispatch.singledispatch(self.generate)
            self.generate.register(lap.BeginSubProcess, self.genBeginSubProcess)
            self.generate.register(lap.EndSubProcess, self.genEndSubProcess)
        
            self.traverse()
            
            # Phase 2 real code generator calls
            
            if self.epmotion_obj_list:
                LA_GenerateEPMotionCode(self.epmotion_obj_list, experiment=self.experiment)
        
    def generate(self,item):
        if( self.mode == lap.ProcessStep.epMotion ):
            self.epmotion_obj_list.append(item)
        else:
            logging.debug("super gen: generic item: %s" % item )
            #raise TypeError("Type not supported.")
        
    def genBeginSubProcess(self, process_step):
        logging.debug("** begin  ")
        if(process_step.interpreter() == lap.ProcessStep.epMotion):
            self.mode = lap.ProcessStep.epMotion
            self.epmotion_obj_list.append(process_step)
            
    def genEndSubProcess(self, process_step):
        logging.debug("** end  ")
        if(process_step.interpreter() == lap.ProcessStep.epMotion):
            self.mode = lap.ProcessStep.sila
            self.epmotion_obj_list.append(process_step)
            
    def generateLML(self,parent_item, item):
        logging.debug("LML: gen call - item %s" %item)
        self.lml_gen.addSubprocess(parent_item, item)
        

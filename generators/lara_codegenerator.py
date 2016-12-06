#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: LA_CodeGenerator
# FILENAME: lara_codegenerator.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# CREATION_DATE: 2013/11/25
# LASTMODIFICATION_DATE: 2016/06/02
#
# BRIEF_DESCRIPTION: Codegenerator base class for LARA
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


import logging
import singledispatch  # will be included in python 3.4 functools library; for python < 3.3 plese use pip install singledispatch

class LA_CodeGenerator(object):
    """ LARA Codegenerator base class """
    def __init__ (self, object_to_parse):
        self.object_to_parse = object_to_parse
        
    def traverse(self):   
        for step in self.object_to_parse:
            self.generate(step)
            
    def traverse4lml(self):
        #~ next_subprocess = self.object_to_parse.exp_begin_item
        logging.info("iterating through steps ....")
        
        for parent_subprocess, subprocess in self.object_to_parse.process_list.items():
            self.generateLML(parent_subprocess, subprocess)
            
        #~ while next_subprocess :
            #~ logging.debug(next_subprocess)
            #~ self.generateLML(next_subprocess)
            #~ next_subprocess = next_subprocess.flowNext()
            

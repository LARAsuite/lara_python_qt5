#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: LA_LMLGenerator
# FILENAME: lmlgenerator.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# CREATION_DATE: 2016/06/05
# LASTMODIFICATION_DATE: 2016/06/05
#
# BRIEF_DESCRIPTION: LARA markup language LML generator class for LARA
# DETAILED_DESCRIPTION:
#
# TODO: - file info handling 
#                       
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
import datetime
import os.path
import xml.etree.ElementTree as ET

from PyQt4 import Qt, QtCore

class LA_LMLGenerator(QtCore.QObject):
    textAdded = QtCore.pyqtSignal()
    def __init__(self, experiment=None, filename=""):
        super(LA_LMLGenerator,self).__init__()
        
        logging.debug("LML: in codegen")
        
        self.experiment = experiment
        self.filename = filename
                
        self.initExpLML()

    def name(self):
        return(self.filename)
                
    def initExpLML(self):
        # preparing experiment XML structure
        self.exp_lml_root = ET.Element("LARA", version="0.1", filetype="Experiment", md5sum="000000000000000000000000000000")
        self.exp_lml_param = ET.SubElement(self.exp_lml_root, "Parameters")
        self.exp_lml_autosys = ET.SubElement(self.exp_lml_root, "Automation_System")
        self.exp_lml_proc = ET.SubElement(self.exp_lml_root, "Process")
        
        ET.SubElement(self.exp_lml_param, "ExperimentView", width=str(self.experiment.scene_def_width), height=str(self.experiment.scene_def_height) )
        
    def addSubprocess(self, parent_subprocess, subprocess) :
        logging.debug(subprocess)
        logging.debug(subprocess.step_name)
        
        def_item_pos = QtCore.QPointF(30.0,200.0)
        lml_sp = ET.SubElement(self.exp_lml_proc, "SubProcess", name=subprocess.step_name, 
                                x_pos=str(def_item_pos.x()),y_pos=str(def_item_pos.y()) )
                                
        lml_sp.set("uuid", str(id(subprocess)) )
        
        if parent_subprocess : lml_sp.set("parent", str(id(parent_subprocess)) )
        
        
        #~ if subprocess != self.experiment.begin_item :
            #~ lml_sp.set("parent", str(id(subprocess.parent)) )
        #~ 
    def saveExpXMLFile(self):
        exp_out_file = self.experiment.xml_fileinfo.fileName().toAscii()
        try:
            ET.ElementTree(self.exp_lml_root).write(exp_out_file , encoding='UTF-8', xml_declaration=True, method="xml")
            logging.debug("lara: Experiment XML outputfile %s written" % self.experiment.name())
        except IOError:
            logging.Error("Cannot write Experiment XML outputfile %s !!!" % self.experiment.name())

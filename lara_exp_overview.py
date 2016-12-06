#!/usr/bin/env python
# -*- coding: utf-8 -*-

#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: LA_ExperimentOverview
# FILENAME: lara_experiment_overview.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# VERSION: 0.0.3
#
# CREATION_DATE: 2014/09/15
# LASTMODIFICATION_DATE: 2014/09/15
#
# BRIEF_DESCRIPTION: Provides an overview of an LARA experiment
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

from PyQt4 import Qt, QtCore, QtGui, QtXml

import generators.lara_html5_generator as lht5
#~ import generators.lara_svg_generator as lsvg

class LA_ExperimentOverview(QtGui.QTextEdit):
    """ Generates an overview tab in MainCentralTab with details of the experiment 
    """
    textAdded = QtCore.pyqtSignal()
    def __init__(self, parent=None, report=None):
        super(LA_ExperimentOverview, self).__init__(parent)
        
        self.setObjectName(report.name())
        self.setReadOnly(True) 
        
        self.report = report
        
        self.report.textAdded.connect(self.updateText)
        
        self.setHtml(self.report.textHtml() )

    def updateText(self):
        self.setHtml(self.report.textHtml() )
        
    def setExperiment(self, experiment):
        self.current_experiment = experiment
        
    def experiment(self):
        return(self.current_experiment)
        

class LA_ExperimentTimeline(QtCore.QObject):
    """ Generates a timeline of the experiment - could be extended to timeline browser
    """
    expChanged = QtCore.pyqtSignal()
    def __init__(self, parent=None, experiment=None, time_line_filename=""):
        super(LA_ExperimentTimeline, self).__init__(parent)
        
        self.exp = experiment
        self.tl_filename = time_line_filename
        
        self.event_dict = {}
        
        #self.report.expChanged.connect(self.updateTimeline)
        
    def updateTimeline(self):
        
        start_of_next_subprocess = 0.0

        process_order = ""
        
        next_subprocess = self.exp.exp_begin_item
        logging.info("new traversing - traversing could be nicer !! e.g. by defining experiment as iterator -> ver 0.3")
        while next_subprocess :
            curr_subprocess_name = next_subprocess.name()
            print(curr_subprocess_name)
            # retrieving the totalDuration
            sp_total_duration = next_subprocess.totalDuration()
            
            self.event_dict[curr_subprocess_name] = [start_of_next_subprocess, sp_total_duration]
            
            # process entry in 
            process_order += curr_subprocess_name + " ("+ str(sp_total_duration) + "s) -> "
            self.exp.exp_ov.newPragraph("process","pr_p1",process_order)
            
            start_of_next_subprocess += sp_total_duration
            
            try:
                if next_subprocess == self.exp.exp_end_item :
                    break
                else :
                    # #print(next_subprocess.flowCon().endItem())
                    # logging.debug("next ---")
                    
                    next_subprocess = next_subprocess.flowNext()
            except:
                break

        #self.event_dict = {"inoculation":[2.0,1.0],"incubation":[3.0,3.0],"growth":[4.0,2.0],"induction":[6.0,0.5]} #event_dict
        logging.info("re activate timeline creation")
        #~ lsvg.GenerateTimeLine(figure_name=self.tl_filename, width=640.0, x_max= start_of_next_subprocess, event_dict=self.event_dict)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: LA_Experiment
# FILENAME: lara_experiment.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# CREATION_DATE: 2013/05/14
# LASTMODIFICATION_DATE: 2016/04/17
#
# BRIEF_DESCRIPTION: Experiment classes for LARA - an experiment is a set of processes
# DETAILED_DESCRIPTION:
#
# TO_DOs:
#  - overviews handling
#  - removing uuids ?
#  - process_view
#  - container manager
#  - nicer zoom
#  - context menu
#  - automation system -> lam / XML
#  - insert in line
#  - selecting line
#  - line handling
#  - auto move objects
#  - cut copy flow connector handling
# ____________________________________________________________________________
"""
__version__ = "0.0.3"

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
import math
import itertools
import datetime
import xml.etree.ElementTree as ET

import lara_process as lap
import lara_material as lam
import lara_devices as lad
import lara_exp_overview as la_expov

from process_manager import lara_sila_process_manager as lasila_pm

import generators.supergen_codegenerator as sgcg

from PyQt4 import Qt, QtCore, QtGui

class LA_ExperimentView(QtGui.QGraphicsView):
    InsertItem, LineConnect, InsertText, MoveItem  = range(4)
    """Subclassed QGraphicsView because of draMoveEvent and settings
       also to handle close event
    """
    def __init__(self, parent):
        super(LA_ExperimentView, self).__init__(parent=None)
        
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        #self.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        #~ self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        #self.setFocusPolicy(QtGui.Qt.NoFocus)
        #self.setObjectName(self.experiment_name + "_gv")

        self.setAcceptDrops(True)
        
        self.def_transformation = self.transform()
        
        self.current_mouse_mode = LA_ExperimentView.MoveItem
    
        parent.pointerTypeSig.connect(self.setMode)
        
    def setExperiment(self, experiment):
        self.current_experiment = experiment
        self.setScene(experiment)
        
    def experiment(self):
        return(self.current_experiment)

    def setMode(self, mode):
        logging.debug("changing to %s mode" % mode)
        self.current_mouse_mode = mode
    
    def zoomIn(self):
        
        #setTransform(QTransform::fromScale(sx, sy));
        zoom_scale = 0.75
        #~ old_view_matrix = curr_view.matrix()
        #~ self.resetMatrix()
        #~ curr_view.translate(old_view_matrix.dx(), old_view_matrix.dy())
        self.scale(zoom_scale, zoom_scale)
        #setTransform(QTransform::fromScale(sx, sy));
        
    def zoomOut(self):
        zoom_scale = 1.25
        #~ old_view_matrix = curr_view.matrix()
        #~ self.resetMatrix()
        #~ curr_view.translate(old_view_matrix.dx(), old_view_matrix.dy())
        self.scale(zoom_scale, zoom_scale)
        
    def zoomDef(self):
        zoom_scale = 1.0
        
        #setTransform(QTransform::fromScale(sx, sy));
        
        #~ old_view_matrix = curr_view.matrix()
        #~ self.resetMatrix()
        #~ curr_view.translate(old_view_matrix.dx(), old_view_matrix.dy())
        self.setTransform(self.def_transformation)

    def dragEnterEvent(self, event):   # might be omitted ??
        if event.mimeData().hasFormat('application/lara-dnditemdata'):
            event.acceptProposedAction()
        else:
            event.ignore()
        super(LA_ExperimentView, self).dragEnterEvent(event)

    def dragMoveEvent(self, event): 	# very important for dragging
        if event.mimeData().hasFormat('application/lara-dnditemdata'):
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def mousePressEvent(self, event):
        if self.current_mouse_mode == LA_ExperimentView.MoveItem:
            modifiers = QtGui.QApplication.keyboardModifiers()  
            if modifiers == QtCore.Qt.ShiftModifier:       # vary drag action depending on holding shift key 
                self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
            else :
                self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)   # mode, when clicked into scene
            event.ignore()
        super(LA_ExperimentView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setDragMode(QtGui.QGraphicsView.NoDrag)
        event.ignore()
        super(LA_ExperimentView, self).mouseReleaseEvent(event)
   
    def mouseMoveEvent(self,event):
        super(LA_ExperimentView, self).mouseMoveEvent(event) #QtGui.QGraphicsView.mouseMoveEvent(self, event)
        
class LA_Experiment(QtGui.QGraphicsScene):
    InsertItem, LineConnect, InsertText, MoveItem  = range(4)

    #itemInserted = QtCore.pyqtSignal(lap.LA_SubProcess)
    #textInserted = QtCore.pyqtSignal(QtGui.QGraphicsTextItem)
    itemSelected = QtCore.pyqtSignal(QtGui.QGraphicsItem)
    valueChanged = QtCore.pyqtSignal()

    def __init__(self, xml_fileinfo=None, parentWidget=None):
        self.experiment_gv = LA_ExperimentView(parentWidget)
        super(LA_Experiment, self).__init__(self.experiment_gv)
        
        self.scene_def_width = 3062
        self.scene_def_height = 1600
                
        self.xml_fileinfo = xml_fileinfo 
        self.experiment_name = self.xml_fileinfo.baseName()
        
        self.lara_mainwindow = parentWidget #experiment_gv.parent()
        self.tool_item_lst = self.lara_mainwindow.tool_item_lst
    
        self.lara_mainwindow.central_tw.addTab(self.experiment_gv, self.experiment_name)
        
        #~ logging.info("exp overview could be subclassed in textedit in future versions")
        #~ self.exp_ov = lht5.LA_Html5Generator(self.experiment_name + "_overview")
        #~ self.overview_te = LA_ExperimentOverview(self.lara_mainwindow, self.exp_ov)
        #~ self.lara_mainwindow.central_tw.addTab(self.overview_te, self.experiment_name + "_overview")
        #~ self.exp_ov.insertImage("timeline","timeline1","/tmp/timeline.svg", "Timeline of experiment")
    
        self.process_list = {} # main subprocess data structure: linked list of subprocesses 
        self.container_stream = {} # automatic container handling 
        self.copy_cut_stack = []

        self.connecting_line = None  # line that is used by the line draw tool to connect objects (not final connector!) 
        self.curr_line_colour = QtCore.Qt.red
                
        self.diag_item_previous = None
        self.exp_begin_item = None
        self.exp_end_item = None
        self.current_mouse_mode = LA_Experiment.MoveItem
        
        # devices
        self.automation_sys = lad.LabAutomationSystem()
        
        self.newcontainer_db = None
        self.container_location_db = None
        
        #~ # containers        
        #~ self.newcontainer_db = lam.newContainerDB(experiment=self)
        #~ self.container_location_db = lam.ContainerLocationDB(self.automation_sys)
        #~ 
        #~ self.exp_timeline = LA_ExperimentTimeline(experiment=self, time_line_filename="timeline")
        
        self.lara_mainwindow.pointerTypeSig.connect(self.setMode)
        self.lara_mainwindow.editCopySig.connect(self.copyItems)
        self.lara_mainwindow.editCutSig.connect(self.cutItems)
        self.lara_mainwindow.editPasteSig.connect(self.pasteItems)
        
        self.valueChanged.connect(self.updateInfoViews)

        self.setObjectName(self.experiment_name + "_gs") 
        self.experiment_gv.setObjectName(self.experiment_name + "_gv")
        self.experiment_gv.setExperiment(self)
        
    def name(self):
        return(self.experiment_name)
        
    #~ def containerDBModel(self):
        #~ """ Function doc """
        #~ return(self.newcontainer_db)
        
    def xmlFileInfo(self):
        return(self.xml_fileinfo)
        
    def initExpLML(self):
        # preparing experiment XML structure
        self.exp_lml_root = ET.Element("LARA", version="0.1", filetype="Experiment", md5sum="000000000000000000000000000000")
        self.exp_lml_param = ET.SubElement(self.exp_lml_root, "Parameters")
        self.exp_lml_autosys = ET.SubElement(self.exp_lml_root, "Automation_System")
        self.exp_lml_proc = ET.SubElement(self.exp_lml_root, "Process")

    def initNewExp(self):
        # this needs to be here in order to have the visible plane at the correct position
        self.setSceneRect(QtCore.QRectF(0, 0, self.scene_def_width, self.scene_def_height))
        
        # LML file
        self.initExpLML()
        
        # Automation system - without filename -> default, remove from constructor !
        # automation system description needs to be moved into LML file
        self.automation_sys.setDefaultDevices()
        
        #  creating a Begin process item
        tool_item_class = self.tool_item_lst["BeginProcess"].diagramClass() # retriving class of BeginProcess
        
        def_item_pos = QtCore.QPointF(30.0,200.0)
        
        self.exp_begin_item = tool_item_class(experiment=self, position=def_item_pos )
        self.exp_begin_item.setContextMenu(self.lara_mainwindow.itemMenu)
        
        # adding item to process dict. and generate LML entry 
        self.process_list[self.diag_item_previous] = self.exp_begin_item
        self.diag_item_previous = self.exp_begin_item
        lml_sp = ET.SubElement(self.exp_lml_proc, "SubProcess", name=self.diag_item_previous.name(), 
                                x_pos=str(def_item_pos.x()),y_pos=str(def_item_pos.y()) )

        self.exp_begin_item.setLMLNode(lml_sp) # linking LML node to subprocess
        self.exp_begin_item.initNewSubProcess() # might be redundand ! use python object id: id(object)
        lml_sp.set("uuid",str(self.exp_begin_item.uuid()) )
        
        self.addItem(self.exp_begin_item) # adding begin item to scene

        # End process item
        tool_item_class = self.tool_item_lst["EndProcess"].diagramClass()
       
        end_item_pos = def_item_pos + QtCore.QPointF(1224.0,0.0) # QtCore.QPointF(2224.0,0.0)
        
        self.exp_end_item = tool_item_class(experiment=self, position=end_item_pos )
        lml_sp_end = ET.SubElement(self.exp_lml_proc, "SubProcess", name=self.exp_end_item.name(),
                                x_pos=str(end_item_pos.x()),y_pos=str(end_item_pos.y()) )
        self.exp_end_item.setLMLNode(lml_sp_end)
        self.exp_end_item.initNewSubProcess()
        lml_sp_end.set("uuid",str(self.exp_end_item.uuid()) )

        self.addItem(self.exp_end_item)
        
        # disabled for TALE development
        #~ flow_con = ProcFlowConnector(start_item=self.exp_begin_item, end_item=self.exp_end_item, scene=self)
        #~ flow_con.setColour(self.curr_line_colour)
                #~ 
        #~ self.exp_begin_item.addFlowCon(flow_con)
        #~ self.exp_end_item.addFlowCon(flow_con)
        #~ self.exp_begin_item.setNextStep(self.exp_end_item)
            #~ 
        #~ flow_con.setZValue(+1000.0)
        #~ self.addItem(flow_con)     # adding arrow to graphics scene 
        #~ flow_con.updatePosition()
                
        # Container manager
        #~ tool_item_class = self.tool_item_lst["ContainerManager"].diagramClass()
        #~ cm_item_pos = def_item_pos + QtCore.QPointF(0.0,-150.0)
        #~ subprocess_item = tool_item_class(experiment=self, position=cm_item_pos )
        #~ lml_sp_cm = ET.SubElement(self.exp_lml_proc, "SubProcess", name=subprocess_item.name(), 
                        #~ x_pos=str(cm_item_pos.x()),y_pos=str(cm_item_pos.y()) )
        #~ subprocess_item.setLMLNode(lml_sp_cm)
        #~ subprocess_item.initNewSubProcess()
        #~ lml_sp_cm.set("uuid",str(subprocess_item.uuid()) )
        #~ self.addItem(subprocess_item)      
                
        ET.SubElement(self.exp_lml_param, "ExperimentView", width=str(self.scene_def_width), height=str(self.scene_def_height) )
        
    def delSubProcess(self, sub_process_to_del):
        """ deleting a sub process from process list
        """
        if isinstance(sub_process_to_del, lap.LA_ProcessElement):
                sub_process_to_del.removeFlowConnectors()
            
        proc_lst_keys = self.process_list.itervalues()
        previous_subprocess = None
        next_subprocess = proc_lst_keys.next()
        
        logging.warning(" !! container handling on deletion !!! needs to be implemented")
        while next_subprocess :
            if  next_subprocess == sub_process_to_del:
                if sub_process_to_del in self.process_list:     # req. for the last item in dict 
                    temp_next_sp = self.process_list[sub_process_to_del]
                    self.exp_lml_proc.remove(sub_process_to_del.LMLNode())
                    del self.process_list[sub_process_to_del]
                    del self.process_list[previous_subprocess]
                    self.process_list[previous_subprocess] = temp_next_sp
                else :
                    del self.process_list[previous_subprocess]  # last item
                    self.exp_lml_proc.clear()
                break
            if next_subprocess in self.process_list :
                previous_subprocess = next_subprocess
                next_subprocess = self.process_list[next_subprocess]
            else:
                break
        
    def copyItems(self):
        """ next versions: only copy information about the item, not the item itself
        """
        for item in self.selectedItems():
            if isinstance(item, lap.LA_ProcessElement):
                #~ self.exp_lml_proc.remove(item.LMLNode())
                #~ item.removeFlowConnectors()
                #self.copy_cut_stack.append(item)
                logging.debug("adding item to copy stack cl %s na %s" % (item.__class__, item.__class__.__name__) )
                new_item = item.__class__(experiment=self, position=QtCore.QPointF(300.0,200.0), visible=True)
                del self.copy_cut_stack[:] # empty list before filling with new elements
                self.copy_cut_stack.append(new_item)
                
    def cutItems(self):
        """ next versions: only cut information about the item, not the item itself
        """
        for item in self.selectedItems():
            if isinstance(item, lap.LA_ProcessElement):
                #~ self.exp_lml_proc.remove(item.LMLNode())
                #~ item.removeFlowConnectors()
                del self.copy_cut_stack[:] # empty list before filling with new elements
                self.copy_cut_stack.append(item)
                logging.debug("adding item to cut stack")
                item.hide()
            
    def pasteItems(self):
        """ paste new instances of the items with same characteristics (for multiple paste)
        """
        logging.debug("stack len %i" % len(self.copy_cut_stack) )
        try :
            for paste_item in self.copy_cut_stack :
                logging.debug("paste fr stack: %s" %  paste_item.name() )
                paste_item.show()
            
        except IndexError:
            logging.debug("stack empty")
        
    def openExpLMLfile(self, lml_filename=""):
        self.exp_lml_tree = ET.parse( lml_filename )
        
        #reading all experiment parameters
        proc_view_param = self.exp_lml_tree.findall( 'Parameters/ExperimentView' )
        self.scene_def_width = int(proc_view_param[0].get("width"))
        self.scene_def_height = int(proc_view_param[0].get("height"))
        
        self.setSceneRect(QtCore.QRectF(0, 0, self.scene_def_width, self.scene_def_height))
        
        #~ logging.debug("reading lml file proc parameters w: %i h:%i" % (self.scene_def_width, self.scene_def_height) )
        
        # reading automation system
        self.automation_sys.loadDevices(self.exp_lml_tree)
        
        # reading all processes
        sp_uuid_dict = {}
        uuid_parent_dict = {}
        
        for subprocess in self.exp_lml_tree.findall( 'Process/SubProcess' ):
            logging.debug("reading lml file sp %s" % subprocess)
            
            name_sp = subprocess.get("name")
            x_pos = float(subprocess.get("x_pos") )
            y_pos = float(subprocess.get("y_pos") )
            
            curr_uuid = subprocess.get("uuid")
            parent_uuid = subprocess.get("parent")
            
            tb_item = self.tool_item_lst[name_sp]
            
            if tb_item :
                subprocess_class = tb_item.diagramClass()
                subprocess_item = subprocess_class(experiment=self, position=QtCore.QPointF(x_pos,y_pos))
                subprocess_item.setLMLNode(subprocess)
                #subprocess_item.initNewSubProcess()
                subprocess_item.initParameters()
                self.addItem(subprocess_item)
                self.process_list[self.diag_item_previous] = subprocess_item
                
                sp_uuid_dict[curr_uuid] = subprocess_item
                
                if subprocess_item.name() == "BeginProcess": 
                    self.exp_begin_item = subprocess_item
                if subprocess_item.name() == "EndProcess": 
                    self.exp_end_item = subprocess_item
                
                if parent_uuid :
                    uuid_parent_dict[curr_uuid] = parent_uuid
                
                if False: # switching off arrow connection self.diag_item_previous :
                    flow_con = ProcFlowConnector(start_item=self.diag_item_previous, end_item=subprocess_item)
                    flow_con.setColour(self.curr_line_colour)
                    self.diag_item_previous.addFlowCon(flow_con)
                    subprocess_item.addFlowCon(flow_con)
                    
                    flow_con.setZValue(+1000.0)
                    self.addItem(flow_con)     # adding arrow to graphics scene 
                    flow_con.updatePosition()
                
                self.diag_item_previous = subprocess_item
            else :
                logging.error("key not in list")
            
        self.exp_lml_root = self.exp_lml_tree.getroot()
        self.exp_lml_proc = self.exp_lml_tree.find( 'Process' )

        # now creating all connections
        
        for to_connect in uuid_parent_dict.keys():
            try: 
                start_item = sp_uuid_dict[uuid_parent_dict[to_connect]]
                end_item = sp_uuid_dict[to_connect]
                flow_con = ProcFlowConnector(start_item=start_item, end_item=end_item, parent=self)
                flow_con.setColour(self.curr_line_colour)
                
                start_item.addFlowCon(flow_con)
                end_item.addFlowCon(flow_con)
                start_item.setNextStep(end_item)
            
                flow_con.setZValue(+1000.0)
                self.addItem(flow_con)     # adding arrow to graphics scene 
                flow_con.updatePosition()
                
            except KeyError:
                logging.error("LNL key error: %s " % to_connect)
                
        self.valueChanged.emit()
        
    def saveExpXMLFile(self):
        exp_out_file = self.xmlFileInfo().fileName().toAscii()
        try:
            sgcg.SuperGen(self, mode=lap.ProcessStep.lml)
            
            logging.debug("lara: Experiment XML outputfile %s written" % self.name())
        except IOError:
            logging.Error("Cannot write Experiment XML outputfile %s !!!" % self.name())
            
    def beginOfExperiment(self):
        return(self.exp_begin_item)
        
    #~ def containerStream(self):
        #~ return(self.container_stream)
        
    #~ def requestContainerFromStream(self, container_function="", container_type="Greiner96NwFb", lidding_state="U", min_num = 1):
        #~ cont_function = container_function + container_type + lidding_state
        #~ 
        #~ try :
            #~ curr_min_num = self.container_stream[cont_function]
        #~ 
            #~ # there are containers in the stream
            #~ if min_num > curr_min_num:
                  #~ self.newcontainer_db.add( container_function=cont_function, container_type=container_type, lidding_state=lidding_state, num = min_num - curr_min_num)
                  #~ self.container_stream[cont_function] = min_num
                  #~ 
        #~ except KeyError :
            #~ self.newcontainer_db.add( container_function=cont_function, container_type=container_type, lidding_state=lidding_state, num = min_num)
            #~ self.container_stream[cont_function] = min_num
            
    #~ def defDefaultStartLocation(self, container_function="MasterPlate", container_type="Greiner96NwFb", lidding_state="L", dev_pos=()):
        #~ # ("Thermo_carousel",1,1,"int")
        #~ cont_function = container_function + container_type + lidding_state
        #~ logging.info("this info could later be used to generate a watcher or experiment")
        #~ try :
            #~ num = self.container_stream[cont_function]
            #~ for i in range(num) :
                #~ cont_name = cont_function + str(i+1)
                #~ # adds only a new location, if the location is not alredy defined
                #~ if cont_name not in self.container_location_db : 
                    #~ self.container_location_db.update({cont_name: (self.automation_sys[dev_pos[0]],(dev_pos[1],dev_pos[2]+i),dev_pos[3]) })
                  #~ 
        #~ except KeyError :
            #~ logging.error("default cont location ERROR")
                    
    def compileExperiment(self):
        if len(self.process_list) > 0:
            logging.debug("now compiling all files %s" % self.experiment_name)
                        
            # generate all 
            sgcg.SuperGen(self)
            
            logging.debug("compiling of %s done" % self.experiment_name)
        else:
            logging.debug("no processes found")
        
    def runExperiment(self):
        logging.debug("now compiling momentum files %s" % self.experiment_name)
        if len(self.process_list) > 0:
            logging.debug("now compiling momentum files %s" % self.experiment_name)
            
            lasila_pm.LA_SiLAProcessManager(self, self.automation_sys, self.newcontainer_db, self.container_location_db)        
            logging.debug("run done ")
        else:
            logging.debug("no processes found")


    def updateInfoViews(self):
        #~ self.exp_timeline.updateTimeline()
        logging.info("switch on .... update info views")
        pass
            
    def setMode(self, mode):
        logging.debug("changing to %s mode" % mode)
        self.current_mouse_mode = mode
        
    def setLineConnectMode(self):
        logging.debug("changing to line mode")
        self.current_mouse_mode = self.LineConnect
    
    def setItemMoveMode(self):
        logging.debug("changing to item move mode")
        self.current_mouse_mode = self.MoveItem
        
    def setLineColour(self, colour):
        self.curr_line_colour = colour
        if self.isItemChange(ProcFlowConnector):
            item = self.selectedItems()[0]
            item.setColour(self.curr_line_colour)
            self.update()
            
    def itemSelected(self, item):
        """ handler for selections """
        logging.debug("item selected")
        item.item_label.setStyleSheet(' background-color: lightgreen')
        #~ font = item.font()
        #~ color = item.defaultTextColor()
        #~ self.fontCombo.setCurrentFont(font)
        #~ self.fontSizeCombo.setEditText(str(font.pointSize()))
        #~ self.boldAction.setChecked(font.weight() == QtGui.QFont.Bold)
        #~ self.italicAction.setChecked(font.italic())
        #~ self.underlineAction.setChecked(font.underline())
        #~ 
        
    def mousePressEvent(self, mouseEvent):
        # left button required for context menue
        # if (mouseEvent.button() != QtCore.Qt.LeftButton):
        #   return
        if self.current_mouse_mode == self.InsertItem:
            logging.debug("lines selceted 2")
        elif self.current_mouse_mode == self.LineConnect:
            #logging.debug("line drawing")
            self.connecting_line = QtGui.QGraphicsLineItem(QtCore.QLineF(mouseEvent.scenePos(),
                                        mouseEvent.scenePos()))
            self.connecting_line.setPen(QtGui.QPen(self.curr_line_colour, 5.0))
            self.addItem(self.connecting_line)

        super(LA_Experiment, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if self.current_mouse_mode == self.LineConnect and self.connecting_line:
            #logging.debug("line drawing move")
            newLine = QtCore.QLineF(self.connecting_line.line().p1(), mouseEvent.scenePos())
            self.connecting_line.setLine(newLine)
        elif self.current_mouse_mode == self.MoveItem:
            super(LA_Experiment, self).mouseMoveEvent(mouseEvent)
            #logging.debug("moving item")

    def mouseReleaseEvent(self, mouseEvent):
        if self.connecting_line and self.current_mouse_mode == self.LineConnect:
            startItems = self.items(self.connecting_line.line().p1(), QtCore.Qt.IntersectsItemShape, QtCore.Qt.DescendingOrder )  # selects all items of graphicscene at this point 
            if len(startItems) and startItems[0] == self.connecting_line:
                startItems.pop(0)
                
            endItems = self.items(self.connecting_line.line().p2(), QtCore.Qt.IntersectsItemShape, QtCore.Qt.AscendingOrder)
            if len(endItems) and endItems[0] == self.connecting_line:
                endItems.pop(0)

            self.removeItem(self.connecting_line)
            self.connecting_line = None

            if len(startItems) and len(endItems) and \
                    isinstance(startItems[0], lap.LA_ProcessElement) and \
                    isinstance(endItems[0], lap.LA_ProcessElement) and \
                    startItems[0] != endItems[0]:

                startItem = startItems[0]
                endItem = endItems[0]

                flow_con = ProcFlowConnector(start_item=startItem, end_item=endItem)
                flow_con.setColour(self.curr_line_colour)
                
                startItem.addFlowCon(flow_con)
                endItem.addFlowCon(flow_con)
                endItem.setParentUUID(flow_con)
                startItem.setNextStep(endItem)
                
                flow_con.setZValue(+1000.0)
                self.addItem(flow_con)     # adding arrow to graphics scene 
                flow_con.updatePosition()
                
        elif self.current_mouse_mode == self.MoveItem:
            #~ logging.debug("redrawing all lines")
            
            for curr_item in self.selectedItems():
                if isinstance(curr_item, QtGui.QGraphicsPathItem):
                   logging.debug("lines selceted 1") 
            
            self.update() # important to remove drawing artefacts
        
        self.connecting_line = None
        
        # very important for signal flow - preventing counting bug of spinbox widget
        super(LA_Experiment, self).mouseReleaseEvent(mouseEvent)
        
    def dragEnterEvent(self, event):
        #logging.debug("drag enter Diagram scene")
        if event.mimeData().hasFormat('application/lara-dnditemdata'):
            if event.source() == self:
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()
        super(LA_Experiment, self).dragEnterEvent(event)
        
    def dragMoveEvent(self, event):
        #logging.debug("drag enter Diagram scene")
        if event.mimeData().hasFormat('application/lara-dnditemdata'):
            if event.source() == self:
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()
        super(LA_Experiment, self).dragMoveEvent(event)
        
    def dropEvent(self, event):
        logging.debug("diagram scene: item dropped")
        if event.mimeData().hasFormat('application/lara-dnditemdata'):
            itemData = event.mimeData().data('application/lara-dnditemdata')
            dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.ReadOnly)

            diagram_class = dataStream.readQVariant().toPyObject()
            logging.warning("Converting PyObjects could be different in different operation systems")

            curr_mouse_pos = event.scenePos()

            logging.debug("event pos = %s-%s"% (curr_mouse_pos.x(), curr_mouse_pos.y()) ) 
            
            if len(self.process_list) == 0:
               # self.initNewExp()
               pass
                
            subprocess_item = diagram_class(experiment=self, position=curr_mouse_pos)
                                    
            self.addItem(subprocess_item)
            
            lml_sp = ET.SubElement(self.exp_lml_proc, "SubProcess", name=subprocess_item.name(),
                                    x_pos=str(curr_mouse_pos.x()),y_pos=str(curr_mouse_pos.y())  )
            subprocess_item.setLMLNode(lml_sp)
            subprocess_item.initNewSubProcess()
            lml_sp.set("uuid",str(subprocess_item.uuid()) )

            self.process_list[self.diag_item_previous] = subprocess_item
            
            if self.diag_item_previous :
                flow_con = ProcFlowConnector(start_item=self.diag_item_previous, end_item=subprocess_item)
                flow_con.setColour(self.curr_line_colour)
                
                self.diag_item_previous.addFlowCon(flow_con)
                subprocess_item.addFlowCon(flow_con)
                subprocess_item.setParentUUID(flow_con)
                self.diag_item_previous.setNextStep(subprocess_item)
                
                flow_con.setZValue(+1000.0)
                self.addItem(flow_con)     # adding arrow to graphics scene 
                flow_con.updatePosition()
            
            self.diag_item_previous = subprocess_item
            
            #newIcon.setAttribute(QtCore.Qt.WA_DeleteOnClose)

            if event.source() == self:
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                #event.accept()
                event.acceptProposedAction()
        else:
            logging.debug("mime data not correct")
            event.ignore()
        super(LA_Experiment, self).dropEvent(event)
        logging.debug("ds: item finally dropped")
    
    # make the experiment iterable     
    def __iter__(self):
        self.steps_list = []

        next_subprocess = self.exp_begin_item
        logging.info("iterating through steps ....")
        while next_subprocess :
            logging.debug(next_subprocess)
            self.steps_list += next_subprocess.steps()
            try:
                if next_subprocess == self.exp_end_item :
                    break
                else :
                    #~ #print(next_subprocess.flowCon().endItem())
                    #~ logging.debug("next ---")
                    
                    next_subprocess = next_subprocess.flowNext()
            except:
                break
        
        #~ logging.debug("--------------> steps list %s", self.steps_list )
        for step in self.steps_list:
          yield step
        
        
class LA_Connector(object):
    """ Class doc """
    def __init__(self, start_item, end_item):
        """ Class initialiser """
        
        self.curr_start_item = start_item
        self.curr_end_item = end_item

    def startItem(self):
        return(self.curr_start_item)

    def endItem(self):
        return(self.curr_end_item)
        
class SimpleArrow(LA_Connector, QtGui.QGraphicsLineItem):
    """ cos can be removed and replaced by just points ?"""
    def __init__(self, start_item=None, end_item=None, parent=None, scene=None):
        logging.info("init can be nicer")
        QtGui.QGraphicsLineItem.__init__(self,parent=parent, scene=scene)
        super(SimpleArrow, self).__init__(start_item, end_item)

        self.arrowHead_polygon = QtGui.QPolygonF()

        self.setAcceptDrops(True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.arrowColour = QtCore.Qt.black
        self.line_thickness = 6.0
        self.setPen(QtGui.QPen(self.arrowColour, self.line_thickness, QtCore.Qt.SolidLine,
                    QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

    def setColour(self, colour):
        self.arrowColour = colour

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QtCore.QRectF(p1, QtCore.QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = super(SimpleArrow, self).shape()
        path.addPolygon(self.arrowHead_polygon)
        return path

    def updatePosition(self):
        # mapping from item to scene coordinate system
        line = QtCore.QLineF(self.mapFromItem(self.curr_start_item, 0, 0), 
                             self.mapFromItem(self.curr_end_item, 0, 0))
        self.setLine(line)

    def paint(self, painter, option, widget=None):
        if (self.curr_start_item.collidesWithItem(self.curr_end_item)):
            return

        curr_pen = self.pen()
        curr_pen.setColor(self.arrowColour)
        arrowSize = 12.0
        painter.setPen(curr_pen)
        painter.setBrush(self.arrowColour)
        
        bnd_rect_sti = self.curr_start_item.boundingRect()
        bnd_rect_endi = self.curr_end_item.boundingRect()

        centerLine = QtCore.QLineF(self.curr_start_item.pos() + QtCore.QPointF(bnd_rect_sti.width(),bnd_rect_sti.height()/2), 
                        self.curr_end_item.pos() + QtCore.QPointF(-15, bnd_rect_endi.height()/2 ) ) 
        self.setLine(centerLine)
        
        # head can be drawn much simpler: select just two points behind the tip and connect them
        
        line = self.line()
        
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (math.pi * 2.0) - angle
        
        # upper arrow point
        arrowP1 = line.p2() - QtCore.QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi / 3.0) * arrowSize)
        # lower arrow point
        arrowP2 = line.p2() - QtCore.QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)
        self.arrowHead_polygon.clear()
        
        for pg_point in [line.p2(), arrowP1, arrowP2]:
            self.arrowHead_polygon.append(pg_point) 
        
        painter.drawLine(line)
        painter.drawPolygon(self.arrowHead_polygon)
        
        if self.isSelected():
            painter.setPen(QtGui.QPen(QtCore.Qt.blue, 4, QtCore.Qt.DashLine))
            dash_line = QtCore.QLineF(line)
            dash_line.translate(0, 8.0)
            painter.drawLine(dash_line)
            dash_line.translate(0,-16.0)
            painter.drawLine(dash_line)
            
    def dragEnterEvent(self,event):
        logging.debug("line hit by item")

class SplineArrow(LA_Connector, QtGui.QGraphicsPathItem):
    def __init__(self, start_item=None, end_item=None, parent=None, scene=None):
        
        LA_Connector.__init__(self, start_item, end_item)
        QtGui.QGraphicsPathItem.__init__(self, parent=parent, scene=scene)
    
        #~ self.arrowHead_polygon = QtGui.QPolygonF()
        #~ self.setAcceptHoverEvents(True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        
        #~ self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        
        self.arrowColour = QtCore.Qt.green
        self.line_thickness = 4.0
        self.setPen(QtGui.QPen(self.arrowColour, self.line_thickness, QtCore.Qt.SolidLine,
                    QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                    
        self.connector_line_path = QtGui.QPainterPath()

        #~ super(SplineArrow, self)
        
        self.start_end = [self.mapFromItem(self.curr_start_item, 0, 0), 
                          self.mapFromItem(self.curr_end_item, 0, 0)]
                          
    def setColour(self, colour):
        self.arrowColour = colour

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.start_end[0]
        p2 = self.start_end[1]
        return QtCore.QRectF(p1, QtCore.QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = super(SplineArrow, self).shape()
        #path.addPolygon(self.arrowHead_polygon)
        return(path)

    def updatePosition(self):
        # mapping from item to scene coordinate system
        
        self.start_end = [self.mapFromItem(self.curr_start_item, 0, 0), 
                            self.mapFromItem(self.curr_end_item, 0, 0)]

        #~ line = QtCore.QLineF(self.mapFromItem(self.curr_start_item, 0, 0), 
                             #~ self.mapFromItem(self.curr_end_item, 0, 0))
        #~ self.setLine(line)
        self.connector_line_path = QtGui.QPainterPath(self.start_end[0])

    def hoverEnterEvent(self, event):
        logging.debug("hover over line")
        #painter.setPen(QPen(myColor, 1, Qt.DashLine))
        
    def mousePressEvent(self, mouseEvent):
        logging.debug("line pressed")
        
    def paint(self, painter, option, widget=None):
        if (self.curr_start_item.collidesWithItem(self.curr_end_item)):
            return

        curr_pen = self.pen()
        curr_pen.setColor(self.arrowColour)
        arrowSize = 12.0
        painter.setPen(curr_pen)
        painter.setBrush(self.arrowColour)

        
        bnd_rect_sti = self.curr_start_item.boundingRect()
        bnd_rect_endi = self.curr_end_item.boundingRect()
        
                
        self.start_end = [self.curr_start_item.pos() + QtCore.QPointF(bnd_rect_sti.width(),bnd_rect_sti.height()/2), 
                            self.curr_end_item.pos() + QtCore.QPointF(-15, bnd_rect_endi.height()/2 ),
                            self.curr_start_item.pos() + QtCore.QPointF(bnd_rect_sti.width(),bnd_rect_sti.height()), 
                            self.curr_end_item.pos() + QtCore.QPointF(0, bnd_rect_endi.height())]
                            
        p1 = self.curr_start_item.pos() + QtCore.QPointF(bnd_rect_sti.width(),bnd_rect_sti.height()/2)
        p2 = self.curr_end_item.pos() + QtCore.QPointF(-15, bnd_rect_endi.height()/2 )
        
        self.connector_line_path = QtGui.QPainterPath(p1)
        
        
        #self.connector_line_path.moveTo(self.start_end[0])
        # path.cubicTo(pos.x()-60, pos.y(), newPos.x()+60, newPos.y(), newPos.x(),newPos.y())
        
        self.connector_line_path.cubicTo(p1.x() + 60, p1.y(), p2.x() - 60, p2.y(), p2.x(), p2.y())
        
        #self.connector_line_path.cubicTo(self.start_end[0], self.start_end[3], self.start_end[1])

        
        
        #path.cubicTo(p1.x() + 60, p1.y(), p2.x() - 60, p2.y(), p2.x(), p2.y())
        
        #~ self.connector_line_path.moveTo(self.curr_start_item.pos() + QtCore.QPointF(bnd_rect_sti.width(),bnd_rect_sti.height()/2))
        #~ self.connector_line_path.lineTo(self.curr_end_item.pos() + QtCore.QPointF(-15, bnd_rect_endi.height()/2 ))

        #~ centerLine = QtCore.QLineF(self.curr_start_item.pos() + QtCore.QPointF(bnd_rect_sti.width(),bnd_rect_sti.height()/2), 
                        #~ self.curr_end_item.pos() + QtCore.QPointF(-15, bnd_rect_endi.height()/2 ) ) 
        #~ self.setLine(centerLine)
        
        # head can be drawn much simpler: select just two points behind the tip and connect them
        
        #~ line = self.line()
        
        #~ angle = math.acos(line.dx() / line.length())
        #~ if line.dy() >= 0:
            #~ angle = (math.pi * 2.0) - angle
        #~ 
        #~ # upper arrow point
        #~ arrowP1 = line.p2() - QtCore.QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                        #~ math.cos(angle + math.pi / 3.0) * arrowSize)
        #~ # lower arrow point
        #~ arrowP2 = line.p2() - QtCore.QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                        #~ math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)
        #~ self.arrowHead_polygon.clear()
        #~ 
        #~ for pg_point in [line.p2(), arrowP1, arrowP2]:
            #~ self.arrowHead_polygon.append(pg_point) 
        
        #~ painter.drawLine(line)
        #~ painter.drawPolygon(self.arrowHead_polygon)
        
        painter.strokePath(self.connector_line_path, curr_pen)
        
        #~ self.setSelected(True)

        if self.isSelected():
            print "sel"
        #self.update(0.0,0.0, 900.0,900.0)
        
        if self.isSelected():
            #~ logging.debug("repainting selected arrow")
            #~ painter.setPen(QtGui.QPen(QtCore.Qt.blue, 20, QtCore.Qt.DashLine))
            curr_pen = QtGui.QPen(QtCore.Qt.blue, 10,  QtCore.Qt.DashLine,
                    QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
            dash_line = QtGui.QPainterPath(self.connector_line_path)
            dash_line.translate(0, 40.0)
            painter.strokePath(dash_line, curr_pen) #painter.drawPath(dash_line)
            dash_line.translate(0,-80.0)
            painter.strokePath(dash_line, curr_pen)
        
        self.update()

class ProcFlowConnector(SimpleArrow):
    """ Process Flow Connector Class """
    def __init__ (self, start_item=None, end_item=None, parent=None, scene=None):
        super(ProcFlowConnector,self).__init__(start_item=start_item, end_item=end_item, parent=parent, scene=scene)
        
        # adjusting the number of containers in the stream
        #~ for container in end_item.container_stream:
            #~ if container in start_item.container_stream:
                #~ # if the number in source is too low, encrease to the number in target:
                #~ logging.debug("container %s : start: %i - end %i" %(container, start_item.container_stream[container], end_item.container_stream[container] ))
                #~ if start_item.container_stream[container] < end_item.container_stream[container] :
                    #~ start_item.container_stream[container] = end_item.container_stream[container]
        #~ 
class ContFlowConnector(LA_Connector):
    """ Container Flow connector class """
    
    def __init__ (self, start_item=None, end_item=None):
        """ Class initialiser """
        pass

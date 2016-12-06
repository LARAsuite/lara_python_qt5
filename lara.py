#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: LARA_main
# FILENAME: lara.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# CREATION_DATE: 2013/04/24
# LASTMODIFICATION_DATE: 2016/04/17
#
# BRIEF_DESCRIPTION: Main GUI classes for LARA process editor
# DETAILED_DESCRIPTION:
# TO_DO : - XML generation move into generator
#         - recent file and recent tabs
#         - cut 
#         - paste
#         - correct drawing
#         - selection
#         - resize with slider 
#
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

import sys
import os
import logging
import pkgutil
import argparse

import xml.etree.ElementTree as ET

from PyQt4 import Qt, QtCore, QtGui

sys.path.append("generators")
sys.path.append("process_manager")

import lara_rc
import lara_experiment as la_exp
import lara_exp_overview as la_expov

    
class LA_ToolBoxWidget(QtGui.QListWidget):
    """This QListWidget organizes the tool items in the MainToolBox tabwidget
       to be dragged upon the process editor/experiment tab
    """
    def __init__(self, parent=None):
        super(LA_ToolBoxWidget, self).__init__(parent)

        self.setMaximumWidth(parent.maximumWidth()-22)        
        self.setIconSize(QtCore.QSize(96, 64))
        
        self.setViewMode(QtGui.QListView.IconMode)
        self.setFlow(QtGui.QListView.LeftToRight)
        self.setWrapping(True)
        self.setDragEnabled(True)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)

    def mousePressEvent(self, mouseEvent):
        if (mouseEvent.button() == QtCore.Qt.LeftButton):
            # it is important that this happens only once at the beginning of the drag action
            child = self.itemAt(mouseEvent.pos())
            if not child:
                logging.warning("toolbox-widget: no item clicked")
                return
            pixmap = QtGui.QPixmap(child.pixmap())
            
            itemData = QtCore.QByteArray()
            dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
            dataStream.writeQVariant(child.diagramClass())  # relate class with toolbox item
            mimeData = QtCore.QMimeData()
            mimeData.setData('application/lara-dnditemdata', itemData)
            
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
            
            drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction | QtCore.Qt.TargetMoveAction, QtCore.Qt.MoveAction)
       
        super(LA_ToolBoxWidget, self).mousePressEvent(mouseEvent)

class LA_CentralTabWidget(QtGui.QTabWidget):
    """ Container for all process and process info widgets
    """
    def __init__(self, parent):
        super(LA_CentralTabWidget, self).__init__(parent=None)
        
        self.parent = parent
        self.setTabsClosable(True)
        self.setAcceptDrops(True)

    # this is required for the CentralTabWidget to accept drags and drops
    def dragEnterEvent(self, event): 
        if event.mimeData().hasFormat('application/lara-dnditemdata'):
            
            if event.source() == self:  # dragging inside the CentralTabWidget
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()
        super(LA_CentralTabWidget, self).dragEnterEvent(event)

    def dropEvent(self, event): 
        if event.mimeData().hasFormat('application/lara-dnditemdata'):
                        
            # triggering new_action to generate a new tab if no tabs present...
            if self.count() == 0:
                self.parent.new_act.trigger()
                event.acceptProposedAction() # changed from event.accept()
            else:
                logging.info("central tab widget: new experiment existis ")
        else : 
            event.ignore()

class LA_MainWindow(QtGui.QMainWindow):
    """Generating the main application window
    """
    MaxRecentFiles = 5
    pointerTypeSig = QtCore.pyqtSignal(int) # this signal is used to set the pointer type (move item, arrow draw) 
    editCopySig = QtCore.pyqtSignal()
    editCutSig = QtCore.pyqtSignal()
    editPasteSig = QtCore.pyqtSignal()
    unselctAllSig = QtCore.pyqtSignal()
        
    def __init__(self):
        super(LA_MainWindow, self).__init__(parent=None)
        self.settings = QtCore.QSettings("Ismeralda", "lara")
        self.setWindowTitle("LARA " +  __version__ )
        
        self.lara_default_working_dir = os.getcwd()
        
        self.experiments = {}
        self.tool_item_lst = {}
        
        self.recentFileActs = []   
                
        self.createActions()
        self.createMenus()
        self.createToolbars()
        
        self.createLeftToolTabWidget(self, 142) # side tools widget for lara modules
        
        self.central_tw = LA_CentralTabWidget(self)
        self.setCentralWidget(self.central_tw)
        self.readLARASettings()
        
        self.central_tw.tabCloseRequested.connect(self.closeTab)
        self.showMaximized()
        
    def createActions(self):
        self.exit_act = QtGui.QAction(QtGui.QIcon(':/linux/quit'),"E&xit", self, shortcut="Ctrl+X",
                                      statusTip="Quit LARA", triggered=self.close)                
        #~ self.new_act = QtGui.QAction(QtGui.QIcon(':/linux/new'),"&New Experiment", self, shortcut="Ctrl+N",
                                     #~ statusTip="New LARA project", triggered=lambda new_lml_filename="": self.new_experiment_action(new_lml_filename="" ) )
        self.new_act = QtGui.QAction(QtGui.QIcon(':/linux/new'),"&New Experiment", self, shortcut="Ctrl+N",
                                     statusTip="New LARA project", triggered=self.newExperimentAction )

        self.open_act = QtGui.QAction(QtGui.QIcon(':/linux/open'),"&Open", self, shortcut="Ctrl+O",
                                      statusTip="Open LARA project", triggered=self.openExperimentAction)
                                      
        for i in range(LA_MainWindow.MaxRecentFiles):
            self.recentFileActs.append(QtGui.QAction(self, visible=False, triggered=self.openRecentExperimentAction))
                
        self.pointerTypeGroup = QtGui.QActionGroup(self, enabled=True) # action group is exclusive by default
        self.move_item_act = QtGui.QAction(QtGui.QIcon(':/linux/pointer'),"&Pointer", self.pointerTypeGroup, checkable=True, shortcut="Ctrl+p",
                                           statusTip="draw connection line", triggered=self.moveItemAction)
        self.line_connect_act = QtGui.QAction(QtGui.QIcon(':/linux/line_connect'),"L&ine", self.pointerTypeGroup, checkable=True,shortcut="Ctrl+L",
                                              statusTip="draw connection line", triggered=self.connectItemsAction)

        self.copy_act = QtGui.QAction(QtGui.QIcon(':/linux/copy'),"&Copy", self, shortcut="Ctrl+c",
                                      statusTip="copy item", triggered=self.editCopyAction)
        self.cut_act = QtGui.QAction(QtGui.QIcon(':/linux/cut'),"&Cut", self, shortcut="Ctrl+x",
                                     statusTip="cut item", triggered=self.editCutAction)
        self.paste_act = QtGui.QAction(QtGui.QIcon(':/linux/paste'),"&Paste", self, shortcut="Ctrl+v",
                                       statusTip="paste item", triggered=self.editPasteAction)
                                       
        self.zoom_in_act = QtGui.QAction(QtGui.QIcon(':/linux/zoom_out'),"zoom &in", self, shortcut="Ctrl++",
                                         statusTip="zoom in", triggered=self.zoomInAction)
        self.zoom_def_act = QtGui.QAction(QtGui.QIcon(':/linux/zoom_in'),"zoom &defaulf", self, shortcut="Ctrl+D",
                                          statusTip="reset zoom to default", triggered=self.zoomDefaultAction)
        self.zoom_out_act = QtGui.QAction(QtGui.QIcon(':/linux/zoom_in'),"zoom &out", self, shortcut="Ctrl+-",
                                          statusTip="zoom out", triggered=self.zoomOutAction)
                    
        self.about_act = QtGui.QAction("A&bout", self, shortcut="Ctrl+B",
                                       triggered=self.aboutAction)
                
        self.compile_act = QtGui.QAction(QtGui.QIcon(':/linux/compile'),"&Compile", self, shortcut="Ctrl+M",
                                                     statusTip="Generate executable code for all experiments", triggered=self.compileAction)
                
        self.run_experiment_act = QtGui.QAction(QtGui.QIcon(':/linux/run_experiment'),"&Run Experiment", self, shortcut="Ctrl+R",
                                                statusTip="Run current experiment", triggered=self.runExperimentAction)

    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).fileName()
        
    def defaultAction(self,mode):
        logging.debug("LARA default action")
        return()
        
    def loadExperiment(self, lml_filename=""):
        if lml_filename != "" :
            curr_FI = QtCore.QFileInfo(lml_filename)
            
            curr_exp = la_exp.LA_Experiment(curr_FI,self)
            if os.path.isfile(lml_filename):
                curr_exp.openExpLMLfile(lml_filename)
            else :
                curr_exp.initNewExp()
                
            self.experiments[curr_exp.name()] = curr_exp
            self.lara_default_working_dir = curr_FI.absolutePath()
        
    def openExperimentAction(self):
        url1 = QtCore.QUrl("file://")
        url2 = QtCore.QUrl("file:///home")
        urls = [url1,url2]
        new_filname_dia = QtGui.QFileDialog()
        #~ new_filname_dia.setSidebarUrls(urls);
    
        new_filename_default = self.lara_default_working_dir
        lml_filename = new_filname_dia.getOpenFileName(self, 'Select LARA file to be opened...',new_filename_default,'LML files (*.lml)')
        
        if lml_filename != "" :
            self.loadExperiment(lml_filename)
            self.updateRecentFileSettings(filename=lml_filename)
            
    def openRecentExperimentAction(self):
        action = self.sender()
        if action:
            self.loadExperiment(action.data())
    
    def newExperimentAction(self):
        logging.debug("new exp action 1")
    
        new_filename_default =  self.lara_default_working_dir + "/%s_%s.lml" %( QtCore.QDateTime.currentDateTime().toString("yyMMdd_hhmmss"),"process")
        new_lml_filename = QtGui.QFileDialog.getSaveFileName(self , 'Select New empty LARA file to be used...',new_filename_default,  'LML files (*.lml)')
        
        logging.debug("new exp action %s " % new_lml_filename )
        
        if new_lml_filename != "" :
            self.loadExperiment(new_lml_filename)
            self.updateRecentFileSettings(filename=new_lml_filename)

    def editCopyAction(self):
        self.editCopySig.emit()
            
    def editCutAction(self):
        self.editCutSig.emit()
        
    def editPasteAction(self):
        self.editPasteSig.emit()
   
    def zoomDefaultAction(self):
        curr_view = self.central_tw.currentWidget()        
        if(curr_view) :
            curr_view.zoomDef()

    def zoomChanged(self, scale):
        newScale = scale.left(scale.indexOf("%")).toDouble()[0] / 100.0
        curr_view = self.central_tw.currentWidget()        
        if(curr_view) :
            oldMatrix = curr_view.matrix()
            curr_view.resetMatrix()
            curr_view.translate(oldMatrix.dx(), oldMatrix.dy())
            curr_view.scale(newScale, newScale)
        
    def zoomInAction(self):
        curr_view = self.central_tw.currentWidget()        
        if(curr_view) :
            curr_view.zoomIn()
        
    def zoomOutAction(self):
        curr_view = self.central_tw.currentWidget()
        if(curr_view) :
            curr_view.zoomOut()

    def moveItemAction(self,mode):
        logging.debug("switched to move item")
        self.pointerTypeSig.emit(la_exp.LA_Experiment.MoveItem)
        QtGui.QApplication.restoreOverrideCursor()
        # unselect all items in scene
        self.unselctAllSig.emit()
        
    def connectItemsAction(self,mode):
        logging.debug("switched to line connection")
        self.pointerTypeSig.emit(la_exp.LA_Experiment.LineConnect)
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

    def compileAction(self):
        curr_experiment = self.central_tw.currentWidget().experiment()
        
        logging.info("could be later packed into a try except box")
        curr_experiment.compileExperiment()
        
        #~ try:
            #~ 
        #~ except:
            #~ QtGui.QMessageBox.warning(self,"Code Generator Warning", "Error during compilation of experiment !")
            #~ logging.error("error during compilation of experiment")
            
    def runExperimentAction(self):
        curr_experiment = self.central_tw.currentWidget().experiment()
        
        logging.debug("running experiment: %s -- could be later packed into a try except box" % curr_experiment.name())
        curr_experiment.run_experiment()
        #~ curr_experiment.run_experiment()

    def aboutAction(self):
        QtGui.QMessageBox.about(self, "About LARA","<b>LARA %s</b> is a Laboratory Automation Robotic Assistant meta programming framework." % __version__)
        
    def updateRecentFileSettings(self, filename=""):
        recent_files_list = self.settings.value('files/recent_files', {})

        try:
            del recent_files_list[filename] #recent_files_list.remove(filename) # delete occurence of the name in the list
        except ValueError:
            pass

        recent_files_list.insert(0, filename) # putting name in front
        del recent_files_list[LA_MainWindow.MaxRecentFiles:] # truncating list

        self.settings.setValue("files/recent_files", files)

        self.updateRecentFileActions()
        
    def updateRecentFileActions(self):
        recent_files_list = self.settings.value("files/recent_files", []).toStringList() # this will change with pyqt5

        num_recent_files = min(len(recent_files_list), LA_MainWindow.MaxRecentFiles)

        for i in range(num_recent_files):
            text = "&%d %s" % (i + 1, self.strippedName(recent_files_list[i]))
            self.recentFileActs[i].setText(text)
            self.recentFileActs[i].setData(recent_files_list[i])
            self.recentFileActs[i].setVisible(True)

        for j in range(num_recent_files, LA_MainWindow.MaxRecentFiles):
            self.recentFileActs[j].setVisible(False)

        self.separatorAct.setVisible((num_recent_files > 0))

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.new_act)
        self.fileMenu.addAction(self.open_act)
        self.separatorAct = self.fileMenu.addSeparator()
        for i in range(LA_MainWindow.MaxRecentFiles):
            self.fileMenu.addAction(self.recentFileActs[i])
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exit_act)
        self.updateRecentFileActions() # fills content of recent files
        
        self.itemMenu = self.menuBar().addMenu("&Item")
        self.itemMenu.addAction(self.cut_act)
        self.itemMenu.addSeparator()
        # property could be added

        self.itemMenu = self.menuBar().addMenu("&View")
        self.itemMenu.addAction(self.zoom_in_act)
        self.itemMenu.addAction(self.zoom_def_act)
        self.itemMenu.addAction(self.zoom_out_act)
        
        self.aboutMenu = self.menuBar().addMenu("&Help")
        self.aboutMenu.addAction(self.about_act)

    def createContextMenu(self):
        #~ self.imagesTable.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        #~ self.imagesTable.addAction(self.addImagesAct)
        #~ self.imagesTable.addAction(self.removeAllImagesAct)
        pass

    def createToolbars(self):
        self.file_tb = self.addToolBar("File")
        self.file_tb.addAction(self.exit_act)
        self.file_tb.addAction(self.new_act)
        self.file_tb.addAction(self.open_act)
                
        self.edit_tb = self.addToolBar("Edit")
 
        self.edit_tb.addAction(self.copy_act)
        self.edit_tb.addAction(self.cut_act)
        self.edit_tb.addAction(self.paste_act)
        self.edit_tb.addSeparator()
        
        self.edit_tb.addAction(self.move_item_act)
        self.edit_tb.addAction(self.line_connect_act)

        self.compile_run_tb = self.addToolBar("Compile/Run")
        self.compile_run_tb.addAction(self.compile_act)
        self.compile_run_tb.addSeparator()
        self.compile_run_tb.addAction(self.run_experiment_act)
        
        self.zoom_tb = self.addToolBar("Zoom")
        #~ zoom_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        #~ zoom_slider.setRange(5, 200)
        #~ zoom_slider.setValue(100)
        #~ self.zoom_tb.addWidget(zoom_slider)
        self.zoom_cb = QtGui.QComboBox()
        self.zoom_cb.addItems(["50%", "75%", "100%", "125%", "150%"])
        self.zoom_cb.setCurrentIndex(2)
        self.zoom_cb.currentIndexChanged[str].connect(self.zoomChanged)
        self.zoom_tb.addWidget(self.zoom_cb)
        #~ self.zoom_tb.addAction(self.zoom_in_act)
        #~ self.zoom_tb.addAction(self.zoom_out_act)
        
    def createLeftToolTabWidget(self,parent, max_tool_tab_width):
        """ the simple plugin magic happens here: plugins subdirectories are screened for modules and included in tooltab widget
        """
        self.left_docwidget_dw = QtGui.QDockWidget(self)

        main_tooltab_widget = QtGui.QTabWidget(parent)
        main_tooltab_widget.setTabPosition(QtGui.QTabWidget.East)

        main_tooltab_widget.setMaximumWidth(max_tool_tab_width)
     
        # simple "plugin" routine : importing subprocess item modules from the following subdirectories:
        # tabs will appear in alphabetical order
        #~ self.item_modules = { "analysis":[], "container":[], "cultivation":[], "process_flow":[], "liquid_handling":[],  "xNA_processing":[]  }
        self.item_modules = { "cultivation":[], "process_flow":[], "xNA_processing":[] }
        
        try:
            for package_name in sorted(self.item_modules.iterkeys()):     # iterate through all package directories
                sys.path.append(package_name)
                logging.debug("pack name : %s", package_name)
                package = __import__( package_name, fromlist=[""])
                prefix = package.__name__ + "."
                logging.debug("prefix : %s of package: %s" % (prefix, package))
                                
                itemWidget = LA_ToolBoxWidget(main_tooltab_widget)
                for loader, module_name, ispkg in pkgutil.iter_modules(package.__path__, prefix):
                    logging.debug( "Found submodule %s (is a package: %s)" % (module_name, ispkg) )
                    module = __import__(module_name, fromlist=[""])
                
                    tool_item = module.InitItem(itemWidget)
                    self.tool_item_lst[tool_item.name()]=tool_item
                    self.item_modules[package_name] = tool_item.diagramClass()
                main_tooltab_widget.addTab(itemWidget, Qt.QString(package_name)) # adding a tab for each package
    
        except ImportError, e:
            error_msg = "failed to import module - %s" % e
            sys.stderr.write(error_msg)
        
        self.left_docwidget_dw.setWidget(main_tooltab_widget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.left_docwidget_dw )
 
    def closeTab(self,index):
        tab_widget2close = self.central_tw.widget(index)
        if type(tab_widget2close) == la_expov.LA_ExperimentOverview :
            experiment = tab_widget2close.experiment()
            # saving experiment before closing
            #~ temp disabled to reprogram xml output experiment.saveExpXMLFile() 
            del self.experiments[experiment.name()]
            self.central_tw.removeTab(index-1)
            self.central_tw.removeTab(index-1)
        else :
            # saving experiment before closing
            experiment = tab_widget2close.experiment() 
            logging.debug("!!! trying to close exp %s - check indexing after adding of overviews ... " % experiment.name())
            #~ experiment.saveExpXMLFile()
            
            del self.experiments[experiment.name()]
            self.central_tw.removeTab(index)
            self.central_tw.removeTab(index) 
            
    def saveAllExpXMLFiles(self):
        for experiment in self.experiments.itervalues() :
            experiment.saveExpXMLFile()
                
    def saveOverviews(self):
        for experiment in self.experiments.itervalues() :
            experiment.exp_ov.save()

    def readLARASettings(self):
        self.lara_default_working_dir = self.settings.value("application/working_dir", "").toString() # this will change with pyqt5
        if not self.lara_default_working_dir :
            self.lara_default_working_dir = os.getcwd()
        #~ recent_files_list = QtCore.QStringList() # might be superflues
        recent_files_list = self.settings.value("files/recent_tabs", []).toStringList() # this will change with pyqt5
        
        for recent_file_name in recent_files_list: 
            self.loadExperiment(recent_file_name)
           
    def writeLARASettings(self):
        self.settings.setValue("application/working_dir", self.lara_default_working_dir )
        
        recent_files_list = QtCore.QStringList() # this is freshly generated to contain the latest state
        for experiment in self.experiments.itervalues() :
            recent_files_list << experiment.xmlFileInfo().absoluteFilePath()
        self.settings.setValue("files/recent_files", recent_files_list)
        self.settings.setValue("files/recent_tabs", recent_files_list)
        
    def closeEvent(self, event):
        shutdown_message =  'Shutting down LARA, now - but first saving everything ... \n'
        sys.stderr.write(shutdown_message)
        # save all open experiments to XML files
        self.saveAllExpXMLFiles()
        
        # save experiment overview html files
        #~ self.saveOverviews()
        # save LARA program settings
        self.writeLARASettings()
        shutdown_message =  '... done, have a nice day :)\n'
        sys.stderr.write(shutdown_message)
        
if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s| %(module)s.%(funcName)s:%(message)s', level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(description="LARA - planning your robot experiments from a scientist's perspective")

    parser.add_argument('-s','--server', action='store_true', help='run LARA in server mode')
    parser.add_argument('-v','--version', action='version', version='%(prog)s ' + __version__)
        
    parsed_args = parser.parse_args()
    
    if parsed_args.server :
        logging.info("runnig LARA in server mode now")
        self.lara_default_working_dir = os.getcwd()
        #~ exp = la_exp.LA_Experiment()
        
    if not parsed_args.server :
        logging.info("runnig LARA in GUI mode")
        qt_app = Qt.QApplication(sys.argv)  # recommended way to start pyqt application for a save destroy on exit
        
        # if Gtk-CRITICAL ** Error occurs, uncomment:
        #~ qt_app.setStyle('cleanlooks')
        
        mw = LA_MainWindow()
        mw.show()
        
        sys.exit(qt_app.exec_()) # exec_ might be replaced in python3/qt5 to exec !

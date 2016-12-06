#!/usr/bin/env python
# -*- coding: utf-8 -*-

#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: LARA_Material
# FILENAME: lara_material.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# VERSION: 0.0.3
#
# CREATION_DATE: 2013/05/14
# LASTMODIFICATION_DATE: 2014/05/06
#
# BRIEF_DESCRIPTION: Material classes for LARA
# DETAILED_DESCRIPTION:
#
# 2dict algorithm by Matt Anderson
# http://stackoverflow.com/questions/3318625/efficient-bidirectional-hash-table-in-python
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

import logging
import itertools
import csv          #csv reading module

from PyQt4 import Qt, QtCore, QtGui

class LA_Material(object):
    """Docstring for class SubstanceMixture."""

    #: Doc comment for class attribute Foo.bar.
    #: It can have multiple lines.
    def __init__(self, material_name) :
        self.material_name = material_name;
        
class Container(LA_Material):
    """Docstring for class Container"""
    #def __init__(self) :
    
    #: Doc comment for init
    def __init__(self, container_name="", barcode="", lidding_state="U", description="") :
        self.container_name = container_name
        self.bar_code = barcode
        self.description = description
        self.curr_lidding_state = lidding_state
        
        self.std_bar_code_template = '"NC" + Format(Now, "yyMMddHHmmss") + "." + Format(WallClock, "fff")'

    #: returns number of wells 
    def std_container_num_wells(short_name):
        return( )

    def name(self):
        return(self.container_name)
        
    def setLidded(self):
        self.lidding_state = "L"
        
    def setUnlidded(self):
        self.lidding_state = "U"
        
    def liddingState(self):
        return(self.curr_lidding_state)

    def barCode(self):
        return(self.bar_code)
            
    def description(self):
        return(self.description)
        
class StandardContainer(Container):        
    """StandardContainer --- Important: typeof(container_type) m u s t  be string not QString !!!   """
    #: Doc comment for init
    def __init__(self, container_name="", container_type="Greiner96NwFb", barcode="", lidding_state="U", description=""):
        super(StandardContainer, self).__init__(container_name=container_name, barcode=barcode, lidding_state=lidding_state, description=description)
        logging.debug("in stdcont typ: --%s--" % container_type )
        
        # vendor name, material, num_wells, height, order num
        self.std_container_param = {  "Greiner96NwFb":{'cont_class':"plate",'full_name':"96 Greiner Clear round well  flat bt.", 
                                        'material':'PS', 'order_num':'578N96-121',
                                        'wells_rows_num':8, 'wells_cols_num':12,
                                        'height': 15.0, 'stackHeight':13.13,'thickness':12, 
                                        'bar_code_template': self.std_bar_code_template
                                        },
                                 "Greiner96NwFbLid":{'cont_class':"lid",'full_name':"Greiner micro titer plate, flat bottom ", 
                                        'material':'PS', 'order_num':'578N96-121',
                                        'wells_rows_num':8, 'wells_cols_num':12,
                                        'height': 8.0, 'stackHeight':7.93, 'thickness':12, 
                                        'bar_code_template': self.std_bar_code_template
                                        },
                                "Greiner96DwRb":{'cont_class':"plate",'full_name':"Greiner micro titer plate, flat bottom ", 
                                        'material':'PS', 'order_num':'578N96-121',
                                        'wells_rows_num':8, 'wells_cols_num':12,
                                        'height': 23.44, 'stackHeight':22.2,'thickness':12, 
                                        'bar_code_template': self.std_bar_code_template
                                        },
                                "Greiner96DwRbLid":{'cont_class':"lid",'full_name':"Greiner micro titer plate, flat bottom ", 
                                        'material':'PS', 'order_num':'578N96-121',
                                        'wells_rows_num':8, 'wells_cols_num':12,
                                        'height': 8.0, 'stackHeight':7.13,'thickness':12, 
                                        'bar_code_template': self.std_bar_code_template
                                        },
                                "ThermoTroughDw":{'cont_class':"plate",'full_name':"Greiner micro titer plate, flat bottom ", 
                                        'material':'PS', 'order_num':'578N96-121',
                                        'wells_rows_num':8, 'wells_cols_num':12,
                                        'height': 41.4, 'stackHeight':40.3,'thickness':12, 
                                        'bar_code_template': self.std_bar_code_template
                                        },
                                "BravoWashDw":{'cont_class':"plate",'full_name':"96 V11 11961.001 Autofilling MicroWash", 
                                        'material':'PS', 'order_num':'578N96-121',
                                        'wells_rows_num':8, 'wells_cols_num':12,
                                        'height': 41.4, 'stackHeight':40.3,'thickness':12, 
                                        'bar_code_template': self.std_bar_code_template
                                        },
                                "TipBoxDw":{'cont_class':"plate",'full_name':"96 V11 LT250 Tip Box 19477.002", 
                                        'material':'PS', 'order_num':'578N96-121',
                                        'wells_rows_num':8, 'wells_cols_num':12,
                                        'height': 41.4, 'stackHeight':40.3,'thickness':12, 
                                        'bar_code_template': self.std_bar_code_template
                                }}
        
        if container_type in self.std_container_param :
            self.container_type = container_type
        else :
            logging.error("container type %s not defined" % container_type)
            #~ sys.exit('Container %s is not defined as standard container !' % ( container_type ))
            
        #cont_element = self.std_container_param['Greiner96nwpLid']                                
        #logging.debug(str(cont_element['type']))
        #self.readContainerCSV()

    def contType(self):
        return(self.container_type)
        
    def fullName(self):
        return(self.std_container_param[self.container_type]['full_name'])
    
    def stdContainerFullName(self, std_container_type):
        return(self.std_container_param[std_container_type]['full_name'])   
        
    def stdContTypes(self):
        return( self.std_container_param.keys())
                                
    def contClass(self):
        return(self.std_container_param[self.container_type]['cont_class'])                                
                                
    def contClassByType(self, std_container_type):
        return(self.std_container_param[std_container_type]['cont_class'])
 
    def height(self):
        return(self.std_container_param[self.container_type]['height'])
    
    def stdContainerHeight(self, std_container_type):
        return(self.std_container_param[std_container_type]['height'])
        
    def stackHeight(self):
        return(self.std_container_param[self.container_type]['stackHeight'])
        
    def stdContainerStackHeight(self, std_container_type):
        return(self.std_container_param[std_container_type]['stackHeight'])

    def rowsNum(self):
        return(self.std_container_param[self.container_type]['wells_rows_num'])
        
    def stdContainerRowsNum(self, std_container_type):
        return(self.std_container_param[std_container_type]['wells_rows_num'])

    def colsNum(self):
        return(self.std_container_param[self.container_type]['wells_cols_num']) 

    def stdContainerColsNum(self, std_container_type):
        return(self.std_container_param[std_container_type]['wells_cols_num'])        
    
    def stdBarcodeTemplate(self):
        return(self.std_container_param[self.container_type]['bar_code_template'])
    
    def stdContainerStdBarcodeTemplate(self, std_container_type):
        return(self.std_container_param[std_container_type]['bar_code_template'])
    
    def readContainerCSV_disa(self):
        csv_filename = "lara/130911_MDO_deepwell_growth_containers.csv"
        logging.warning("needs to be adjusted that description is parsed correctly")
        with open(csv_filename, 'rb') as f:
            csv_reader = csv.DictReader(f, delimiter = ';', skipinitialspace=True, dialect = "excel" ) 
            try:
                for csv_row in csv_reader:
                    self.container_list.append(csv_row)
            except csv.Error, e:
                sys.exit('file %s, line %d: %s' % (csv_filename, csv_reader.line_num, e))
            f.close()
        #logging.debug(type(self.container_list))
        #for curr_cont in container_list:
          #logging.debug(curr_cont['description  '])
        return()

class newContainerDB(QtGui.QStandardItemModel):
    """ Class doc """
    
    def __init__ (self, parent=None, experiment=None):
        """ Class initialiser """
        super(newContainerDB, self).__init__(0,7)
        self.exp = experiment
        
        self.initDataModel()
        
        csv_filename = "lara/130911_MDO_deepwell_growth_containers.csv"
        # filling with external container info
        #self.readContainerCSV(csv_filename)
        
        # adding table to overview
        self.updateOverview()
        self.dataChanged.connect(self.updateOverview)
        
    def initDataModel(self):
        self.setHeaderData(0, QtCore.Qt.Horizontal, "Name")
        self.setHeaderData(1, QtCore.Qt.Horizontal, "Function")
        self.setHeaderData(2, QtCore.Qt.Horizontal, "Num")
        self.setHeaderData(3, QtCore.Qt.Horizontal, "Container Type")
        self.setHeaderData(4, QtCore.Qt.Horizontal, "Lidding\nState")
        self.setHeaderData(5, QtCore.Qt.Horizontal, "Bar code")
        self.setHeaderData(6, QtCore.Qt.Horizontal, "Description")
        
    def add(self, container_function="", container_type="Greiner96NwFb", lidding_state="L", num = 1):
        item_list = []
        for n in range(1,1+num) :
            
            curr_item_list = self.findItems(container_function, column=1)
            container_name = container_function + str(len(curr_item_list)+1)
             
            if lidding_state == "L" :
                #curr_lidding_state = "L"  # that's because we generate the lid first ;)
                #container_name = container_function + "_" + container_type 
                curr_item_list = self.findItems(container_function+"Lid",column=1)
                container_lid_name =  container_name + "Lid" #+ str(len(curr_item_list)+1) #container_function + "Lid" + str(n)
                curr_container_function = container_function + "Lid" 
                cont_type = container_type + "Lid"
                
                item_list = [ QtGui.QStandardItem(container_lid_name), QtGui.QStandardItem(curr_container_function), 
                              QtGui.QStandardItem("1"), QtGui.QStandardItem(container_type + "Lid"),
                              QtGui.QStandardItem(lidding_state), QtGui.QStandardItem("123"), QtGui.QStandardItem("empty description")]
                            
                row = self.appendRow(item_list)
                
                curr_lidding_state="L"  # for the container 
                
            else :
                curr_lidding_state = "U"
                
            item_list = [ QtGui.QStandardItem(container_name), QtGui.QStandardItem(container_function),
                          QtGui.QStandardItem("1"), QtGui.QStandardItem(container_type),
                          QtGui.QStandardItem(curr_lidding_state), QtGui.QStandardItem("123"), QtGui.QStandardItem("empty description")]
            row = self.appendRow(item_list)

    def properties(self, container_name):
        container_item_list = self.findItems(container_name, QtCore.Qt.MatchExactly,0)
        cont_properties = (str(self.item(container_item_list[0].row(),4).text()))
        logging.debug("container properties :")
        print(cont_properties)
        return(cont_properties)
            
    def updateOverview(self):
        header_items = ["Container Name", "Bar code", "Type", "Lidding State", "Number" ]
        
        tab_data = [[self.data(self.index(i,0)).toString(),
                     self.data(self.index(i,5)).toString(),
                     self.data(self.index(i,3)).toString(),
                     self.data(self.index(i,4)).toString(),
                     self.data(self.index(i,2)).toString() ] for i in range(self.rowCount())]

        self.exp.exp_ov.newPragraph("containers","cont1","Containers used in Experiment" )
        self.exp.exp_ov.constructTable("cont1","cont2","Container List", header_items, tab_data )
        self.exp.exp_ov.textAdded.emit()
        
    def readContainerCSV(self,csv_filename):
        with open(csv_filename, 'r') as f:
            csv_reader = csv.DictReader(f, delimiter = ';', skipinitialspace=True, dialect = "excel" ) 
            try:
                for csv_row in csv_reader:
                    item_list = [QtGui.QStandardItem(csv_row["container_name"]), QtGui.QStandardItem("1"),
                                 QtGui.QStandardItem(csv_row["container_type"]),
                                 QtGui.QStandardItem(csv_row["has_lid"]), QtGui.QStandardItem(csv_row["bar_code"]),
                                 QtGui.QStandardItem(csv_row["container_description"]),
                                 QtGui.QStandardItem(""), QtGui.QStandardItem("") ]
                    row = self.appendRow(item_list)
                    
            except csv.Error, e:
                sys.exit('file: %s, line %d: %s' % (csv_filename, csv_reader.line_num, e))
            f.close()        

class ContainerDB_disa(dict):
    """ ContainerDB is a dictonary that connects a container name with a Standardcontainer"""
    # structure: container_name - container_class )
    def __init__(self, iterable=(), **kwargs):
        csv_filename = "lara/130911_MDO_deepwell_growth_containers.csv"
        
        # filling with external container info
        self.readContainerCSV(csv_filename)
        #logging.debug("lam: container csv processed")
        # filling with parameter given container info
        self.update(iterable, **kwargs)  
    
    def update(self, iterable=(), **kwargs):
        if hasattr(iterable, 'iteritems'):
            iterable = iterable.iteritems()
        for (key, value) in itertools.chain(iterable, kwargs.iteritems()):
            if key not in self:
                self[key] = value
                
    def add(self, container_name="", container_type="", lidding_state=False):
        if lidding_state == True :
            curr_lidding_state = False  # that's because we generate the lid first ;)
            key_lid =  container_name + "Lid"
            cont_type = container_type + "Lid"
            containerLid_new =  StandardContainer(container_name=key_lid, container_type=cont_type,
                                           lidding_state=curr_lidding_state )
            self[key_lid] = containerLid_new
            curr_lidding_state=True   # for the container 
        else :
            curr_lidding_state = False
        container_new =  StandardContainer(container_name=container_name, container_type=container_type, 
                                           lidding_state=curr_lidding_state )
        self[container_name] = container_new        

    def readContainerCSV(self,csv_filename):
        #logging.warning("needs to be adjusted that description is parsed correctly, binary mode removed")
        with open(csv_filename, 'r') as f:
            csv_reader = csv.DictReader(f, delimiter = ';', skipinitialspace=True, dialect = "excel" ) 
            try:
                for csv_row in csv_reader:
                    key = csv_row["container_name"]
                    if csv_row["has_lid"] == "1":
                        curr_lidding_state = False  # that's because we generate the lid first ;)
                        key_lid = csv_row["container_name"] + "Lid"
                        containerLid_new =  StandardContainer(container_name=key_lid, container_type=csv_row["container_type"],
                                                       barcode=csv_row["bar_code"], lidding_state=curr_lidding_state, description=csv_row["container_description"] )
                        self[key_lid] = containerLid_new
                        curr_lidding_state=True   # for the container 
                    else :
                        curr_lidding_state = False
                    container_new =  StandardContainer(container_name=key, container_type=csv_row["container_type"], 
                                                       barcode=csv_row["bar_code"], lidding_state=curr_lidding_state, description=csv_row["container_description"])
                    self[key] = container_new
                      
            except csv.Error, e:
                sys.exit('file: %s, line %d: %s' % (csv_filename, csv_reader.line_num, e))
            f.close()
            
    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, dict.__repr__(self))

class ContainerLocationDB(dict):
    """ two way dictionary: format: "container_name":(device,(stack,nest),int/ext) """
    def __init__(self, automation_system, iterable=(), **kwargs):
        self.update( iterable, **kwargs)
        
        self.automation_system = automation_system
        self.device_dict = {}
        logging.info("define iterator that returns only plates")

    def update(self, iterable=(), **kwargs):
        if hasattr(iterable, 'iteritems'):
            iterable = iterable.iteritems()
        for (key, value) in itertools.chain(iterable, kwargs.iteritems()):
            self[key] = value

    def __setitem__(self, key, value):
        value[0].loadNest(value[1],value[2]) # loading plate in device
        
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        value = self[key]
        dict.__delitem__(self, key)
        dict.__delitem__(self, value)

    def autoLoad(self, container, device_name, stack_num, int_ext):
        logging.debug("lam: === autoload cont:%s dev %s" %(container, device_name))
        # first removing old stuff
        try :
            old_cont_position = self[container]
            logging.debug("cldb: remove old container")
            old_cont_position[0].rmNest(old_cont_position[1],old_cont_position[2])
        except KeyError:
            logging.error("Key error") 
        
        # now creating new entry
        logging.debug("cldb: autoload new container")
        device = self.automation_system[device_name]
        free_nest_pos = device.firstFreeNest(stack_num, int_ext)
        self[container] = (device, (stack_num, free_nest_pos), int_ext)
        logging.debug("cldb: free pos at %s found" % free_nest_pos)
        return(str(free_nest_pos))

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, dict.__repr__(self))
        
    #~ def __iter__(self):
        #~ return self
#~ 
    #~ # use yield if possible !
    #~ def next(self):

""" 
some well helper functions
"""
    
def wellname2coord(wellname):
    return( (ord(wellname[0]) - ord('A') + 1, int(wellname[1:])) )

def coord2wellname(coord):
    return( chr(ord('A') - 1  + coord[0]) + str(coord[1]) )


class SubstanceMixture():
    """ Class doc """
    def __init__ (self):
        """ Class initialiser """
        self.concentration = 0.0 # mol/l
        pass
    
# this is just in case we need a tree 
class TreeNode(list):
    def __init__(self, iterable=(), **attributes):
        self.attr = attributes
        list.__init__(self, iterable)
    def __repr__(self):
        return '%s(%s, %r)' % (type(self).__name__, list.__repr__(self), self.attr)  

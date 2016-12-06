#!/usr/bin/env python
# -*- coding: utf-8 -*-

#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: LA_Html5Generator
# FILENAME: lara_html5_generator.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# VERSION: 0.0.3
#
# CREATION_DATE: 2013/05/14
# LASTMODIFICATION_DATE: 2014/09/17
#
# BRIEF_DESCRIPTION: html5 generator classes for LARA - an experiment is a set of processes
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

import logging
import math
import datetime
import os.path
import xml.etree.ElementTree as ET

from PyQt4 import Qt, QtCore, QtGui

class LA_Html5Generator(QtCore.QObject):
    textAdded = QtCore.pyqtSignal()
    def __init__(self, report_name=""):
        super(LA_Html5Generator,self).__init__()
        
        self.report_name = report_name
        
        self.report_elements = {}
        
        self.initExpOvDOM()
        
        self.initReportStructure()
    
    def name(self):
        return(self.report_name)
        
    def initExpOvDOM(self):
        style_sheet_name = "lara/lara_report_style.css"
        
        self.expov_root = ET.Element("html", lang="en")
        ET.SubElement(self.expov_root, "meta", charset="UTF-8")
        #ET.SubElement(self.expov_root, "link", rel="stylesheet", type="text/css", href=style_sheet_name)
        #css_elm.setAttribute("media" , "screen")
        
        self.head = ET.SubElement(self.expov_root, "head")
        title = ET.SubElement(self.head, "title")
        title.text = "Exp Overview Title"
        self.body = ET.SubElement(self.expov_root, "body")
        
        self.report_elements["body"] = self.body
        
    def initReportStructure(self):
        self.newReportTitle("body", "repTitle", "Process - " + str(self.report_name) , "Benjamin Lear", str(datetime.datetime.now()) )
        
        self.newChapterTitle("body", "description", "1. Description")

        self.newSubChapterTitle("description", "timeline", "1.2 Timeline")

        self.newChapterTitle("body", "material_methods", "2. Materials and Methods")
        
        self.newChapterTitle("body", "substances", "2.1. Substances")
        
        self.newChapterTitle("body", "containers", "2.2 Containers")
        
        self.newChapterTitle("body", "devices", "2.3 Devices")

        self.newChapterTitle("body", "process", "3. Process")
        
    def listReportElements(self):
        return(self.report_elements.keys())
        
    def newReportTitle(self, parent_tag, tag, title, authors, date):
        if tag in self.report_elements:
            ET.remove(self.report_elements[tag])
            #del self.report_elements[tag] # will be overwritten anyway
            
        div =  ET.SubElement(self.report_elements[parent_tag], "div" )
        h1 =   ET.SubElement(div, "h1" )
        h1.text = title
        
        par_date =  ET.SubElement(div, "p" )
        par_date.text = "Creation date:  " + date
        par_authors = ET.SubElement(div, "p" )
        par_authors.text = "Experimenter:  " + authors 
        
        self.report_elements[tag] = h1
        self.textAdded.emit()

    def newChapterTitle(self, parent_tag, tag, title):
        if tag in self.report_elements:
            ET.remove(self.report_elements[tag])
            #del self.report_elements[tag] # will be overwritten anyway
        
        div =  ET.SubElement(self.report_elements[parent_tag], "div" )
        h2 =   ET.SubElement(div, "h2" )
        h2.text = title
        
        self.report_elements[tag] = div
        self.textAdded.emit()
        
    def newSubChapterTitle(self, parent_tag, tag, title):
        if tag in self.report_elements:
            ET.remove(self.report_elements[tag])
            #del self.report_elements[tag] # will be overwritten anyway
        
        div =  ET.SubElement(self.report_elements[parent_tag], "div" )
        h3 =   ET.SubElement(div, "h3" )
        h3.text = title
        
        self.report_elements[tag] = div
        self.textAdded.emit()
        
    def newPragraph(self, parent_tag, tag, text):
        if tag in self.report_elements:
            self.report_elements[parent_tag].remove(self.report_elements[tag])
        
        par =   ET.SubElement(self.report_elements[parent_tag], "p" )
        par.text = text
        
        self.report_elements[tag] = par
        
        self.textAdded.emit()
        
    def insertImage(self, parent_tag, tag, image_filename, caption_text):
        if tag in self.report_elements:
            self.report_elements[parent_tag].remove(self.report_elements[tag])
        
        if os.path.isfile(image_filename):
            image = ET.SubElement(self.report_elements[parent_tag], "div" )
            image.set("class","figure")
            
            ET.SubElement(image, "img", src=image_filename )
            image_caption = ET.SubElement(image, "div" )
            image_caption.set("class","FigureCaption")
            image_caption.text = caption_text
            
            #~ # this will be valid in html5
            #~ image = ET.SubElement(self.report_elements[parent_tag], "figure", src = image_name )

            self.report_elements[tag] = image
            
        self.textAdded.emit()
        
    def constructTable(self, parent_item_name, item_name, tab_caption, header_items, data):

        item_ref = self.report_elements[parent_item_name]

        logging.info("table border should be moved to style sheet")
        table = ET.SubElement(item_ref, "table", border="1"  )
        table.set("class","report")
        self.report_elements[item_name] = table
        caption = ET.SubElement(table, "caption")
        caption.text = tab_caption
        
        table_head = ET.SubElement(table, "thead" )
        table_row = ET.SubElement(table_head, "tr" )
        for head_item in header_items:
            th = ET.SubElement(table_row, "th" )
            th.text = head_item
        
        table_body = ET.SubElement(table, "tbody" )
        for row in data:
            table_row = ET.SubElement(table_body, "tr" )
            for col in row:
                td = ET.SubElement(table_row, "td" )
                td.text = str(col)
                
        self.textAdded.emit()

    def textHtml(self):
        return( ET.tostring(self.expov_root, encoding="UTF-8", method="html") )
    
    def root(self):
        return(self.expov_root)
        
    def save(self):
        exp_out_file = "Overview_" + experiment.xmlFileInfo().fileName().toAscii() + ".html"
        try:
            with open(exp_out_file, 'w') as f:
                f.write('<!DOCTYPE html>')
                ET.ElementTree(self.expov_root).write(f, 'UTF-8',method="html")
            f.close()
            logging.debug("lara: Experiment XML outputfile %s written" % experiment.name())
        except IOError:
            logging.Error("Cannot write Experiment XML outputfile %s !!!" % experiment.name())

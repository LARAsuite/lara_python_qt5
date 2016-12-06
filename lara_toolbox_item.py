#!/usr/bin/env python
# -*- coding: utf-8 -*-

#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: lara_toolbox_item
# FILENAME: lara_toolbox_item.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# VERSION: 0.0.3
#
# CREATION_DATE: 2013/05/05
# LASTMODIFICATION_DATE: 2014/14/15
#
# BRIEF_DESCRIPTION: lara_toolbox_item
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


from PyQt4 import Qt, QtCore, QtGui
#import logging

class LA_ToolBoxItem(QtGui.QListWidgetItem):
    """ LARA toolbox item for mainwindows toolbox side tab"""
    
    def __init__(self, text="", icon=None, parent=None):
        super(LA_ToolBoxItem, self).__init__(icon, text ,parent)

        self.setTextAlignment(QtCore.Qt.AlignHCenter)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled )
        
    def diagramClass(self):
        return(self.diagram_class)
                
    def pixmap(self):
        return(self.icon.pixmap(64))
        
    def text(self):
        return(self.text)

    def name(self):
        return(self.item_name)

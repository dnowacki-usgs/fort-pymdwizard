#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
License:            Creative Commons Attribution 4.0 International (CC BY 4.0)
                    http://creativecommons.org/licenses/by/4.0/

PURPOSE
------------------------------------------------------------------------------
Provide a pyqt widget for a Citation <citation> section


SCRIPT DEPENDENCIES
------------------------------------------------------------------------------
    None


U.S. GEOLOGICAL SURVEY DISCLAIMER
------------------------------------------------------------------------------
Any use of trade, product or firm names is for descriptive purposes only and
does not imply endorsement by the U.S. Geological Survey.

Although this information product, for the most part, is in the public domain,
it also contains copyrighted material as noted in the text. Permission to
reproduce copyrighted items for other than personal use must be secured from
the copyright owner.

Although these data have been processed successfully on a computer system at
the U.S. Geological Survey, no warranty, expressed or implied is made
regarding the display or utility of the data on any other system, or for
general or scientific purposes, nor shall the act of distribution constitute
any such warranty. The U.S. Geological Survey shall not be held liable for
improper or incorrect use of the data described and/or contained herein.

Although this program has been used by the U.S. Geological Survey (USGS), no
warranty, expressed or implied, is made by the USGS or the U.S. Government as
to the accuracy and functioning of the program and related program material
nor shall the fact of distribution constitute any such warranty, and no
responsibility is assumed by the USGS in connection therewith.
------------------------------------------------------------------------------
"""

from lxml import etree

from PyQt5.QtGui import QPainter, QFont, QPalette, QBrush, QColor, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox
from PyQt5.QtWidgets import QWidget, QLineEdit, QSizePolicy, QComboBox, QTableView, QFormLayout, QLabel
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPlainTextEdit, QRadioButton, QFrame
from PyQt5.QtWidgets import QStyleOptionHeader, QHeaderView, QStyle, QScrollArea, QGroupBox
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, QSize, QRect, QPoint



from pymdwizard.core import utils
from pymdwizard.core import xml_utils

from pymdwizard.gui.wiz_widget import WizardWidget
from pymdwizard.gui.ui_files import UI_Citation
from pymdwizard.gui.single_date import SingleDate
from pymdwizard.gui.repeating_element import RepeatingElement

class Citation(WizardWidget): #

    drag_label = "Citation <citation>"

    def __init__(self, parent=None, include_lwork=True):
        self.include_lwork = include_lwork
        WizardWidget.__init__(self, parent=parent)

    def build_ui(self, ):
        """
        Build and modify this widget's GUI

        Returns
        -------
        None
        """
        self.ui = UI_Citation.Ui_Form()
        self.ui.setupUi(self)

        if self.include_lwork:
            self.lworkcit_widget = Citation(parent=self, include_lwork=False)
            self.lworkcit_widget.ui.fgdc_lworkcit.deleteLater()
            self.ui.lworkcite_ext.layout().addWidget(self.lworkcit_widget)
        else:
            self.lworkcit_widget = None
        self.ui.lworkcite_ext.hide()

        self.ui.series_ext.hide()
        self.ui.pub_ext.hide()
        self.ui.fgdc_pubdate = SingleDate(label='', show_format=False)
        self.ui.pubdate_layout.addWidget(self.ui.fgdc_pubdate)

        self.onlink_list = RepeatingElement(add_text='Add online link',
                                            remove_text='Remove last',
                                            widget_kwargs={'label': 'Link'})
        self.onlink_list.add_another()
        self.ui.onlink_layout.addWidget(self.onlink_list)

        self.fgdc_origin = RepeatingElement(add_text='Add originator',
                                            remove_text='Remove last',
                                            widget_kwargs={'label': 'Originator'})
        self.fgdc_origin.add_another()
        self.ui.originator_layout.addWidget(self.fgdc_origin)

        self.setup_dragdrop(self)

    def connect_events(self):
        """
        Connect the appropriate GUI components with the corresponding functions

        Returns
        -------
        None
        """
        self.ui.radio_lworkyes.toggled.connect(self.include_lworkext_change)
        self.ui.radio_seriesyes.toggled.connect(self.include_seriesext_change)
        self.ui.radio_pubinfoyes.toggled.connect(self.include_pubext_change)



    def include_seriesext_change(self, b):
        """
        Extended citation to support series information of the record.

        Parameters
        ----------
        b: qt event

        Returns
        -------
        None
        """
        if b:
            self.ui.series_ext.show()
        else:
            self.ui.series_ext.hide()

    def include_pubext_change(self, b):
        """
        Extended citation to support publication information of the record.

        Parameters
        ----------
        b: qt event

        Returns
        -------
        None
        """
        if b:
            self.ui.pub_ext.show()
        else:
            self.ui.pub_ext.hide()

    def include_lworkext_change(self, b):
        """
        Extended citation to support a larger body of information for the record.

        Parameters
        ----------
        b: qt event

        Returns
        -------
        None
        """
        if b:
            self.ui.lworkcite_ext.show()
        else:
            self.ui.lworkcite_ext.hide()


    def dragEnterEvent(self, e):
        """
        Only accept Dragged items that can be converted to an xml object with
        a root tag called 'citation'

        Parameters
        ----------
        e : qt event

        Returns
        -------
        None

        """
        mime_data = e.mimeData()
        if e.mimeData().hasFormat('text/plain'):
            parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
            element = etree.fromstring(mime_data.text(), parser=parser)
            if element.tag in ['citation', 'citeinfo']:
                e.accept()
        else:
            e.ignore()


         
                
    def _to_xml(self):
        """
        encapsulates the QLineEdit text in an element tag

        Returns
        -------
        citation element tag in xml tree
        """
        citeinfo = xml_utils.xml_node('citeinfo')

        for origin in self.fgdc_origin.get_widgets():
            xml_utils.xml_node('origin', text=origin.added_line.text(),
                               parent_node=citeinfo)

        pubdate = xml_utils.xml_node("pubdate",
                                     text=self.ui.fgdc_pubdate.get_date(),
                                     parent_node=citeinfo)
        title = xml_utils.xml_node("title", self.ui.fgdc_title.text(),
                                   parent_node=citeinfo)
        # geoform = xml_utils.xml_node("geoform", self.ui.fgdc_geoform.text(), parent=citeinfo)

        if self.ui.radio_seriesyes.isChecked():
            serinfo = xml_utils.xml_node('serinfo', parent_node=citeinfo)
            sername = xml_utils.xml_node('serinfo',
                                         text=self.ui.fgdc_sername.text(),
                                         parent_node=serinfo)
            issue = xml_utils.xml_node('issue', text=self.ui.fgdc_issue.text(),
                                       parent_node=serinfo)

        if self.ui.radio_pubinfoyes.isChecked():
            pubinfo = xml_utils.xml_node('pubinfo', parent_node=citeinfo)
            pubplace = xml_utils.xml_node('pubplace', parent_node=pubinfo,
                                          text=self.ui.fgdc_pubplace.text())
            publish = xml_utils.xml_node('publish', parent_node=pubinfo,
                                         text=self.ui.fgdc_publish.text())

        for onlink in self.onlink_list.get_widgets():
            onlink_node = xml_utils.xml_node('onlink', parent_node=citeinfo,
                                             text=onlink.added_line.text())

        if self.include_lwork and self.ui.radio_lworkyes.isChecked():
            lworkcit = xml_utils.xml_node('lworkcit', parent_node=citeinfo)
            lwork = self.lworkcit_widget._to_xml()
            lworkcit.append(lwork)

        return citeinfo

    def _from_xml(self, citeinfo):
        """
        parses the xml code into the relevant citation elements

        Parameters
        ----------
        citation - the xml element status and its contents

        Returns
        -------
        None
        """
        try:
            if citeinfo.tag == "citation":
                citeinfo = citeinfo.xpath('citeinfo')[0]
            elif citeinfo.tag != 'citeinfo':
                print("The tag is not 'citation' or 'citeinfo'")
                return

            self.fgdc_origin.clear_widgets()
            if citeinfo.findall("origin"):
                for origin in citeinfo.findall('origin'):
                    origin_widget = self.fgdc_origin.add_another()
                    origin_widget.added_line.setText(origin.text)
            else:
                self.fgdc_origin.add_another()

            utils.populate_widget_element(self.ui.fgdc_pubdate.ui.lineEdit,
                                          citeinfo, 'pubdate')
            utils.populate_widget_element(self.ui.fgdc_title, citeinfo, 'title')

            self.onlink_list.clear_widgets()
            if citeinfo.findall("onlink"):
                for onlink in citeinfo.findall('onlink'):
                    onlink_widget = self.onlink_list.add_another()
                    onlink_widget.added_line.setText(onlink.text)
            else:
                self.onlink_list.add_another()

            if citeinfo.xpath('serinfo'):
                self.ui.radio_seriesyes.setChecked(True)
                utils.populate_widget(self.ui.fgdc_serinfo, citeinfo.xpath('serinfo')[0])
            else:
                self.ui.radio_seriesyes.setChecked(False)

            if citeinfo.xpath('pubinfo'):
                self.ui.radio_pubinfoyes.setChecked(True)
                utils.populate_widget(self.ui.fgdc_publish, citeinfo.xpath('publish')[0])
            else:
                self.ui.radio_pubinfoyes.setChecked(False)

            if citeinfo.xpath('lworkcit'):
                self.ui.radio_lworkyes.setChecked(True)
                self.lworkcit_widget._from_xml(citeinfo.xpath('lworkcit/citeinfo')[0])

        except KeyError:
            pass


if __name__ == "__main__":
    utils.launch_widget(Citation,
                        "Citation testing")


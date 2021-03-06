# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SimplePhotogrammetryRoutePlannerDialog
                                 A QGIS plugin
 A imple photogrammetry route planner.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-04-24
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Xiangyong Luo
        email                : solo_lxy@126.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os,string

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import *

from PyQt5.QtCore import (Qt, pyqtSignal)

from qgis.core import *

from qgis.utils import iface

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'sprp'))

from sprp.core.alg import *
from sprp.export.shapefile import *
from sprp.export.memory import *

MAIN_DLG = None

def setProgressVaue(currentValue,totalValue,msg):
    #print(MAIN_DLG)
    MAIN_DLG.progressChanged.emit(currentValue,totalValue,msg)
    QApplication.processEvents()

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sprp_dialog_base.ui'))


class SimplePhotogrammetryRoutePlannerDialog(QtWidgets.QDialog, FORM_CLASS):

    progressChanged = pyqtSignal(int,int,str)

    def __init__(self, parent=None):
        """Constructor."""
        super(SimplePhotogrammetryRoutePlannerDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.stackedWidget.setCurrentIndex(0)
        
        self.setupConnection()
        
        self.wkt_polygon = None

        global MAIN_DLG
        MAIN_DLG = self

    def setupConnection(self):
        self.selectPathBtn.clicked.connect(self.selectPath)
        self.calculateBtn.clicked.connect(self.doCalcuate)

        self.polygonModeRadioButton.clicked.connect(self.polygonModeRadioButton_clicked)
        self.lineModeRadioButton.clicked.connect(self.lineModeRadioButton_clicked)

        self.selectLinePushButton.clicked.connect(self.selectLinePushButton_clicked)
        self.selectPolygonBtn.clicked.connect(self.selectPolygonBtn_clicked)
        
        self.progressChanged.connect(self.setProgressValue)

        self.saveCheckBox.clicked.connect(self.saveCheckBox_triggered)

    def checkToSaveFile(self,sc,path,basename):
        if self.saveCheckBox.isChecked():
            if os.path.exists(path) == True:
                sfe = ShapefileExportor(path,basename)
                sfe.save(sc)
            else:
                QMessageBox.warning(self, "Error"," Please select a correct path!")
                return 

    def saveCheckBox_triggered(self):
        if self.saveCheckBox.isChecked():
            self.fileNameEdit.setEnabled(True)
            self.savePathEdit.setEnabled(True)
            self.selectPathBtn.setEnabled(True)
        else:
            self.fileNameEdit.setEnabled(False)
            self.savePathEdit.setEnabled(False)
            self.selectPathBtn.setEnabled(False)

    def setProgressValue(self,currentValue,totalValue,msg):
        self.progressBar.setFormat("%p% --\t" + msg)
        self.progressBar.setRange(0,totalValue)
        self.progressBar.setValue(currentValue)
        #self.progressBar.setText(msg)
        

    ################################################################################
    # polygon
    def selectPolygonBtn_clicked(self):
        vectorDraftLyr = QgsVectorLayer('Polygon?crs=epsg:4326', 
                                        'Please Draw A Polygon for Planning' ,
                                        "memory")
        QgsProject().instance().addMapLayer(vectorDraftLyr)

        #vectorDraftLyr.startEditing()
      
        # remove the original myvl
        #QgsProject.instance().layerTreeRoot().removeChildNode(myvl)
        # set layer active 
        self.hide()
        iface.setActiveLayer(vectorDraftLyr)
        # start edit
        iface.actionToggleEditing().trigger()
        # enable tool
        iface.actionAddFeature().trigger() 
        #self.show()

        iface.actionToggleEditing().triggered.connect(self.endDrawPolygon)

        #print("get here") 

    def endDrawPolygon(self):
        iface.actionToggleEditing().triggered.disconnect(self.endDrawPolygon)
        self.show()
        vlayer = iface.activeLayer()

        selection = vlayer.getFeatures()
        count = vlayer.featureCount()
        #print("??????????????????????????????%d" % count)
        for feature in selection:
            geom = feature.geometry()
            geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
            if geom.type() == QgsWkbTypes.PolygonGeometry:
                if geomSingleType:
                    x = geom.asPolygon()
                    #print("Polygon: ", x, "length: ", geom.length(),"area: ", geom.area())
                    #print(geom.asWkt())

                    self.wkt_polygon = geom.asWkt()
                    

    ################################################################################
    # line 
    def selectLinePushButton_clicked(self):
        #self.hide()
        vectorDraftLyr = QgsVectorLayer('LineString?crs=epsg:4326', 
                                        'Please Draw A Line for Planning' , 
                                        "memory")
        QgsProject().instance().addMapLayer(vectorDraftLyr)
        # set layer active 
        self.hide()
        iface.setActiveLayer(vectorDraftLyr)
        # start edit
        iface.actionToggleEditing().trigger()
        # enable tool
        iface.actionAddFeature().trigger() 
        #self.show()
        iface.actionToggleEditing().triggered.connect(self.endDrawLine)

    def endDrawLine(self):
        iface.actionToggleEditing().triggered.disconnect(self.endDrawLine)
        self.show()
        vlayer = iface.activeLayer()
    
        selection = vlayer.getFeatures()
        count = vlayer.featureCount()
        #print("??????????????????????????????%d" % count)
        for feature in selection:
            geom = feature.geometry()
            geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
            if geom.type() == QgsWkbTypes.LineGeometry:
                if geomSingleType:
                    x = geom.asPolyline()
                    print("Line: ", x, "length: ", geom.length())
                    pstr_list = []
                    for index in range(len(x) - 1):
                        resStr = "{},{},{},{}".format(x[index].x(),x[index].y()
                                                    ,x[index+1].x(), x[index+1].y())
                        pstr_list.append(resStr)
                    
                    print(pstr_list)
                    self.startEndPointEdt.setText(';'.join(pstr_list))


    def polygonModeRadioButton_clicked(self):
        if self.polygonModeRadioButton.isChecked():
            self.stackedWidget.setCurrentIndex(1)

    def lineModeRadioButton_clicked(self):
        if self.lineModeRadioButton.isChecked():
            self.stackedWidget.setCurrentIndex(0)

    def selectPath(self):
        # dlg = QtWidgets.QFileDialog(self)
        # dlg.setFileMode(QFileDialog::Directory)
        self.save_dir_name = QFileDialog.getExistingDirectory(self,"Select Save Directory","/")
        print(self.save_dir_name)
        self.savePathEdit.setText(self.save_dir_name)

    def doCalcuate(self):
        focusLength = float(self.focusLengthEdit.text())
        pixelSize = float(self.pixelSizeEdit.text())
        gsd = float(self.gsdEdit.text())
        flightSpeed = float(self.flightSpeedEdit.text())
        courseOverlap = float(self.courseOverlapSpin.value()) / 100
        sidewiseOverlap = float(self.sidewiseOverlapSpin.value()) / 100

        cameraWidth = int(self.cameraWidthEdit.text())
        cameraHeight = int(self.cameraHeightEdit.text())

        if self.saveCheckBox.isChecked():
            if self.savePathEdit.text() =='' or self.fileNameEdit.text() =='':
                QMessageBox.warning(self, "Warning"," Please enter the filename and filepath!")
                return

            if os.path.exists(self.savePathEdit.text()) is not True:
                QMessageBox.warning(self, "Error"," Please select a correct path!")
                return 
            

        ##################################
        # ???????????????
        if self.polygonModeRadioButton.isChecked():
            if self.wkt_polygon:
                # try:
                sc = SimplePolygonCalculator(self.wkt_polygon, 
                                    **{
                                    "cameraWidth": cameraWidth,
                                    "cameraHeight":cameraHeight,
                                    "focusLength":focusLength,
                                    "pixelSize":pixelSize,
                                    "gsd":gsd,
                                    "flightSpeed":flightSpeed,
                                    "courseOverlap":courseOverlap,
                                    "sidewiseOverlap":sidewiseOverlap, 
                                })

                sc.calculate()
                me = MemoryExportor()
                me.save(sc)

                self.checkToSaveFile(sc,self.savePathEdit.text(),self.fileNameEdit.text())
                # except Exception as e:
                #     QMessageBox.warning(self, "Error",str(e))
                #     return 
            else:
                QMessageBox.warning(self, "Warning"," Please draw a polygon!")

            return

        ##################################

        leftExpand = int(self.leftExpandEdit.text())
        rightExpand = int(self.rightExpandEdit.text())

        startEndPoint = ()
        startEndPointStr = "{}".format(self.startEndPointEdt.text())
        if not self.multiLineCheckBox.isChecked():
            
            startEndPoint = startEndPointStr.split(",")

            if len(startEndPoint) != 4:
                QMessageBox.warning(self, "Warning"," Start End Point Format Error!")
                return 


        if self.multiLineCheckBox.isChecked():
            lines = []

            startEndLines = startEndPointStr.split(";")

            for linestr in startEndLines:
                lines.append(linestr.split(","))

            print(lines)

            lineIndex = 0
            for line in lines:
                lineIndex = lineIndex + 1
                sc = SimpleStripCalculator(float(line[0]),float(line[1]),
                                    float(line[2]),float(line[3]),
                                    leftExpand,rightExpand, 
                                    **{
                                    "cameraWidth": cameraWidth,
                                    "cameraHeight":cameraHeight,
                                    "focusLength":focusLength,
                                    "pixelSize":pixelSize,
                                    "gsd":gsd,
                                    "flightSpeed":flightSpeed,
                                    "courseOverlap":courseOverlap,
                                    "sidewiseOverlap":sidewiseOverlap, 
                                })

                sc.calculate()
                me = MemoryExportor()
                me.save(sc)

                self.checkToSaveFile(sc,self.savePathEdit.text(),"{}-{}".format(self.fileNameEdit.text(),lineIndex))
        else:
            sc = SimpleStripCalculator(float(startEndPoint[0]),float(startEndPoint[1]),
                                 float(startEndPoint[2]),float(startEndPoint[3]),
                                leftExpand,rightExpand, 
                                **{
                                "cameraWidth": cameraWidth,
                                "cameraHeight":cameraHeight,
                                "focusLength":focusLength,
                                "pixelSize":pixelSize,
                                "gsd":gsd,
                                "flightSpeed":flightSpeed,
                                "courseOverlap":courseOverlap,
                                "sidewiseOverlap":sidewiseOverlap, 
                            })

            sc.set_pogress_callback(setProgressVaue)

            sc.calculate()
            me = MemoryExportor()
            me.save(sc)

            self.checkToSaveFile(sc,self.savePathEdit.text(),self.fileNameEdit.text())


        stastics_str = """
            <font size="3">
            <table cellspacing="0" width=100% >
                <thead>
                    <tr bgcolor="#69c401"  style="color:aliceblue">
                        <td align="center" width=30% >specification</td>
                        <td align="center" width=50%>value</td>
                        <td align="center">comment</td>
                    </tr>
                </thead>
                <tr >
                    <td style="border-bottom:1px solid #69c401">Flight Height(m)</td>
                    <td style="border-bottom:1px solid #69c401" align="center">{:.2f}</td>
                    <td style="border-bottom:1px solid #69c401"></td>
                </tr>

                <tr>
                    <td style="border-bottom:1px solid #69c401">Couseline Count</td>
                    <td style="border-bottom:1px solid #69c401" align="center">{}</td>
                    <td style="border-bottom:1px solid #69c401"></td>
                </tr>

                <tr>
                    <td style="border-bottom:1px solid #69c401">Point Count</td>
                    <td style="border-bottom:1px solid #69c401" align="center">{}</td>
                    <td style="border-bottom:1px solid #69c401"></td>
                </tr>

                <tr>
                    <td style="border-bottom:1px solid #69c401">Distance(km)</td>
                    <td style="border-bottom:1px solid #69c401" align="center">{:.2f}</td>
                    <td style="border-bottom:1px solid #69c401"></td>
                </tr>

                <tr>
                    <td style="border-bottom:1px solid #69c401">Working Time(minute)</td>
                    <td style="border-bottom:1px solid #69c401" align="center">{:.2f}</td>
                    <td style="border-bottom:1px solid #69c401">no turning time</td>
                </tr>
            </table>
            </font>
        """

        
        stastics = sc.stastics()
        self.stasticTextEdit.setHtml(stastics_str.format(
            stastics["flightHeight"],
            stastics["couselineCount"],
            stastics["pointCount"],
            stastics["distance"],
            stastics["workingTime"]
        ))

        iface.messageBar().pushMessage("Info", 
            "Compelte a automatic photogrammetry route planning.", level=Qgis.Info, duration=3)
        
    def calculateExpandPoint(self,start_long, start_lat,end_long,end_lat,
                         courseline, sidewayline,leftExpand=0,rightExpand=0):
        geod = pyproj.Geod(ellps="WGS84")
        angle,backAngle,distanceTmp = geod.inv(start_long, start_lat,end_long,end_lat)


        print("courseline={}\nsidewayline={}\nleftExpand=={}\nrightExpand=={}\n".format(
            courseline, sidewayline,leftExpand,rightExpand))

        lineStardEndPoints = []
        result = []
        forwardAngle = 0

        totalLine = leftExpand + rightExpand + 1
        currentLineIndex = 0
        self.progressBar.setValue(0)

        long = start_long
        lat = start_lat
        for index in range(leftExpand):
            long,lat,tmpAngle = geod.fwd(long,lat, angle-90,sidewayline)
            e_long,e_lat,tempAngle = geod.fwd(long,lat, angle,distanceTmp)
            lineStardEndPoints.append((long,lat,e_long,e_lat))
            
            

        lineStardEndPoints.append((start_long, start_lat,end_long,end_lat))

        long = start_long
        lat = start_lat
        for index in range(rightExpand):
            long,lat,tmpAngle = geod.fwd(long,lat, angle+90,sidewayline)
            e_long,e_lat,tempAngle = geod.fwd(long,lat, angle,distanceTmp)
            lineStardEndPoints.append((long,lat,e_long,e_lat))


        for line in lineStardEndPoints:
            lineResults,forwardAngle = caculateLine(float(line[0]),float(line[1]),
                                                float(line[2]),float(line[3]),
                                                courseline)

            result.append(lineResults)

            currentLineIndex = currentLineIndex + 1

            self.progressBar.setValue(int(currentLineIndex/totalLine * 100))

        return result,forwardAngle
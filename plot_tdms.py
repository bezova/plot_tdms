## pyQT4
##from PyQt4 import QtCore, QtGui
#from PyQt4.QtGui import QApplication, QMainWindow# QWidget #QMainWindow
##from PyQt4.QtGui import QAction, QIcon #QSizePolicy
#from PyQt4 import uic

#%% PyQt5
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog#, QMainWindow
from PyQt5 import uic

import os
import pyqtgraph as pg
import numpy as np
import pandas as pd
from LoadData import LoadData


# #IMPORT MATPLOT WIDGETS
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
#
# from matplotlib.figure import Figure
import numpy as np


qtCreatorFile = "plot_tdms_layout.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

#%%
class View(QtBaseClass):
    def __init__(self, model, parent=None):
        super(View, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model = model
        #register to model function to update plots
        self.model.update_plots = self.update_plots
        self.loadData = LoadData() #class to load tdms

        pg.setConfigOptions(antialias=True)
        #set parameters (need to moove to some data load class)
        # make white background
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        
        self.init_UI()

    def init_UI(self):
        # set signals for all buttons
        self.ui.actionLoad.triggered.connect(self.load_dataFiles)
        self.ui.action_About.triggered.connect(self.show_about_messageBox)

        pgLayoutWidget = pg.GraphicsLayoutWidget()
        self.ui.verticalLayout.addWidget(pgLayoutWidget)
        #do not need setLayout if created by designer
        #self.ui.centralwidget.setLayout(self.ui.plot_verticalLayout)

        # set plot #1
        pl1 = pgLayoutWidget.addPlot(name='CH1')
        pl1.setLabel('left', 'P', units='psi')
        pl1.showGrid(x=True, y=True)
        self.curvePl1 = pl1.plot(pen=(255, 0, 0), name="CH1")
        #add legend
        self.pl1Legend = pl1.addLegend()
        self.pl1LegenNamesList = []

        # set plot #2
        pgLayoutWidget.nextRow()
        pl2 = pgLayoutWidget.addPlot(name='CH2')
        pl2.setLabel('left', 'P', units='psi')
        pl2.showGrid(x=True, y=True)
        self.curvePl2 = pl2.plot(pen=(0, 255, 0), name="CH2")
        # add legend
        self.pl2Legend = pl2.addLegend()
        self.pl2LegenNamesList = []
        #link X axis between pl1 and pl2
        pl2.setXLink(pl1)

        # set plot #3
        pgLayoutWidget.nextRow()
        labelsNamesPl3 = {'left': 'P, psi', 'bottom': 't, seconds'}
        pl3 = pgLayoutWidget.addPlot(name='CH12')
        pl3.setLabel('left', 'P', units='psi')
        pl3.setLabel('bottom', 'time', units='s')
        pl3.showGrid(x=True, y=True)
        self.curvePl3_1 = pl3.plot(pen=(255, 0, 0), name="CH1")
        self.curvePl3_2 = pl3.plot(pen=(0, 255, 0), name="CH2")
        #set downsamplinfg here or while updating data (if here ->can set auto)
        #self.curvePl3_1.setDownsampling(ds=4)
        #self.curvePl3_2.setDownsampling(ds=4)
        self.pl3Legend = pl3.addLegend()
        self.pl3LegenNamesList = []


        #add linearRegion to plot #3
        self.linearRegion = pg.LinearRegionItem()
        #self.linearRegion.setZValue(-10) #QGraphicsItem property - puts it under all
        pl3.addItem(self.linearRegion)

        #arrange interaction between Region and plots
        def linearRegion_update_pl2():
            #update pl2 if changed linear region
            pl2.setXRange(*self.linearRegion.getRegion(), padding=0)
            
        def pl2_update_lenearRegion():
            #update linear region if changed plot2
            self.linearRegion.setRegion(pl2.getViewBox().viewRange()[0])
        
        self.linearRegion.sigRegionChanged.connect(linearRegion_update_pl2)
        pl2.sigXRangeChanged.connect(pl2_update_lenearRegion)
        pl2_update_lenearRegion()
  
    #convinient way to get view variable instead of def get_gritChecked() function
    # @property #if checked
    # def grid_checked(self):
    #     self.ui.grid_checkbox.isChecked()

    # def show_about_messageBox_static(self):
    #     # version with static function API
    #     QMessageBox.information(self, "About plot_tdms", "Plots 2 channel HFPM TDMS data\nAndrey Bogdan (c) 2017")

    @staticmethod
    def show_about_messageBox():
        #version with property-based api
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Plots 2 channel HFPM TDMS data")
        msg.setInformativeText("(c) Andrey Bogdan 2017")
        msg.setWindowTitle("About plot_tdms")
        msg.setDetailedText("The details are as follows:")
        #msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        #msg.buttonClicked.connect(msgbtn)
        retValue = msg.exec_()

    def load_dataFiles(self):
        loadedData = self.loadData.load()
        if loadedData:
            self.model.data = loadedData
            self.model.generate_curve()

    def update_plots(self, data):
        dat1 = data.values[:,0][::4] #decimate to approx 50Hz (200/4)
        name1, name2 = data.columns
        dat2 = data.values[:,1][::4]
        self.curvePl1.setData(dat1)
        self.curvePl2.setData(dat2)
        self.curvePl3_1.setData(dat1, name=name1)
        self.curvePl3_2.setData(dat2, name=name2)

        #clear legend if already existed
        for name in self.pl1LegenNamesList:
            self.pl1Legend.removeItem(name)
        self.pl1LegenNamesList = []

        for name in self.pl2LegenNamesList:
            self.pl2Legend.removeItem(name)
        self.pl2LegenNamesList = []

        for name in self.pl3LegenNamesList:
            self.pl3Legend.removeItem(name)
        self.pl3LegenNamesList = []

        #add items to legend and remember their names to be able to remove later
        self.pl1Legend.addItem(self.curvePl1, name1)
        self.pl1LegenNamesList = [name1]

        self.pl2Legend.addItem(self.curvePl2, name2)
        self.pl2LegenNamesList = [name2]

        self.pl3Legend.addItem(self.curvePl3_1, name1)
        self.pl3Legend.addItem(self.curvePl3_2, name2)
        self.pl3LegenNamesList = [name1, name2]

        dataLen = len(dat1)
        #self.linearRegion.setRegion([0, dataLen-1])
        self.linearRegion.setBounds([0, dataLen-1])

class Model(object):
    def __init__(self):
        self.update_plots = None #placeholder will have reference to View
        self.data = None #placeholder for data loaded

    def generate_random(self):
        #generates random data for initial demo plot
        nPoints = 10000
        dat1 = 0.01*np.random.rand(nPoints)
        dat2 = np.random.rand(nPoints)+10.
        data = pd.DataFrame({'col1': dat1, 'col2': dat2})
        self.update_plots(data)

    def generate_curve(self):
        #send real data to plot
        self.update_plots(self.data['channels'])

class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.model = Model()
        #self.controller = Controller(self.model)
        self.view = View(self.model)#, self.controller)
        self.view.show()
        self.start()

    def start(self):
        self.model.generate_random()
        #self.view.load_dataFiles()

if __name__ == '__main__':
    import sys

    app = App(sys.argv)
    sys.exit(app.exec_())
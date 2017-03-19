import os
from PyQt5.QtWidgets import QFileDialog
from nptdms import TdmsFile
import pandas as pd
#from collections import OrderedDict

class LoadData(object):
    def __init__(self, dirPath=None):
        if not dirPath:
            dirPath = os.getcwd()
        self.dirPath = dirPath


    def load(self, fileNames=None, loadedFiles=[]):
        if not fileNames:
            fileNames, filterName = QFileDialog.getOpenFileNames(parent=None,
                                                                 caption='Open data file(s)',
                                                                 directory=self.dirPath,
                                                                 filter="Data Files (*.tdms *.h5);;All Files (*.*)")
        if fileNames:
            self.dirPath = os.path.dirname(fileNames[0])
            # can only read one tdms file
            # TBD: implement multiple files
            # TBD implement reading .hdf5
            for fileName in fileNames[:1]:
                extension = os.path.splitext(fileName)[1]
                if extension == '.tdms':
                    return self._read_tdms_file(fileName)

    def _read_tdms_file(self, fileName):
        #reads one tdms file
        tdmsFile = TdmsFile(fileName)

        groupNames = tdmsFile.groups()
        groupObj = tdmsFile.object(groupNames[0])
        groupProps = groupObj.properties

        if len(groupProps) != 0:
            # open and read TDMS file format of year 2016
            # incriment
            incriment = groupProps['wf_increment']
            # start time
            timeFormat = '%Y_%m_%d_%H_%M_%S.%f'
            startTime = pd.to_datetime(groupProps['wf_start_time'], format=timeFormat)
            # use startTime.date .seconds etc to get details

            # get names of channels
            channelObjs = tdmsFile.group_channels(groupNames[0])
            channelNames = [obj.channel for obj in channelObjs]
            # will also work for 2015

        else:
            # format of year 2015
            channelObjs = tdmsFile.group_channels(groupNames[0])
            channelProps = [obj.properties for obj in channelObjs]

            # get names of channels
            channelNames = [cP['NI_ChannelName'] for cP in channelProps]

            # incriment
            incriment = channelProps[0]['wf_increment']

            # start time (from properties of first channel)
            timeFormat = '%Y_%m_%d_%H_%M_%S.%f'
            startTime = pd.to_datetime(channelProps[0]['wf_start_time'],
                                       format=timeFormat)

        data = tdmsFile.as_dataframe(absolute_time=False)
        # rename data columns to channel names
        data.columns = channelNames

        out = {}
        out['filename'] = fileName
        out['starttime'] = startTime
        out['dt'] = incriment
        out['channels'] = data #channels names are in pandas columns
        return out

if __name__ == '__main__':
    loadData = LoadData()
    #loaded = loadData.load(['TW_2016_02_15_22_41_25.tdms'])
    #print(loaded.data['channels'].head())
    if True:
        import sys
        from PyQt5.QtWidgets import QApplication
        import pandas as pd

        app = QApplication(sys.argv)
        loaded = loadData.load()
        if loaded:
            print(loaded['channels'].head())
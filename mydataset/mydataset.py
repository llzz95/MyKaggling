from progressbar import ProgressBar
import numpy as np


class MyDataSet(object):
    def __init__(self,filename:str,nrows=None):
        self.__filename = filename
        self.__progress = 0
        self.__data = self.getData(nrows)
        # assert isinstance(self.__data,np.ndarray)


    def getData(self,nrows):
        #Need to be completed
        # with open(self.__filename,mode='r') as f:
        #     with ProgressBar() as bar:
        #         for line in f.readlines():
        #             pass
        import pandas as pd
        data = pd.read_csv(self.__filename,nrows=nrows,header=None)
        # data  = np.loadtxt(dtype=np.int32,delimiter=',',)
        return data

    def getNextBatch(self,batch_size:int):
        self.__progress %= (len(self.__data)-1)
        data = self.__data[self.__progress:self.__progress+batch_size]
        self.__progress+=batch_size
        return data


    @property
    def shape(self):
        return self.__data.shape
    @property
    def data(self):
        return self.__data
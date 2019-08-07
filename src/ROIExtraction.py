'''
Created on Jul 31, 2019

@author: Oscar Cuadros Linares
'''

import javabridge
import bioformats
from bioformats import log4j
from bioformats.omexml import OMEXML
import cv2 as cv2
import numpy as np
import src.Util as ut
import math
import matplotlib.pyplot as plt
import threading







class ResizeTileThread(threading.Thread):
    tileGray=None
        
    def __init__(self, tile, physicalX, physicalY, inMag, outMag, width, height):
       
        threading.Thread.__init__(self)
        self.tile = tile
        self.physicalX = physicalX
        self.physicalY = physicalY
        self.inMag = inMag
        self.outMag = outMag
        self.height = height
        self.width = width
              
    
    def run(self):
        self.resizeTile()
    
    def join(self, timeout=None):
        threading.Thread.join(self, timeout=timeout)
        print('end')
        return self.tileGray     
        
    def resizeTile(self):
                                               
        newResolution = ut.computeResolution(self.physicalX, self.physicalY, self.width, self.height, self.inMag , self.outMag)
            
        self.tile.shape = (int(self.height), int(self.width), 3)
               
        # resize tile
        tileResized = imgResize(self.tile, newResolution)
        self.tileGray = cv2.cvtColor(tileResized, cv2.COLOR_BGR2GRAY)
        



class ResizeVSI:
    def __init__(self, fName, outMag):
        '''
        :param outMag: output magnitude
        '''
        self.fName = fName
        self.outMag = outMag
        self.nThreadsX = 20
        self.nThreadsY = 20 
                
    
    def process(self):
        # starting jvm
        threadLock = threading.Lock()
        javabridge.start_vm(class_path=bioformats.JARS, run_headless=True, max_heap_size='8G')
        
        try:
                     
            
            log4j.basic_config()
            class ResizeTile(threading.Thread):
                tileGray=None
                    
                def __init__(self, reader, nThreadsX, threadX, physicalX, physicalY, inMag, outMag, height, tileBeginY):
                   
                    threading.Thread.__init__(self)
                    self.reader = reader
                    self.nThreadsX = nThreadsX
                    self.threadX = threadX
                    self.physicalX = physicalX
                    self.physicalY = physicalY
                    self.inMag = inMag
                    self.outMag = outMag
                    self.height = height
                    self.tileBeginY = tileBeginY
                    
                           
                
                def run(self):
                    self.process()
                
                def join(self, timeout=None):
                    threading.Thread.join(self, timeout=timeout)
                    return self.tileGray     
                    
                def process(self):
                    
                    
                    tileBeginX = ut.minMax(self.threadX , 0, self.nThreadsX, 0, sizeX)
                    width = ut.minMax(self.threadX + 1 , 0, self.nThreadsX, 0, sizeX) - tileBeginX
                                 
                    tile = self.reader.openBytesXYWH(0, tileBeginX, self.tileBeginY, width, self.height)
                                                                                                    
                    newResolution = ut.computeResolution(self.physicalX, self.physicalY, width, self.height, self.inMag , self.outMag)
                        
                    tile.shape = (int(self.height), int(width), 3)
                           
                    # resize tile
                    tileResized = imgResize(tile, newResolution)
                    self.tileGray = cv2.cvtColor(tileResized, cv2.COLOR_BGR2GRAY)
                      
            
          
            
            # reading metadata   
            ome = OMEXML(bioformats.get_omexml_metadata(path=self.fName))
            sizeX = ome.image().Pixels.get_SizeX()
            sizeY = ome.image().Pixels.get_SizeY()
                
            physicalX = ome.image().Pixels.get_PhysicalSizeX()
            physicalY = ome.image().Pixels.get_PhysicalSizeY()
                
            print('Original size: ', sizeX, sizeY)
            print('Original physical pixel size: ', physicalX, physicalY)
            
            # computing input magnification
            inMag = np.round(np.float(ome.instrument(0).Objective.get_NominalMagnification()), 0)
            
            hMosaicGray = []
            vMosaicGray = []
            # initialize variables         
            
            tileBeginY = 0
            tileCounter = 0;
        
            for threadY in range(0, self.nThreadsY):  # <=
                              
                imageReader = bioformats.formatreader.make_image_reader_class()
                   
                reader = imageReader()
                reader.setId(self.fName)
                
                # computing begin and height size 
                tileBeginY = ut.minMax(threadY , 0, self.nThreadsY, 0, sizeY)
                height = ut.minMax(threadY + 1 , 0, self.nThreadsY, 0, sizeY) - tileBeginY
                            
                
                threadsX = []    
                for threadX in range(0, self.nThreadsX):
                    thread = ResizeTile(reader, self.nThreadsX, threadX, physicalX, physicalY, inMag, self.outMag, height, tileBeginY)
                    thread.start()
                    threadsX.append(thread)
                 
                for threadX in range(0, self.nThreadsX):  # <=
                    if(threadX > 0):
                       
                        hMosaicGray = np.concatenate((hMosaicGray, threadsX[threadX].join()), axis=1)
                        
                    else:
                       
                        hMosaicGray = threadsX[threadX].join()
                                        
                    tileCounter = tileCounter + 1
                
                if(threadY > 0):
                    vMosaicGray = np.concatenate((vMosaicGray, hMosaicGray), axis=0)
                else:
        
                    vMosaicGray = hMosaicGray
            
                hMosaicGray = []
                progress = (tileCounter * 100) / (self.nThreadsX * self.nThreadsY)
                print("processing", str(progress) + ' %')
                     
        
        finally:
            javabridge.kill_vm()
    


        print("success")
    
        plt.imshow(vMosaicGray, cmap='jet')
        plt.show()
        return vMosaicGray    
            
   
    
def rescaleMicroscopeMagnification(fileName, outMag):
    '''
    Reading a vsi image tile by tile and return an small TIFF image
    :param outMag:  output magnification 
    '''
    # The number of threads is also the number of tiles
    nThreadsX = 20
    nThreadsY = 10
    
    # starting jvm
    javabridge.start_vm(class_path=bioformats.JARS, run_headless=True, max_heap_size='8G')
        
    try:
        log4j.basic_config()
               
        ome = OMEXML(bioformats.get_omexml_metadata(path=fileName))
        sizeX = ome.image().Pixels.get_SizeX()
        sizeY = ome.image().Pixels.get_SizeY()
            
        physicalX = ome.image().Pixels.get_PhysicalSizeX()
        physicalY = ome.image().Pixels.get_PhysicalSizeY()
            
        print('Original size: ', sizeX, sizeY)
        print('Original physical pixel size: ', physicalX, physicalY)
        
        # computing input magnification
        inMag = np.round(np.float(ome.instrument(0).Objective.get_NominalMagnification()), 0)
        
        # initialize variables         
        tileBeginX = 0
        tileBeginY = 0
        tileCounter = 0;
        
        hMosaicGray = []
        vMosaicGray = []
        
        numberOfTilesY = nThreadsY  # tmp delete it
        
        for y in range(0, numberOfTilesY):  # <=
                              
            # computing begin and height size 
            tileBeginY = ut.minMax(y , 0, numberOfTilesY, 0, sizeY)
            height = ut.minMax(y + 1 , 0, numberOfTilesY, 0, sizeY) - tileBeginY
            
            imageReader = bioformats.formatreader.make_image_reader_class()
            reader = imageReader()
            reader.setId(fileName)
        
            
            
            
            threadsX = []    
            for threadX in range(0, nThreadsX):  # <= 
                tileBeginX = ut.minMax(threadX , 0, nThreadsX, 0, sizeX)
                width = ut.minMax(threadX + 1 , 0, nThreadsX, 0, sizeX) - tileBeginX
                
                tile = reader.openBytesXYWH(0, tileBeginX, tileBeginY, width, height)
                thread = ResizeTileThread(tile, physicalX, physicalY, inMag, outMag, width, height)
                thread.start()
                threadsX.append(thread)
                            
            for x in range(0, nThreadsX):  # <=
                if(x > 0):
                   
                    hMosaicGray = np.concatenate((hMosaicGray, threadsX[x].join()), axis=1)
                    
                else:
                   
                    hMosaicGray = threadsX[x].join()
                                        
                tileCounter = tileCounter + 1
                   
                            
            if(y > 0):
                vMosaicGray = np.concatenate((vMosaicGray, hMosaicGray), axis=0)
            else:
        
                vMosaicGray = hMosaicGray
            
            hMosaicGray = []
            progress = (tileCounter * 100) / (nThreadsX * numberOfTilesY)
            print("processing", str(progress) + ' %')
        
    finally:
        javabridge.kill_vm()
     
    print("success")
    
    plt.imshow(vMosaicGray, cmap='jet')
    plt.show()
    return vMosaicGray




def imgResize(image, resolution=250000.0):
    '''
    Resize to 250000 (500x500) pixels aprox resolution    
    default resolution 500x500     
    '''
    
    height, width = image.shape[:2]
    
    factor = math.sqrt(resolution / (height * width))  
     
    if factor < 1.0:
        # print ( "Image resized by scale factor " + str(factor)) 
        return cv2.resize(image, (0, 0), fx=factor, fy=factor, interpolation=cv2.INTER_AREA) 
    else:
        return image        

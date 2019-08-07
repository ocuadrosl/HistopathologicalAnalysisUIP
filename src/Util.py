'''
Created on Aug 6, 2019

@author: oscar
'''

import numpy as np




def computeResolution(physicalX, physicalY, sizeX, sizeY, inputMagnification, outputMagnification):
    '''
    physical in micrometers
    '''
    
    eyePice = 10.0 #10x
    magnificationDifference = ((inputMagnification * eyePice) - (outputMagnification * eyePice)) + 0.00000000001 
        
    outputPhysicalX = (physicalX * magnificationDifference) + physicalX
    outputPhysicalY = (physicalY * magnificationDifference) + physicalY
    
    # print outputPhysicalY, outputPhysicalY
        
    sizeXOutput = sizeX / outputPhysicalX
    sizeYOutput = sizeY / outputPhysicalY
    
    # print sizeXOutput, sizeYOutput
    
    return sizeXOutput * sizeYOutput
    
   
def minMax(inputValue, orgMin, orgMax, newMin, newMax):
    den = 0.00000001 if  orgMax == orgMin else orgMax - orgMin 
    # print inputValue, ( ((newMax - newMin) * (inputValue - orgMin)) / den) + newMin
    return  (((newMax - newMin) * (inputValue - orgMin)) / den) + newMin


def cartesianToPolar(x, y, cx=0, cy=0):
    
    x -= cx
    y -= cy
    
    r = np.sqrt(x ** 2 + y ** 2)
    t = np.arctan2(y, x)
    return [r, t]


def matrixToCartesian(col, row, size):
    
    fraction = ((size / 2) + 1 / 2)
    return (col - fraction, -row + fraction)


def vectorToMatrixIndex(index, height):
    
    return (index // height, index % height) 







     
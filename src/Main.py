'''
Created on Jul 31, 2019

@author: Oscar Cuadros Linares
'''

import src.ROIExtraction as roi
import src.VSI as vsi
import cv2 as cv2

if __name__ == '__main__':
  
    fileName='/home/oscar/data/biopsy/Dataset 1/B 2009 8854/B 2009 8854 A.vsi'
    
    image = vsi.rescaleMicroscopeMagnification(fileName, 5)
    
    outFileName = '/home/oscar/data/biopsy/tiff/' + (fileName.split('/').pop()).split('.')[0]+'.tiff'
    
    
    cv2.imwrite(outFileName, image)
    
    
    
    #roi.identifyHighDensity(image, 3)
   

    
    
      
    print("DONE")
    
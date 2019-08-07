'''
Created on Jul 31, 2019

@author: Oscar Cuadros Linares
'''

import src.ROIExtraction as roi

if __name__ == '__main__':
  
    fileName='/home/oscar/data/biopsy/B526-18  B 20181107/Image01B526-18  B .vsi'
    roi.rescaleMicroscopeMagnification(fileName, 5)
    
    #r = roi.ResizeVSI(fileName,5)
    #r.process()
    
    
      
    print("DONE")
    
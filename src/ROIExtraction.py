'''
Created on Jul 31, 2019

@author: Oscar Cuadros Linares
'''



import cv2 as cv2
import numpy as np
import matplotlib.pyplot as plt
      


def identifyHighDensity(self, imageGray, maskSize=3):
    
    '''
    This function computes the probability [0-100] of a pixel belongs to a 
    high density region
    '''
    _ , otsu = cv2.threshold(imageGray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    height,width = imageGray.shape
    
    foreground = np.zeros((height, width, 1), np.float32)
    
    #foreground[np.where(otsu == [255])] = imageGray
    
    np.where(otsu==[255], foreground, imageGray)
    
    plt.imshow(foreground, cmap='jet')
    plt.show()
    
    
    height,width = foreground.shape
    
    
    maxDensity = pow(maskSize, 2) 
    maskCenter = maskSize//2
   
    output = np.zeros((height, width, 1), np.float32)
    
    
    for h in range(0, height):
        
        for w in range(0, width):
            
            if foreground[h, w] != 0:  # 255
                count = 0
                
                for i in range(h - maskCenter, h + maskCenter):
                    for j in range(w - maskCenter, w + maskCenter):
                        
                        try:  # out of bound, improve it... 
                            if foreground[i, j] > 0:  # <255
                                count = count + 1
                                # print count
                        except:
                            pass  # do nothing
                
                # if (count * 100) / maxDensity > 100:
                    # print (count * 100) / maxDensity
                output[h, w] = ((count * 100) / maxDensity)  # 255- ...
                       
        return output





















'''
Created on Jul 31, 2019

@author: Oscar Cuadros Linares
'''

import javabridge
import bioformats
from bioformats import log4j
from bioformats.omexml import OMEXML

    
def rescaleMicroscopeMagnification(fileName, outputMagnification, numberOfTilesX, numberOfTilesY):
    '''
    Reading a vsi image tile by tile and return an small TIFF image 
    '''
    javabridge.start_vm(class_path=bioformats.JARS, run_headless=True, max_heap_size='8G')
        
    try:
        log4j.basic_config()
        imageReader = bioformats.formatreader.make_image_reader_class()
        reader = imageReader()
        reader.setId(fileName)
        
        ome = OMEXML(bioformats.get_omexml_metadata(path=fileName))
        sizeX = ome.image().Pixels.get_SizeX()
        sizeY = ome.image().Pixels.get_SizeY()
            
        physicalX = ome.image().Pixels.get_PhysicalSizeX()
        physicalY = ome.image().Pixels.get_PhysicalSizeY()
            
        print('Original size: ', sizeX, sizeY)
        print('Original physical pixel size: ', physicalX, physicalY)
        
    finally:
        javabridge.kill_vm()
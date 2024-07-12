import os
import sys
import numpy as np
#import matplotlib.pyplot as plt
import PIL #ok
import PIL.Image
import PIL.ImageDraw
import xml.etree.ElementTree as ET
#from skimage import io, transform
import cv2
import time
from skimage import exposure

class BBoxWrapper:
    def __init__(self, classid, score, xmin ,ymin, xmax, ymax):
        self.classid = classid
        self.score = score
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
    def __str__(self):
        return f'{self.classid} {self.score} ' \
               f'{self.xmin} {self.ymin} {self.xmax} {self.ymax}'

def normalisation(image):
    iLow, iHigh = np.percentile(image, (0.005,99.995)) # Leica (0.002,99.998), Zeiss (0.2,99.8) // Leica (0.005,99.995), Zeiss (0.5,99.5)
#    print("iLow : "+str(iLow)+", iHigh : "+str(iHigh))
    image=exposure.rescale_intensity(image, in_range=(int(iLow), int(iHigh)))
    return image
    
               
def slicesFromYolo_fct(images_location,annotations_location,slices_location):
    #images_location = os.path.join(dataset_location, 'images/train')
    #annotations_location = os.path.join(dataset_location, 'annotations/train')
    
    try:

        filename_list_xml_train = sorted(os.listdir(annotations_location))
        #display(filename_list_xml_train[:4])

        i=1
        for filename_xml in filename_list_xml_train:       # 'BloodImage_00000.xml'
            if filename_xml.lower().endswith('.xml'):
                filepath_xml = os.path.join(             # '/../../BloodImage_00000.xml'
                    annotations_location, filename_xml)  
                tree = ET.parse(filepath_xml)            # xml.etree.ElementTree.ElementTree
                
                filename = tree.find('./filename').text  # 'BloodImage_00000'
                w = tree.find('./size/width').text       # '640'
                h = tree.find('./size/height').text      # '480'
                d = tree.find('./size/depth').text       # '3'
                
                filepath_jpg = os.path.join(             # '/../../BloodImage_00000.jpg'
                    images_location, filename) #+'.jpg')
                
                assert os.path.isfile(filepath_jpg)
                

                image=cv2.imread(filepath_jpg,-1)
                image=normalisation(image)
                
                object_elemnts = tree.findall('./object')  # [xml.etree.ElementTree.ElementTree, ...]
                for obj_el in object_elemnts:
                
                    name = obj_el.find('./name').text         # 'RBC'
                    xmin = obj_el.find('./bndbox/xmin').text  # '233'
                    ymin = obj_el.find('./bndbox/ymin').text  # '368'
                    xmax = obj_el.find('./bndbox/xmax').text  # '338'
                    ymax = obj_el.find('./bndbox/ymax').text  # '452'
                    
                    #if name in classes:
                        #classid = classes.index(name)
                    bbw = BBoxWrapper(classid=0, score=1.0,
                                      xmin=int(xmin), ymin=int(ymin),
                                      xmax=int(xmax), ymax=int(ymax))

                    slice_i=image[bbw.ymin:bbw.ymax,bbw.xmin:bbw.xmax]
                    slicepath_jpg = os.path.join(slices_location, name)
                    sliceName=filename.replace('.tif', '_')+name+"_"+str(i)
                    if not os.path.exists(slicepath_jpg):
                        os.makedirs(slicepath_jpg)
                    cv2.imwrite(slicepath_jpg+'/'+sliceName+'.tif',slice_i)
                    i=i+1
                    
                    #else:
                    #    raise  # pass
    except:
        return

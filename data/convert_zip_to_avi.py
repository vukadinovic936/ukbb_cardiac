# David Ouyang 4/10/2020

# Notebook which iterates through a folder of subfolders,
# Read manifest file to choose views
# and convert DICOM files to AVI files of a defined size 
# natively, original size, previous implementatin was (112 x 112)

# Milos Vukadinovic 6/5/2021
# adaptation of the script

import re
import os, os.path
from os.path import splitext
import pydicom as dicom
import numpy as np
from pydicom.uid import UID, generate_uid
import shutil
from multiprocessing import dummy as multiprocessing
import time
import subprocess
import datetime
from datetime import date
import sys
import cv2
import matplotlib.pyplot as plt
import sys
from shutil import copy
import math
import random
from tqdm import  tqdm
from matplotlib.pyplot import imshow

def convert_zip_to_avi(directory = '/workspace/data/NAS/UKBB_Backup/', remove = False):
    
    """
        NOTE: be cautious when using this function, if you specify remove=True
        all the .zip files and subdirectories are of the specified 'directory'
        are going to be deleted

        Args:
            directory string
                the path to the directory containing zip files downloaded from UKBB
            remove bool
                specify if you want to remove the zip files from the directory after converting them
        Return:
            True/False based on wether the action was executed succesfully
    """
#    os.system(f"data/unzipAll.rc {directory}")
    cropSize = (112,112)

    for item in tqdm(os.listdir(directory)):
        if(os.path.isdir(os.path.join(directory, item))):
            if(os.path.exists(os.path.join(directory, item, "manifest.csv"))
            or os.path.exists(os.path.join(directory, item, "manifest.cvs"))):
                try:
                    patient = "undefined"
                    views = {}
                    manifest = "manifest.csv" if os.path.exists(os.path.join(directory, item, "manifest.csv")) else "manifest.cvs"
                    print(manifest)
                    with open(os.path.join(directory, item, manifest), 'r') as manifest:
                        for i, line in enumerate(manifest.readlines()):
                            if i>0:
                                linesplit = line.split(',')
                                filename = linesplit[0]
                                patient = linesplit[1].replace(" ","")
                                view = linesplit[6].split('_')[-1]
                                
                                if view in views.keys():
                                    views[view].append(filename)
                                else:
                                    views[view] = [filename]
                    for view in views.keys():
                        out = "this is the cv2 video writer"
                        viewDict = {}
                        for i, file in enumerate(views[view]):                 
                            video_filename = os.path.join(directory, item+"_"+patient + "_" + view + '.avi')
                            if(os.path.exists(video_filename)):
                                continue
                            frame = dicom.dcmread(os.path.join(directory, item, file), force = True)
                            framecount = int(frame.InstanceNumber)
                            framearray = frame.pixel_array
                            framearray = (framearray/np.max(framearray)*255.0).astype(np.uint8)
                            viewDict[framecount] = framearray
                            
                        framelist = list(viewDict.keys())
                        framelist.sort()
            
                        for i in framelist:
                            
                            framearray = viewDict[i]
                            
                            if i == 1:
                                (x,y) = framearray.shape
                                cropSize = (y,x)
                                fps = 20
                                fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
                                out = cv2.VideoWriter(video_filename, fourcc, fps, cropSize, True)
                                
                            output = cv2.resize(framearray, cropSize, interpolation = cv2.INTER_CUBIC)
                            output = cv2.merge([output, output, output])
                            out.write(output)
                            
                        out.release()
                except: 
                    print(f"The example {item} was corrupted")

    os.system(f'rm -R -- {directory}*/')
    if remove:
        # Remove intermediate files
        os.system(f'rm -rf {directory}*.zip')

if __name__ == "__main__":
    convert_zip_to_avi(directory = '/workspace/data/NAS/UKBB_Backup/', remove = True)

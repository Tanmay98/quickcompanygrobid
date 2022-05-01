import os
import glob 
import shutil

input_folder = "./rajasthan_xmls"
s = os.listdir(input_folder)
src = input_folder
dest_fldr =  ("./rajasthan_main")



for i in s:
	# if i.endswith(".training.segmentation.tei.xml"):
	# 	shutil.copy(os.path.join(src,i),dest_fldr)
	 if i.endswith(".training.segmentation"):
	 	shutil.copy(os.path.join(src,i),dest_fldr)
	#if i.endswith(".training.fulltext.tei.xml"):
	#	shutil.copy(os.path.join(src,i),dest_fldr)
	#if i.endswith(".training.fulltext"):
	#	shutil.copy(os.path.join(src,i),dest_fldr)

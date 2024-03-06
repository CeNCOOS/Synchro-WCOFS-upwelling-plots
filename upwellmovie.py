#
import os
import glob
#
# This code takes sequentially numbered plot files and uses gm convert to create
# an animated gif.  The code globs the files in the directory and then sorts
# them by the file time.
#
# -dispose clear images for next image (so titles don't overwrite)
# -delay creates a 2 second delay between images
# *.gif is create a give movie
# gm convert -dispose previous -delay 200 *.png heat_wave_recent.gif
# 
# how do we put in a file list for the *.png ?
#
filepath='/home/flbahr/heat_content/'
filepre='upwell_test_'
fileend='.png'
files=glob.glob(filepath+filepre+'*'+fileend)
files.sort(key=os.path.getmtime)
lf=len(files)
thelist=[]
for k in range(0,lf):
    thelist.append(files[k])
command='gm convert -dispose previous -delay 200 {} /home/flbahr/heat_content/upwell_movie.gif'.format(' '.join(thelist))
os.system(command)

import xarray as xr
import numpy as np
import scipy.io
from scipy import integrate
from scipy.interpolate import griddata
import datetime as dt
import time, scipy.io
from wcof_load_s3_synchro_fix import wcof_load_s3_synchro_fix
import pickle
import matplotlib.pyplot as plt
import matplotlib as mpl
import pdb
import cartopy.feature as cf
import cartopy.crs as ccrs
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.ticker as mticker
from cartopy.mpl.ticker import (LongitudeFormatter,LatitudeFormatter)
import pandas as pd
#
# get the current date so we can get the current month
#
atime=dt.datetime.now()
# current month
current_month=atime.month
# so since we are in the next month the previous month should all be there
current_year=atime.year
cmap1=mpl.colormaps['bwr']
cmap2=mpl.colormaps['viridis']
#
# book keeping on months and number of days per month in a standard year
dayspermonth=[31,28,31,30,31,30,31,31,30,31,30,31]
monthstring=['january',
             'february',
             'march',
             'april',
             'may',
             'june',
             'july',
             'august',
             'september',
             'october',
             'november',
             'december']
#
# check if it is a leap year
#
isleap=current_year%4
if isleap==0:
    dayspermonth[1]=29
#
string_year=str(current_year)
if current_month > 9:
    string_month=str(current_month)
else:
    string_month='0'+str(current_month)
#
# define a loop in time
#
current_day=atime.day
if current_day > 9:
    string_day=str(current_day)
else:
    string_day='0'+str(current_day)
io=0
# define start time so we can see how long this takes to run
tic=time.time()
#
atime=dt.datetime(current_year,current_month,atime.day)
# load the data
[timearray,temparray,ugeoarray,sfctemp,lat,lon,lat_v,lon_v,lat_r,lon_r]=wcof_load_s3_synchro_fix(atime)
alat=(lat_v[:,0:-1]+lat_v[:,1:])/2
alon=(lon_v[:,0:-1]+lon_v[:,1:])/2
toc=time.time()
print(toc-tic)
temparray=temparray*24*60*60 # convert from m/s to m/day
isize=temparray.shape
mm=isize[0]
nmap=np.arange(0,mm)
# generated the various maps
for i in nmap:
    if i < 10:
        istring='0'+str(i)
    else:
        istring=str(i)
    ts=string_year+'/'+string_month+'/'+string_day+' hours into forecast '+str(i)
    fig,axs=plt.subplots(1,3,subplot_kw={'projection': ccrs.PlateCarree()},figsize=(16,8))
    zw=np.arange(-12,13,1)
    thefig=axs[0].contourf(alon,alat,temparray[i,:,:],levels=zw,cmap=cmap1)
    g1=axs[0].gridlines(draw_labels=True)
    axs[0].coastlines('10m')
    axs[0].add_feature(cf.NaturalEarthFeature('physical','land','10m',edgecolor='face',facecolor='#808080'))
    g1.top_labels=False
    g1.right_labels=False
    axs[0].set_xlim(-123,-121.5)
    axs[0].set_ylim(36,37.5)
    g1.xlocator=mticker.FixedLocator([-123,-122.5,-122,-121.5])
    g1.ylocator=mticker.FixedLocator([36,36.5,37,37.5])
    divider=make_axes_locatable(axs[0])
    ax_cb=divider.new_horizontal(size='5%',pad=0.1,axes_class=plt.Axes)
    fig.add_axes(ax_cb)
    plt.colorbar(thefig,cax=ax_cb)
    axs[0].title.set_text('w Ekman (m/day)')
    #
    zl=np.arange(-0.5,0.51,0.01)
    thefig2=axs[1].contourf(lon_v,lat_v,ugeoarray[i,:,:],levels=zl,cmap=cmap1)
    g2=axs[1].gridlines(draw_labels=True)
    axs[1].coastlines('10m')
    axs[1].add_feature(cf.NaturalEarthFeature('physical','land','10m',edgecolor='face',facecolor='#808080'))
    g2.top_labels=False
    g2.right_labels=False
    g2.left_labels=False
    axs[1].set_xlim(-123,-121.5)
    axs[1].set_ylim(36,37.5)
    g2.xlocator=mticker.FixedLocator([-123,-122.5,-122,-121.5])
    g2.ylocator=mticker.FixedLocator([36,36.5,37,37.5])
    divider2=make_axes_locatable(axs[1])
    ax_db=divider2.new_horizontal(size='5%',pad=0.1,axes_class=plt.Axes)
    fig.add_axes(ax_db)
    plt.colorbar(thefig2,cax=ax_db)
    axs[1].title.set_text('u Geostrophic (m/s)')
    xt=timearray[i]
    txr=pd.to_datetime(str(xt))
    dstr=txr.strftime('%Y-%m-%d %H:%M')
    # set up the super title relative to subplots
    fig.suptitle(dstr,fontsize=25,y=0.8)
    #
    thefig3=axs[2].contourf(lon_r,lat_r,sfctemp[i,:,:],levels=[10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5],cmap=cmap2)
    g3=axs[2].gridlines(draw_labels=True)
    axs[2].coastlines('10m')
    axs[2].add_feature(cf.NaturalEarthFeature('physical','land','10m',edgecolor='face',facecolor='#808080'))
    g3.top_labels=False
    g3.right_labels=False
    g3.left_labels=False
    axs[2].set_xlim(-123,-121.5)
    axs[2].set_ylim(36,37.5)
    g3.xlocator=mticker.FixedLocator([-123,-122.5,-122,-121.5])
    g3.ylocator=mticker.FixedLocator([36,36.5,37,37.5])
    divider3=make_axes_locatable(axs[2])
    ax_eb=divider3.new_horizontal(size='5%',pad=0.1,axes_class=plt.Axes)
    fig.add_axes(ax_eb)
    plt.colorbar(thefig3,cax=ax_eb)
    axs[2].title.set_text('SST ($^\circ$C)')
    plt.savefig('/home/flbahr/heat_content/upwell_test_'+istring+'.png',dpi=300,bbox_inches='tight',pad_inches=0.25)
    plt.clf()
    plt.close()
import xarray as xr
import numpy as np
import scipy.io
from scipy import integrate
from scipy.interpolate import griddata
import datetime as dt
import time, scipy.io
from wcof_load_s3_synchro30day import wcof_load_s3_synchro30day
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
# This code is to try and deal with issues arrising from NOAA server errors.  I'm having too many to keep the code up and running.
# These errors are out of my control.  So I have to build code to handle these faults and try to make up for them.
#
# Weird Bug here, but make sure to run this first
#import salem
#from shapely import geometry
# grab some boundary information for possible use later?
#sanctuary_outline= salem.read_shapefile('/home/flbahr/heat_content/shapefiles/USMaritimeLimitsAndBoundariesSHP/USMaritimeLimitsNBoundaries.shp')
#sanctuary_outline.crs = 'epsg:4326'
#eez_shape = sanctuary_outline[(sanctuary_outline['REGION'] == "Pacific Coast") & (sanctuary_outline['EEZ'])]
#bbox = ((eez_shape['max_y'].max(),eez_shape['min_y'].min()),(eez_shape['max_x'].max(),eez_shape['min_x'].min()))
#geom = geometry.box(minx=bbox[1][1],maxx=bbox[1][0],miny=bbox[0][1],maxy=bbox[0][0])
#
# Get latitude and longitude that defines the model domain.  Since the THREDDS server at UCSC is down for the moment working to get at the code.
#
# for synchro we don't care about 10km lat and lon we want the 4 km data
#roms_ds=xr.open_dataset('/home/flbahr/heat_content/WCOFS_SST_2022.nc',decode_cf=True) #different size lat and lon, this may be what we need before truncating?
#roms_temp_latitudeUCSC =roms_ds['lat']
#roms_temp_longitudeUCSC=roms_ds['lon']
#[mx,my]=np.meshgrid(roms_temp_longitudeUCSC,roms_temp_latitudeUCSC)
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
#thedays=np.arange(atime.day,-1,-1)
io=0
# define start time so we can see how long this takes to run
tic=time.time()
#
atime=dt.datetime(current_year,current_month,atime.day)
#pdb.set_trace()
#
#for offset in thedays:
#    print(offset)
##    try:
#[timearray,temparray,lat,lon]=wcof_load_s3_synchro(atime)
print(atime)
[timearray,temparray,ugeoarray,sfctemp,lat,lon,lat_v,lon_v,lat_r,lon_r]=wcof_load_s3_synchro30day(atime)
alat=(lat_v[:,0:-1]+lat_v[:,1:])/2
alon=(lon_v[:,0:-1]+lon_v[:,1:])/2
##        #[timearray,temparray]=wcof_load_s3(atime,offset,24,mx,my)
##        if io==0:
##            bigtime=timearray
##            bigtemp=np.expand_dims(temparray,axis=0)
##            io=1
##        else:
##            bigtime=np.append(bigtime,timearray)
##            tmptmp=np.expand_dims(temparray,axis=0)
##            bigtemp=np.vstack((bigtemp,tmptmp))
##    except:
##        print('failed for this date\n')
#        pass # failed to get data for this date
toc=time.time()
print(toc-tic)
temparray=temparray*24*60*60 # convert from m/s to m/day
#pdb.set_trace()
isize=temparray.shape
mm=isize[0]
nmap=np.arange(0,mm)
#nmap=np.arange(0,10)
#pdb.set_trace()
#mercator_crs=ccrs.Mercator()

for i in nmap:
    if i < 10:
        istring='00'+str(i)
    else:
        if i < 100:
            istring='0'+str(i)
        else:
            istring=str(i)
    ts=string_year+'/'+string_month+'/'+string_day+' hours into forecast '+str(i)
    #ax1=plt.subplot(3,1,1)
    fig,axs=plt.subplots(1,3,subplot_kw={'projection': ccrs.PlateCarree()},figsize=(16,8))
#    thefig=axs[0].contourf(lon,lat,temparray[i,:,:],levels=[-2.5,-2.0,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5],cmap=cmap1)
    #thefig=axs[0].contourf(alon,alat,temparray[i,:,:],levels=[-2.5,-2.0,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5],cmap=cmap1)
    zw=np.arange(-12,13,1)
    thefig=axs[0].contourf(alon,alat,temparray[i,:,:],levels=zw,cmap=cmap1)
    g1=axs[0].gridlines(draw_labels=True)
    axs[0].coastlines('10m')
    axs[0].add_feature(cf.NaturalEarthFeature('physical','land','10m',edgecolor='face',facecolor='#808080'))
    g1.top_labels=False
    g1.right_labels=False
#    g1.xlabels_top=False
#    g1.ylabels_left=False
    axs[0].set_xlim(-123,-121.5)
    axs[0].set_ylim(36,37.5)
    g1.xlocator=mticker.FixedLocator([-123,-122.5,-122,-121.5])
    g1.ylocator=mticker.FixedLocator([36,36.5,37,37.5])
    divider=make_axes_locatable(axs[0])
    ax_cb=divider.new_horizontal(size='5%',pad=0.1,axes_class=plt.Axes)
    #ax_cb=divider.new_horizontal(size='5%',pad=0.05,axes_class=plt.Axes)
    fig.add_axes(ax_cb)
    plt.colorbar(thefig,cax=ax_cb)
    axs[0].title.set_text('w Ekman (m/day)')
    #axs[0].title.set_text('w Ekman (m^2/s)')
    #axs[0].title.set_text('U Ekman Transport (m^2/s)')
    #
    #
    #
    zl=np.arange(-0.5,0.51,0.01)
    thefig2=axs[1].contourf(lon_v,lat_v,ugeoarray[i,:,:],levels=zl,cmap=cmap1)
    #thefig2=axs[1].contourf(lon,lat,ugeoarray[i,:,:],levels=[-1.0,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1],cmap=cmap1)
    #thefig2=axs[1].contourf(lon,lat,ugeoarray[i,:,:],levels=[-1.0,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1],cmap=cmap1)
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
    #axs[1].title.set_text('w Geostrophic (s)')
    axs[1].title.set_text('u Geostrophic (m/s)')
    xt=timearray[i]
    txr=pd.to_datetime(str(xt))
    dstr=txr.strftime('%Y-%m-%d %H:%M')
    fig.suptitle(dstr,fontsize=25,y=0.8)
    #plt.xlabel(dstr)
   #
   #
   #
    thefig3=axs[2].contourf(lon_r,lat_r,sfctemp[i,:,:],levels=[10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5,19,19.5,20,20.5],cmap=cmap2)
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
    axs[2].title.set_text(r'SST ($^\circ$C)')
    ##plt.subplots_adjust(top=0.85)
    ##plt.savefig('/home/flbahr/heat_content/upwell_test_'+istring+'.png',dpi=300,bbox_inches='tight',pad_inches=0.25)
    # uncomment when the code is fixed
    plt.savefig('c:/upwelling/figs_for_upwell/upwell_test_'+istring+'.png',dpi=300,bbox_inches='tight',pad_inches=0.25)
    ##pdb.set_trace()
    plt.clf()
    plt.close()


##for i in nmap:
##    #thefig=plt.pcolor(lon,lat,temparray[i,:,:],vmin=-0.00002,vmax=0.00005)
##    #thefig=plt.pcolor(lon,lat,temparray[i,:,:],vmin=-1,vmax=0.5)
##    thefig=plt.contourf(lon,lat,np.log(np.abs(temparray[i,:,:])),np.arange(-6,2,0.5))
##    #thefig=plt.pcolor(lon,lat,np.log(np.abs(temparray[i,:,:])),vmin=-6,vmax=0)
##    thefig.axes.set_xlim(-123,-121.5)
##    thefig.axes.set_ylim(36,37.5)
##    plt.colorbar()
##    if i < 10:
##        istring='0'+str(i)
##    else:
##        istring=str(i)
##    #ts=string_year+'/'+string_month+' hours into forecast '+str(i*3+3)
##    ts=string_year+'/'+string_month+'/'+string_day+' hours into forecast '+str(i)
##    plt.title(ts)
##    plt.savefig('/home/flbahr/heat_content/upwell_fig_'+istring+'.png',dpi=300,bbox_inches='tight',pad_inches=0.25)
##    plt.clf()
###

#pfile=open('/home/flbahr/heat_content/wcofs_'+monthstring[current_month-1]+'_'+string_year+'.p','wb')
#pobj=[bigtime,bigtemp]
#pickle.dump(pobj,pfile)
# Have to close pickle file for it to write EOF and thus be readable.  If we don't do this
# the file has the data but is unreadable and just takes up space
#pfile.close()

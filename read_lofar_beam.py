# plots dynamic spectra from h5 files
# To run:
#       $ python read_lofar_beam.py filename start-minute end-minute
# Inputs:
#       filename - any LOFAR dynamic spectrum HDF5 file
# Optional:
#       start-minute
#       end_minute
#       -- only specify if small portions of data need to be plotted
#           after initial run
#
# created by Diana Morosan: morosand@tcd.ie
# Please acknowledge the use of this code


from pylab import figure,imshow,xlabel,ylabel,title,close,colorbar
import h5py
import datetime
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib import dates
import sys


# extracting time and frequency information from h5 file
file = str(sys.argv[1])
f = h5py.File( file, 'r' )
data = f[ 'SUB_ARRAY_POINTING_000/BEAM_'+str(list(f.attrs.values())[6])[16:19]+'/STOKES_'+str(list(f.attrs.values())[6])[21:22] ][:,:]

t_lines = data.shape[0]
f_lines = data.shape[1]

total_time = f.attrs.values()[22] #in seconds
print( 'Total integration time in seconds:', total_time )

if len(sys.argv)>2:
    start_min = int(sys.argv[2])
    end_min = int(sys.argv[3])
else:
    start_min = 0.
    end_min = total_time/60.

start_time_line = int( (start_min/(total_time/60.))*t_lines )
end_time_line = int( (end_min/(total_time/60.))*t_lines )

start_freq = list(f.attrs.values())[30] #in MHz
end_freq = list(f.attrs.values())[8] 

t_resolution = (total_time/t_lines)*1000. #in milliseconds
f_resolution = (end_freq - start_freq)/f_lines #in MHz


# extracting time information
time = list(f.attrs.values())[12]
year = int(str(time)[0:4])
month = int(str(time)[5:7])
day = int(str(time)[8:10])
hour = int(str(time)[11:13])
minute = int(str(time)[14:16])
second = int(str(time)[17:19])

t = datetime.datetime(year, month, day, hour, minute, second)
start_time = t + datetime.timedelta( minutes = start_min )
end_time = t + datetime.timedelta( minutes = end_min )
print( 'Start time of observation UT:', str(start_time.date()) + ' ' + str(start_time.time()) )

#plotting dynamic spectrum for specified times
data = f['SUB_ARRAY_POINTING_000/BEAM_'+str(f.attrs.values()[6])[16:19]+
         '/STOKES_'+str(f.attrs.values()[6])[21:22]][start_time_line:end_time_line,:]

#normalizing frequency channel responses
for sb in xrange(data.shape[1]):
    data[:,sb] = data[:,sb]/np.median(data[:,sb])
data = np.transpose(data)

#plot
plt.figure(1,figsize=(18,9))
imshow(data,vmin=1.00,vmax=1.4,aspect='auto',
       extent=(start_time,end_time,end_freq,start_freq))
xlabel('Start Time: ' + str( start_time.date() ) + ' ' + str(start_time.time()), fontsize = 16)
ylabel('Frequency (MHz)', fontsize = 16)
title('LOFAR Dynamic Spectrum', fontsize = 16)
ax = plt.gca()
ax.xaxis_date()
ax.xaxis.set_major_locator(dates.MinuteLocator())
ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
ax.xaxis.set_major_locator( MaxNLocator(nbins = 6) )
plt.savefig('LOFAR_dynamic_spectrum.png')
plt.show()
close()


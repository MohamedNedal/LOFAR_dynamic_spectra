# plots dynamic spectra from h5 files
# To run:
#       $ python read_lofar_beam.py filename start-minute end-minute
# Inputs:
#       filename - any LOFAR dynamic spectrum HDF5 file
#       --> make sure code is in the same folder as both .h5
#          and .raw data files
# Optional:
#       start-minute
#       end_minute
#       -- only specify if small portions of data need to be plotted
#
# created by Diana Morosan: morosand@tcd.ie
# Please acknowledge the use of this code
#
# Compatible with Python 3.6



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
beam = f.attrs['FILENAME'].decode("utf-8")[16:19]
stokes = f.attrs['FILENAME'].decode("utf-8")[21:22]
sap = f.attrs['FILENAME'].decode("utf-8")[11:14]

data = f[ 'SUB_ARRAY_POINTING_'+sap+'/BEAM_'+beam+'/STOKES_'+stokes ]

t_lines = data.shape[0]
f_lines = data.shape[1]

total_time = f.attrs['TOTAL_INTEGRATION_TIME'] #in seconds
print( 'Total integration time in seconds:', total_time )

if len(sys.argv)>2:
    start_min = int(sys.argv[2])
    end_min = int(sys.argv[3])
else:
    start_min = 0.
    end_min = total_time/60.

start_time_line = int( (start_min/(total_time/60.))*t_lines )
end_time_line = int( (end_min/(total_time/60.))*t_lines )

start_freq = f.attrs['OBSERVATION_FREQUENCY_MIN'] #in MHz
end_freq = f.attrs['OBSERVATION_FREQUENCY_MAX']

t_resolution = (total_time/t_lines)*1000. #in milliseconds
f_resolution = (end_freq - start_freq)/f_lines #in MHz


# extracting time information
#
time = f.attrs['OBSERVATION_START_UTC'].decode("utf-8")
t = datetime.datetime.strptime( time, '%Y-%m-%dT%H:%M:%S.%f000Z' )
print( 'Start time of observation UT:', str(t.date()) + ' ' + str(t.time()) )

start_time = t + datetime.timedelta( minutes = start_min )
end_time = t + datetime.timedelta( minutes = end_min )
print( 'Start time of dynamic spectrum UT:', str(start_time.date()) + ' ' + str(start_time.time()) )

# extracting data for specified times
#
data = f[ 'SUB_ARRAY_POINTING_'+sap+'/BEAM_'+beam+'/STOKES_'+stokes ][start_time_line:end_time_line,:]

# normalizing frequency channel responses
#
for sb in range(data.shape[1]):
    data[:,sb] = data[:,sb]/np.median(data[:,sb])
data = np.transpose(data)

# plot dynamic spectrum
#
plt.figure(1,figsize=(16,7))
imshow(data,vmin=0.90,vmax=1.80,aspect='auto',
       extent=(dates.date2num(start_time),dates.date2num(end_time),end_freq,start_freq))
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


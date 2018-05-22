# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 16:47:42 2015

@author: Adrian Sinclair
Photon-Counting project: python script whose purpose is to load photon_counter bof file and program fpga with bof file.
"""
import corr
import time
import matplotlib.pyplot as plt
import struct
import numpy as np

katcp_port=7147
roach = '192.168.40.56' 
fpga = corr.katcp_wrapper.FpgaClient(roach, katcp_port, timeout=10)
time.sleep(1)
if (fpga.is_connected() == True):
    print 'Connected to the FPGA '
else:
    print 'Not connected to the FPGA'

#bitstream='coincidence_counter_2015_Aug_18_1033.bof' #creating string named bitstream for bof file
#fpga.upload_bof(bitstream,3000) # upload bof file onto the fpga
#fpga.progdev('coincidence_counter_2015_Aug_18_1033.bof') #Now that the bof file is on the fpga program the fpga with corresponding bof file

#print 'Bof file uploaded...'
path='/home/user1/Desktop/adrian/psu_therm/'
filename=raw_input('enter file name: ')
period=raw_input('enter counting period in number of Tclk\'s:')
fpga.write_int('period',int(period))
bramFilltime=int(period)*(1/(200e06))*32768
print 'The time to fill the bram is:',bramFilltime,' seconds'
bram_fills=raw_input('enter number of 32768 measurement chunks taken:')
data_file=open(path+filename+'.data','w')
data_file.write('#Counts \n')

i = 0;
fpga.write_int('reset',0)
fpga.write_int('reset',1)
fpga.write_int('reset',0)
data=struct.unpack('>32768L',fpga.read('counts',131072))

while (i < int(bram_fills)):
    valid=fpga.read_int('valid')
    if valid==1:
        data=struct.unpack('>32768L',fpga.read('counts',131072))

        #fake_data=data
        for k in range(len(data)):
            data_file.write(str(float(data[k]))+'\n')
            #data_file.write(str(float(data[k]))+'|'+str(fake_data[k])+'\n')
        #data_file.write(str(data))
        fpga.write_int('reset',0)
        fpga.write_int('reset',1)
        fpga.write_int('reset',0)
        i=i+1
    
data_file.close()

output_data=np.loadtxt(path+filename+'.data',skiprows=1)
plt.clf()
plt.hist(output_data, bins=np.arange(0,100,1),normed=1,histtype='step',align='left')
plt.show()

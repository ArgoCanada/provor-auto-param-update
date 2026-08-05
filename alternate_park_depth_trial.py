#!/usr/env/python

import sys
import ftplib
from io import BytesIO

import pandas as pd
import provorpy as ppy

update_from_command_file = True
update_from_user_list = False

#------------------------------------------------------------------------------
# connect to DFO FTP server
#------------------------------------------------------------------------------

url = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
ftp = ftplib.FTP(url, user=username, passwd=password)
ct = pd.Timestamp('now', tz='utc')
imei_numbers = ftp.nlst()
logfile = 'log/auto-update-log.log'

alternating_parking_floats = ['300125062035430']

for imei in alternating_parking_floats:
    # get most recent profile time for each float
    files = ftp.nlst(f'{imei}/*technical*.txt')
    r = BytesIO()
    ftp.retrbinary(f'RETR {files[-1]}', r.write)
    last_profile_time = ppy.read_tech_file_time(r)
    cycle = int(files[-1].split('_')[1])
    print(imei, cycle, last_profile_time)
    within_last_day = ct - last_profile_time < pd.Timedelta(hours=26)
    last_command_time = ppy.file_time(ftp.nlst(f'{imei}/*_command*.txt'), kind='cts5')
    recent_command = abs(last_command_time - last_profile_time) < pd.Timedelta(hours=12)
    param_update = within_last_day

    if True:
        update = True
        print(f'Updating {imei}...')

        filename = f'commands/{ct.year}{ct.month}{ct.day}_{imei}_auto_park_update_cmd.txt'
        if cycle % 2 == 0:
            old_depth = 1000
            new_depth = 2000
            print('!param-pattern_01-1:2000')
            print('!param-pattern_01-2:2000')
            print('!param-sensor_04-49:1980')
        else:
            old_depth = 2000
            new_depth = 1000
            print('!param-pattern_01-1:1000')
            print('!param-pattern_01-2:1000')
            print('!param-sensor_04-49:980')
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

# list of any floats to exclude - possibly because manual command was uploaded
imei_exclude = []

cts5_floats = [
    '300125062902880', '300125062426150', '300125062423120',
    '300125062031400', '300125062035430', '300534060123910',
    '300125062907910', '300125062909910', '300125063319510',
    '300125063310200', '300125063315260', '300125063318510',
    '300125063419060', '300125063414050', '300125063413300',
    '300125063217740', '300125063211730', '300125063213730',
    '300125063215730', '300125063415280', '300125063313520',
    '300125063411300', '300125063318200', '300125063217730',
    '300125063128670', '300125063212730', '300125063712060',
]

imei_numbers = list(set(imei_numbers) - set(imei_exclude) - set(cts5_floats))

#------------------------------------------------------------------------------
# check timing info, previous commands - CTS4 floats
#------------------------------------------------------------------------------

update = False
for imei in imei_numbers:

    # get most recent profile time for each float
    last_profile_time = ppy.file_time(ftp.nlst(f'{imei}/*.bin'))
    print(imei, last_profile_time)
    within_last_day = ct - last_profile_time < pd.Timedelta(hours=26)
    print(ftp.nlst(f'{imei}/*cmd.txt'))
    last_command_time = ppy.file_time(ftp.nlst(f'{imei}/*cmd.txt'))
    recent_command = abs(last_command_time - last_profile_time) < pd.Timedelta(hours=12)
    param_update = within_last_day

    if param_update:

        update = True
        print(f'Updating {imei}...')

        if update_from_command_file:
            # check time of command file - make sure it corresponds to this profile
            # effectively this means that the process must be manually started with 
            # human uploading a command file. Note sending PV=0 to tested floats could
            # cause an exception to this rule
            last_command_file = ftp.nlst(f'{imei}/*.txt')[-1]
            r = BytesIO()
            ftp.retrbinary(f'RETR {last_command_file}', r.write)
            df = ppy.read_cmd_response(r)
            new_time = df.Value.loc['PM 4'] - 5 if 'PM 4' in df.index else last_profile_time.hour - 5
            new_time = new_time + 24 if new_time < 0 else new_time
        elif update_from_user_list: # this does not work right now - need a way to do it per float?   
            df = pd.read_csv(f'{imei}_time_list.csv')
            new_time = df.param.iloc[0]
            df.iloc[:-1] = df.iloc[1:]
            df.iloc[-1] = new_time
            df.to_csv('time_list.csv')
        else:
            raise ValueError('No source for new time selected')
    
        filename = f'commands/{ct.year:04d}{ct.month:02d}{ct.day:02d}_{imei}_auto_time_update_cmd.txt'
        with open(filename, 'w') as f:
            f.write(f'!PM 4 {new_time:d}\r\n')
            f.write('!PC 0 1 4 2\r\n')
        
        with open(filename, 'rb') as f:
            ftp.storbinary(f'STOR {imei}/remote/RUDICS_cmd.txt', f)
        
        with open(logfile, 'a') as f:
            old_time = df.Value.loc['PM 4'] if 'PM 4' in df.index else last_profile_time.hour
            f.write(f'\n[{ct.year:04d}-{ct.month:02d}-{ct.day:02d}] Updated {imei} surfacing time from {old_time} to {new_time}')

#------------------------------------------------------------------------------
# alternate parking depth - specific CTS5 floats
#------------------------------------------------------------------------------

alternating_parking_floats = [
    '300125062031400',
    '300125062035430',
    '300125062423120',
    '300125062426150',
    '300125062902880',
    '300125062907910',
    '300125062909910',
]

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

    if param_update:
        update = True
        print(f'Updating {imei}...')

        filename = f'commands/{ct.year:04d}{ct.month:02d}{ct.day:02d}_{imei}_auto_park_update_cmd.txt'
        with open(filename, 'w') as f:
            if cycle % 2 == 0:
                old_depth = 1000
                new_depth = 2000
                f.write('!param-pattern_01-1:2000\r\n')
                f.write('!param-pattern_01-2:2000\r\n')
                f.write('!param-sensor_04-14:10\r\n')
                f.write('!param-sensor_04-23:30\r\n')
                f.write('!param-sensor_04-32:30\r\n')
                f.write('!param-sensor_04-41:2\r\n')
                f.write('!param-sensor_04-49:1980\r\n')
            else:
                old_depth = 2000
                new_depth = 1000
                f.write('!param-pattern_01-1:1000\r\n')
                f.write('!param-pattern_01-2:1000\r\n')
                f.write('!param-sensor_04-14:10\r\n')
                f.write('!param-sensor_04-23:30\r\n')
                f.write('!param-sensor_04-32:30\r\n')
                f.write('!param-sensor_04-41:2\r\n')
                f.write('!param-sensor_04-49:980\r\n')
        
        with open(filename, 'rb') as f:
            ftp.storbinary(f'STOR {imei}/remote/_command.txt', f)
        
        with open(logfile, 'a') as f:
            f.write(f'\n[{ct.year:04d}-{ct.month:02d}-{ct.day:02d}] Updated {imei} park depth from {old_depth} to {new_depth}')
            
if not update:
    with open(logfile, 'a') as f:
        f.write(f'\n[{ct.year:04d}-{ct.month:02d}-{ct.day:02d}] No floats to be updated today')

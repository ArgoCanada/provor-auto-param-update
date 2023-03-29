
from warnings import warn
import copy
import pandas as pd

from . import configure

def get_ftp_info():
    config = configure.read_config()
    cfg_copy = copy.deepcopy(config)

    for k in ['ftp_url', 'ftp_username']:
        if k not in config.keys():
            ks = k.replace('ftp_', '')
            warn(f'FTP {ks} not in .config file, returning blank string. Add it by running provorpy.configure.configure({k}=...')
            cfg_copy[k] = ''

    url = cfg_copy['ftp_url']
    user = cfg_copy['ftp_username']

    return url, user

def file_time(file):

    if hasattr(file, '__iter__') and len(file) == 0:
        return pd.Timestamp('1950-01-01', tz='utc')
    f = file[-1] if hasattr(file, '__iter__') else file
    f = file[-2] if f.split('/')[-1] == 'RUDICS_cmd.txt' else f

    date_string = f.split('/')[-1].split('_')[0]
    time_string = f.split('/')[-1].split('_')[1]

    return pd.Timestamp(
        year=int(f'20{date_string[:2]}'), 
        month=int(date_string[2:4]), 
        day=int(date_string[4:]),
        hour=int(time_string[:2]), 
        minute=int(time_string[2:4]), 
        second=int(time_string[4:]), tz='utc')

def read_cmd_response(file):

    params = []
    vals = []

    f = open(file, 'r') if not hasattr(file, 'read') else file
    f.seek(0)

    for line in f:
        line = line.decode() if type(line) is bytes else line
        line = line.split('-')[0].strip()
        if line[0] == '!':
            l = line[1:]
            params.append(' '.join(l.split(' ')[:-1]))
            vals.append(int(l.split(' ')[-1]))
    
    df = pd.DataFrame(data=dict(Value=vals), index=params)

    return df
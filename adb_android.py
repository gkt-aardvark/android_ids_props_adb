from subprocess import call, check_output
from datetime import datetime as dt
import re
import os

'''for the pixel 3 xl on android 11 but will work on others maybe'''

logfile = 'adb_data.log'

if not os.path.exists(logfile):
    with open(logfile, 'w') as f:
        f.write('Log Entries for ADB data pull:\n')

def logentry (entry):
    '''yeah, yeah, yeah, whatever'''
    current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(logfile, 'a') as f:
        line = f'{current_time} - {entry}\n'
        f.write(line)

def format_parcel(parcel):
    '''cleans up output of the service call iphonesubinfo'''
    
    data = parcel.replace(b'.', b'')
    regex = b'\'(.*?)\''
    value = b"".join(re.findall(regex, data)).decode('ascii').strip()
    return value

def get_ids():
    '''wrote it this way because different phones have different values
    that have to be called in the iphonesubinfo, some of which don't
    overlap with the values from other phones, so... I will just get
    all of them, eliminate the ones that aren't numbers, dedup them
    and id them by their characteristics'''
    
    parcels = []
    for i in range(1, 23): #this seems to be the possible range
        val = format_parcel(check_output(f'adb shell service call iphonesubinfo {i}', shell=True))
        parcels.append(val)
    values = list(set(parcels))
    values = [x for x in values if x[1:].isdigit() and len(x) > 4]

    imei = imsi = iccid = msisdn = vmn = ''
    ids = {}
    for val in values:
        if len(val) >= 18 and val.startswith('89'):
            ids.update({'ICCID': val})
        elif val.startswith('+'):
            ids.update({'Voicemail': val})
        elif len(val) == 15 and (val.startswith('35') \
                                or val.startswith('99') \
                                or val.startswith('86') \
                                or val.startswith('01')):
            ids.update({'IMEI': val})
        elif len(val) == 15:
            ids.update({'IMSI': val})
        else:
            ids.update({'MSISDN': val})
    
    return ids

def get_prop():
    prop_list = [   
                'ro.serialno',
                'ro.product.brand',
                'ro.product.device',
                'ro.product.brand',
                'ro.product.manufacturer',
                'ro.product.model',
                'ro.build.date',
                'ro.build.date.utc',
                'ro.build.description', 
                'ro.build.fingerprint',
                'ro.board.platform',
                'ro.build.version.release',
                'ro.build.version.release_or_codename',
                'ro.secure',
                'ro.build.product',
                'gsm.operator.alpha',
                'gsm.operator.iso-country',
                'gsm.sim.operator.alpha',
                'gsm.sim.operator.iso-country',
                'gsm.sim.operator.numeric',
                'ro.build.version.security_patch',
                ]
    props = {prop: check_output(f'adb shell getprop {prop}', shell=True).strip().decode('utf-8') for prop in prop_list}
    return props

if __name__ == '__main__':
    ids = get_ids()
    print ('\n'.join([f'{key}: {ids.get(key)}' for key in ids]))
    props = get_prop()
    print ('\n'.join([f'{key}: {props.get(key)}' for key in props]))

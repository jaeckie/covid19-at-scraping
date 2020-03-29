# -*- coding: utf-8 -*-

import re
import os
import pandas as pd
import urllib.request

from datetime import datetime

def jsdata2dict(jsdata):
    """
    ----------
    jsdata : string
        raw string containing the data.

    Returns
    -------
    jsdict : dictionary
        contains key-value pairs of respective data.

    """
    jsdict = {}
    i = 0
    for entry in jsdata.split(','):
        if (i % 2) == 0:
            key = entry.split(':')[-1].replace('"', '')
        else:
            jsdict[key] = float(entry.split(':')[-1].replace('}', '')) 
        i += 1
    return jsdict


if __name__ == '__main__':
    print('current working-dir: %s' % os.getcwd())
    base_url = 'https://info.gesundheitsministerium.at/'
    print('scraping data from: %s' % base_url)
    user_agent = "user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
    
    url = 'https://info.gesundheitsministerium.at/data/SimpleData.js'
    request = urllib.request.Request(url, data=None,
                            headers={'User-Agent' : user_agent})
    resource = urllib.request.urlopen(request)
    data = resource.read().decode('utf-8')
    #data = str(urllib.request.urlopen(request).read())
    
    # datetime
    # results between " "
    r0 = re.compile(r'".*"') # r'\d{2}.d{2}.d{4}'
    s0 = r0.search(data)
    datetime_string = s0.group().replace('"', '')
    dt = datetime.strptime(datetime_string, '%d.%m.%Y %H:%M.%S')
    print('last data update: %s' % dt)
    
    # TODO: compare datatime with current pandas dataframe   
    
    #r1 = re.compile('Erkrankungen = %d+;')
    r1 = re.compile(r'\d+;')
    s1 = r1.search(data)
    infections = int(s1.group().replace(';', ''))

    # urls for structured data
    urls = {'altersverteilung' : 'https://info.gesundheitsministerium.at/data/Altersverteilung.js',
        'bezirke' : 'https://info.gesundheitsministerium.at/data/Bezirke.js',
        'bundesland' : 'https://info.gesundheitsministerium.at/data/Bundesland.js' ,
        'geschlechtsvert' : 'https://info.gesundheitsministerium.at/data/Geschlechtsverteilung.js',}
    
    data_dict_raw = {}  
    df_dict = {}
    # content of dp%s = [ x ]
    p = re.compile(r'\{.*\}')
    
    for key, val in urls.items():
       request = urllib.request.Request(val, data=None,
                            headers={'User-Agent' : user_agent})
       resource = urllib.request.urlopen(request)
       data = resource.read().decode('utf-8')
       data_dict_raw[key] = data
       
       s = p.search(data)
       data_str = s.group()
       res_dict = jsdata2dict(data_str)

       # write dataframe for all dicts, add total cases and store
       df = pd.DataFrame.from_dict([res_dict])
       df['Zeit'] = dt
       df.set_index('Zeit', inplace=True)
       df['Erkrankungen_Sum'] = infections
       df_dict[key] = df
       filename = 'covid19-at-%s.csv' % key
       if not os.path.isfile(filename):
           df.to_csv(filename, encoding='utf-8')
       else:
          df.to_csv(filename, encoding='utf-8', mode='a', header=False) 
        
    print('data saved')
   
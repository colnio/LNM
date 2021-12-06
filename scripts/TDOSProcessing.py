from os import listdir
from os.path import isfile, join
import pandas as pd
#import math
import numpy as np
import re
from matplotlib import cm
import matplotlib.pyplot as plt
import seaborn as sns 
import sys 

def interp(df, new_index):
    """Return a new DataFrame with all columns values interpolated
    to the new_index values."""
    df_out = pd.DataFrame(index=new_index)
    df_out.index.name = df.index.name

    for colname, col in df.iteritems():
        df_out[colname] = np.interp(new_index, df.index, col)

    return df_out

mypath = '2021-12-06_m11_d4_6K_copy'
file_list = [[]]

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
#print(onlyfiles[0])
#sys.exit()
for file in onlyfiles:
    if '.dat' in file:
        file_parts = file.rsplit('_')
        file_parts[2] = file_parts[2][2:].replace(',','.')
        file_parts.append(file)
        file_list.append(file_parts)
        #print(file_parts)
        #sys.exit()

file_list = file_list[1:][:]

file_df = pd.DataFrame(file_list, columns=['Type','Range','Vg','Empty','Cont','Temp', 'Field', 'Serie', 'FullName'])
file_df['Vg'] = pd.to_numeric(file_df['Vg'])
file_df = file_df.sort_values(by=['Vg', 'Serie'])

Vg_s = file_df['Field'].unique()

full_data = pd.DataFrame()

for Vg in Vg_s:
    new_data = pd.DataFrame()
    for file in file_list:
        data_f = False
        if file[-3] == Vg:
            data_f = file[-1]
            int_data_serie = int(re.search(r'\d+', file[-2])[0])
            if(int_data_serie > 5):
                continue
            data_serie = file[-2]
        if data_f:
            data_f = pd.read_csv(mypath + '/' + data_f, delimiter = '\t', decimal = ',', index_col = 1, names=['dV','Vsd','I','Time','Vg','1','2','3','4'])
            
            data_f = data_f.drop(['1','2','3', '4', 'Vg', 'Time', 'dV'], axis = 1).sort_index()
            #print(file)

            bounds = []
            bounds.append(round(data_f.index[0] * 100)/100.0)
            bounds.append(round(data_f.index[-1] * 100)/100.0)
            bounds = np.linspace(bounds[0], bounds[1], num=1000)
            if new_data.empty:
                new_data = interp(data_f, bounds).rename(columns={"I": data_serie})
            else:
                int_res = interp(data_f, bounds)['I']
                #print(int_res)
                new_data.insert(1, data_serie, int_res)
            #print(new_data)
            #print(file)
    new_data = new_data.mean(axis = 1)\
        .reset_index(name=Vg)
    new_data = new_data.groupby(np.arange(len(new_data))//10).mean()
    if full_data.empty:
        full_data = new_data
    else:
        full_data.insert(len(full_data.columns), Vg, new_data[Vg])
print(full_data)
full_data = full_data.set_index('Vsd')

diff_data = full_data.diff() / 0.00016
diff_data.values[0] = diff_data.values[1]

diff_data.to_csv('2.csv')


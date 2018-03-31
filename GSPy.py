#import zipfile
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import math
#from scipy.interpolate import interp1d
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

#Läser in filer i mappen som denna fil körs från
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
autograf_snd = [f for f in os.listdir(dir_path) if re.match(r'.*\.snd', f, re.I)]
autograf_snd = sorted(autograf_snd)
autograf_prv = [f for f in os.listdir(dir_path) if re.match(r'.*\.prv', f, re.I)]
autograf_prv = sorted(autograf_prv)

#Extraherar data från .snd och skickar tillbaka x (parameter) och y (djup)
def extrct (flnme, l_start, l_end):
    with open(flnme,'r') as data:
        rel_lines = data.readlines()
        rel_lines = rel_lines[l_start:l_end]
        for j in range(0, len(rel_lines)):
            rel_lines[j] = re.findall(r'\S+',rel_lines[j])
            rel_lines[j] = [maybe_float(v) for v in rel_lines[j]]
        y = [item[0] for item in rel_lines]
        x = [item[1] for item in rel_lines]  
    return (x,y)

#Plottar och skriver ut diagram
def pltsnd (x,y,flnme,method) :
    
    y2 = np.linspace(0, math.ceil(max(y)), num=1000, endpoint=True)
    f = interp1d(y, x, kind='linear',bounds_error=False)
    
    x3 = savgol_filter(f(y2), 41, 2, mode='interp')

    plt.plot(x,y,'x')
#    plt.plot(f(y2),y2,'--')
    plt.plot(x3,y2,'-')

    plt.gca().invert_yaxis()
    plt.title(flnme)
    plt.ylabel('Djup [m]')
    plt.ylim([math.ceil(max(y)),0])
    plt.grid(True)
    if method == 'vim':
        plt.xlabel('hv/0.2m')
    elif method == 'slb':
        plt.xlabel('s/0.2m') #sekunder / 0.2 m
    elif method == 'hfa':
        plt.xlabel('slag/0.2m')
    plt.savefig('export/' + flnme + method + '.png', bbox_inches='tight')
    plt.close()
    return

#Konverterar de strängar som går till floats
def maybe_float(sträng):
    try:
        return float(sträng)
    except (ValueError, TypeError):
        return sträng

#Kollar igenom alla .snd-filer och skickar info till extrct och pltsnd, DETTA KÖRS FÖRST
for filnamn in autograf_snd:
    with open(filnamn,'r') as snd_file:
        found = 0
        for i, line in enumerate(snd_file):
            if re.search(r'HFA', line):
                found = 1
                method = 'hfa'
                startline=i+1
            elif re.search(r'SLB', line):
                found = 1
                method = 'slb'
                startline=i+1
            elif re.search(r'VIM', line):
                found = 1
                method = 'vim'
                startline=i+1
            elif re.match(r'\*', line) and found == 1:
                found = 0
                endline = i
                (x,y) = extrct(filnamn,startline,endline)
                pltsnd(x,y,filnamn,method)

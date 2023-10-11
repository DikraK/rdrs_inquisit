# !/usr/bin/python3

import streamlit as st 
import pandas as pd
import numpy as np
import os
from configparser import ConfigParser
import branca

import folium
from folium.plugins import Draw
from streamlit_folium import folium_static

#============================ READ CONFIGURATION
#
config = ConfigParser()
config.read("Configuration.ini")

# caldas statoma
exppath                  = config["EXPPATH"]['statoma_caldas_dir']

# time information
years                    = config["PERIOD"]["timeperiod"].split(',') 
yearfirst                = int(years[0])
yearend                  = int(years[1])

#============================= FUNCTIONS
#%% LOAD DATA
# function to load the data and cache it
@st.cache_data
def load_data(namevar, year, directory):
    # Create an empty DataFrame to store the concatenated data
    data = pd.DataFrame()

    # Loop through the files in the directory
    for filename in os.listdir(directory):
        
        if "SD" in namevar:
            suffixe = f"_statoma_{namevar}_001"
        else:
            suffixe = f"_statoma_{namevar}_000"
        
        if suffixe in filename  and f"{str(year)}" in filename:
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path, delim_whitespace=True, header='infer')  # Load the statoma file
            df = df.iloc[:, 1:3]  # Select the 1st and 2nd columns
            data = pd.concat([data, df], axis=0, ignore_index=True)
        
    return(data)        

#============================ END READ CONFIGURATION

st.write("""
## Number of assimilated stations in CaLDAS over the reanalysis period
""")


year_to_look = st.slider('Select a year', min_value=yearfirst, max_value=yearend)

if 2014 <= year_to_look <= 2016 or 1992 <= year_to_look <= 1994 :
    
    if 2014 <= year_to_look <= 2016:
        name_exp    = "DRS2014A"
    elif 1992 <= year_to_look <= 1994:
        name_exp    = "DRS1992A"
        
    # extract the name of the directory
    dirname         = dict()
    dirname['TT']   = f"{exppath}/{name_exp}/RSAS01TEST/gridpt/mist/statoma/screen/yin"  
    dirname['TD']   = dirname['TT']
    dirname['SD']   = f"{exppath}/{name_exp}/RSAS01TEST/gridpt/mist/statoma/snow/yin" 

    option          = st.selectbox("Variables",("TT", "TD", "SD"))

    # extract the datasets 

    data_var    = load_data(option, year_to_look, dirname[option])

    # group by coordinates
    grouped_var = data_var.groupby(['LAT', 'LON']).size().reset_index(name='count')
    
    grouped_var['LON'] = grouped_var['LON'] -360
    grouped_var['count'][grouped_var['count'] > 365] = 365
    
    # do the map
    colormap = brana.colormap.cm.LinearColormap(colors=['magenta', 'green', 'red'], vmin=0, vmax=365)
 
    m        = folium.Map(location=[45.5, -93.56], zoom_start=2.4)    
    grouped_var.apply(lambda row:folium.Circle(location=[row["LAT"], row["LON"]], 
                                            color=colormap(row['count']), fill=True,  fill_opacity=0.2,
                                            radius=30).add_to(m), axis=1)

    m.add_child(colormap)
    folium.map.LayerControl('topleft', collapsed= False).add_to(m)
    
    folium_static(m)

else:
    
    st.write("""
    ### Currently this RDRS year is not run - only 1992-1994 and 2014-2016 are available
    """)


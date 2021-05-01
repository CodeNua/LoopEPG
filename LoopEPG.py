# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 12:19:43 2021

@author: codenua

LoopEPG
Copyright (C) 2021  CodeNua

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import csv, os
import datetime
from lxml import etree


# Paths to the CSV and XML files
csvProgFile     = "Schedule.csv"
csvChanFile     = "Channel.csv"
xmlOutputFile   = "XMLTV_out.xml"


# Get's current working directory
path = str(os.getcwd())                                 
csvProgPath   = path + '/' + csvProgFile
csvChanPath   = path + '/' + csvChanFile
xmlOutputPath = path + '/' + xmlOutputFile

# ---------------------------------------------------------------------
# Load in the CSVdata from CSV file, create list of dictionaries 
# ---------------------------------------------------------------------
EPGchan = []    # Channel List
EPGprog = []    # Programme Schedule List

with open(csvChanPath, 'r') as csvfile:
    
    CSVdata = csv.DictReader(csvfile, delimiter = ',')
    for row in CSVdata:
        EPGchan.append(row)

with open(csvProgPath, 'r') as csvfile:
    
    CSVdata = csv.DictReader(csvfile, delimiter = ',')
    for row in CSVdata:
        EPGprog.append(row)
        

# -------------------------------------------
# Get the datetime of Today at Midnight
# -------------------------------------------
today_midnight = datetime.datetime.combine(datetime.date.today(), datetime.time.min).astimezone()


# -------------------------------------------
# SPLASH SCREEN
# -------------------------------------------
print("---------------------------------------------------")
print("* LoopEPG  -  V1         Copyright 2021")
print("* Midnight Today:       ",today_midnight)
print("---------------------------------------------------")

print("Upcoming Dates for EPG:")

# Create a dictionary to store the next date of these days
DayToDate = {"Mon" : 0,"Tue" : 0,"Wed" : 0,"Thu" : 0,"Fri" : 0,"Sat" : 0,"Sun" : 0}
 
# Enter the date of each day in the forthcoming 7 days
for day in range(7):
    DayToDate[(today_midnight + datetime.timedelta(days=day)).strftime("%a")] = today_midnight + datetime.timedelta(days=day)

# Print out the dates
for key in DayToDate:
    print(key, DayToDate[key].strftime("%Y%m%d%H%M%S %z"))  # String format required for XMLTV 


# ---------------------------------------------------------------------------
# Work through the Programme Schedule and create start and stop times
# for each day in the next 7 days, in appropriate format with timezone
# ---------------------------------------------------------------------------
for row in EPGprog:
    
    # Find the date of the next "Day" from the "Schedule.csv" file 
    Date   = DayToDate[row["Day"]]
    
    # Get the Start and End times from CSV, calculate duration
    Start    = datetime.datetime.strptime(row["Start"].zfill(4),"%H%M") # zfill with leading zeros, Excel sometimes drops these
    End      = datetime.datetime.strptime(row["End"].zfill(4)  ,"%H%M")
    Duration = End - Start
    
    # Check if duration passes midnight, set flag if it does
    PastMidnight = 0
    if Duration < datetime.timedelta(0):
        
        PastMidnight = 1
        Duration = Duration + datetime.timedelta(days=1)   
    
    # Calculate the datetimes with timezone to enter into the EPG, store as new keys
    EPGstart = datetime.datetime.combine(Date, Start.time()).astimezone()
    EPGstop  = datetime.datetime.combine(Date + datetime.timedelta(days=PastMidnight), (Start + Duration).time()).astimezone()
    
    row["EPGstart"] = EPGstart
    row["EPGstop"]  = EPGstop
    
    # Print it to the terminal for debug
    # print(row["Day"], "-", row["EPGstart"], "-", row["EPGstop"], Duration, row["Programme"])


# -------------------------------------------
# Create the XMLTV data
# -------------------------------------------
# Create the XMLTV structure
import xml.etree.ElementTree as ET

# create the file structure
XML_TV    = ET.Element('tv')
XML_TV.set('generator-name',"LoopEPG")
XML_TV.set('generator-url',"http://www.blah.0")
XML_TV.set('date',today_midnight.strftime("%Y%m%d"))


for row in EPGchan:
    XML_chan = ET.SubElement(XML_TV, 'channel')
    XML_chan.set('id',row["ID"])
    
    XML_dispName = ET.SubElement(XML_chan, 'display-name')
    XML_dispName.text = row["Display Name"]
    
    XML_icon = ET.SubElement(XML_chan, 'icon')
    XML_icon.set('src', row["Icon"])
    
    XML_URL = ET.SubElement(XML_chan, 'url')
    XML_URL.text = row["URL"]

# Work through the Programme Schedule List and enter the data into the XMLTV structure
for row in EPGprog:

    XML_prog  = ET.SubElement(XML_TV, 'programme')
    XML_prog.set('start',    row["EPGstart"].strftime("%Y%m%d%H%M%S %z"))
    XML_prog.set('stop',     row["EPGstop"].strftime("%Y%m%d%H%M%S %z"))
    XML_prog.set('channel',  row["Channel"])
    
    
    XML_title = ET.SubElement(XML_prog, 'title')
    XML_title.set('lang',"en")
    XML_title.text = row["Programme"]
    
    
    XML_desc  = ET.SubElement(XML_prog, 'desc')
    XML_desc.set('lang',"en")
    XML_desc.text = row["Description"]

# create a new XML file with the results
XML_TV_str = ET.tostring(XML_TV, encoding='ISO-8859-1', method='xml')

# Print for debug
# print("\n\r", XML_TV_str)
print("")
print("EPGchan Length:          ", len(EPGchan), "rows")
print("EPGprog Length:          ", len(EPGprog), "rows")
print("XMLTV String Length:     ", len(XML_TV_str), "characters")


# -------------------------------------------
# Create and Write the XMLTV file
# -------------------------------------------
# Open XMLTV file, write data, close file
with open(xmlOutputPath, "wb") as XMLTVfile:
    XMLTVfile.write(XML_TV_str)

print("\n\rAll Done! :)")

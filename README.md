# LoopEPG
Creates an XMLTV like file based on static data from a CSV file, looping every week.

Requires Python 3.

Channel names and details are defined in 'Channel.csv'.  The schedule is defined in 'Schedule.csv'.  Example CSV files are found in 'Example.zip'. 

# How it works

The script determines the dates of the forthcoming weekdays, Mon, Tue, Wed, Thu, Fri, Sat, Sun.  For example, it is now Friday 9th April 2021, so the next dates are:

```
Mon - 2021/04/12
Tue - 2021/04/13
Wed - 2021/04/14
Thu - 2021/04/15
Fri - 2021/04/09  << i.e. Today
Sat - 2021/04/10  << i.e. Tomorrow
Sun - 2021/04/11
```

Next, the script looks for the day names in the 'Schedule.csv' file.  It will then apply the dates calculated above to those days, and add on time deltas for the show start and stop times.  There is some logic to determine if a show runs past midnight.  

The show start / stop times, titles, descriptions are exported in an XML file.  The structure should be compatible with the XMLTV style.  Has been tested with NextPVR V4.

The software is provided as is with no warranty.

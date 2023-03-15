#!/bin/usr/python3

# script to transfer chrony data to influxdb2
# supports sourcestats

import getopt
import os
import socket
import sys
import threading
import time

from pprint import pprint
import subprocess

from dataclasses import dataclass

# Your InfluxDB Settings
from datetime import datetime

hostname = socket.gethostname()

# Number of seconds between updates
update_interval = 10

debug = False

if "-d" in sys.argv:
    debug = True


@dataclass
class chrony_sourcestat:
    name_ip: str = ""
    np: int = 0
    nr: int = 0
    span: int = 0
    frequency: float = 0
    freq_skew: float = 0
    offset: float = 0
    stddev: float = 0
    sourcetype: str = ""


from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "chrony"


try:
    with InfluxDBClient.from_config_file("config.ini") as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        while True:
            # TODO: check return code, chrony may not be running or access may be denied
            sourcestats_str = subprocess.check_output("chronyc -c sourcestats", shell=True)

            sourcestat_lines = sourcestats_str.splitlines()

            sourcestats = []

            
            points = []

            for line in sourcestat_lines:
                # host/IP, NP, NR, span (seconds), frequency error (ppm), frequency skew (ppm), offset (seconds), standard deviation (seconds)
                # GPS,16,11,241,-0.084,0.026,0.065314554,0.000001596
                datapoints = str(line).replace("b'", "").replace("'","").split(",")

                sourcestat = chrony_sourcestat();

                # look up the hostname if it looks like an IP
                if "." in datapoints[0]:
                    try:
                        source_hostname = socket.gethostbyaddr(datapoints[0])
                        sourcestat.name_ip = source_hostname[0]
                        sourcestat.sourcetype = "remote"
                    except socket.herror:
                        sourcestat.name_ip = datapoints[0]
                        sourcestat.sourcetype = "remote"
                else:
                    sourcestat.name_ip = datapoints[0]
                    sourcestat.sourcetype = "local"

                
                sourcestat.np = int(datapoints[1])
                sourcestat.nr = int(datapoints[2])
                sourcestat.span = int(datapoints[3])
                sourcestat.frequency = float(datapoints[4])
                sourcestat.freq_skew = float(datapoints[5])
                sourcestat.offset = float(datapoints[6])
                sourcestat.stddev = float(datapoints[7])
                if debug == True:
                    print(sourcestat)

                # check if span is greater than 0, in this case it's actually getting data
                if sourcestat.span > 0:
                    sourcestats.append(sourcestat)

            for source in sourcestats:
                p = Point("sourcestats").tag("host", hostname).tag("sourcename", source.name_ip).tag("sourcetype", source.sourcetype).field("np", source.np)
                points.append(p)
                p = Point("sourcestats").tag("host", hostname).tag("sourcename", source.name_ip).tag("sourcetype", source.sourcetype).field("nr", source.nr)
                points.append(p)
                p = Point("sourcestats").tag("host", hostname).tag("sourcename", source.name_ip).tag("sourcetype", source.sourcetype).field("span", source.span)
                points.append(p)
                p = Point("sourcestats").tag("host", hostname).tag("sourcename", source.name_ip).tag("sourcetype", source.sourcetype).field("frequency", source.frequency)
                points.append(p)
                p = Point("sourcestats").tag("host", hostname).tag("sourcename", source.name_ip).tag("sourcetype", source.sourcetype).field("freq_skew", source.freq_skew)
                points.append(p)
                p = Point("sourcestats").tag("host", hostname).tag("sourcename", source.name_ip).tag("sourcetype", source.sourcetype).field("offset", source.offset)
                points.append(p)
                p = Point("sourcestats").tag("host", hostname).tag("sourcename", source.name_ip).tag("sourcetype", source.sourcetype).field("stddev", source.stddev)
                points.append(p)
            
            write_api.write(bucket=bucket, record=points)
                
            time.sleep(update_interval)
            

except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            print ("Done.\nExiting.")

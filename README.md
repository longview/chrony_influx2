# chrony_influx2
A script to report more detailed chrony statistics to influxdb2


Requires influxdb-client
```
pip install influxdb-client
```

(pip is provided as "python3-pip" on Red Hat-like distros)

Statistics reported currently is the output is chronyc sourcestats. Sources with a span of 0 are ignored since they're presumed missing.

IP addresses are looked up using the system DNS, at present only tested with IPv4 (it will break with IPv6). Sources that are not reported by IP are tagged as local, to allow easy separation of local refclocks and remote NTP sources in the data.

Tested on Raspbian, RHEL 9.0/9.1, and Centos Stream 9.

The suggested service control script has a 60 second delay on startup; this is done since chrony's output immediately on startup tends to have large spikes due to e.g. RTC offsets. The delay allows this to settle before logging starts. It's also useful in cases where influxdb is running on the same computer, since influxdb will normally take longer to start up than this script.

## Making chrony auto-restart
chrony is pretty reliable, but I have observed failures. At least one failure was caused by gpsd becoming unstable for some reason.

You can use the edit command to add an override.conf to the service:
```
sudo systemctl edit chrony
```
Then paste in:
```
[Service]
Restart=on-failure
RestartSec=30
```

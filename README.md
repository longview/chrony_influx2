# chrony_influx2
A script to report more detailed chrony statistics to influxdb2


Requires influxdb-client
```
pip install influxdb-client
```

Statistics reported currently is the output is chronyc sourcestats. Sources with a span of 0 are ignored since they're presumed missing.

IP addresses are looked up using the system DNS, at present only tested with IPv4 (it will break with IPv6). Sources that are not reported by IP are tagged as local, to allow easy separation of local refclocks and remote NTP sources in the data.

Tested on Raspbian & RHEL 9.0

## Making chrony auto-restart
chrony is pretty reliable, but I have observed failures.

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

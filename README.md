# GeoTraceroute

Geolocation utilizes [traceroute](https://linux.die.net/man/8/traceroute), [globe.gl](https://globe.gl/) and [IPinfo.io](https://ipinfo.io/) to visualize the route/path to a host over the internet in real-time.

https://user-images.githubusercontent.com/57968347/138023883-281f3282-d7d2-426a-8d41-5c677833855f.mp4

# Dependencies

- Python
- IPinfo.io free account (50K requests/month)

# Setup

1. get an IPinfo.io free account (directions [here](https://ipinfo.io/signup)).
2. install source (`git clone https://github.com/jdoiro3/GeoTraceroute`)
3. paste access token into `static/scripts/token.json`
4. create Python venv, activate and install packages
```shell
python3 -m venv env
source env/bin/activate
python3 -m pip install -r requirements.txt
```
4. run `python3 start_server.py`


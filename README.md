# Description  

(c) Arnim Eijkhoudt \<arnime _squiggly_ kpn-cert.nl\>, 2018, KPN-CERT, GPLv2 license
  
ExitGather is a Python script to generate a list of IP addresses being used as TOR and VPN exit nodes. It takes the online downloads of VPN config files from various providers, grabs the IPv4/IPv6 addresses and hostnames from those files and generates CSV output for matching against other sources. This makes it easy to analyze dumps, threat intel data, etc. for e.g. OPSEC failures.
  
# Requirements  
  
1) Python 2.7.x
2) [required] Python DateUtil: https://pypi.python.org/pypi/python-dateutil/
3) A working internet connection
  
# Installation  
  
1) git clone https://github.com/uforia/exitgather.git
2) pip install python-dateutil (or whatever you use for package management)

# Usage  
  
1) Edit any configuration settings/URLs you like in exitgather.py
2) Create your DLDIR and OUTPUTDIR
3) Run ./exitgather.py

Usage notes:
- ExitGather will automatically resolve hostnames
- Use -q to surpress diagnostic output

# Caveats, miscellaneous, TODO, etc.  
  
- Asynchronous DNS lookups
- More VPN providers
- Create storage and output directories
- Output formats (JSON?)
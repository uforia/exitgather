#!/usr/bin/env python

### (c) 2018 Arnim Eijkhoudt <arnime _squigglything_ kpn-cert.nl>, GPLv2 licensed except where
### otherwise indicated.

URLLIST={'TOR':'https://check.torproject.org/exit-addresses'}
DLDIR='download'
OUTPUTDIR='output'

import sys,re,optparse,os,dateutil.parser

### Python 2/3 compatibility
try:
	from urllib.request import urlopen
except ImportError:
	from urllib2 import urlopen

def download(options,urls):
	for source in urls:
		url=URLLIST[source]
		if options.verbose:
			print("U) Downloading "+url)
		try:
			response=urlopen(url)
		except KeyboardInterrupt:
			print("E) CTRL-C pressed, stopping!")
			sys.exit(1)
		except:
			print("E) An error occurred downloading "+url)
		try:
			with open(DLDIR+'/'+source,'wb') as f:
				f.write(response.read())
		except IOError:
			print("E) An error occurred writing "+url+ " to disk!")
		except KeyboardInterrupt:
			print("E) CTRL-C pressed, stopping!")
			sys.exit(1)
		if options.verbose:
			print("U) Download done!")

def generate(options,urls):
	for source in urls:
		try:
			with open(DLDIR+'/'+source,'r') as f:
				exitnodelist=f.read().split("ExitNode ")
		except IOError:
			if options.verbose:
				print("E) An error occurred opening "+source+"!")
			sys.exit(1)
		try:
			f=open(OUTPUTDIR+'/'+source+'.csv','w')
			f.write('"ExitNode","IPAddress","Published","Last Seen","Status","Comment"\n')
			for raw_entry in exitnodelist:
				entry=raw_entry.split('\n')
				if entry:
					exitnode=entry[0].lower()
					if re.search('[0-9a-f]{40}', exitnode):
						status=''
						comment=''
						publishedtimestamp=entry[1].split(' ')[1]+'T'+entry[1].split(' ')[2]+'Z'
						laststatustimestamp=entry[2].split(' ')[1]+'T'+entry[2].split(' ')[2]+'Z'
						if dateutil.parser.parse(publishedtimestamp) > dateutil.parser.parse(laststatustimestamp):
							status="Node may no longer be an exit node"
						if dateutil.parser.parse(publishedtimestamp) < dateutil.parser.parse(laststatustimestamp):
							status="Verified exit node"
						exitaddress,exitaddresstimestamp=entry[3].split(' ')[1],entry[3].split(' ')[2]+'T'+entry[3].split(' ')[3]+'Z'
						f.write('"'+exitnode+'","'+exitaddress+'","'+publishedtimestamp+'","'+laststatustimestamp+'","'+status+'","'+comment+'"\n')
		except:
			raise
			if options.verbose:
				print("An error occurred parsing the contents")
			f.close()

if __name__=="__main__":
	cli=optparse.OptionParser(usage="usage: %prog [-q]")
	cli.add_option('-q','--quiet',dest='verbose',action='store_false',default=True,help='[optional] Do not print progress, errors')
	(options,args)=cli.parse_args()
	download(options,URLLIST)
	generate(options,URLLIST)

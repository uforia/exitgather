#!/usr/bin/env python

### (c) 2018 Arnim Eijkhoudt <arnime _squigglything_ kpn-cert.nl>, GPLv2 licensed except where otherwise indicated.

URLLIST={
	'TOR':{'URL':'https://check.torproject.org/exit-addresses','Type':'TOR','Format':'TOR'},
}
#	'IPVanish':{'URL':'https://www.ipvanish.com/software/configs/configs.zip','Type':'OpenVPN','Format':'ZIP'},
#	'NordVPN':{'URL':'https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip','Type':'OpenVPN','Format':'ZIP'}
#}
DLDIR='download'
OUTPUTDIR='output'

import sys,re,optparse,os,dateutil.parser,zipfile,fnmatch,time

### Python 2/3 compatibility
try:
	from urllib.request import urlopen
except ImportError:
	from urllib2 import urlopen

def download(options,urls):
	for key in urls:
		sourceurl,sourcetype,sourceformat,destination=urls[key]['URL'],urls[key]['Type'],urls[key]['Format'],key+'-'+os.path.basename(urls[key]['URL'])
		if options.verbose:
			print("U) Downloading "+sourceurl)
		try:
			response=urlopen(sourceurl,None,15)
		except KeyboardInterrupt:
			print("E) CTRL-C pressed, stopping!")
			sys.exit(1)
		except:
			raise
			print("E) An error occurred downloading "+sourceurl)
			continue
		try:
			with open(DLDIR+'/'+destination,'wb') as f:
				f.write(response.read())
		except IOError:
			print("E) An error occurred writing "+sourceurl+" to disk!")
		except KeyboardInterrupt:
			print("E) CTRL-C pressed, stopping!")
			sys.exit(1)
		if os.path.splitext(destination)[1].lower()=='.zip':
			try:
				with zipfile.ZipFile(DLDIR+'/'+destination,'r') as z:
					if sourcetype=='OpenVPN':
						ovpnconfigs=[file for file in z.namelist() if file.lower().endswith('.ovpn')]
						z.extractall(DLDIR,ovpnconfigs)
				os.unlink(DLDIR+'/'+destination)
			except IOError:
				print("E) An error occurred unzipping "+sourceurl+"!")
			except KeyboardInterrupt:
				print("E) CTRL-C pressed, stopping!")
				continue
		if options.verbose:
			print("U) Download done!")

def generate(options,urls):
	for key in urls:
		sourceurl,sourcetype,sourceformat=urls[key]['URL'],urls[key]['Type'],urls[key]['Format']
		destination=time.strftime("%Y-%m-%dT%H-%M-%S",time.gmtime())+'-'+sourcetype+'-exit-nodes.csv'
		if sourcetype=='TOR' and sourceformat=='TOR':
			sourcefile=key+'-'+os.path.basename(urls[key]['URL'])
			try:
				with open(DLDIR+'/'+sourcefile,'r') as f:
					exitnodelist=f.read().split("ExitNode ")
			except IOError:
				if options.verbose:
					print("E) An error occurred opening "+destination+"!")
				sys.exit(1)
			try:
				f=open(OUTPUTDIR+'/'+destination,'w')
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
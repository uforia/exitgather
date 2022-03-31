#!/usr/bin/env python3

### (c) 2018 Arnim Eijkhoudt <arnime _squigglything_ kpn-cert.nl>, GPLv2 licensed except where otherwise indicated.

URLLIST={
	'TOR':{'URL':'https://check.torproject.org/exit-addresses','Type':'TOR','Format':'TOR'},
	'IPVanish':{'URL':'https://www.ipvanish.com/software/configs/configs.zip','Type':'OpenVPN','Format':'OpenVPN'},
	'NordVPN':{'URL':'https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip','Type':'OpenVPN','Format':'OpenVPN'},
	'PureVPN':{'URL':'https://d32d3g1fvkpl8y.cloudfront.net/heartbleed/windows/New+OVPN+Files.zip','Type':'OpenVPN','Format':'OpenVPN'},
	'PrivateInternetAccessVPNIP':{'URL':'https://www.privateinternetaccess.com/openvpn/openvpn-ip.zip','Type':'OpenVPN','Format':'OpenVPN'},
	'PrivateInternetAccessVPNTCP':{'URL':'https://www.privateinternetaccess.com/openvpn/openvpn-tcp.zip','Type':'OpenVPN','Format':'OpenVPN'},
	'TunnelbearVPN':{'URL':'https://s3.amazonaws.com/tunnelbear/linux/openvpn.zip','Type':'OpenVPN','Format':'OpenVPN'},
	'TorGuardVPNUDP':{'URL':'https://torguard.net/downloads/OpenVPN-UDP.zip','Type':'OpenVPN','Format':'OpenVPN'},
	'TorGuardVPNTCP':{'URL':'https://torguard.net/downloads/OpenVPN-TCP.zip','Type':'OpenVPN','Format':'OpenVPN'},
	'HideMyAssVPN':{'URL':'https://vpn.hidemyass.com/vpn-config/vpn-configs.zip','Type':'OpenVPN','Format':'OpenVPN'},
	'VyprVPN':{'URL':'https://support.goldenfrog.com/hc/en-us/articles/360011055671-What-are-the-VyprVPN-server-addresses-','Type':'PPTP-L2TP','Format':'HTML'}
}

import sys, re, optparse, os, dateutil.parser, zipfile, fnmatch, time, socket, itertools
import urllib.request

DLDIR = 'download'
OUTPUTDIR = 'output'
IPV4_ADDRESS = re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
IPV6_ADDRESS = re.compile(
    '(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
)
OpenVPN_ADDRESS = re.compile('(remote .* ([0-9]{1,5}))', re.IGNORECASE)


def download(options, urls):
    for key in urls:
        sourceurl, sourcetype, sourceformat, destdir, destfile = (
            urls[key]['URL'],
            urls[key]['Type'],
            urls[key]['Format'],
            DLDIR + '/' + key + '/',
            key + '-' + os.path.basename(urls[key]['URL']),
        )
        if options.verbose:
            print("U) Downloading " + sourceurl)
        try:
            request = urllib.request.Request(sourceurl)
            request.add_header(
                ('User-Agent'),
                (
                    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'
                ),
            )
            opener = urllib.request.build_opener()
        except KeyboardInterrupt:
            print("E) CTRL-C pressed, stopping!")
            sys.exit(1)
        except:
            raise
            print("E) An error occurred downloading " + sourceurl)
            continue
        try:
            if not os.path.exists(destdir):
                os.makedirs(destdir)
            with open(destdir + destfile, 'wb') as f:
                f.write(opener.open(request).read())
        except IOError:
            print("E) An error occurred writing " + sourceurl + " to disk!")
        except KeyboardInterrupt:
            print("E) CTRL-C pressed, stopping!")
            sys.exit(1)
        if os.path.splitext(destfile)[1].lower() == '.zip':
            try:
                with zipfile.ZipFile(destdir + destfile, 'r') as z:
                    if sourcetype == 'OpenVPN':
                        ovpnconfigs = [
                            file
                            for file in z.namelist()
                            if file.lower().endswith('.ovpn')
                        ]
                        z.extractall(destdir, ovpnconfigs)
                os.unlink(destdir + destfile)
            except IOError:
                raise
                print("E) An error occurred unzipping " + destdir + destfile + "!")
            except KeyboardInterrupt:
                print("E) CTRL-C pressed, stopping!")
                continue
        if options.verbose:
            print("U) Download done!")


def generate(options, urls):
    for key in urls:
        sourceurl, sourcetype, sourceformat = (
            urls[key]['URL'],
            urls[key]['Type'],
            urls[key]['Format'],
        )

        if not options.overwrite:
            partfilename = '{}-'.format(time.strftime("%Y-%m-%dT%H-%M-%S", time.gmtime()))
        else:
            partfilename = ''

        if sourcetype == 'TOR' and sourceformat == 'TOR':
            destfile = (
                OUTPUTDIR
                + '/'
                + partfilename
                + sourcetype
                + '-exit-nodes.csv'
            )
            if options.verbose:
                print("U) Generating list of " + key + " exit node IPs...")
            sourcefile = (
                DLDIR + '/' + key + '/' + key + '-' + os.path.basename(urls[key]['URL'])
            )
            try:
                with open(sourcefile, 'r') as f:
                    exitnodelist = f.read().split("ExitNode ")
            except IOError:
                if options.verbose:
                    print("E) An error occurred opening " + sourcefile + "!")
                sys.exit(1)
            try:
                f = open(destfile, 'w+')
                f.write(
                    '"ExitNode","IPAddress","Published","Last Seen","Status","Comment"\n'
                )
                for raw_entry in exitnodelist:
                    entry = raw_entry.split('\n')
                    if entry:
                        exitnode = entry[0].lower()
                        if re.search('[0-9a-f]{40}', exitnode):
                            status = ''
                            comment = ''
                            publishedtimestamp = (
                                entry[1].split(' ')[1]
                                + 'T'
                                + entry[1].split(' ')[2]
                                + 'Z'
                            )
                            laststatustimestamp = (
                                entry[2].split(' ')[1]
                                + 'T'
                                + entry[2].split(' ')[2]
                                + 'Z'
                            )
                            if dateutil.parser.parse(
                                publishedtimestamp
                            ) > dateutil.parser.parse(laststatustimestamp):
                                status = "Node may no longer be an exit node"
                            if dateutil.parser.parse(
                                publishedtimestamp
                            ) < dateutil.parser.parse(laststatustimestamp):
                                status = "Verified exit node"
                            exitaddress, exitaddresstimestamp = (
                                entry[3].split(' ')[1],
                                entry[3].split(' ')[2]
                                + 'T'
                                + entry[3].split(' ')[3]
                                + 'Z',
                            )
                            f.write(
                                '"'
                                + exitnode
                                + '","'
                                + exitaddress
                                + '","'
                                + publishedtimestamp
                                + '","'
                                + laststatustimestamp
                                + '","'
                                + status
                                + '","'
                                + comment
                                + '"\n'
                            )
            except:
                if options.verbose:
                    print("An error occurred parsing the contents of " + sourcefile)
                f.close()
        if sourcetype == 'OpenVPN' and sourceformat == 'OpenVPN':
            destfile = (
                OUTPUTDIR
                + '/'
                + partfilename
                + key
                + '-exit-nodes.csv'
            )
            if options.verbose:
                print(
                    "U) Generating list of "
                    + key
                    + " exit node IPs. This may be slow if this VPN provider uses hostnames in their configs!"
                )
            matches = []
            sourcedir = DLDIR + '/' + key
            try:
                g = open(destfile, 'w+')
                g.write('"Provider","IPAddress","Ports","Comment"\n')
            except IOError:
                if options.verbose:
                    print("E) Error opening output file " + destfile + "!")
                    continue
            try:
                for root, dirnames, filenames in os.walk(sourcedir):
                    for filename in fnmatch.filter(filenames, '*.ovpn'):
                        matches.append(os.path.join(root, filename))
            except IOError:
                if options.verbose:
                    print("E) An error occurred parsing the OpenVPN files for " + key)
                continue
            for filename in matches:
                comment = ''
                try:
                    with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                        for line in f.readlines():
                            exitnodes = OpenVPN_ADDRESS.finditer(line)
                            for remoteline in [line.group(0) for line in exitnodes]:
                                exitnodeentry, exitnodeport = (
                                    remoteline.split(' ')[1],
                                    remoteline.split(' ')[2],
                                )
                                if not IPV4_ADDRESS.match(
                                    exitnodeentry
                                ) and not IPV6_ADDRESS.match(exitnodeentry):
                                    try:
                                        exitnodeip = socket.gethostbyname(exitnodeentry)
                                    except socket.error:
                                        if options.verbose:
                                            print(
                                                "E) Could not resolve "
                                                + exitnodeentry
                                                + "!"
                                            )
                                            exitnodeip = (
                                                'Host '
                                                + exitnodeentry
                                                + ' not found: 3(NXDOMAIN)'
                                            )
                                else:
                                    exitnodeip = exitnodeentry
                except IOError:
                    if options.verbose:
                        print(
                            "E) An error occurred reading or finding the IP in "
                            + filename
                            + "! Is this an OpenVPN config file?"
                        )
                        continue
                g.write(
                    '"'
                    + key
                    + '","'
                    + exitnodeip
                    + '","'
                    + exitnodeport
                    + '","'
                    + comment
                    + '"\n'
                )
        if sourcetype == 'PPTP-L2TP' and sourceformat == 'HTML':
            destfile = (
                OUTPUTDIR
                + '/'
                + partfilename
                + key
                + '-exit-nodes.csv'
            )
            if options.verbose:
                print(
                    "U) Generating list of "
                    + key
                    + " exit node IPs. This may be slow if this VPN provider uses hostnames on their webpages!"
                )
            matches = []
            sourcefile = (
                DLDIR + '/' + key + '/' + key + '-' + os.path.basename(urls[key]['URL'])
            )
            sourcedir = DLDIR + '/' + key
            try:
                g = open(destfile, 'w+')
                g.write('"Provider","IPAddress","Ports","Comment"\n')
            except IOError:
                if options.verbose:
                    print("E) Error opening output file " + destfile + "!")
                    continue
            try:
                with open(sourcefile, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f.readlines():
                        exitnodesv4 = IPV4_ADDRESS.finditer(line)
                        exitnodesv6 = IPV6_ADDRESS.finditer(line)
                        for exitnodeip in [
                            line.group(0)
                            for line in itertools.chain(exitnodesv4, exitnodesv6)
                        ]:
                            g.write(
                                '"'
                                + key
                                + '","'
                                + exitnodeip
                                + '","500,1723,4500","PPTP, L2TP, IPSEC tunneling"\n'
                            )
            except IOError:
                if options.verbose:
                    print("E) An error occurred reading " + filename + "!")
                    continue


if __name__ == "__main__":
    cli = optparse.OptionParser(usage="usage: %prog [-q]")
    cli.add_option(
        '-q',
        '--quiet',
        dest='verbose',
        action='store_false',
        default=True,
        help='[optional] Disable progress/error info (default: enabled)',
    )
    cli.add_option(
        '-o',
        '--overwrite',
        dest='overwrite',
        action='store_true',
        default=False,
        help='[optional] Overwrite destination file instead of datetime file (default: disabled)',
    )
    (options, args) = cli.parse_args()
    try:
        if not os.path.exists(DLDIR):
            if options.verbose:
                print("U) Creating download directory...")
            os.makedirs(DLDIR)
    except:
        if options.verbose:
            print("U) An error occured creating the download directory, exiting!")
            sys.exit(1)
    try:
        if not os.path.exists(OUTPUTDIR):
            if options.verbose:
                print("U) Creating output directory...")
            os.makedirs(OUTPUTDIR)
    except:
        if options.verbose:
            print("U) An error occured creating the output directory, exiting!")
            sys.exit(1)
    download(options, URLLIST)
    generate(options, URLLIST)

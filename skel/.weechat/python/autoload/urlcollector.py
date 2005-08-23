#!/usr/bin/env python

import weechat, string, os, sys

UC_NAME="UrlCollector"
UC_VERSION="0.1"
UC_HISTORYSIZE=10
UC_BROWSER="firefox"
# UC_REMOTE must be yes or no
UC_REMOTE="no"
UC_REMOTEHOST="127.0.0.1"
UC_REMOTEPORT=22

weechat.register (UC_NAME, UC_VERSION, "", "Url collector for weechat !!!")
weechat.add_message_handler("privmsg", "uccheck")
weechat.add_command_handler("url", "ucmain")


class urlCollector:
    def __init__(self, historysize = UC_HISTORYSIZE):
        # init
        self.urls = {}
        self.historysize = 5
        # control
        self.setHistorysize(historysize)

    def setHistorysize(self, count):
        if count > 1:
            self.historysize = count

    def getHistorysize(self):
        return self.historysize

    def addUrl(self, url, channel, server):
        # check for server
        if not self.urls.has_key(server):
            self.urls[server] = {}
        # check for chan
        if not self.urls[server].has_key(channel):
            self.urls[server][channel] = []
        # add url
        if url in self.urls[server][channel]:
            self.urls[server][channel].remove(url)
        self.urls[server][channel].insert(0, url)
        # removing old urls
        while len(self.urls[server][channel]) > self.historysize:
            self.urls[server][channel].pop()
            
    def getUrl(self, index, channel, server):
        url = ""
        if self.urls.has_key(server):
            if self.urls[server].has_key(channel):
                if len(self.urls[server][channel]) >= index:
                    url = self.urls[server][channel][index-1]
                
        return url
        

    def prnt(self, channel, server):
        found = True
        if self.urls.has_key(server):
            if self.urls[server].has_key(channel):
                weechat.prnt("-[" + UC_NAME + "]- " + channel + "@" +  server)
                if len(self.urls[server][channel]) > 0:
                    i = 1
                    for url in self.urls[server][channel]:
                        weechat.prnt(" --> " + str(i) + " : " + url)
                        i += 1
                else:
                    found = False
            else:
                found = False
        else:
            found = False

        if not found:
            weechat.prnt("-[" + UC_NAME + "]- " + channel + "@" +  server + " : no entries")
            
def ucgetinfos(command):
    infos = string.split(command, " ")
    chan = infos[2]
    message = string.join(infos[3:], " ")[1:]
    return (chan, message)

def uccheck(server, args):
    global uc
    chan, message = ucgetinfos(args)
    for word in string.split(message, " "):
        if word[0:7] == "http://" or word[0:8] == "https://" or word[0:6] == "ftp://":
            uc.addUrl(word, chan, server)
    # check for dead childs
    while True:
        try:
            mypid, status = os.waitpid(0, os.WNOHANG)        
        except:
            break
        else:
            if mypid <= 0:
                break

def ucopen(largs):
    global uc, ucbrowser, ucremote, ucremotehost, ucremoteport
    found = False
    index = 1
    
    if largs[0] != "":
        try:
            index = int(largs[0])
        except:
            pass
        else:
            found = True
    else:
        found = True

    if found and index > 0:
        url = uc.getUrl(index, weechat.get_info("channel"), weechat.get_info("server"))
        if url == "":
            weechat.prnt("-[" + UC_NAME + "]- unable to load url : undefined index")
        else:
            weechat.prnt("-[" + UC_NAME + "]- loading " + url +" ... (" + ucbrowser + ")")
            childpid = os.fork()
            if (childpid == 0):
                sys.stdout.close()
                sys.stderr.close()
                try:
                    if ucremote:
                        os.execlp("ssh", "ssh", "-p", str(ucremoteport), ucremotehost, "export DISPLAY=:0.0 ; " + ucbrowser + " " + url);
                    else:
                        argl = string.split(ucbrowser, " ")
                        argl.append(url)
                        os.execvp(argl[0], argl)
                except:
                    pass
                os._exit(-1)
    else:
        weechat.prnt("-[" + UC_NAME + "]- unable to load url : undefined index")

def ucerrargs():
    weechat.prnt("-[" + UC_NAME + "]- syntax error : missing arguments or bad value")

def ucmethod(largs):
    global ucremote
    method = 'local'
    if ucremote:
        method = 'remote'

    if largs[0] == 'set':
        if len(largs) > 2:
            if largs[2] == 'local':
                ucremote = False
                weechat.prnt("-[" + UC_NAME + "]- method is set to 'local'")
            elif largs[2] == 'remote':
                ucremote = True
                weechat.prnt("-[" + UC_NAME + "]- method is set to 'remote'")
            else:
                ucerrargs()
        else:
            ucerrargs()
    else:
        if ucremote:
            weechat.prnt("-[" + UC_NAME + "]- method is set to 'remote'")
        else:
            weechat.prnt("-[" + UC_NAME + "]- method is set to 'local'")

def ucremoteportf(largs):
    global ucremoteport
    if largs[0] == 'set':
        if len(largs) > 2:
            try:
                port = int(largs[2])
            except:
                ucerrargs()
            else:
                ucremoteport = port
                weechat.prnt("-[" + UC_NAME + "]- remote port is set to '" + str(ucremoteport) + "'")
        else:
            ucerrargs()
    else:
        weechat.prnt("-[" + UC_NAME + "]- remote port is set to '" + str(ucremoteport) + "'")

def ucremotehostf(largs):
    global ucremotehost
    if largs[0] == 'set':
        if len(largs) > 2:
            ucremotehost= largs[2]
            weechat.prnt("-[" + UC_NAME + "]- remote host is set to '" + ucremotehost + "'")
        else:
            ucerrargs()
    else:
        weechat.prnt("-[" + UC_NAME + "]- remote host is set to '" + ucremotehost + "'")

def ucsize(largs):
    global uc
    if largs[0] == 'set':
        if len(largs) > 2:
            try:
                size = int(largs[2])
            except:
                ucerrargs()
            else:
                weechat.prnt("-[" + UC_NAME + "]- setting history to " + str(size) + " entries")
                uc.setHistorysize(size)
        else:
            ucerrargs()
    else:
        weechat.prnt("-[" + UC_NAME + "]- history size is set to " + str(uc.getHistorysize()) + " entries")

def ucbrowserf(largs):
    global ucbrowser
    if largs[0] == 'set':
        if len(largs) > 2:
            ucbrowser = string.join(largs[2:], " ")
            weechat.prnt("-[" + UC_NAME + "]- setting browser to '" + ucbrowser + "'")
        else:
            ucerrargs()
    else:
        weechat.prnt("-[" + UC_NAME + "]- browser is set to '" + ucbrowser + "'")

def uclist():
    global uc
    uc.prnt(weechat.get_info("channel"), weechat.get_info("server"))
        
def uchelp():
    weechat.prnt("")
    weechat.prnt("-[" + UC_NAME + "]- (help)")
    weechat.prnt("")
    weechat.prnt(" Usage : ")
    weechat.prnt("    /url help :")
    weechat.prnt("        -> display this help")
    weechat.prnt("    /url list :")
    weechat.prnt("        -> display list of recorded urls in the current channel")
    weechat.prnt("    /url set browser %browser%")
    weechat.prnt("        -> set the browser command to launch urls to %browser%")
    weechat.prnt("    /url get browser")
    weechat.prnt("        -> get current the browser command")
    weechat.prnt("    /url set size %size%")
    weechat.prnt("        -> set the number of url to record to %size%")
    weechat.prnt("    /url get size")
    weechat.prnt("        -> get the current history size")
    weechat.prnt("    /url set method [local|remote]")
    weechat.prnt("        -> set the method to launch urls with a local/remote browser")
    weechat.prnt("    /url get method")
    weechat.prnt("        -> get the current method to browse urls")
    weechat.prnt("    /url set remotehost %host_addr%")
    weechat.prnt("        -> set the remote host to browse urls to %host_addr%")
    weechat.prnt("    /url get remotehost")
    weechat.prnt("        -> get the current remote host")
    weechat.prnt("    /url set remoteport %host_port%")
    weechat.prnt("        -> set the port for the remote host to %host_port%")
    weechat.prnt("    /url get remoteport")
    weechat.prnt("        -> get the current remote host port")
    weechat.prnt("    /url [n]")
    weechat.prnt("        -> launch url designed by n in `/url list`")
    weechat.prnt("    /url")
    weechat.prnt("        -> launch the first entry in `/url list`")
    weechat.prnt("")

def ucmain(server, args):

    largs = string.split(args, " ")
    #strip spaces
    while '' in largs:
        largs.remove('')
    while ' ' in largs:
        largs.remove(' ')

    if largs[0] == 'help':
        uchelp()
    elif largs[0] == 'list':
        uclist()
    elif largs[0] == 'set' or largs[0] == 'get':
        if len(largs) > 1:
            if largs[1] == 'browser':
                ucbrowserf(largs)
            elif largs[1] == 'size':
                ucsize(largs)
            elif largs[1] == 'remotehost':
                ucremotehostf(largs)
            elif largs[1] == 'remoteport':
                ucremoteportf(largs)
            elif largs[1] == 'method':
                ucmethod(largs)
            else:
                ucerrargs()
        else:
            ucerrargs()
    else:
        ucopen(largs)
                

uc = urlCollector()
ucbrowser = os.getenv('WEECHAT_BROWSER', UC_BROWSER)

if string.lower(UC_REMOTE) == "yes":
    ucremote = True
else:
    ucremote = False

ucremotehost = UC_REMOTEHOST
ucremoteport = UC_REMOTEPORT


import weechat, string, popen2

EX_NAME="Executor"
EX_VERSION="0.1"

weechat.register (EX_NAME, EX_VERSION, "", "Execute system commands in Weechat")
weechat.add_command_handler("exec", "exmain")

def exexec(cmd):
    proc = popen2.Popen3(cmd, True)
    status = proc.wait()
    results = []
    if status == 0:
        results = proc.fromchild.readlines()
    else:
        results = proc.childerr.readlines()
    return status, results

def excmdbuf(args):
    status, results = exexec(string.join(args, " "))
    if status == 0:
        weechat.prnt("-[" + EX_NAME + "]- command `" + string.join(args, " ") + "` sucessfully launched")
        for line in results:
            weechat.prnt(string.rstrip(line, '\n'))
    else:
        weechat.prnt("-[" + EX_NAME + "]- an error occured while running command `" + string.join(args, " ") + "`")
        for line in results:
            weechat.prnt(string.rstrip(line, '\n'))
            
def excmdchan(args):
    status, results = exexec(string.join(args, " "))
    if status == 0:
        weechat.prnt("-[" + EX_NAME + "]- command `" + string.join(args, " ") + "` sucessfully launched")
        for line in results:
            weechat.command(string.rstrip(line, '\n'))
    else:
        weechat.prnt("-[" + EX_NAME + "]- an error occured while running command `" + string.join(args, " ") + "`")
        for line in results:
            weechat.prnt(string.rstrip(line, '\n'))


def exchdir(args):
    newdir = "."
    if args == []:
        if os.environ.has_key('HOME'):
            newdir = os.environ['HOME']
    else:
        newdir = args[0]
    try:
        os.chdir(newdir)
    except:
        weechat.prnt("-[" + EX_NAME + "]- an error occured while running command `cd " + newdir + "`")
    else:
        weechat.prnt("-[" + EX_NAME + "]- command `cd " + newdir + "` sucessfully launched")
            

def exhelp():
    weechat.prnt("")
    weechat.prnt("-[" + EX_NAME + "]- (help)")
    weechat.prnt("")
    weechat.prnt(" Usage : ")
    weechat.prnt("    /exec :")
    weechat.prnt("        -> display this help")
    weechat.prnt("    /url %command% :")
    weechat.prnt("        -> display result of %command% in the current buffer")
    weechat.prnt("    /url -o %command% :")
    weechat.prnt("        -> display result of %command% in the current channel")
    weechat.prnt("")

def exmain(server, args):    
    largs = string.split(args, " ")
    
    #strip spaces
    while '' in largs:
        largs.remove('')
    while ' ' in largs:
        largs.remove(' ')

    if len(largs) ==  0:
        exhelp()
    else:
        if len(largs) ==  1:
            if largs[0] == '-o':
                exhelp()
            elif largs[0] == 'cd':
                exchdir([])
            else:
                excmdbuf(largs)
        else:
            if largs[0] == '-o':
                excmdchan(largs[1:])
            elif largs[0] == 'cd':
                exchdir(largs[1:])
            else:
                excmdbuf(largs)


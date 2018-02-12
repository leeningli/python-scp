#!/usr/bin/python
# -*- encoding=utf-8 -*-
# version: 1.0
# auth: leeningli
# date: 2018-02-12
    
import sys
import os
import traceback
import re

from config import leeConfig
from common.scolor import scolor
from common import leeIp
from common.qauto import QAuto

reload(sys)
sys.setdefaultencoding('utf8')

def get_realpath():
    return os.path.split(os.path.realpath(__file__))[0]

def get_binname():
    return os.path.split(os.path.realpath(__file__))[1]

def signal_handler(signal, frame):
    pid = os.getpid();
    #print "kill these pids: ",pid
    os.system("kill -9 %d" % pid)
    sys.exit(0)

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal_handler)
    try:
        scol = scolor()
        args = sys.argv[1:]
        if len(args) < 2 or str(args[0]).lower() in ["help","--help","-h","?"]:
            scol.error("usage:\n\t%s iphosts command [user] [timeout]" % (sys.argv[0]))
            sys.exit(1)

        iphosts = args[0]
        command = args[1]
        username = "wls81"
        timeout = 5
        port = 22
        
        if len(args) > 2:
            username = args[2]
        if len(args) > 3:
            timeout = int(args[3])

        iphosts = re.split("[,;\s]+", iphosts)
        scol = scolor()
        qa = QAuto()
        
        print("####### confirm #######")
        print("# username: %s" % (username))
        print("#   cmdstr: %s" % (command))
        print("#  timeout: %s" % (timeout))
        print("#######################")
        resp = raw_input("Are you sure?(y/n):")
        resp = str(resp).strip().lower()
        if resp not in ["y","yes"]:
            sys.exit(1)
        
        for (idx,ip) in enumerate(iphosts):
            scol.info("############# [%s] %s #############" % (idx+1,ip))
            scol.info("#### command: %s" % (command))
            if leeIp.is_ip(ip) == False:
                scol.error("invalid ip: %s" % (ip))
                continue

            (flag, passwds, resstr) = qa.try_to_exe(ip,command,user=username, genpasswds=leeConfig.get_passwds, timeout=timeout)
            if flag == False and passwds:
                pass
#                 msg = u"[error] try to execute %s@%s, passwords:%s" % (username, ip, " -> ".join(passwds))
#                 scolor.error(msg)
                
            pswstr =  " -> ".join(passwds)
            print("Try Passwords: "+pswstr)
            print("FEEDBACK:\n==========")
            print(resstr)
                
    except Exception, expt:
        scolor.error(expt)
        pass

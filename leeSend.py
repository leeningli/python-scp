#!/usr/bin/python
# -*- encoding=utf-8 -*-
# version: 1.0
# auth: leeningli
# date: 2018-02-12
# send file to remote host
    
import sys
import os
import traceback
import re
from optparse import OptionParser

from config import leeConfig
from common.scolor import scolor
from common.slog import slog

from common.qauto import QAuto
from common import leeIp

reload(sys)
sys.setdefaultencoding('utf8')

def get_realpath():
    return os.path.split(os.path.realpath(__file__))[0]

def get_binname():
    return os.path.split(os.path.realpath(__file__))[1]


if __name__ == "__main__":
    log = slog("/tmp/sendto.log", debug=True)
    try:
        parser = OptionParser()
        parser.add_option("-i", "--ii",  
                          action="store", dest="ii", default=None,  
                          help="iphosts file or iphosts string", metavar="IPHOSTS_OR_IPHOSTS_FILE")
        parser.add_option("-s", "--src",  
                          action="store", dest="src", default=None,  
                          help="file or dir to be sent", metavar="FILE_OR_DIR")
        parser.add_option("-d", "--dest",  
                          action="store", dest="dest", default="/tmp",  
                          help="remote directory to store file(s), use '/tmp' as default", metavar="REMOTE_DESTINATION_DIR")
        parser.add_option("-u", "--username",  
                          action="store", dest="username", default="wls81",  
                          help="the same default username to send, use 'wls81' as default", metavar="USERNAME")
        parser.add_option("-p", "--port",  
                          action="store", dest="port", default=22,  
                          help="remote port", metavar="REMOTE _PORT")
        parser.add_option("-t", "--timeout",  
                          action="store", dest="timeout", default=120,  
                          help="global timeout", metavar="TIMEOUT")
        parser.add_option("-q", "--quiet",  
                          action="store_true", dest="quiet", default=False,  
                          help="quiet model")
        (options, args) = parser.parse_args()  
        #check if file exist
        ii = options.ii
        srcfile = options.src
        destdir = options.dest
        username = options.username
        timeout = int(options.timeout) if options.timeout else 120
        port = options.port
        quiet = options.quiet
        
        if not ii or not srcfile:
            parser.print_help()
            sys.exit(1)

        srcfile = os.path.abspath(srcfile)
        if os.path.exists(srcfile) == False:
            scolor.error("File Not Exist! File: %s" % (srcfile))
            sys.exit(1)

        print("")
        print("#"*60)
        print("## iphosts or iphosts file: %s" % (ii))
        print("## file or directory: %s" % (srcfile))
        print("## destination directory: %s" % (destdir))
        print("## scp user: %s" % (username))
        print("## port: %s" % (port))
        print("## timeout: %s" % (timeout))
        print("#"*60)
        print("")
        
        if quiet == False:
            while True:
                resp = raw_input("Are You Sure ? (y or n) ")
                if str(resp).strip().lower() in ["n","no"]:
                    sys.exit(1)
                elif str(resp).strip().lower() in ["y","yes"]:
                    break

        iphosts = []
        if os.path.exists(ii) == False:
            iphosts = re.split("[,;\s]+", ii)
        else:
            with open(ii,"r") as fd:
                for line in fd:
                    line = str(line).strip()
                    if line.startswith("#") or line == "": continue
                    iphosts.append(line)
            
        scol = scolor()
        qa = QAuto()
        for ip in iphosts:
            if leeIp.is_ip(ip) == False:
                scol.error("invalid ip: %s, ignore" % (ip))
                continue

            (flag, passwds, resstr) = qa.try_to_send(ip,srcfile, destdir,user=username, genpasswds=leeConfig.get_passwds, timeout=timeout)
            pswstr =  " -> ".join(passwds)
            logobj = {
                      "orders":["IP","USER","FROM","TO","PASSWORD","TIMEOUT","RESULT","FEEDBACK"],
                      "IP": ip,
                      "USER": username,
                      "FROM": srcfile,
                      "TO": destdir,
                      "PASSWORD": pswstr,
                      "TIMEOUT": timeout,
                      "RESULT": "success" if flag else "fail",
                      "FEEDBACK": "\n"+resstr.strip()
            }
            if flag:
                log.dictlog(level="info", width=10, **logobj)
            else:
                log.dictlog(level="warn", width=10, **logobj)
                
    except Exception, expt:
        print traceback.format_exc()
        pass

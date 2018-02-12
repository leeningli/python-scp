#!/usr/bin/python
# -*- encoding=utf-8 -*-
# version: 1.0
# auth: leeningli
# date: 2018-02-12

import pexpect
from pexpect import pxssh
from pexpect.pxssh import ExceptionPxssh
import perf

import traceback
import os
import types


def goto2(iphost, username, password='', ssh_key=None, max_try=2, login_timeout=2, port=None):
    try:
        child = pxssh.pxssh()
        # Disable host key checking.
        child.SSH_OPTS = (child.SSH_OPTS
                + " -o 'StrictHostKeyChecking=no'"
                + " -o 'UserKnownHostsFile /dev/null' ")
        #child.force_password = True
        flag = False
        for idx in range(max_try):
            flag = child.login(iphost, username, password=password, ssh_key=ssh_key, port=port, login_timeout=login_timeout)
            if flag == True:
                child.interact()
                break
    except Exception,e:
        print traceback.format_exc()
        raise
    
def goto(iphost, username, password='', terminal_type='ansi',
                original_prompt=r"[#$]", login_timeout=10, port=None,
                auto_prompt_reset=True, ssh_key=None, quiet=True,
                sync_multiplier=1, check_local_ip=True, callback=None,dimensions=None):

        ssh_options = ''
        if quiet:
            ssh_options = ssh_options + ' -q'
        if not check_local_ip:
            ssh_options = ssh_options + " -o'NoHostAuthenticationForLocalhost=yes'"
        if port is not None:
            ssh_options = ssh_options + ' -p %s'%(str(port))
        if ssh_key is not None:
            try:
                os.path.isfile(ssh_key)
            except:
                raise ExceptionPxssh('private ssh key does not exist')
            ssh_options = ssh_options + ' -i %s' % (ssh_key)
        cmd = "ssh %s -l %s %s" % (ssh_options, username, iphost)
        
        # This does not distinguish between a remote server 'password' prompt
        # and a local ssh 'passphrase' prompt (for unlocking a private key).
        child = pexpect.spawn(cmd,dimensions=dimensions)
        i = child.expect(["(?i)are you sure you want to continue connecting", original_prompt, "(?i)(?:password)|(?:passphrase for key)", "(?i)permission denied", "(?i)terminal type", pexpect.TIMEOUT, "(?i)connection closed by remote host"], timeout=login_timeout)

        # First phase
        if i==0:
            # New certificate -- always accept it.
            # This is what you get if SSH does not have the remote host's
            # public key stored in the 'known_hosts' cache.
            child.sendline("yes")
            i = child.expect(["(?i)are you sure you want to continue connecting", original_prompt, "(?i)(?:password)|(?:passphrase for key)", "(?i)permission denied", "(?i)terminal type", pexpect.TIMEOUT])
        if i==2: # password or passphrase
            child.sendline(password)
            i = child.expect(["(?i)are you sure you want to continue connecting", original_prompt, "(?i)(?:password)|(?:passphrase for key)", "(?i)permission denied", "(?i)terminal type", pexpect.TIMEOUT])
        if i==4:
            child.sendline(terminal_type)
            i = child.expect(["(?i)are you sure you want to continue connecting", original_prompt, "(?i)(?:password)|(?:passphrase for key)", "(?i)permission denied", "(?i)terminal type", pexpect.TIMEOUT])

        # Second phase
        if i==0:
            # This is weird. This should not happen twice in a row.
            child.close()
            raise ExceptionPxssh('Weird error. Got "are you sure" prompt twice.')
        elif i==1: # can occur if you have a public key pair set to authenticate.
            ### TODO: May NOT be OK if expect() got tricked and matched a false prompt.
            pass
        elif i==2: # password prompt again
            # For incorrect passwords, some ssh servers will
            # ask for the password again, others return 'denied' right away.
            # If we get the password prompt again then this means
            # we didn't get the password right the first time.
            child.close()
            raise ExceptionPxssh('password refused')
        elif i==3: # permission denied -- password was bad.
            child.close()
            raise ExceptionPxssh('permission denied')
        elif i==4: # terminal type again? WTF?
            child.close()
            raise ExceptionPxssh('Weird error. Got "terminal type" prompt twice.')
        elif i==5: # Timeout
            #This is tricky... I presume that we are at the command-line prompt.
            #It may be that the shell prompt was so weird that we couldn't match
            #it. Or it may be that we couldn't log in for some other reason. I
            #can't be sure, but it's safe to guess that we did login because if
            #I presume wrong and we are not logged in then this should be caught
            #later when I try to set the shell prompt.
            raise ExceptionPxssh('timeout')
        elif i==6: # Connection closed by remote host
            child.close()
            raise ExceptionPxssh('connection closed')
        else: # Unexpected
            child.close()
            raise ExceptionPxssh('unexpected login response')

        if type(callback) == types.FunctionType:
            callback()
        child.sendline()
        child.interact()
    
@perf.show_time_cost
def goexe(iphost, username, cmdstr, password='', ssh_key=None, max_try=2, timeout=3, conn_timeout=2, login_timeout=2, port=None):
       
    try:
        child = pxssh.pxssh(options={"ConnectTimeout":conn_timeout,"StrictHostKeyChecking": "no","UserKnownHostsFile": "/dev/null"},timeout=30)  # global timeout default is 30
        #child.force_password = True
        flag = False
        
        for idx in range(max_try):
                flag = child.login(iphost, username, password=password, ssh_key=ssh_key, port=port, login_timeout=login_timeout)
                if flag == True:
                    child.sendline(cmdstr)
                    child.prompt(timeout=timeout)  # match the prompt
                    resstr = child.before          # print everything before the prompt.
                    child.close()
                    ary = str(resstr).split("\n")
                    otext ="\n".join(ary[1:-1])
                    return (True,otext)
                    break
        return (False,None)
    except pxssh.ExceptionPxssh,e:
        return (False,str(e))
    except pexpect.exceptions.EOF, e:
        return (False,"EOF")
    except Exception,e:
        return False,traceback.format_exc()

def send(iphost, user, filename, dst_path, password="", ssh_key=None, timeout=10, conn_timeout=2, port=22):
    """
    attention: timeout shoud great than conn_timeout, just timeout > conn_timeout
    """
    try:
        if not password and not ssh_key:return False,""
        timeout = timeout if timeout else 10
        cmdline = 'scp -o ConnectTimeout=%s -P %s -p -r %s %s@%s:%s' % (conn_timeout, port, filename, user, iphost, dst_path)   
        if ssh_key:
            cmdline = 'scp -o ConnectTimeout=%s -P %s -i %s -r %s %s@%s:%s' % (conn_timeout,port, ssh_key, filename, user, iphost, dst_path)   
    
        flag = True
        allstr = ""

        TIMEOUT = pexpect.TIMEOUT
        EOF = pexpect.EOF

        child = pexpect.spawn(cmdline, timeout=30)
        
        exp_ary = [
            "yes/no\)\?", # 0
            "assword:",  # 1
            TIMEOUT,  # 2
            EOF, # 3
            "FATAL",  # 4
            "[N|n]o route to host",  # 5
            "Connection [R|r]efused",  # 6
            "Host key verification failed",  # 7
            "Illegal host key",  # 8
            "Connection Timed Out",  # 9
            "Interrupted system call",  # 10
            "connection lost",  #11
            "lost connection",  # 12
            "Authentication failed",  # 13
            "Destination Unreachable",  # 14
            "no such file",  # 15
            "Killed by signal 1",  # 16
            "[N|n]o such file or directory",  # 17
            "(?i)permission denied",  # 18
            "(?i)terminal type",  # 19
            "(?i)connection closed by remote host",  # 20
        ]
        exit_flag = False
        while exit_flag == False:
            i = child.expect(exp_ary, timeout=timeout)

            if i==0:
                child.sendline("yes")
                continue
            if i==1: # password or passphrase
                child.sendline(password)
                continue
            if i == 2:
                flag = False
                allstr = "Timeout"
                exit_flag = True  # timeout,退出
                break
            if i == 3:
                exit_flag = True  # eof,退出
                break
            if i not in [0, 1, 3]:
                flag = False
                allstr = exp_ary[i]
                break
                #exit_flag = True
            #print i,i
        if flag == True:
            allstr = child.before
        child.close()
        #child.kill()
        return (flag, allstr)
    except Exception,e:
        return False,traceback.format_exc()

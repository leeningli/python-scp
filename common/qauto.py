#!/usr/bin/python
# -*- encoding=utf-8 -*-
# version: 1.0
# auth: leeningli
# date: 2018-02-12

import types
from . import utils

class QAuto(object):
    
    def __init__(self, debug=False):
        self._debug = debug
        self._ip_user_passwd_dict = {}

    def _set_right_passwd(self, iphost, user, passwd):
        key = "%s_%s" % (iphost,user)
        iup_map = self._ip_user_passwd_dict
        iup_map[key] = passwd
    
    def _get_right_passwd(self, iphost, user):
        key = "%s_%s" % (iphost,user)
        return self._ip_user_passwd_dict.get(key,None)
        
    def try_to_send(self, iphost, filename, dst_path, user=None, genpasswds=None, timeout=60, port=22):
        right_passwd = self._get_right_passwd(iphost, user)
        if right_passwd:
            flag, allstr = utils.send(iphost, user, filename, dst_path, password=right_passwd, ssh_key=None, timeout=timeout, conn_timeout=2, port=port)
            return (flag, [right_passwd], allstr)
        
        if type(genpasswds) != types.FunctionType:
            return (False, [], "No Method to Produce Passwords")
        
        passwds = genpasswds(iphost, user)
        if not passwds:
            return (False, [], "No Passwords")
    
        (flag, lst_passwd, allstr) = (False, [], "Unkown")
        for password in passwds:
            flag, allstr = utils.send(iphost, user, filename, dst_path, password=password, ssh_key=None, timeout=timeout, conn_timeout=2, port=port)
            lst_passwd.append(password)
            if flag == True:
                self._set_right_passwd(iphost, user, password)
                break
        return flag, lst_passwd, allstr
    
    def try_to_exe(self, iphost, cmdstr, user=None, genpasswds=None, timeout=10, port=22):
        right_passwd = self._get_right_passwd(iphost, user)
        if right_passwd:
            flag, allstr = utils.goexe(iphost, user, cmdstr, password=right_passwd, max_try=1, timeout=timeout, port=port)
            return (flag, [right_passwd], allstr)
        
        if type(genpasswds) != types.FunctionType:
            return (False, [], "No Method to Produce Passwords")
        
        passwds = genpasswds(iphost, user)
        if not passwds:
            return (False, [], "No Passwords")
    
        (flag, lst_passwd, allstr) = (False, [], "Unkown")
        for password in passwds:
            flag, allstr = utils.goexe(iphost, user, cmdstr, password=password, max_try=1, timeout=timeout, port=port)
            lst_passwd.append(password)
            if flag == True:
                self._set_right_passwd(iphost, user, password)
                break
        return flag, lst_passwd, allstr

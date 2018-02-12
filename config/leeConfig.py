#!/usr/bin/python
# -*- encoding=utf-8 -*-
# version: 1.0
# auth: leeningli
# date: 2018-02-12
# config file,set your username and password

class comm(object):
    def __init__(self):
        self._usermap = {
            "uat":{
                "root":["qazwsx1234","asdf12345"],
                "admin":["qazwsx1234","asdf12345"],
            },
            "prd":{
                "root":["qazwsx1234","asdf12345"],
                "admin":["qazwsx1234","asdf12345"],
            }
        }
    
    def get_usermap(self):
        return self._usermap

def get_passwds(ipaddr, user):
    USERPSW_MAP = comm().get_usermap()
    env = "prd"
    if str(ipaddr).startswith("10.25."):
        env = "uat"
    passwds = list()
    try:
        conf = USERPSW_MAP.get(env,{})
        passwds = conf.get(user,[])
        if env == "prd":
            conf = USERPSW_MAP.get("uat", {})
            sends = conf.get(user,[])
            passwds.extend(sends)
        else:
            conf = USERPSW_MAP.get("prd", {})
            sends = conf.get(user,[])
            passwds.extend(sends)
        return passwds
    except Exception:
        return None
    
    
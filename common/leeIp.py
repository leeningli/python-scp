#!/usr/bin/python
# -*- encoding=utf-8 -*-
# version: 1.0
# auth: leeningli
# date: 2018-02-12

def is_ip(ipaddr):
    ipsegs = str(ipaddr).split(".")
    if len(ipsegs) != 4:
        return False
    try:
        for seg in ipsegs:
            seg_int = int(seg)
            if seg_int < 0 or seg_int > 255 or len(str(seg_int)) != len(seg):
                return False
    except Exception:
        return False
    return True
#!/usr/bin/python
# -*- encoding=utf-8 -*-
# version: 1.0
# auth: leeningli
# date: 2018-02-12

def show_time_cost(func):
    def _deco(*args, **kwargs):
        import time
        t1 = int(time.time()*1000)
        ret = func(*args, **kwargs)
        cost = (int(time.time()*1000) - t1)
        print("[PERF-BEGIN]")
        print("Method: %s" % func.__name__)
        print("Args: %s" % str(args))
        print("Kwargs: %s" % str(kwargs))
        print("Cost: %s(ms)" % cost)
        print("[PERF-END]")
        return ret
    return _deco
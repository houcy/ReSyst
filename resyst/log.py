#!/usr/bin/env python
# coding: utf-8
"""
    resyst.log
    ~~~~~~~~~~~~~

    TODO: Description

    :copyright: 2017, Jonathan Racicot, see AUTHORS for more details
    :license: MIT, see LICENSE for more details
"""
def debug(_msg):
    log("[>] {:s}".format(_msg))

def error(_msg):
    log("[-] {:s}".format(_msg))

def warn(_msg):
    log("[!] {:s}".format(_msg))

def info(_msg):
    log("[=] {:s}".format(_msg))

def log(_msg): print (_msg, flush=True)

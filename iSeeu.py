#! /usr/bin/env python
#coding=utf-8

import isee
if __name__=="__main__":
    #logfile=log_stream.log_stream("main")
    iseeu=isee.iSeeu_App(redirect=True,filename="iseeu.log")
    iseeu.MainLoop()
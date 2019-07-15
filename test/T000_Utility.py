#!/usr/bin/python3
import sys,os,getopt,json
strLibPath = os.path.split(sys.argv[0])[0]
strLibPath = os.path.abspath(strLibPath + "/../")
sys.path.append(strLibPath)

from A3Lib import *
import A3Lib.Utility as AU

opts,args = getopt.gnu_getopt(sys.argv[1:],"f:",["ask","why="])
conf = [f[1] for f in opts if f[0] == "-f"]
conf = AU.dGetSetting(conf[0])

strWorkDir = os.getcwd()
lAB1Files = AU.lGetAB1Files(strWorkDir)
print("\n".join(lAB1Files))
print(AU.dRunExternalProg([conf['ExternalProg']['ttuner'],'-sa','all.seq', '-qa','all.seq.qual'," ".join(lAB1Files)])) 

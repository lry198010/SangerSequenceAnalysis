#!/usr/bin/python3
import sys,os,getopt,json
strLibPath = os.path.split(sys.argv[0])[0]
strLibPath = os.path.abspath(strLibPath + "/../")
sys.path.append(strLibPath)

from A3Lib import *
import A3Lib.Utility as AU
import A3Lib.Quality as AQ
import A3Lib.Assembly as AA

conf = AU.dGetSetting('/home/lry/soft/SangerSequenceAnalysis/config.default')
strDir = os.path.abspath(sys.argv[1])
lTtunerPars = [conf['BaseCalling']['Program'],conf['BaseCalling']['Params']]
strSeqFile = strDir + '/' + conf['rawSeq']
strQualFile = strDir + '/' + conf['rawQual']
strWorkDir = os.getcwd()
lAB1Files = AU.lGetAB1Files(strWorkDir)
dSeq,dQual,lCallFail = AU.dBaseCallingByTtunerPerAB1(lTtunerPars,lAB1Files,'.seq','.qual',0,1)
print(dSeq.keys())

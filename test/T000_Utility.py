#!/usr/bin/python3
import sys,os,getopt,json
strLibPath = os.path.split(sys.argv[0])[0]
strLibPath = os.path.abspath(strLibPath + "/../")
sys.path.append(strLibPath)

from A3Lib import *
import A3Lib.Utility as AU
import A3Lib.Quality as AQ

opts,args = getopt.gnu_getopt(sys.argv[1:],"f:",["ask","why="])
conf = [f[1] for f in opts if f[0] == "-f"]
conf = AU.dGetSetting(conf[0])

strWorkDir = os.getcwd()
print(strWorkDir)
lAB1Files = AU.lGetAB1Files(strWorkDir)
#print(AU.iGetSeqQualFileByTtuner([conf['ExternalProg']['ttuner'], '-sa', strWorkDir + "/" + conf['rawSeq'],'-qa', strWorkDir + '/' + conf['rawQual'], '-if'], lAB1Files, strWorkDir + '/' + conf['AB1ListFile']))

#print(AU.dGetSeqFromFastFile(strWorkDir + '/' + conf['rawSeq']))
#print(AU.dGetQualFromFastFile(strWorkDir + '/' + conf['rawQual']))
#print(AQ.dGetSeqQualStatByTtunerOut(strWorkDir + '/' + conf['rawSeq']))
#AQ.dQualityStat(lAB1Files,conf,strWorkDir)
strSeqFile = strWorkDir + '/' + conf['rawSeq']
dCleanCover = dict()
#dVectorStat = AQ.dGetSeqVectorStat(strSeqFile,conf,strWorkDir,dCleanCover)
dLQStat = AQ.dGetSeqQualStatByTtunerOut(strSeqFile,conf,strWorkDir,dCleanCover)

for k,v in dLQStat.items():
    print(v + [k])

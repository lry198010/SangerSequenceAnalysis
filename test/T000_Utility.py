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

dQualStat = AQ.dQualityStat(lAB1Files,conf,strWorkDir)
for k,lStat in dQualStat.items():
    print(lStat)

#strSeqFile = strWorkDir + '/' + conf['rawSeq']
#dLQCover = dict()
#dLQStat = AQ.dGetSeqQualStatByTtunerOut(strSeqFile,conf,strWorkDir,dLQCover)
#dVectorCover = dict()
#dVectorStat = AQ.dGetSeqVectorStat(strSeqFile,conf,strWorkDir,dVectorCover)
#AQ.bRefineQVRegion(dVectorCover,conf)
#dCombinedCover = AQ.dCleanCoverCombine([dLQCover,dVectorCover])
#dHQRegion = AQ.dGetMaxRegion(dCombinedCover,conf)
#for k in dCombinedCover.keys():
#    print(k)
#    if k in dLQCover: print(dLQCover[k])
#    if k in dVectorCover: print(dVectorCover[k])
#    print(dCombinedCover[k])
#    print(dHQRegion[k])

#dLQStat = AQ.dGetSeqQualStatByTtunerOut(strSeqFile,conf,strWorkDir,dCleanCover)

#for k,v in dLQStat.items():
#    print(v + [k])

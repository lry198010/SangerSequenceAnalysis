#!/usr/bin/python3
import sys,os,getopt,json
strLibPath = os.path.split(sys.argv[0])[0]
strLibPath = os.path.abspath(strLibPath + "/../")
sys.path.append(strLibPath)

from A3Lib import *
import A3Lib.Utility as AU
import A3Lib.Quality as AQ
import A3Lib.Assembly as AA

opts,args = getopt.gnu_getopt(sys.argv[1:],"f:",["ask","why="])
conf = [f[1] for f in opts if f[0] == "-f"]
conf = AU.dGetSetting(conf[0])

strWorkDir = os.getcwd()
print(strWorkDir)

lAB1Files = AU.lGetAB1Files(strWorkDir)
lAB1 = [os.path.split(i)[1] for i in lAB1Files]

dRegion = dict()
dQualStat = AQ.dQualityStat(lAB1Files,conf,strWorkDir,dRegion)
for k,lStat in dRegion.items():
    if dRegion[k][0] == -1: del dRegion[k]

strSeqFile = strWorkDir + '/' + conf['rawSeq']
strQualFile = strWorkDir + '/' + conf['rawQual']
dHQSeq = AU.dGetSubSeqFromFile(strSeqFile,dRegion,-1,1)
dHQQual = AU.dGetSubQualFromFile(strQualFile,dRegion,-1,1)
sQualRm = set(lAB1) - set(dHQSeq.keys())
#print(len(dHQSeq),len(dHQQual))
dSeqASStat = dict()
dASStat = AA.dCap3Assembly(dHQSeq,dHQQual,conf,strWorkDir,dSeqASStat)
dQualRm = dict()
for strSeqId in sQualRm:
    dSeqASStat[strSeqId] = 'R'
    strSample = AU.strGetAB1SampleName(strSeqId,'.',1)
    if not strSample in dQualRm:
        dQualRm[strSample] = []
    dQualRm[strSample].append(strSeqId)

for strSeqId in dQualStat.keys():
    if strSeqId in dSeqASStat:
        dQualStat[strSeqId].append(dSeqASStat[strSeqId])
    else:
        dQualStat[strSeqId].append('M')

strQCFile = strWorkDir + '/' + conf['Qual']['SaveTo']
lQCTitle = ['SampleName','SeqFile','rawLength','LowQualLen','LowQualLen%','HQRegion','LQRegion','VectLen','VectLen%','NVectRegion','VectRegion','LVLen','LVLen%','HRegion','PassRe    gionStart','passRegionEnd','Stat[M/R/E/S/A]']
AU.bWriteDLTable(dQualStat,strQCFile,lQCTitle,0,'\r\n')

for strSample in dASStat.keys():
    if strSample in dQualRm:
        dASStat[strSample] += [len(dQualRm[strSample]),';'.join(dQualRm[strSample])]
    else:
        dASStat[strSample] += [0,''] 

strASFile = strWorkDir + '/' + conf['Assembly']['Report']
lASTitle = ['SampleName','AssemblyStat','ContigNum','ContigLen','ContigAB1','SingletNum','SingletAB1','ExcludeNum','ExcludeAB1','QCRemoveNum','QCRemomveAB1']
AU.bWriteDLTable(dASStat,strASFile,lASTitle,0,'\r\n')

dKeeps = {
            'KeepAB1list' : 'all.ab1.list',
            'KeeprawSeq'  : 'all.fa',
            'KeeprawQual' : 'all.fa.qual',
            'Keepbln'     : 'all.bln',
            'KeepHQSeq'   : 'all.hq.fa',
            'HQQual'      : 'all.hq.fa.qual',
            'KeepHQQual'  : 'all.hq.fa.qual'
        }
for k,v in dKeeps.items():
    strFile = strWorkDir + '/' + v
    if not conf[k] and os.path.isfile(strFile):
        os.remove(strFile)

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

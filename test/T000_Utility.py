#!/usr/bin/python3
import sys,os,getopt,json
strLibPath = os.path.split(sys.argv[0])[0]
strLibPath = os.path.abspath(strLibPath + "/../")
sys.path.append(strLibPath)
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

print(len(lAB1))
print(len(AU.lGetFoward(lAB1,2)))

sys.exit(0)

lTtunerPars = [conf['BaseCalling']['Program'],conf['BaseCalling']['Params']]
strSeqSuff = conf['BaseCalling']['SeqSuff']
strQualSuff = conf['BaseCalling']['QualSuff']
strSeqFile = strWorkDir + '/' + conf['rawSeq']
strQualFile = strWorkDir + '/' + conf['rawQual']
strToList = strWorkDir + '/' + conf['AB1ListFile']

#dSeq = AU.dBaseCallingByTtuner(lTtunerPars,lAB1Files,strSeqFile,strQualFile,strToList)
#sAB1NoCalled = set(lAB1) - set(dSeq.keys())

dSeq,dQual,sAB1NoCalled = AU.dBaseCallingByTtunerPerAB1(lTtunerPars,lAB1Files,strSeqSuff,strQualSuff,0,0)
if len(sAB1NoCalled) > 0:
    print('警告：有AB1文件不能转换为序列文件，' + ','.join(sAB1NoCalled))
else:
    print('完成：BaseCalling')

dSample = AU.dGetAB1Sample(lAB1,".",1)

print('开始：质量检测')
dRegion = dict()
dQualStat = AQ.dQualityStat(strSeqFile,conf,strWorkDir,dRegion)
for k,lStat in dRegion.items():
    if dRegion[k][0] == -1: del dRegion[k]
print('完成：质量检测')

dHQSeq = AU.dGetSubSeqFromFile(strSeqFile,dRegion,-1,1)
dHQQual = AU.dGetSubQualFromFile(strQualFile,dRegion,-1,1)
sQualRm = set(lAB1) - set(dHQSeq.keys())

print('开始：序列拼接')
dSeqASStat = dict()
dASStat = AA.dCap3Assembly(dHQSeq,dHQQual,conf,strWorkDir,dSeqASStat)
print('完成：序列拼接')

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

for strSample in dSample.keys():
    if not strSample in dASStat:
        dASStat[strSample] = [strSample,'N',0,0,'',0,'',0,'',0,'']
    dASStat[strSample] += [len(dSample[strSample]), ';'.join(dSample[strSample])]

strASFile = strWorkDir + '/' + conf['Assembly']['Report']
lASTitle = ['SampleName','AssemblyStat','ContigNum','ContigLen','ContigAB1','SingletNum','SingletAB1','ExcludeNum','ExcludeAB1','QCRemoveNum','QCRemomveAB1','NumAB1Files','AllAB1']
AU.bWriteDLTable(dASStat,strASFile,lASTitle,0,'\r\n')

iNumNAssembly = 0 # Number of sample cann't assembly
iNumPAssembly = 0 # Number of sample patial assembly
iNumAAssembly = 0 # Number of sample complete assembly

for k,lv in dASStat.items():
    if lv[1] == 'A': iNumAAssembly += 1
    if lv[1] == 'P': iNumPAssembly += 1
    if lv[1] == 'N': iNumNAssembly += 1

print('完成：总样品数,',len(dSample),';总测序文件数,',len(lAB1),';完全拼接样品数，',iNumAAssembly,';部分拼接样品数，',iNumPAssembly,';没有拼接样品数，',iNumNAssembly)

print('开始:清理临时文件')
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

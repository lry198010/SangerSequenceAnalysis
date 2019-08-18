#!/usr/bin/python3
import sys,os,getopt,json,random,time
strLibPath = os.path.split(sys.argv[0])[0]
strLibPath = os.path.abspath(strLibPath + "/../")
sys.path.append(strLibPath)
import A3Lib.Utility as AUtil
import A3Lib.Quality as AQual
import A3Lib.Assembly as AASS

def prtUsage():
    print('用法：',sys.argv[0],'-D <WorkDir>')

strInDir = os.getcwd()
opts,args = getopt.gnu_getopt(sys.argv[1:],'D:h')
for opt in opts:
    if opt[0] == '-h' : 
        prtUsage()
        sys.exit(0)
    if opt[0] == '-D' : strInDir = os.path.abspath(opt[1])
    #if opt[0] == '-M' : bSubDirModel = int(opt[1]) 
    #if opt[0] == '-F' : strConfF = opt[1]

strConfDef = 'config.default'
strConfDef = os.path.split(os.path.abspath(__file__))[0] + '/' + strConfDef

dConfDef = AUtil.dGetSetting(strConfDef)

conf = dConfDef
dConfHet = conf['HetezygotesCall']

lDirs = [strInDir]

for strInDir in lDirs:
    lAB1Files = AUtil.lGetAB1Files(strInDir)
    if len(lAB1Files) == 0: continue

    lHetProgs = [dConfHet['Program'],'-min_ratio',dConfHet['min_ratio']]
    dSeq,dQual,dFail =AUtil.dHetCallingByTtunerPerAB1(lHetProgs,lAB1Files,dConfHet['PhdSuff'],1,0) 
    for strSeqId,strSeq in dSeq.items():
        print('>',strSeqId)
        print(strSeq)
    for strSeqId,lQual in dQual.items():
        print('>',strSeqId)
        print(' '.join(lQual))

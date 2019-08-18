#!/usr/bin/python3
import sys,os,getopt,json,random,time
strLibPath = os.path.split(sys.argv[0])[0]
strLibPath = os.path.abspath(strLibPath + "/../")
sys.path.append(strLibPath)
import A3Lib.Utility as AUtil
import A3Lib.Quality as AQual
import A3Lib.Assembly as AASS

def prtUsage():
    print('用法：',sys.argv[0],'-D <WorkDir> -V[VectorTrim] -F <confiFile> -M <runModel[0|1]>')
    print('\trunModel[0|1]:0:just run in the give directory;1 run in the subdirectory in give Directory')

strConfDef = 'config.default'
strConfDef = os.path.split(os.path.abspath(__file__))[0] + '/' + strConfDef

dConfDef = AUtil.dGetSetting(strConfDef)
opts,args = getopt.gnu_getopt(sys.argv[1:],'F:VD:M:h')

strConfF = '' 
bVectorTrim = 0
strInDir = os.getcwd()
bSubDirModel = 0 # AutoModel, scan all sub directory and work in it 
for opt in opts:
    if opt[0] == '-h' : 
        prtUsage()
        sys.exit(0)
    if opt[0] == '-V' : bVectorTrim = 1
    if opt[0] == '-D' : strInDir = os.path.abspath(opt[1])
    if opt[0] == '-M' : bSubDirModel = int(opt[1]) 
    if opt[0] == '-F' : strConfF = opt[1]

if not os.path.isdir(strInDir):
    print('错误：目录不存在，' + strInDir)
    prtUsage()
    sys.exit(1)

strTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
print('拼接开始:' + strTime)
sys.stderr.write('拼接开始:' + strTime + '\n')

print('\tParam:',sys.argv[0])
print('\t\tWorkDir:',strInDir)
print('\t\tVector Screen:',bVectorTrim)
print('\t\tRun Model:',bSubDirModel)
print('\t\tConfigure File:',strConfF)

lDirs = [strInDir]
if not bSubDirModel == 0: lDirs = AUtil.lGetDirs(strInDir)
print('\t总计目录数(单订数):',len(lDirs))

conf = dConfDef

if bVectorTrim == 1:
    conf['Qual']['VectorScreen'] = bVectorTrim

for strWorkDir in lDirs:
    strTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    print('\t\t开始分析目录(订单):',strWorkDir,strTime)
    sys.stderr.write('\t\t开始分析目录(订单):' + strWorkDir + ' ' + strTime + '\n')
    if AUtil.bIsDirAnalysis(strWorkDir,conf):
        print('\t\t\t目录分析过，不执行分析！')
        continue
    
    lAB1Files = AUtil.lGetAB1Files(strWorkDir)
    if len(lAB1Files) == 0: continue
    lAB1Files = [AUtil.strWhiteSpaceRMFromFileName(f) for f in lAB1Files]

    random.shuffle(lAB1Files)
    lAB1 = [os.path.split(i)[1] for i in lAB1Files]

    lProgPars = [conf['BaseCalling']['Program'],conf['BaseCalling']['Params']]
    strSeqSuff = conf['BaseCalling']['SeqSuff']
    strQualSuff = conf['BaseCalling']['QualSuff']
    strSeqFile = strWorkDir + '/' + conf['rawSeq']
    strQualFile = strWorkDir + '/' + conf['rawQual']
    strToList = strWorkDir + '/' + conf['AB1ListFile']
    iSampleIndex = conf['SampleIndex']

    #dSeq = AUtil.dBaseCallingByTtuner(lProgPars,lAB1Files,strSeqFile,strQualFile,strToList)
    #sAB1NoCalled = set(lAB1) - set(dSeq.keys())
    print('\t\t\t开始：BaseCalling')
    dSeq,dQual,sAB1NoCalled = AUtil.dBaseCallingByTtunerPerAB1(lProgPars,lAB1Files,strSeqSuff,strQualSuff,0,0)
    if len(sAB1NoCalled) > 0:
        print('\t\t\t\t警告：有AB1文件不能转换为序列文件，' + ','.join(sAB1NoCalled))
    else:
        print('\t\t\t完成：BaseCalling')

    if len(dSeq) == 0:continue

    AUtil.bWriteSeqToFile(dSeq,strSeqFile)
    AUtil.bWriteQualToFile(dQual,strQualFile)

    dSample = AUtil.dGetAB1Sample(lAB1,".",iSampleIndex)

    print('\t\t\t开始：质量检测')
    dRegion = dict()
    dQualStat = AQual.dQualityStat(strSeqFile,conf,strWorkDir,dRegion)
    lEmptyHQ = []
    for k in dRegion.keys():
        if dRegion[k][0] == -1: lEmptyHQ.append(k)
    for k in lEmptyHQ:
        del dRegion[k]
    print('\t\t\t完成：质量检测')

    dHQSeq = AUtil.dGetSubSeqFromFile(strSeqFile,dRegion,-1,1)
    dHQQual = AUtil.dGetSubQualFromFile(strQualFile,dRegion,-1,1)
    sQualRm = set(lAB1) - set(dHQSeq.keys())

    print('\t\t\t开始：序列拼接')
    dSeqASStat = dict()
    dASStat = AASS.dCap3Assembly(dHQSeq,dHQQual,conf,strWorkDir,dSeqASStat,'\t\t\t\t')
    print('\t\t\t完成：序列拼接')

    dQualRm = dict()
    for strSeqId in sQualRm:
        dSeqASStat[strSeqId] = 'R'
        strSample = AUtil.strGetAB1SampleName(strSeqId,'.',1)
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
    AUtil.bWriteDLTable(dQualStat,strQCFile,lQCTitle,0,'\r\n')

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
    AUtil.bWriteDLTable(dASStat,strASFile,lASTitle,0,'\r\n')

    iNumNAssembly = 0 # Number of sample cann't assembly
    iNumPAssembly = 0 # Number of sample patial assembly
    iNumAAssembly = 0 # Number of sample complete assembly

    for k,lv in dASStat.items():
        if lv[1] == 'Y': iNumAAssembly += 1
        if lv[1] == 'P': iNumPAssembly += 1
        if lv[1] == 'N': iNumNAssembly += 1

    print('\t\t\t订单(目录)拼接结果:',strWorkDir)
    print('\t\t\t\t总样品数:',len(dSample))
    print('\t\t\t\t总测序文件数:',len(lAB1))
    print('\t\t\t\t完全拼接样品数:',iNumAAssembly)
    print('\t\t\t\t部分拼接样品数:',iNumPAssembly)
    print('\t\t\t\t没有拼接样品数:',iNumNAssembly)

    print('\t\t\t开始:清理临时文件')
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

    print('\t\t\t完成:清理临时文件')
    print('\t\t完成分析目录(订单):',strWorkDir,'\n\n')

strTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
print('拼接结束:' + strTime)
sys.stderr.write('拼接结束:' + strTime + '\n')

import os,sys,fileinput #,Utility
strLibPath = os.path.abspath(__file__) 
strLibPath = os.path.split(strLibPath)[0]
sys.path.append(strLibPath)
import Utility

def dQualityStat(lAB1Files,conf,strWorkDir):
    strAB1ListFile = strWorkDir + '/' + conf['AB1ListFile']
    strRawSeq = strWorkDir + '/' + conf['rawSeq']
    strRawQual = strWorkDir + '/' + conf['rawQual']
    lTtunerPar = [conf['ExternalProg']['ttuner'], '-sa', strRawSeq, '-qa', strRawQual,'-if', strAB1ListFile]
    iNumAB1File = Utility.iGetSeqQualFileByTtuner(lTtunerPar, lAB1Files, strAB1ListFile)
    if iNumAB1File > 0:
        dCleanCover = dict()
        dHQStat = dGetSeqQualStatByTtunerOut(strRawSeq,dCleanCover)
        print(dCleanCover)
        #dVectorStat = dGetSeqVectorStat()

# dAb1File = {"sample":[filepath,filepath,...],...}
def getAB1Entries(dAB1File):
    return "ok"

def dGetCleanCover(strSeqFile,dCleanCover = {}):
    dSeq = Utility.dGetSeqFromFastFile(strSeqFile)
    for strSeqN,strSeq in dSeq.items():
        strSeqIdentity = strSeqN.split()[0]
        if not strSeqIdentity in dCleanCover:
            dCleanCover[strSeqIdentity] = [0] * len(strSeq)
    return dCleanCover

# get high quality data from output of ttuner 
# seqname seqlen high_Quality_Start len_of_high_Quality_Region
def dGetSeqQualStatByTtunerOut(strSeqQualFile,conf,strWorkDir,dCleanCover = {}):
    dHQStat = dict()
    dSeq = Utility.dGetSeqFromFastFile(strSeqQualFile)
    for strSeqN in dSeq.keys():
        strSeqIdentity,iSeqLen, iHQStart, iHQLen = strSeqN.split()
        iSeqLen = int(iSeqLen)
        iHQStart = int(iHQStart)
        iHQLen = int(iHQLen)
        if not strSeqN in dCleanCover:
            dCleanCover[strSeqIdentity] = [0] * iSeqLen
        for i in range(0,iHQStart-1):
            dCleanCover[strSeqIdentity][i] += 1
        for i in range(iHQStart + iHQLen-1,iSeqLen):
            dCleanCover[strSeqIdentity][i] += 1
        lHQStat = [Utility.strGetAB1SampleName(strSeqIdentity),strSeqIdentity,int(iSeqLen)]
        if iHQLen > 0:
            lHQStat.append(iSeqLen - iHQLen)
            lHQStat.append((iSeqLen - iHQLen)/iSeqLen * 100)
            lLowRegion = []
            if iHQStart > 1: lLowRegion.append('1-' + str(iHQStart-1))
            if iHQStart + iHQLen < iSeqLen: lLowRegion.append(str(iHQStart + iHQLen) + '-' + str(iSeqLen))
            lHQStat.append(';'.join(lLowRegion))
            lHQStat.append(str(iHQStart) + "-" + str(iHQStart + iHQLen - 1))
        else:
           lHQStat.append(iSeqLen)
           lHQStat.append(100)
           lHQStat.append('1-' + str(iSeqLen-1))
           lHQStat.append('')
        dHQStat[strSeqN] = lHQStat
    return dHQStat

def dGetSeqVectorStat(strSeqFile,conf,strWorkDir,dCleanCover={}):
    lBlast = [conf['ExternalProg']['blastn'], conf['Qual']['Parblastn'],'-query', strSeqFile]
    strStam = strWorkDir + "/" + conf['Stam'] + "."
    strBlastSuff = conf['Qual']['blastSuff']

    dBlnFiles = []

    for VectorName,VectorSeq in conf['Qual']['Vector'].items():
        if os.path.isfile(VectorSeq):
            strBlastOut = strStam + VectorName + strBlastSuff
            print("Run blastn:" + strBlastOut)
            Utility.dRunExternalProg(lBlast + ['-subject',VectorSeq,'-out', strBlastOut])
            dBlnFiles.append(strBlastOut)

    dVectorRegion = dict()
    dCleanCover = dGetCleanCover(strSeqFile,dCleanCover)
    if len(dBlnFiles) > 0:
        for strBlnFile in dBlnFiles:
            dTmpVectorRegion = dGetSeqVectorCover(strBlnFile,conf,dCleanCover)
            for strSeqId,strRegion in dTmpVectorRegion.items():
                if not strSeqId in dVectorRegion:
                    dVectorRegion[strSeqId] = strRegion
                else:
                    dVectorRegion[strSeqId] += ';' + strRegion

    dVectorStat = dGetQVStat(dCleanCover) 
    for strSeqId in dVectorRegion.keys():
        if strSeqId in dVectorStat:
            dVectorStat[strSeqId].append(dVectorRegion[strSeqId])
        else:
            dVectorStat[strSeqId] = [0,0,'','']
    for strSeqId in dVectorStat:
        if not strSeqId in dVectorRegion:
            dVectorStat[strSeqId].append('')
    return dVectorStat


def dGetSeqVectorCover(strBlnFile,conf,dCleanCover={}):
    dSeqVectorRegion = dict()
    isAcc   = conf['Qual']['sAcc']
    iqAcc   = conf['Qual']['qAcc']
    iqLen   = conf['Qual']['qLen']
    iqStart = conf['Qual']['qStart']
    iqEnd   = conf['Qual']['qEnd']
    isStart = conf['Qual']['sStart']
    isEnd   = conf['Qual']['sEnd']
    with fileinput.input(strBlnFile) as lines:
        for line in lines:
            line = line.strip()
            fields = line.split()
            if not fields[iqAcc] in dCleanCover:
                dCleanCover[fields[iqAcc]] = [0] * int(fields[iqLen])
            for i in range(int(fields[iqStart])-1,int(fields[iqEnd])):
                dCleanCover[fields[iqAcc]][i] += 1
            if not fields[iqAcc] in dSeqVectorRegion:
                dSeqVectorRegion[fields[iqAcc]] = []
            strVectorRegion = fields[isAcc] + ':' 
            strVectorRegion += fields[iqStart] + '-' + fields[iqEnd]
            dSeqVectorRegion[fields[iqAcc]].append(strVectorRegion)
    for strSeqId in dSeqVectorRegion.keys():
        dSeqVectorRegion[strSeqId] = ';'.join(dSeqVectorRegion[strSeqId])
    return dSeqVectorRegion

# tb,total base of QV[Quality/Vector];
# tbp,percent of tb
# mcl, max continous length of nQV
def dGetQVStat(dCleanCover):
    dStat = dict()
    for strSeqId,lBase in dCleanCover.items():
        iNumBaseCovered = 0
        iLen = len(lBase)
        for i in lBase:
            if i > 0: iNumBaseCovered += 1
        lMaxHQRegion = lGetMaxRegion(lBase)
        dStat[strSeqId] = [iNumBaseCovered,
                iNumBaseCovered/iLen,
                '-'.join([str(i) for i in lMaxHQRegion])] 
    return dStat

def lGetMaxRegion(lBaseCover,conf = {}):
    iPos = -1
    iNum = 0
    lRegion = [-1,0]
    for i in range(0,len(lBaseCover)):
        if lBaseCover[i] == 0:
            if iPos == -1: iPos = i
            iNum += 1
        else:
            if lRegion[1] < iNum: lRegion = [iPos,iPos + iNum-1]
            if iNum > 0:
                iPos = -1
                iNum = 0
    if lRegion[1] < iNum: lRegion = [iPos,iPos + iNum-1]
    return lRegion


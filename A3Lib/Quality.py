import os,sys,fileinput #,Utility
strLibPath = os.path.abspath(__file__) 
strLibPath = os.path.split(strLibPath)[0]
sys.path.append(strLibPath)
import Utility

def dQualityStat(strSeqFileByTtuner,conf,strWorkDir,dHRegion={}):
    dStat = dict()
    dLQCover = dict()
    dLQStat = dGetSeqQualStatByTtunerOut(strSeqFileByTtuner,conf,strWorkDir,dLQCover)
    dVectorCover = dict()
    dVectorStat = dGetSeqVectorStat(strSeqFileByTtuner,conf,strWorkDir,dVectorCover)
    bRefineQVRegion(dVectorCover,conf)
    dCmbCover = dCleanCoverCombine([dLQCover,dVectorCover])
    dHQRegion = dGetMaxRegion(dCmbCover)
    dQVStat = dGetQVStat(dCmbCover)

    for k,lBase in dCmbCover.items():
        lStat = [Utility.strGetAB1SampleName(k),k,len(lBase)]

        if k in dLQStat:
            lStat += dLQStat[k]
        else:
            lStat += [0,0,'','']

        if k in dVectorStat: 
            lStat += dVectorStat[k]
        else:
            lStat += [0,0,'','']

        if k in dQVStat: 
            lStat += dQVStat[k]
        else:
            lStat += [0,0,'','']

        if k in dHQRegion: 
            lStat += dHQRegion[k]
        else:
            lStat += [-1,0]

        dStat[k] = lStat


    if not conf['Qual']['VectorScreen']:
        dHQRegion = dGetMaxRegion(dLQCover)
    for strSeqId,lRegion in dHQRegion.items():
        dHRegion[strSeqId] = lRegion

    return dStat

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
    dLQRegion = dict()
    dSeq = Utility.dGetSeqFromFastFile(strSeqQualFile)
    for strSeqN in dSeq.keys():
        strSeqId,iSeqLen, iHQStart, iHQLen = strSeqN.split()
        iSeqLen = int(iSeqLen)
        iHQStart = int(iHQStart)
        iHQLen = int(iHQLen)
        if not strSeqId in dCleanCover:
            dCleanCover[strSeqId] = [0] * iSeqLen

        lLowRegion = []
        if iHQLen > 0:
            for i in range(0,iHQStart-1):
                dCleanCover[strSeqId][i] += 1
            for i in range(iHQStart + iHQLen-1,iSeqLen):
                dCleanCover[strSeqId][i] += 1

            if iHQStart > 1: lLowRegion.append('1-' + str(iHQStart-1))
            if iHQStart + iHQLen < iSeqLen: lLowRegion.append(str(iHQStart + iHQLen) + '-' + str(iSeqLen))
        else:
            for i in range(0,iSeqLen):
                dCleanCover[strSeqId][i] += 1
            lLowRegion.append('1-' + str(iSeqLen-1))

        dLQRegion[strSeqId] =';'.join(lLowRegion)

    dLQStat = dGetQVStat(dCleanCover)
    for strSeqId in dLQRegion.keys():
        if strSeqId in dLQStat:
            dLQStat[strSeqId].append(dLQRegion[strSeqId])
        else:
            dLQStat[strSeqId] = [0,0,'','']
    for strSeqId in dLQStat:
        if not strSeqId in dLQRegion:
            dLQStat[strSeqId].append('')
    return dLQStat

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
            if not conf['Qual']['KeepBln']:
                if os.path.isfile(strBlnFile): os.remove(strBlnFile)


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
                iNumBaseCovered/iLen * 100,
                '-'.join([str(i) for i in lMaxHQRegion])] 
    return dStat

def dGetMaxRegion(dCover,conf = {}):
    dRegion = dict()
    for strSeqId,lCover in dCover.items():
        dRegion[strSeqId] = lGetMaxRegion(lCover)
    return dRegion

def lGetMaxRegion(lBaseCover,conf = {}):
    iPos = -1
    iNum = 0
    lRegion = [-1,0]
    for i in range(0,len(lBaseCover)):
        if lBaseCover[i] == 0:
            if iPos == -1: iPos = i
            iNum += 1
        else:
            if lRegion[1] < iNum: lRegion = [iPos + 1,iPos + iNum]
            if iNum > 0:
                iPos = -1
                iNum = 0
    if lRegion[1] < iNum: lRegion = [iPos + 1,iPos + iNum]
    return lRegion

def bRefineQVRegion(dCover,conf):
    iMaxRegion = conf['Qual']['MaxVectsKeep']
    for strSeqId,lBaseCover in dCover.items():
        iPos = -1
        iNum = 0
        for i in range(0,len(lBaseCover)):
            if lBaseCover[i] > 0:
                if iPos == -1: iPos = i
                iNum += 1
            else:
                if iNum <= iMaxRegion:
                    for j in range(iPos,iPos + iNum):
                        lBaseCover[j] = 0
                if iNum > 0:
                    iPos = -1
                    iNum = 0
        if iNum <= iMaxRegion:
            for j in range(iPos,iPos + iNum):
                lBaseCover[j] = 0

def dCleanCoverCombine(ldCleanCover):
    dCombined = dict()
    for dCleanCover in ldCleanCover:
        for strSeqId,lBase in dCleanCover.items():
            if not strSeqId in dCombined:
                dCombined[strSeqId] = [0] * len(lBase)
            for i in range(0,len(lBase)):
                dCombined[strSeqId][i] += lBase[i]
    return dCombined 

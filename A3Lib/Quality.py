import os,sys #,Utility
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
        #print(dCleanCover)
        #dVectorStat = dGetSeqVectorStat()

# dAb1File = {"sample":[filepath,filepath,...],...}
def getAB1Entries(dAB1File):
    return "ok"

def dGetCleanCover(strSeqFile):
    dCleanCover = dict()
    dSeq = Utility.dGetSeqFromFastFile(strSeqFile)
    for strSeqN,strSeq in dSeq.items():
        strSeqIdentity = strSeqN.split()[0]
        dCleanCover[strSeqIdentity] = [0] * len(strSeq)
    return dCleanCover

# get high quality data from output of ttuner 
# seqname seqlen high_Quality_Start len_of_high_Quality_Region
def dGetSeqQualStatByTtunerOut(strSeqQualFile,dCleanCover = {}):
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

def dGetSeqVectorStat(strSeqFile,conf,strWorkDir):
    lBlast = [conf['ExternalProg']['blastn'], conf['Qual']['Parblastn'],'-query', strSeqFile]
    strStam = strWorkDir + "/" + conf['Stam'] + "."
    strBlastSuff = conf['Qual']['blastSuff']
    for VectorName,VectorSeq in conf['Qual']['Vector'].items():
        if os.path.isfile(VectorSeq):
            strBlastOut = strStam + VectorName + strBlastSuff
            print("Run blastn:" + strBlastOut)
            Utility.dRunExternalProg(lBlast + ['-subject',VectorSeq,'-out', strBlastOut])

def dGetSeqVectorCover(strBlnFile,dCleanCover={}):
    dSeqVectorRegion = dict()



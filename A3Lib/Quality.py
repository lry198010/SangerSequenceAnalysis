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
    iNumAB1File = iGetSeqQualFileByTtuner(lTtunerPar, lAB1Files, strAB1ListFile)
    if iNumAB1File > 0:
        dHQStat = dGetSeqQualStatByTtunerOut(strRawSeq)
        dVectorStat = dGetSeqVectorStat()

# dAb1File = {"sample":[filepath,filepath,...],...}
def getAB1Entries(dAB1File):
    return "ok"

# get high quality data from output of ttuner 
# seqname seqlen high_Quality_Start len_of_high_Quality_Region
def dGetSeqQualStatByTtunerOut(strSeqQualFile):
    dHQStat = dict()
    dSeq = Utility.dGetSeqFromFastFile(strSeqQualFile)
    for strSeqN in dSeq.keys():
        strSeqIdentity,iSeqLen, iHQStart, iHQLen = strSeqN.split()
        iSeqLen = int(iSeqLen)
        iHQStart = int(iHQStart)
        iHQLen = int(iHQLen)
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

def dGetSeqVectorStat(strSeqFile,conf):
    pass

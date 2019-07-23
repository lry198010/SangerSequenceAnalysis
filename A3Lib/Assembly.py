import os,sys,fileinput #,Utility
strLibPath = os.path.abspath(__file__) 
strLibPath = os.path.split(strLibPath)[0]
sys.path.append(strLibPath)
import Utility

dKeeps = {
        'KeepSeq'      : '',
        'KeepQual'     : '.qual',
        'KeepCons'     : '.cap.cons',
        'KeepAce'      : '.cap.ace',
        'KeepLinks'    : '.cap.contigs.links',
        'KeepCQual'    : '.cap.contigs.qual',
        'KeepInfo'     : '.cap.info',
        'KeepSinglets' : '.cap.singlets'
         }
def dCap3Assembly(dSeq,dQual,conf,strWorkDir,dSeqStat = {}):
    dSamples = Utility.dGetAB1Sample(dSeq.keys(),'.',1)
    dAssemblyStat = dict()
    strReportF = strWorkDir + '/' + conf['Assembly']['Report']
    for strSample,lSeqs in dSamples.items():
        dSampleSeq = dict()
        dSampleQual = dict()
        lReport = [strSample]
        for strSeq in lSeqs:
            if (strSeq in dSeq) and (strSeq in dQual):
                dSampleSeq[strSeq] = dSeq[strSeq]
                dSampleQual[strSeq] = dQual[strSeq]
        lSeqRemoved = list(set(lSeqs) - set(dSampleSeq.keys()))
        for strSeq in lSeqRemoved:
            dSeqStat[strSeq] = 'E'
        if len(dSampleSeq) > 1:
            strSeqStam = strWorkDir + '/' + strSample + conf['Assembly']['SampleSeq']
            strSeqFile = strSeqStam
            strQualFile = strWorkDir + '/' + strSample + conf['Assembly']['SampleQual']
            print(strSeqFile,strQualFile)
            Utility.bWriteSeqToFile(dSampleSeq,strSeqFile,iBasesPerLine = 60,strNewLine = '\n')
            Utility.bWriteQualToFile(dSampleQual, strQualFile,iBasesPerLine = 60, strNewLine = '\n')
            lCap3Par = []
            lCap3Par.append(conf['ExternalProg']['cap3'])
            lCap3Par.append(strSeqFile)
            strConsFName = '>' + strSeqFile + conf['Assembly']['ConsFName']
            lCap3Par.append(strConsFName)
            print(' '.join(lCap3Par))
            Utility.dRunExternalProg(lCap3Par)
            strContigF = strSeqStam + '.cap.contigs'
            strContigToF = strWorkDir + '/' + strSample + conf['Assembly']['ContigAs']
            lConLen = lRenameContig(strContigF,strContigToF,strSample)
            dSin = Utility.dGetSeqFromFastFile(strSeqStam + dKeeps['KeepSinglets'],1)
            for strSeq in dSin:
                dSeqStat[strSeq] = 'S'
            dASSeq = set(dSampleSeq.keys()) - set(dSin.keys())
            for strSeq in dASSeq:
                dSeqStat[strSeq] = 'A'
            strASStat = 'Y'
            if len(lConLen) > 0:
                if len(dSin) > 0:
                    strASStat = 'P'
            else:
                strASStat = 'N'
            strConLen = ';'.join([str(i) for i in lConLen])
            strConSeq = ';'.join(dASSeq)
            strSinSeq = ';'.join(dSin.keys())
            lReport += [strASStat,len(lConLen),strConLen,strConSeq,len(dSin),strSinSeq]

            for strKeepName,strKeepFile in dKeeps.items():
                strFile = strSeqStam + strKeepFile
                if (not conf['Assembly'][strKeepName]) & os.path.isfile(strFile):
                    os.remove(strFile)
        else:
            lReport += ['N',0,'0','',len(dSampleSeq)]
            lReport.append(';'.join(dSampleSeq.keys()))
        lReport += [len(lSeqRemoved),';'.join(lSeqRemoved)]
        dAssemblyStat[strSample] = lReport
    return dAssemblyStat

def lRenameContig(strContigFile,strToFile,strSample):
    dSeq = Utility.dGetSeqFromFastFile(strContigFile,1)
    lSeqLen = list()
    if len(dSeq) == 0: 
        if os.path.isfile(strContigFile): os.remove(strContigFile)
        return lSeqLen
    iNum = 0
    dSeqRnamed = dict()
    for strSeqId,strBase in dSeq.items():
        strSeqIdNew = ''
        if iNum > 0: strSeqIdNew = str(iNum)
        strSeqIdNew = strSample + strSeqIdNew
        dSeqRnamed[strSeqIdNew] = strBase
        lSeqLen.append(len(strBase))
    
    os.remove(strContigFile)
    Utility.bWriteSeqToFile(dSeqRnamed,strToFile,iBasesPerLine = 80,strNewLine = '\r\n')
    return lSeqLen

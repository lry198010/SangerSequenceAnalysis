import os,sys,fileinput #,Utility
strLibPath = os.path.abspath(__file__) 
strLibPath = os.path.split(strLibPath)[0]
sys.path.append(strLibPath)
import Utility,BioUtil

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
def dCap3Assembly(dSeq,dQual,conf,strWorkDir,dSeqStat = {},strIndent = '\t\t'):
    dSamples = Utility.dGetAB1Sample(dSeq.keys(),'.',1)
    dAssemblyStat = dict()
    strReportF = strWorkDir + '/' + conf['Assembly']['Report']
    for strSample,lSeqs in dSamples.items():
        print(strIndent,'开始样品拼接：',strSample,' 测序文件数：',len(lSeqs))
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
            #print(strSeqFile,strQualFile)
            Utility.bWriteSeqToFile(dSampleSeq,strSeqFile,iBasesPerLine = 60,strNewLine = '\n')
            Utility.bWriteQualToFile(dSampleQual, strQualFile,iBasesPerLine = 60, strNewLine = '\n')
            lCap3Par = []
            lCap3Par.append(conf['ExternalProg']['cap3'])
            lCap3Par.append(strSeqFile)
            strConsFName = '>' + strSeqFile + conf['Assembly']['ConsFName']
            lCap3Par.append(strConsFName)
            #print(' '.join(lCap3Par))
            Utility.dRunExternalProg(lCap3Par)
            dSin = Utility.dGetSeqFromFastFile(strSeqStam + dKeeps['KeepSinglets'],1)
            for strSeq in dSin:
                dSeqStat[strSeq] = 'S'
            sASSeq = set(dSampleSeq.keys()) - set(dSin.keys())
            dSampleSeqFoward = dict() 
            for strSeq in sASSeq:
                dSeqStat[strSeq] = 'A'
                if Utility.bIsFoward(strSeq,iPrimer=2):
                    dSampleSeqFoward[strSeq] = dSampleSeq[strSeq]
            strASStat = 'Y'

            strContigF = strSeqStam + '.cap.contigs'
            strContigToF = strWorkDir + '/' + strSample + conf['Assembly']['ContigAs']
            lConLen = lRenameContig(strContigF,strContigToF,strSample,dSampleSeqFoward)
            if len(lConLen) > 0:
                if len(dSin) > 0:
                    strASStat = 'P'
            else:
                strASStat = 'N'
            strConLen = ';'.join([str(i) for i in lConLen])
            strConSeq = ';'.join(sASSeq)
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
        print(strIndent,'完成样品拼接：',strSample)
    return dAssemblyStat


def lRenameContig(strContigFile,strToFile,strSample,dSampleSeq):
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
        if bToOritation(strBase,dSampleSeq,1):
            strBase = BioUtil.strGetDNAComplement(strBase)
            #strSeqIdNew += ' R'
        strSeqIdNew = strSample + strSeqIdNew
        dSeqRnamed[strSeqIdNew] = strBase
        lSeqLen.append(len(strBase))
    
    os.remove(strContigFile)
    Utility.bWriteSeqToFile(dSeqRnamed,strToFile,iBasesPerLine = 80,strNewLine = '\r\n')
    return lSeqLen

# 0 as dCompSeq, 1 complement of dCompSeq
def bToOritation(strSeq,dCompSeq,iOritation = 0, iThreshold = 0.5):
    if len(dCompSeq) == 0: return False
    iNumOritationIdentity = 0
    if iOritation: strSeq = BioUtil.strGetDNAComplement(strSeq)
    for strSeq1 in dCompSeq.values():
        if BioUtil.iAlignSeqsByKers(strSeq,strSeq1,10) > iThreshold : iNumOritationIdentity += 1
    if iNumOritationIdentity / len(dCompSeq) > 0.5:
        return True
    else:
        return False


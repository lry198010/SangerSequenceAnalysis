import os,json,subprocess,fileinput


AB1FileSuffix = ("ab1","AB1","Ab1","aB1")
def dGetSetting(strSettingJson):
    if not os.path.isfile(strSettingJson):return dict()
    cff = open(strSettingJson,'r')
    conf = json.load(cff)
    cff.close()
    return conf

def lGetDirs(strWorkDir):
    lDirs = []
    with os.scandir(strWorkDir) as dfs:# Directories and files
        for dirEntry in dfs:
            if dirEntry.is_dir():lDirs.append(dirEntry.path)
    return lDirs

def lGetAB1Files(strWorkDir):
    lAB1Files = []
    with os.scandir(strWorkDir) as wkDirScan:
        for dirEntry in wkDirScan:
            if dirEntry.is_file() and dirEntry.path.endswith(AB1FileSuffix):
                lAB1Files.append(dirEntry.path)
    return lAB1Files

# strAB1FilePath: Sample name included in file path, each part of the file path seperated by "."
def strGetAB1SampleName(strAB1FilePath, strSplit = ".", iNameIndex = 1):
    strName = os.path.split(strAB1FilePath)[1]
    if len(strName) == 0:
        return ''
    else:
        lParts = strName.split(strSplit)
        if len(lParts)-1 < iNameIndex:
            return ''
        else:
            return lParts[iNameIndex]


# lAB1Files: Sample name included in file name, parts of file seperate by "."
# return Dict: {"Sample":[file1,file2,...],...}
def dGetAB1Sample(lAB1Files, strSplit = ".", iNameIndex = 1):
    dSample = dict()
    for strAB1File in lAB1Files:
        strSampleName = strGetAB1SampleName(strAB1File,strSplit,iNameIndex)
        if len(strSampleName) > 0:
            if not strSampleName  in dSample:
                dSample[strSampleName] = []
            dSample[strSampleName].append(strAB1File)
    return dSample

def iAB1PathList2File(lAB1Files, strToFileName):
    lAB1s = []
    for strAB1File in lAB1Files:
        if os.path.isfile(strAB1File):
            lAB1s.append(strAB1File)
    iNumAB1s = len(lAB1s)
    if iNumAB1s > 0 :
        fout = open(strToFileName,'w')
        for strAB1 in lAB1s:
            fout.write(strAB1 + '\n')
        fout.close()
    return iNumAB1s

def iGetSeqQualFileByTtuner(lProgPars, lAB1Files,strFileList2File):
    iNumFile = iAB1PathList2File(lAB1Files, strFileList2File)
    if iNumFile <= 0:
        return 0
    else:
        subP = dRunExternalProg(lProgPars + [strFileList2File])
        return iNumFile

def dBaseCallingByTtuner(lProgPars, lAB1Files,strSeqFile, strQualFile,strFileList2File):
    lProgPars = lProgPars + ['-sa', strSeqFile,'-qa',strQualFile, '-if']
    iNumFile = iGetSeqQualFileByTtuner(lProgPars,lAB1Files,strFileList2File) 
    if iNumFile == 0: return dict()
    return dGetSeqFromFastFile(strSeqFile,1)

def dBaseCallingByTtunerDir(lProgPars, strDir,strSeqFile, strQualFile):
    lProgPars = lProgPars + ['-sa', strSeqFile,'-qa',strQualFile, '-id',strDir]
    return(dRunExternalProg(lProgPars)) 
    #return dGetSeqFromFastFile(strSeqFile,1)

def dBaseCallingByTtunerPerAB1(lProgPars,lAB1Files,strSeqSuff, strQualSuff,bKeep = 1,bToSeqId = 0,strToDir='/dev/shm'):
    dSeq = dict()
    dQual = dict()
    lCallFail = []
    for strAB1 in lAB1Files:
        if not os.path.isfile(strAB1): continue
        strFileDir,strFileStam = os.path.split(strAB1)
        if not os.path.isdir(strToDir): strToDir = strFileDir
        strSeqFile = strToDir + '/' + strFileStam + strSeqSuff
        strQualFile = strToDir + '/' + strFileStam + strQualSuff
        lParams = lProgPars + ['-sa', strSeqFile,'-qa',strQualFile, strAB1] 
        subP = dRunExternalProg(lParams)
        if subP.returncode == 0:
            dTmpSeq = dGetSeqFromFastFile(strSeqFile,bToSeqId)
            dTmpQual = dGetQualFromFastFile(strQualFile,bToSeqId)
            for strSeqId,strSeq in dTmpSeq.items():
                if not strSeqId in dSeq: dSeq[strSeqId] = strSeq

            for strSeqId,lQual in dTmpQual.items():
                if not strSeqId in dQual: dQual[strSeqId] = lQual
            if not bKeep:
                if os.path.isfile(strSeqFile): os.remove(strSeqFile)
                if os.path.isfile(strQualFile): os.remove(strQualFile)
        else:
            lCallFail.append(strAB1)
    return (dSeq,dQual,lCallFail)

def dRunExternalProg(lProgPars):
    strRun = " ".join(lProgPars)
    subP = subprocess.run(" ".join(lProgPars),shell = True)
    return subP

def dGetSeqFromFastFile(strFastSeqFile, bToSeqId = 0):
    dSeq = dict()
    strSeqN = ''
    if os.path.isfile(strFastSeqFile):
        with fileinput.input(strFastSeqFile) as lines:
            for line in lines:
                line = line.strip()
                if line.startswith('>'):
                    strSeqN = line.strip('>')
                    if bToSeqId: strSeqN = strSeqN.split()[0]
                    if strSeqN in dSeq: print("Duplication:" + strSeqN)
                    dSeq[strSeqN] = ''
                else:
                    dSeq[strSeqN] += line
    else:
        print("Error, File not exists:" + strFastSeqFile)
    return dSeq

def dGetQualFromFastFile(strFastQualFile,bToSeqId = 0):
    dSeq = dict()
    strSeqN = ''
    if os.path.isfile(strFastQualFile):
        with fileinput.input(strFastQualFile) as lines:
            for line in lines:
                line = line.strip()
                if line.startswith('>'):
                    strSeqN = line.strip('>')
                    if bToSeqId: strSeqN = strSeqN.split()[0]
                    if strSeqN in dSeq: print("Duplication:" + strSeqN)
                    dSeq[strSeqN] = ''
                else:
                    dSeq[strSeqN] += ' ' + line
    else:
        print("Error, File not exists:" + strFastQualFile )
    for strSeqN,strQual in dSeq.items():
        dSeq[strSeqN] = strQual.split()
    return dSeq

def bWriteSeqToFile(dSeq,strToFile,iBasesPerLine = 60,strNewLine = '\n'):
    fout = open(strToFile,'w')
    for strSeqId,strSeq in dSeq.items():
        fout.write('>' + strSeqId + strNewLine)
        lBegin = 0
        lEnd = iBasesPerLine
        if lEnd > len(strSeq):lEnd = len(strSeq)
        while lBegin < len(strSeq):
            fout.write(strSeq[lBegin:lEnd] + strNewLine)
            lBegin = lEnd
            lEnd += iBasesPerLine
            if lEnd > len(strSeq): lEnd = len(strSeq)
    fout.close()

def bWriteQualToFile(dQual, strToFile,iBasesPerLine = 60, strNewLine = '\n'):
    fout = open(strToFile,'w')
    for strSeqId,lQual in dQual.items():
        fout.write('>' + strSeqId + strNewLine)
        lBegin = 0
        lEnd = iBasesPerLine
        if lEnd > len(lQual): lEnd = len(lQual)
        while lBegin < len(lQual):
            fout.write(' '.join(lQual[lBegin:lEnd]) + strNewLine)
            lBegin = lEnd
            lEnd += iBasesPerLine
            if lEnd > len(lQual): lEnd = len(lQual)
    fout.close()

def dGetSubSeqQual(dSeqQual,dRegion,iOffset = -1):
    dSub = dict()
    for strSeqId,lRegion in dRegion.items():
        if strSeqId in dSeqQual:
            iBegin = lRegion[0] + iOffset
            iEnd = lRegion[1] 
            dSub[strSeqId] = dSeqQual[strSeqId][iBegin:iEnd]
    return dSub

def dGetSubSeqFromFile(strSeqFile,dRegion,iOffset = -1, bToSeqId = 1): 
    dSeq = dGetSeqFromFastFile(strSeqFile,bToSeqId)
    return dGetSubSeqQual(dSeq,dRegion,iOffset)

def dGetSubQualFromFile(strQualFile,dRegion,iOffset = -1, bToSeqId = 1):
    dQual = dGetQualFromFastFile(strQualFile,bToSeqId)
    return dGetSubSeqQual(dQual,dRegion,iOffset)

def bWriteDLTable(dData,strToFile,lTitle = [],bKeyWrite = 0,strNewLine = '\n'):
    fout = open(strToFile,'w')
    if len(lTitle) > 0:
        fout.write(','.join([str(i) for i in lTitle]) + strNewLine)
    for k,lEle in dData.items():
        if bKeyWrite:
            lEle = [k] + lEle
        fout.write(','.join([str(i) for i in lEle]) + strNewLine)
    fout.close()

def sGetInforFromQualReport(strQualReport,iOnCol = 1,strSplit = ','):
    sReps = set()
    if os.path.isfile(strQualReport):
        with fileinput.input(strQualReport) as lines:
            for line in lines:
                line = line.strip()
                lFields = line.split(',')
                sReps.add(lFields[iOnCol])
    sReps.remove('SeqFile')
    return sReps

def bIsDirAnalysis(strWorkDir,conf):
    strQualReport = strWorkDir + '/' + conf['Qual']['SaveTo']
    if os.path.isfile(strQualReport):
        sAB1Report = sGetInforFromQualReport(strQualReport,1)
    else:
        return 0

    lAB1Files = lGetAB1Files(strWorkDir)
    sAB1s = set([os.path.split(i)[1] for i in lAB1Files])

    if len(sAB1Report) != len(sAB1s) : return 0
    if len(sAB1Report - sAB1s) != 0  : return 0
    return 1

import os,json,subprocess

AB1FileSuffix = ("ab1","AB1","Ab1","aB1")
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
        return ""
    else:
        lParts = strName.split(strSplit)
        if len(lParts)-1 < iNameIndex:
            return ""
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
    iNumAB1File = 0
    fout = open(strToFileName,'w')
    for strAB1File in lAB1Files:
        if os.path.isfile(strAB1File):
            fout.write(strAB1File,"\n")
            iNumAB1File += 1
    fout.close()
    if iNumAB1File <= 0 : os.remove(strToFileName)
    return iNumAB1File


def dGetSetting(strSettingJson):
    cff = open(strSettingJson,'r')
    conf = json.load(cff)
    cff.close()
    return conf

def dRunExternalProg(lProgPars,lAB1Files):
    strRun = " ".join(lProgPars)
    subP = subprocess.run(" ".join(lProgPars),shell = True)
    return subP

#!/usr/bin/python3

import os, sys, getopt, subprocess, fileinput
# Get the script directory 
strLibPath = os.path.split(sys.path.split(sys.argv[0]))[0] 
sys.path.append(strLibPath)

def getAb1Files(wkdir,ab1ListTo):
    iNumFiles = 0
    fin = open(ab1ListTo,"w")
    with os.scandir(wkdir) as fi:
        for dirEntry in fi:
            if dirEntry.is_file() and dirEntry.path.endswith(("ab1","AB1","Ab1","aB1")):
                fin.writelines([dirEntry.path,"\n"])
                iNumFiles += 1
    fin.close();
    if iNumFiles<=0:
        os.remove(fin)
    return iNumFiles

def getAlignRegion(bln,dRegion):
    if not os.path.exists(bln):
        return
    with fileinput.input(bln) as lines:
        for line in lines:
            fields = line.split("\t")
            if not fields[0] in dRegion:
                dRegion[fields[0]] = [0] * int(fields[1])
            seqRegion = dRegion[fields[0]]
            for i in range(int(fields[13]),int(fields[14])+1):
                seqRegion[i-1] += 1

def getHighQualRegion(dRegion,nMaxVect):
    nMaxVect += 1
    res = dict()
    for k,v in dRegion.items():
        pos = -1
        npos = 0
        res[k] = [0,0]
        for i in range(len(v)): 
            if v[i] > 0:
                if pos >=0:
                    if res[k][1] < npos:
                        res[k] = [pos,npos]
                npos = 0
                pos = -1
            if v[i] == 0:
                if pos == -1:
                    pos = i
                npos += 1
        if pos >=0:
            if res[k][1] < npos:
                res[k] = [pos,npos]
        npos = 0
        for i in range(res[k][0] + res[k][1],len(v)):
            npos += 1
            if npos > nMaxVect:
                break
            if v[i] == 0:
                res[k][1] += npos
                npos = 0
        if npos <= nMaxVect:
            res[k][1] += npos
        res[k][1] = res[k][0] + res[k][1] 
        npos = 0
        for i in range(res[k][0]-1,-1,-1):
            npos += 1
            if npos > nMaxVect:
                break
            if v[i] == 0:
                res[k][0] = i
                npos = 0
        if npos <= nMaxVect:
            res[k][0] = 0
    return res

def getFastSeq(sa):
    res = dict()
    seqN = ""
    with fileinput.input(sa) as lines:
        for line in lines:
            line = line.strip()
            if line.startswith(">"):
                seqN = line
                res[seqN] = ""
            else:
                res[seqN] += line
    return res

def getHighQualSeq(seqD,regionD):
    res = dict()
    for seqN,seq in seqD.items():
        seqN = seqN.strip('>')
        fields = seqN.split() 
        #print(seqN)
        #print(seq)
        if len(fields) == 4:
            sD = set(range(int(fields[2])-1, int(fields[2]) + int(fields[3])))
            if fields[0] in regionD:
                #print(regionD[fields[0]])
                sD = sD & set(range(regionD[fields[0]][0],regionD[fields[0]][1]+1))
            if len(sD) > 100:
                minsD = min(list(sD)) + 1
                maxsD = max(list(sD)) + 1
                seqNN = " ".join([fields[0]," ", fields[1], " ",str(minsD)," ",str(maxsD)])
                res[seqNN] = seq[minsD:maxsD+1]
            else:
                print("High Segement to short:" + seqN + ":" + str(len(sD)))
    return res

def getFastQual(qa): 
    res = dict()
    seqN = ""
    with fileinput.input(qa) as lines:
        for line in lines:
            line = line.strip()
            if line.startswith('>'):
                seqN = line
                #res[seqN] = []
                res[seqN] = ""
            else:
                #res[seqN] = res[seqN] + line.split(" ")
                res[seqN] += ' ' + line
    return res

def getHighQualQual(qualD,regionD):
    res = dict()
    for seqN,qual in qualD.items():
        seqN = seqN.strip('> ')
        fields = seqN.split() 
        if len(fields) == 4:
            sD = set(range(int(fields[2])-1, int(fields[2]) + int(fields[3])))
            if fields[0] in regionD:
                #print(regionD[fields[0]])
                sD = sD & set(range(regionD[fields[0]][0],regionD[fields[0]][1]+1))
            if len(sD) > 100:
                qual = qual.strip(' ')
                quals = qual.split()
                minsD = min(list(sD)) + 1 
                maxsD = max(list(sD)) + 1
                seqNN = " ".join([fields[0]," ", fields[1], " ",str(minsD)," ",str(maxsD)])
                res[seqNN] = quals[minsD:maxsD+1]
            else:
                print("High Segement to short:" + seqN + ":" + str(len(sD)))
    return res

def getSamples(seqHD,nameIndex):
    res = dict()
    for k in seqHD:
        seqNs = k.split(".")
        if not seqNs[nameIndex] in res:
            res[seqNs[nameIndex]] = []
        res[seqNs[nameIndex]].append(k)
    return res

def printSeq(seqN,seq,fTo,nBPerLine,newline):
    fTo.write(seqN + newline)
    lBegin = 0
    lEnd = nBPerLine
    while lBegin < len(seq):
        fTo.write(seq[lBegin:lEnd] + newline)
        lBegin = lEnd
        lEnd += nBPerLine
        if lEnd > len(seq):
            lEnd = len(seq)

def printQual(seqN,qual,fTo,nBPerLine):
    fTo.write(seqN + "\n")
    lBegin = 0
    lEnd = nBPerLine
    while lBegin < len(qual):
        fTo.write(" ".join(qual[lBegin:lEnd]) + "\n")
        lBegin = lEnd
        lEnd += nBPerLine
        if lEnd > len(qual):
            lEnd = len(qual)

def renameContig(seqContigF,toSampleF,toSampleN):
    seqs = getFastSeq(seqContigF)
    seqLen = []
    if len(seqs)>0:
        fTo = open(toSampleF,"w")
        i = 0
        for k,v in seqs.items():
            k = toSampleN
            seqLen.append(str(len(v)))
            if i > 0:
                k = k + str(i)
            printSeq(">" + k,v,fTo,60,"\r\n")
        fTo.close()
    os.remove(seqContigF)
    return ":".join(seqLen)

def rmTmp(fpath):
    if os.path.isfile(fpath):
        os.remove(fpath)

bKeepTmp = 0
nMaxVect = 20 # max length of sequence match vector that not screen
nameIndex = 1

ttuner = "/home/tyhy/biosoft/tracetuner_3.0.6beta/rel/Linux_64/ttuner"
blastn = '/home/tyhy/biosoft/ncbi-blast-2.9.0+/bin/blastn -db /home/tyhy/biosoft/Vector/UniVec -task blastn -reward 1 -penalty -5 -gapopen 3 -gapextend 3 -dust yes -soft_masking true -evalue 700 -searchsp 1750000000000 -max_target_seqs 20 -outfmt "6 qaccver qlen saccver slen length evalue score bitscore nident pident mismatch gapopen gaps qstart qend sstart send qseq sseq"'
cap3 = "/home/tyhy/biosoft/CAP3/cap3"

ab1List = "allab1.list"
sa = "all.seq"
qa = "all.qual"
bln = "all.bln"
sah = ".hq"
qah = ".hq.qual"
c3 = "cap3"

wkdir = os.getcwd();

# Output he parameter used in the analysis
print(" ".join([sys.argv[0],"-wd",wkdir,"-if",ab1List,"-sa",sa,"-qa",qa,"-bl",bln,"-c3",c3]));

# To get the Analysis AB1 File
iNumFiles = getAb1Files(wkdir,ab1List)

# If there are any ab1 files run!
if iNumFiles > 0:
    print("Now, call ttuner to basecalling......")
    subP = subprocess.run(" ".join([ttuner,"-sa", sa,"-qa",qa,"-if",ab1List]),shell=True )

    print("Call blastn search for vectors.......");
    subP = subprocess.run(" ".join([blastn,"-query",sa,"-out",bln]),shell=True)

    print("Quality screen......")

    print("\tGet Vector Blast region......")
    dRegion = {}
    getAlignRegion(bln,dRegion)
    #print(dRegion)

    print("\tGet High Qualit Region......")
    highD = getHighQualRegion(dRegion,nMaxVect)
    #print(highD)

    print("\tRead Sequnec from fasta File......")
    seqD = getFastSeq(sa)
    #print(seqD)

    print("\tGet High Quality sequence......")
    seqHD = getHighQualSeq(seqD,highD)
    #print(len(seqHD))

    print("\tRead Quality from Quality File......")
    qualD = getFastQual(qa)
    #print(qualD)

    print("\tGet High Quality Qual......")
    qualHD = getHighQualQual(qualD,highD)
    #print(len(qualHD)) 

    # Get name of samples
    samples = getSamples(seqHD,nameIndex)
    print("Total samples:", len(samples))

    reportF = open("Assembly_report.csv","w")
    reportF.write("Sample,NumberOfSeq,Status,seqLength(bps),Assemblied,singlets" + "\n")
    iprocess = 0
    for k,v in samples.items():
        print("\t\tProcess sample(",len(v),"):",k,":")
        print("\n".join(["\t\t\t" + m for m in v]))
        seqSamples =  set([s.split()[0] for s in v])
        #print(seqSamples)
        strReport = [k, str(len(v))]
        seqFName = k + sah
        qualFName = k + qah
        conFName = ">" + k + sah + ".cap.consences"
        seqFto = open(seqFName,"w")
        qualFto = open(qualFName,"w")
        iNumSeq = 0
        for seqfaqual in v:
            if len(seqHD[seqfaqual]) > 0 :
                iNumSeq += 1
                printSeq(">" + seqfaqual, seqHD[seqfaqual],seqFto,60,"\n")
                printQual(">" + seqfaqual, qualHD[seqfaqual],qualFto,30)
            else:
                print("\t\tEmpty Sequence:" + seqfaqual)
        seqFto.close()
        qualFto.close()
        if iNumSeq > 0:
            subP = subprocess.run(" ".join([cap3, seqFName, conFName]),shell=True )
            strSinglets = set([aSeq.strip(">").split()[0] for aSeq in getFastSeq(seqFName + ".cap.singlets").keys()])
            strAssemblied = seqSamples - strSinglets
            if len(strSinglets) > 0:
                strReport.append("N")
            else:
                strReport.append("Y")
            strContigLen = renameContig(seqFName + ".cap.contigs",k + ".TXT",k)
            strReport.append(strContigLen)
            strReport.append(":".join(strAssemblied))
            strReport.append(":".join(strSinglets))
            if not bKeepTmp:
                for s in [".cap.consences",".cap.ace",".cap.contigs.links",".cap.contigs.qual",".cap.info",".cap.singlets",".qual",""]:
                    rmTmp(k + sah + s)
        else:
            strReport.append("N") 
            strReport.append("0") 
            strReport.append("") 
            strReport.append(":".join([m.split()[0] for m in v])) 

        reportF.write(",".join(strReport) + "\n")

        iprocess += 1
        if iprocess > 1000:
            break

    reportF.close()

    if not bKeepTmp:
        rmTmp(ab1List)
        rmTmp(sa)
        rmTmp(qa)
        rmTmp(bln)

    print("End of Analysis")


import os,sys,fileinput #,Utility
strLibPath = os.path.abspath(__file__) 
strLibPath = os.path.split(strLibPath)[0]
sys.path.append(strLibPath)
import Utility

dDNAPresent = {
            'A':'A',
            'T':'T',
            'C':'C',
            'G':'G',
            'R':'A,G',
            'Y':'C,T',
            'M':'A,C',
            'K':'G,T',
            'S':'C,G',
            'W':'A,T',
            'H':'A,C,T',
            'B':'C,G,T',
            'D':'A,G,T',
            'V':'A,C,G',
            'N':'N'
        }
dDNAComplement = {
            'A':'T',
            'C':'G',
            'G':'C',
            'T':'A',
            'R':'Y',
            'Y':'R',
            'M':'K',
            'K':'M',
            'S':'W',
            'W':'S',
            'H':'D',
            'B':'V',
            'D':'H',
            'V':'B',
            'N':'N'
        }
lDNALetters = list(dDNAPresent.keys())

def strGetDNAComplement(strDNA):
    lDNA = [''] * len(strDNA)
    iIndex = len(strDNA) - 1
    for i in range(0,iIndex + 1):
        if strDNA[i] in dDNAComplement:
            lDNA[iIndex - i] = dDNAComplement[strDNA[i]]
        else:
            lDNA[iIndex - i] = strDNA[i]
    return ''.join(lDNA)

def dGetKers(strDNA,iKer = 10):
    dKers = dict()
    if iKer <= 0: return dKers
    for i in range(0,len(strDNA) - iKer + 1):
        strSubDNA = strDNA[i:i+iKer]
        if strSubDNA in dKers:
            dKers[strSubDNA] += 1
        else:
            dKers[strSubDNA] = 1
    return dKers

def iAlignSeqsByKers(strDNA1, strDNA2,iKer = 10):
    dKer1 = dGetKers(strDNA1, iKer)
    dKer2 = dGetKers(strDNA2, iKer)
    iNumMatchKers = 0
    for strKer in dKer1.keys():
        if strKer in dKer2:
            iKers = dKer1[strKer]
            if dKer2[strKer]: iKers = dKer2[strKer]
            iNumMatchKers += iKers
    if iNumMatchKers / (len(strDNA2) - iKer  + 1)  > iNumMatchKers / (len(strDNA1) - iKer  + 1) :
        return iNumMatchKers / (len(strDNA2) - iKer  + 1)
    else:
        return iNumMatchKers / (len(strDNA1) - iKer  + 1)

#!/usr/bin/python3
import sys,os,getopt,json
strLibPath = os.path.split(sys.argv[0])[0]
strLibPath = os.path.abspath(strLibPath + "/../")
sys.path.append(strLibPath)
import A3Lib.BioUtil as AB
import A3Lib.Assembly as AA

strDNA1 = 'ATCGAATCGAGGTCAGRMNCTGA'
strDNA2 = 'ATCGGATCGAGGTCAGMMNCTGA'
print(AB.strGetDNAComplement(strDNA1))
print(AB.strGetDNAComplement(''))

print(AB.iAlignSeqsByKers(strDNA1,strDNA2,5))

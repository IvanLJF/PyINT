#! /usr/bin/env python

import numpy as np
import os
import sys  
import getopt
import time
import glob
import argparse

import subprocess
from pyint import _utils as ut


def work(data0):
    cmd = data0[0]
    err_file = data0[1]
    p = subprocess.run(cmd, shell=False,stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout = p.stdout
    stderr = p.stderr
    
    if type(stderr) == bytes:
        aa=stderr.decode("utf-8")
    else:
        aa = stderr
    
    if aa:
        str0 = cmd[0] + ' ' + cmd[1] + ' ' + cmd[2] + ' ' + cmd[3] + '\n'
        #print(aa)
        with open(err_file, 'a') as f:
            f.write(str0)
            f.write(aa)
            f.write('\n')

    return 
#########################################################################

INTRODUCTION = '''
-------------------------------------------------------------------  
       Geneate differential interferograms for one project using GAMMA.
   
'''

EXAMPLE = '''
    Usage: 
            diff_gamma_all.py projectName
            diff_gamma_all.py projectName --parallel 4
            diff_gamma_all.py projectName --parallel 4 --ifgramList-txt /test/ifgram_list.txt
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Geneate differential interferograms for one project using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('--parallel', dest='parallelNumb', type=int, default=1, help='Enable parallel processing and Specify the number of processors.')
    parser.add_argument('--ifgarmList-txt', dest='ifgarmListTxt', help='provided ifgram_list_txt. default: using ifgram_list.txt under projectName folder.')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    start_time = time.time()
    inps = cmdLineParse() 
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    projectDir = scratchDir + '/' + projectName
    ifgDir = scratchDir + '/' + projectName + '/ifgrams'
    templateDict=ut.update_template(templateFile)
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    
    if inps.ifgarmListTxt: ifgramList_txt = inps.ifgarmListTxt
    else: ifgramList_txt = scratchDir + '/' + projectName + '/ifgram_list.txt'
    ifgList0 = ut.read_txt2array(ifgramList_txt)
    ifgList = ifgList0[:,0]
    
    err_txt = scratchDir + '/' + projectName + '/diff_gamma_all.err'
    if os.path.isfile(err_txt): os.remove(err_txt)
    
    data_para = []
    for i in range(len(ifgList)):
        m0 = ut.yyyymmdd(ifgList[i].split('-')[0])
        s0 = ut.yyyymmdd(ifgList[i].split('-')[1])
        cmd0 = ['diff_gamma.py',projectName, m0, s0]
        diff_file0 = ifgDir + '/' + ifgList[i] + '/' + ifgList[i] + '_' + rlks + 'rlks.diff_filt.bmp'
        data0 = [cmd0,err_txt]
        
        k00 = 0
        if os.path.isfile(diff_file0):
            if os.path.getsize(diff_file0) > 0:
                k00 = 1
        if k00==0:
            data_para.append(data0)
    
    ut.parallel_process(data_para, work, n_jobs=inps.parallelNumb, use_kwargs=False)
    print("Generate differential interferograms for project %s is done! " % projectName)
    ut.print_process_time(start_time, time.time())
    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
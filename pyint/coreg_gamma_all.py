#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2019, Yunmeng Cao                   ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Contact : ymcmrs@gmail.com                               ###  
#################################################################

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
    err_txt = data0[1]
    
    p = subprocess.run(cmd, shell=False,stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout = p.stdout
    stderr = p.stderr
    
    if type(stderr) == bytes:
        aa=stderr.decode("utf-8")
    else:
        aa = stderr
        
    if aa:
        str0 = cmd[0] + ' ' + cmd[1] + ' ' + cmd[2] + '\n'
        #print(aa)
        with open(err_txt, 'a') as f:
            f.write(str0)
            f.write(aa)
            f.write('\n')

    return 
#########################################################################

INTRODUCTION = '''
-------------------------------------------------------------------  
       Coregister all of the SLCs to the reference SAR image using GAMMA.
       [with assistant of DEM]
   
'''

EXAMPLE = '''
    Usage: 
            coreg_gamma_all.py projectName
            coreg_gamma_all.py projectName --parallel 4
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Coregister all of the SLCs to the reference SAR image using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('--parallel', dest='parallelNumb', type=int, default=1, help='Enable parallel processing and Specify the number of processors.')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    start_time = time.time()
    inps = cmdLineParse() 
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    projectDir = scratchDir + '/' + projectName 
    slcDir    = scratchDir + '/' + projectName + '/SLC'
    rslcDir    = scratchDir + '/' + projectName + '/RSLC'   
    if not os.path.isdir(rslcDir): os.mkdir(rslcDir)
    
    
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    
    demDir = scratchDir + '/' + projectName + '/DEM' 
    
    Mdate = templateDict['masterDate']
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    
    
    ################## generate SLC of the mater date for S1
    
    if 'S1' in projectName:
        
        SLC_Tab = slcDir + '/' + Mdate + '/' + Mdate + '_SLC_Tab'
        TSLC = slcDir + '/' + Mdate + '/' + Mdate + '.slc'
        TSLCPar = slcDir + '/' + Mdate + '/' + Mdate + '.slc.par'
        
        k0 = 0
        if os.path.isfile(TSLCPar):
            if os.path.getsize(TSLCPar) > 0:
                k0 = 1
        
        if k0 ==0:    
            call_str = 'SLC_mosaic_S1_TOPS ' +  SLC_Tab + ' ' + TSLC + ' ' + TSLCPar + ' ' + rlks + ' ' + azlks
            os.system(call_str)
    
    ######################################################
    
    HGTSIM      = demDir + '/' + Mdate + '_' + rlks + 'rlks.rdc.dem'
    if not os.path.isfile(HGTSIM):
        call_str = 'generate_rdc_dem.py ' + projectName
        os.system(call_str)
    
    
    if 'S1' in projectName: cmd_command = 'coreg_s1_gamma.py'
    else: cmd_command = 'coreg_gamma.py'
        
    err_txt = scratchDir + '/' + projectName + '/coreg_gamma_all.err'
    if os.path.isfile(err_txt): os.remove(err_txt)
    
    data_para = []
    #slc_list = [os.path.basename(fname) for fname in sorted(glob.glob(slcDir + '/*'))]
    slc_list = ut.get_project_slcList(projectName)
    for i in range(len(slc_list)):
        cmd0 = [cmd_command,projectName,slc_list[i]]
        data0 = [cmd0,err_txt]
        data_para.append(data0)
    
    ut.parallel_process(data_para, work, n_jobs=inps.parallelNumb, use_kwargs=False)
    print("Coregister all of the SLCs %s is done! " % projectName)
    ut.print_process_time(start_time, time.time())
    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
import os
import os.path as osp
import glob
import subprocess
from utils import chdir_wrap
import json

config = json.load(open('config.json', encoding='utf-8'))
config_keys = sorted(config.keys())
labid, _, _ = list(map(config.get, config_keys))

@chdir_wrap()
def compile_cpps():

    lab = f'lab{labid}'
    codes = lab + '/codes'
    debug = codes + "/Debug"
    build_failed = []
    subl = False


    if not osp.exists(debug):
        os.mkdir(debug)
    cpps = glob.glob(codes + '/*/*.cpp')
    for cpp in cpps:
        fname = osp.basename(cpp)
        fdir = osp.dirname(cpp)
        fid = osp.splitext(fname)[0]
        if osp.exists(debug + '/' + fid + '.exe'): 
            print(fid + ' compiled already')
            continue

        exec_gbk = f"g++ -std=c++14 -I{fdir} -finput-charset=GBK -fexec-charset=GBK {cpp} -o {debug}/{fid}"
        exec_gbk_utf = f"g++ -std=c++14 -I{fdir} -fexec-charset=GBK {cpp} -o {debug}/{fid}"
        # print(exec_gbk)
        if  os.system(exec_gbk) and os.system(exec_gbk_utf):
            build_failed.append(fid)
            if not subl: 
                subl = True
                subprocess.Popen("subl -n", shell=True)
            subprocess.Popen(f"subl {cpp}", shell=True)   
            print(fid + ' build error!!!<-----------')
        else:
            print(fid + ' build passed')

    build_failed_origin = open(f'{lab}/build.failed.txt').readlines()
    build_failed_new = [ bf for bf in build_failed if bf not in build_failed_origin]
    f = open(f'{lab}/build.failed.txt', 'a')
    f.write('\n'.join(build_failed_new))
    f.close()
    print('\n'.join(build_failed))
    return build_failed

if __name__ == '__main__':
    compile_cpps()
import glob
import shutil
import os
import os.path as osp
import re
import collections
from utils import chdir_wrap
import json

config = json.load(open('config.json'))
config_keys = sorted(config.keys())
labid, problems, _ = list(map(config.get, config_keys))

@chdir_wrap()
def copy_files():

    lab = f'lab{labid}'
    junk = f'junk/{lab}'
    codes = f'{lab}/codes'
    reports = f'{lab}/reports'


    if not osp.exists(lab):
        os.mkdir(lab)
    if not osp.exists(reports):
        os.mkdir(reports)
    if not osp.exists(codes):
        os.mkdir(codes)

    error_sids = []
    submitted_folders = glob.glob(junk + '/**/')
    from collections import OrderedDict
    for folder in submitted_folders:
        if not re.findall(r'\d{12}', folder):
            continue
        sid = re.findall(r'\d{12}', folder)[0]
        cpps = glob.glob(folder + '**/*.cpp', recursive=True)
        cpp_folders = list(OrderedDict.fromkeys((osp.dirname(cpp) for cpp in cpps if osp.isfile(cpp))))
        if len(cpp_folders) == len(problems):
            for i, cpp_folder in enumerate(cpp_folders):
                fid = f'{sid}_{labid}_{problems[i]}'

                if not osp.exists(f'{codes}/{fid}/'):
                    os.mkdir(f'{codes}/{fid}/')
                for f in glob.glob(cpp_folder + '/*.cpp') + glob.glob(cpp_folder + '/*.h'):
                    fext = osp.splitext(osp.basename(f))[1]
                    f2 = f'{codes}/{fid}/{fid}{fext}'
                    shutil.copy2(f, f2)

        else:

            if len(cpps) != len(problems):
                print('sid = ', sid)
                print('cpp_folders = ', cpp_folders)
                print('cpps = ', cpps)
                print(f"error: {sid} 没有全部提交或者提交格式错误 <-----------")
                error_sids.append(sid)

            else:
                print('直接使用cpp顺序拷贝')
                for i, f in enumerate(cpps):
                    fid = f'{sid}_{labid}_{problems[i]}'
                    fext = osp.splitext(osp.basename(f))[1]
                    f2 = f'{codes}/{fid}/{fid}{fext}'
                    if not osp.exists(f'{codes}/{fid}/'):
                        os.mkdir(f'{codes}/{fid}/')
                    shutil.copy2(f, f2)

    D = {}
    fs = glob.glob(junk + '/**/*.doc', recursive=True) + glob.glob(junk + '/**/*.docx', recursive=True)
    sids = [f[12:24] for f in fs]


    sids_counter = collections.Counter(sids)
    for f, sid in zip(fs, sids):
        if D.get(sid) is None:
            D[sid] = 0
        else:
            D[sid] += 1
        fext = osp.splitext(osp.basename(f))[1]
        prob = problems[D[sid]]
        if sids_counter[sid] == 1:
            f2 = f'{reports}/{sid}_{labid}{fext}' 
        else:
            f2 = f'{reports}/{sid}_{labid}_{prob}{fext}'
        shutil.copy2(f, f2)



    s = open('sid_snames.txt', encoding='utf-8').read()
    error_copy = ''.join([re.findall(f'{esid}\t.*\n', s)[0] for esid in error_sids])
    print('提交异常\n', error_copy)
    f = open(f'{lab}/提交异常.txt', 'w')
    f.write(error_copy)
    f.close()


    unsubmitted = []
    for sid_name in s.split('\n'):
        if not sid_name: continue
        sid, _ = sid_name.split('\t')
        if any((sid in f for f in os.listdir(f'{codes}'))):
            continue
        unsubmitted.append(sid)

    unsubmitted = ''.join([re.findall(f'{esid}\t.*\n', s)[0] for esid in unsubmitted])
    print('未提交\n', unsubmitted)
    f = open(f'{lab}/未提交.txt', 'w')
    f.write(unsubmitted)
    f.close()



    return error_copy, unsubmitted

if __name__ == '__main__':
    copy_files()
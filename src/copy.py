from utils import * 
from collections import OrderedDict
from itertools import chain 

def _copy_cpps(error_sids=None):
    
    for folder in junk_new.iterdir():
        sid = folder.name 

        # 只处理 forced 学生
        if is_forced and sid not in sids_forced: continue 

        cpps = [cpp for cpp in folder.rglob('*.cpp') if cpp.is_file()]

        # 使用 OrderedDict 使得 cpp_folders 保持了 cpps 的顺序
        cpp_folders = list(OrderedDict.fromkeys((cpp.parent for cpp in cpps)))


        if len(cpp_folders) == len(problems):
            for i, cpp_folder in enumerate(cpp_folders):
                # fid_dir is the destination dir
                fid_dir = codes / f'{sid}_{labid}_{problems[i]}'
                if not fid_dir.exists():
                    fid_dir.mkdir()

                for f in  chain(cpp_folder.glob('*.cpp'), cpp_folder.glob('*.h')):
                    f2 = fid_dir / f.name 
                    shutil.copy2(f, f2)

        elif len(cpps) == len(problems):
            # print('直接使用cpp顺序拷贝')
            for i, f in enumerate(cpps):
                fid_dir = codes / f'{sid}_{labid}_{problems[i]}'
                if not fid_dir.exists():
                    fid_dir.mkdir()
                f2 = fid_dir / f.name 
                shutil.copy2(f, f2)

        else:
            print(f"error: {sid} 没有全部提交或者提交格式错误 <-----------")
            cpps        = '\n'.join([str(cpp.relative_to(junk_new)) for cpp in cpps])
            cpp_folders = '\n'.join([str(cpp.relative_to(junk_new)) for cpp in cpp_folders])
            print(cpps)
            print(cpp_folders)
            print('')
            error_sids.append(sid)



def _copy_docs():
    # forced 状态下不拷贝 reports
    if is_forced: return 

    D = {}
    fs = [f for f in junk_new.rglob('*.doc*') if f.is_file()]
    fsids = [re.findall(r'\d{12}', str(f))[0] for f in fs]

    sids_counter = collections.Counter(fsids)
    for f, sid in zip(fs, fsids):
        # D 统计 sid 是第几次出现，以便修正报告标题
        if D.get(sid) is None:
            D[sid] = 0
        else:
            D[sid] += 1

        fext = osp.splitext(osp.basename(f))[1]
        prob = problems[D[sid]]
        if sids_counter[sid] == 1:
            f2 = reports / f'{sid}_{labid}{fext}' 
        else:
            f2 = reports / f'{sid}_{labid}_{prob}{fext}'
        shutil.copy2(f, f2)

def _copy_test_case():
    for prob in PROBLEMS:
        shutil.copy2(test_case / f'{labid}_{prob}.txt',        new_test_case)
        shutil.copy2(test_case / f'{labid}_{prob}_answer.txt', new_test_case)

@chdir_wrap()
def copy_files():
    
    error_sids = []
    _copy_test_case()
    _copy_docs()
    _copy_cpps(error_sids)

    submitted = set(_dir.name for _dir in junk_new.iterdir())
    unsubmitted = list(set(sids) - submitted)

    # 写出拷贝异常
    errors = json.load(open(异常json))
    errors['提交异常'] = error_sids
    errors['未提交']   = unsubmitted
    json.dump(errors, open(异常json, 'w'), indent=4, ensure_ascii=False)
    pprint_errors()

if __name__ == '__main__':
    copy_files()
    # copy_files(True)

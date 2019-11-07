import os
import os.path as osp
import shutil
import subprocess
import pandas as pd 
import re
from utils import chdir_wrap
import json

config = json.load(open('config.json'))
config_keys = sorted(config.keys())
labid, problems, _ = list(map(config.get, config_keys))

@chdir_wrap()
def exe2output(forced=False, show_in_sublime=False):

    seps = ['=========\n']
    sids = open('student_ids.txt').read().splitlines()
    ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')

    lab = f'lab{labid}'
    os.chdir(lab)


    files = ['TLE.failed.txt', '测例输出.xlsx']
    for f in files:
        if not osp.exists(f):
            continue
        elif not forced:
            return

        fname, fext = osp.splitext(f)
        shutil.copyfile(f, fname + '.backup' + fext)
        os.remove(f)

    TLE = []
    already_sublime_new_window = False 
    for prob_i, prob in enumerate(problems):
        D = {}
        D['sid'] = ['输入'] + sids
        col = f'{labid}_{prob}'
        lines = open('test_case\\{col}.txt'.format(col=col)).read()
        found = False
        for sep in seps:
            if sep in lines:
                lines = lines.split(sep) 
                found = True
                break
        if not found: lines = lines.split('\n')
        for i, line in enumerate(lines):
            if not line: continue
            new_col = [line]
            open('line.txt', 'w').write(line + '\n')
            for sid in sids:
                s = ''
                if osp.exists(f'codes/Debug/{sid}_{col}.exe') :
                    # and f'{sid}\t问题{prob}测例{i+1}\tTimeLimitedError\t{line}' not in sTLE:
                    
                    try:
                        fin, fout = open('line.txt'), open('out.txt', 'w')
                        p = subprocess.Popen(f"codes\\Debug\\{sid}_{col}.exe", stdin=fin, stdout=fout)
                        p.wait(timeout=1)
                        s = open('out.txt').read()
                    except subprocess.TimeoutExpired:
                        p.kill()
                        if show_in_sublime: 
                            if not already_sublime_new_window:
                                already_sublime_new_window = True
                                subprocess.Popen("subl -n", shell=True)
                            subprocess.Popen(f"subl codes/{sid}_{col}/{sid}_{col}.cpp", shell=True)   
                        # subprocess.Popen(f"start codes\\Debug\\{sid}_{col}.exe", shell=True)
                        line = line.replace('\n', ' ')
                        TLE.append((sid, prob, i+1, line))
                        open('TLE.failed.txt', 'a').write(f'{sid}\t问题{int(prob)}测例{i+1}\tTimeLimitedError\t{line}\n')
                        print(f'{sid}\t问题{int(prob)}测例{i+1}\tTimeLimitedError\t{line}')

                new_col.append(ILLEGAL_CHARACTERS_RE.sub('', s))
            D[f'问题{prob}\n测例{i+1}'] = new_col

        df = pd.DataFrame(D)
        if prob_i == 0:
            writer = pd.ExcelWriter('测例输出.xlsx', engine='openpyxl')
        else:
            writer = pd.ExcelWriter('测例输出.xlsx', engine='openpyxl', mode='a')
        df.to_excel(writer, f'问题{prob}', index=False)
        writer.save()
    return TLE

if __name__ == '__main__':
    exe2output(forced=True)
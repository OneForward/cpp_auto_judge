import os
import os.path as osp
import shutil
import subprocess
import pandas as pd
import re
from utils import chdir_wrap
import json
import glob
config = json.load(open('config.json'))
config_keys = sorted(config.keys())
labid, problems, scores = list(map(config.get, config_keys))
scores = dict(zip(problems, scores))

def WA2str(wrong_cases):
    W = [int(x) for x in wrong_cases]
    W.sort()
    start, end, out = -1, -1, []
    for i, x in enumerate(W):
        if x == end+1:
            end += 1
        else:
            if 0 < i:
                out.append((start, end))
            start = end = x 
        if i == len(W)-1:
            out.append((start, end))
    outstr = []
    for st, ed in out:
        if st == ed:
            outstr.append(str(st))
        else:
            outstr.append(f'{st}-{ed}')
    return '、'.join(outstr)
            
@chdir_wrap()
def ans2scores(show_in_sublime=False):
    
    lab = f'lab{labid}'
    sids = open('student_ids.txt').read().splitlines()
    os.chdir(lab)

    df_scores = {'学号': sids}
    df_scores.update({'问题'+prob: [scores[prob]]*len(sids)
                      for prob in problems})
    df_scores = pd.DataFrame(df_scores)
    df_scores = df_scores.set_index(['学号'])
    

    D = {sid: [] for sid in sids }

    lines = open('build.failed.txt').readlines()
    lines = set(lines)
    for line in lines:
        if not line:
            continue
        sid, _, prob = re.match(r'(\d*)_(\d*)_(.*)', line).groups()
        D[sid].append(f'问题{int(prob)}：编译错误')
        df_scores.loc[sid][f'问题{prob}'] -= int(scores[prob]*0.25)
    
    too_many_wrongs = []
    def lines2DB(lines, warning):
        DB = {}
        for line in lines:
            sid, prob_case, _, _ = line.split('\t')
            prob, case = re.findall('[0-9]+', prob_case)
            if DB.get((sid, prob)) is None:
                DB[(sid, prob)] = [case]
            else:
                DB[(sid, prob)].append(case)
        already_sublime_new_window = False
        for sid, prob in DB.keys():
            wrong_cases = DB.get((sid, prob))
            prob = f'{int(prob):02}'
            df_scores.loc[sid][f'问题{prob}'] -= int(scores[prob]/20*len(wrong_cases))
            
            D[sid].append(f'问题{int(prob)}测例{WA2str(wrong_cases)}: 运行{warning}')
                        

            if len(wrong_cases) >= 7:
                too_many_wrongs.append(f'{sid}\t{prob}\t运行出现较多{warning}({len(wrong_cases)}次)')
                if show_in_sublime: 
                    if not already_sublime_new_window:
                        already_sublime_new_window = True
                        subprocess.Popen("subl -n", shell=True)
                    subprocess.Popen(f"subl codes/{sid}_{labid}_{prob}/{sid}_{labid}_{prob}.cpp", shell=True)
                    
            

    lines = open('TLE.failed.txt').readlines()
    lines2DB(lines, '异常')

    lines = []
    for prob in problems:
        lines += open(f'WA.failed.{prob}.txt').readlines()

    lines2DB(lines, '答案错误')

    prob_cols = [col for col in df_scores.columns if '问题' in col] + ['报告']
    df_scores = df_scores.assign(报告=[20]*len(sids), 总分=lambda x: x[prob_cols].sum(axis=1), 
        扣分说明=['\n'.join(D[sid]) for sid in sids])
    
    unsubmitted = open('未提交.txt').readlines()
    unsub_data = {col: 0 for col in prob_cols}
    unsub_data.update({'总分':0, '扣分说明': 'Unsubmitted'})
    unsub_data = pd.Series(unsub_data)
    for unsub in unsubmitted:
        sid = re.findall(r'\d{12}', unsub)[0]
        df_scores.loc[sid] = unsub_data


    df = pd.DataFrame(df_scores)
    try:
        df.to_excel('扣分说明.xlsx', sheet_name='扣分说明', engine='openpyxl')
    except PermissionError:
        df.to_excel('扣分说明.new.xlsx', sheet_name='扣分说明', engine='openpyxl')

    f = open('太多扣分异常.txt', 'w')
    f.write('\n'.join(too_many_wrongs))
    f.close()

    print('\n'.join(too_many_wrongs))


    for prob in problems:
        if not osp.exists(f'junk/{prob}'):
            os.makedirs(f'junk/{prob}')
        else:
            shutil.rmtree(f'junk/{prob}')
            os.makedirs(f'junk/{prob}')

    full_score = [sid for sid in sids if df_scores['总分'].loc[sid] == 100]
    for sid in full_score:
        for prob in problems:
            for f in glob.glob(f'codes/{sid}*{prob}/*.cpp'):
                shutil.copy(f, f'junk/{prob}/{osp.basename(f)}')

    open(f'优秀代码.txt', 'a').close()
    return df_scores


if __name__ == '__main__':
    ans2scores(show_in_sublime=False)

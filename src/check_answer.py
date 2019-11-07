import pandas as pd 
import os
from utils import chdir_wrap
import json

config = json.load(open('config.json', encoding='utf-8'))
config_keys = sorted(config.keys())
labid, problems, _ = list(map(config.get, config_keys))


def issubseq(subList, S):
    S = ''.join(S.lower().split())   
    current_pos = 0
    for s in subList:
        current_pos = S.find(s.lower(), current_pos) + 1
        if current_pos == 0 : return False
    return True

@chdir_wrap()
def check_answer():
    lab = f'lab{labid}'
    os.chdir(lab)
    WA = {}
    for prob in problems:
        df=pd.read_excel('测例输出.xlsx', sheet_name=f'问题{prob}')
        df1 = df.set_index(['sid'])
        cols = df1.columns
        sids = df1.index[1:]
        WA[prob] = {sid:[] for sid in sids}
        answers = open(f'test_case/{labid}_{prob}_answer.txt').readlines()
        fout = []
        for sid in sids:
            for i, ans in enumerate(answers):
                ans = ans.split()
                s_out = df1[cols[i]][sid]

                # s_out == s_out : True if s_out not nan
                if s_out == s_out and not issubseq(ans, s_out):
                    WA[prob][sid].append(i+1)
                    fout.append(f'{sid}\t问题{prob}测例{i+1}\tWrong Answer\t \n')
            if len(WA[prob][sid]) == 10:
                print(f'{sid}\t问题{prob}测例全错')
        f = open(f'WA.failed.{prob}.txt', 'w')
        f.write(''.join(fout))
        f.close()
    WAreview = [(sid, prob, len(val))for prob in WA.keys() for sid, val in WA[prob].items() if len(val)>5]
    WAreview.sort(key=lambda review: review[2], reverse=True)
    WAreview = [f'{sid}\t问题{prob}\t错误\t{lenval}'  for sid, prob, lenval in WAreview]
    open(f'WA.review.txt', 'w').write('\n'.join(WAreview))
    print('\n'.join(WAreview))
    return WA

if __name__ == '__main__':
    check_answer()
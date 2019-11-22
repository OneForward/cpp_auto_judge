import pickle
from autojudge import AutoJudge, AutoJudgeSingle
from itertools import chain 
from utils import *

def wrong2str(wrong_cases):
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

def print_errors(auto_judge, sid, prob) :
    
    if auto_judge.STATE.get(sid) == 'BUILD FAILED':
        return f'问题{int(prob)}：编译错误'

    s = []
    if auto_judge.TLE.get(sid):
        s.append(f'问题{int(prob)}测例{wrong2str(auto_judge.TLE[sid])}: 运行异常')
    if auto_judge.WA.get(sid)  :
        s.append(f'问题{int(prob)}测例{wrong2str(auto_judge.WA[sid])}: 运行错误')
    return '\n'.join(s)


def release_excel():
    
    # STEP 1: 输出分数与测评
    PS = problems_str     = [f'问题{int(prob)}({SCORES[prob]}分)' for prob in PROBLEMS]
    PM = problems_str_map = dict(zip(PROBLEMS, problems_str))

    # 构造一张行为学号，列为问题、分数、测评的评价表格 df
    df = {'学号': sids}
    df.update({col: [0]*len(sids) for col in problems_str + ['报告(20分)', '总分']})
    df.update({'扣分说明': [''] * len(sids)})
    df = pd.DataFrame(df)
    df = df.set_index(['学号'])

    dfs_out = {}
    errors = { sid: [] for sid in sids }
    for prob in PROBLEMS:    
        # 加载 评测该问题的 auto_judge
        auto_judge = pickle.load(open(cache / f'{prob}.pkl', 'rb'))

        # 构造一张行为学号，列为测例，内容为输出的表格 dfs_out[prob]
        index  = [f'问题{int(prob)}\n测例{i+1}' for i in range(10)]
        output = pd.DataFrame(auto_judge.outputs, index=index).transpose()
        dfs_out[prob] = output

        # 逐学号更新 评价表格
        for sid in sids:
            df.loc[sid, PM[prob]] = auto_judge.scores.get(sid)
            errors[sid].append(print_errors(auto_judge, sid, prob))

    df['报告(20分)'] = 20
    df['扣分说明'] = ['\n'.join(e for e in errors[sid] if e) for sid in sids]

    SCORES_COLS = problems_str + ['报告(20分)'] # 需要被计算的列名
    df['总分']    = df[SCORES_COLS].sum(axis=1)

    df.to_excel (cache / '扣分说明.xlsx')
    df.to_pickle(cache / '扣分说明.pkl')

    # STEP 2: 输出同学们代码的输出
    # time.strftime("%Y_%m_%d_%H_%M_%S")
    writer = pd.ExcelWriter(cache / "测例输出.xlsx", engine='openpyxl')
    for prob in PROBLEMS:
        dfs_out[prob].to_excel(writer, f'问题{int(prob)}', index=True)
    writer.save()

def release_zip():
    archive_files = [
        f'工科平台班_实验{int(labid)}_打分.xlsx',
        '测例输出.xlsx',
        '优秀代码',
        'test_case'
    ]

    fzip = cache / 'archive_files'
    if fzip.exists():
        shutil.rmtree(fzip)
    fzip.mkdir()

    for f in archive_files:
        f = lab / f
        if not f.exists():
            print(f'{f} is not available')
        if f.is_file():
            shutil.copy2(f, fzip / f.name)
        else:
            shutil.copytree(f, fzip / f.name)
    
    shutil.make_archive(str(root / f'实验{labid}反馈'), 'zip', base_dir=fzip)
    shutil.copy2(lab / f'工科平台班_实验{int(labid)}_打分.xlsx', root)

def recommend_cpp():

    shutil.rmtree(lab / '优秀代码')

    lines = open(lab / '优秀代码.txt').read().split()

    recommend_sids = [sid for sid in sid_snames.keys() if any(line in sid for line in lines)]
    for sid in recommend_sids:
        print(sid, '\t', sid_snames[sid])
        sid_path = lab / '优秀代码' / sid
        if not sid_path.exists():
            os.makedirs(sid_path)

        for f in codes.glob(f'{sid}*/*.*'):
            fpath = sid_path / f.parent.name
            if not fpath.exists():
                shutil.copytree(f.parent, fpath)
    
        for f in reports.glob(f'{sid}*.*'):
            sid_path = lab / '优秀代码' / sid
            shutil.copy2(f, sid_path)

def auto_judge():
    ouput_dir = lab
    test_case = root / 'test_case'
    SID_RE    = re.compile(r'\d{12}')

    for prob in PROBLEMS:
        code_dirs = [code_dir for code_dir in codes.iterdir() if code_dir.name.endswith(prob)]
        finput    = test_case / f'{labid}_{prob}.txt'
        fanswer   = test_case / f'{labid}_{prob}_answer.txt'
        

        auto_judge_pkl = ouput_dir / '.cache' / f'{prob}.pkl'

        auto_judge = AutoJudge(code_dirs, ouput_dir, finput, fanswer, SID_RE)
        auto_judge.load(auto_judge_pkl)
        auto_judge.process(fullscore=SCORES[prob])
        auto_judge.save(auto_judge_pkl)


if __name__ == '__main__':
    # auto_judge()
    # release_excel()
    # recommend_cpp()
    # release_zip()
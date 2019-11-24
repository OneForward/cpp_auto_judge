import pickle, re
from autojudge import AutoJudge
from itertools import chain 
from utils import *

SID_RE      = re.compile(r'\d{12}')

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

        # 构造一张行为学号，列为测例，内容为输出的表格 dfs_out[prob]
        output_cols = [f'问题{int(prob)}\n测例{i+1}' for i in range(10)]
        df_out = {'学号': sids}
        df_out.update({col: ['']*len(sids) for col in output_cols})
        df_out = pd.DataFrame(df_out)
        df_out = df_out.set_index(['学号'])
        dfs_out[prob] = df_out

        code_dirs = [code_dir for code_dir in codes.iterdir() if code_dir.name.endswith(prob)]
        for code_dir in code_dirs:
            auto_judge_pkl = pkl_dir / f'{code_dir.name}.pkl'
            auto_judge = AutoJudge.load_pkl(auto_judge_pkl)

            sid = student_id = SID_RE.findall(code_dir.name)[0]
            
            df.loc[sid, PM[prob]] = auto_judge.score
            errors[sid].append(auto_judge.errors(prob_name=f'问题{int(prob)}'))
            df_out.loc[sid, output_cols] = auto_judge.output

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
    
    for prob in PROBLEMS:
        code_dirs = [code_dir for code_dir in codes.iterdir() if code_dir.name.endswith(prob)]
        finput    = test_case / f'{labid}_{prob}.txt'
        fanswer   = test_case / f'{labid}_{prob}_answer.txt'

        auto_judge = AutoJudge(None, lab, finput, fanswer, SEPARATORS)

        for code_dir in code_dirs:
            auto_judge_pkl = pkl_dir / f'{code_dir.name}.pkl'
            auto_judge.reset(code_dir)
            auto_judge.load(auto_judge_pkl)
            auto_judge.process(fullscore=SCORES[prob])
            auto_judge.save(auto_judge_pkl)


if __name__ == '__main__':
    auto_judge()
    release_excel()
    # recommend_cpp()
    # release_zip()
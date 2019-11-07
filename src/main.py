from move_redundant_files import move_redundant_files
from copy_files import copy_files
from compile_cpps import compile_cpps
from exe2output import exe2output
from check_answer import check_answer
from scores import ans2scores
from recommend_cpp import recommend_cpp


# move_redundant_files()
# error_copy, unsubmitted = copy_files()
# build_failed = compile_cpps()
TLE = exe2output(forced=True)
WA = check_answer()
df_scores = ans2scores()
# recommend_cpp()


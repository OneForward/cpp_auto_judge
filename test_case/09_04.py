from pathlib import Path 

fpath = Path(__file__)
cases = open(fpath.parent / f'{fpath.stem}.txt').read().split('\n')

KEY =  [int(d) for d in '8734962']
anss = []
for case in cases:
	ans = [ord(c) + KEY[i%len(KEY)] for i, c in enumerate(case)]
	ans = [ (x-32) % 91 + 32 for x in ans ]
	ans = ''.join(chr(d) for d in ans)
	anss.append(ans)

open(fpath.parent / f'{fpath.stem}_answer.txt', 'w').write('\n'.join(anss))

		
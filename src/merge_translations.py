# One-off helper: merges the translator outputs (out1..out5.json) with the id->Russian list into translations.json.
import json, sys
T = '/tmp/claude-0/-home-user/9165a64a-5649-519e-bc94-f6abb736deaf/scratchpad/tr/'
allk = json.load(open(T + 'all.json', encoding='utf-8'))
by_id = {str(x['id']): x for x in allk}
res = {}
for i in range(1, 6):
    res.update(json.load(open(T + 'out%d.json' % i, encoding='utf-8')))
missing = [k for k in by_id if k not in res or not res[k].get('en') or not res[k].get('kk')]
print('missing ids:', missing)
out = {}
for k, x in by_id.items():
    if k in res:
        out[x['ru']] = {'en': res[k]['en'].strip(), 'kk': res[k]['kk'].strip()}
json.dump(out, open('/home/user/hemabridge-site/src/translations.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=False)
print(len(out), 'entries')

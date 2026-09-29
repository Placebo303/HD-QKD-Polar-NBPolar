import json, math
R=json.load(open('workspace/probes/eff-sweep-native/results.json'))
d=json.load(open('workspace/probes/scl-gate-t3/design.json'))
H=d['H'];N=32768;HN=H*N
def wil(k,n,z=1.959964):
    p=k/n;dd=1+z*z/n;c=(p+z*z/(2*n))/dd;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/dd
    return max(0,c-h),min(1,c+h)
print(R['H']==H,R['HN'],R['blocks_per_seed'],R['seeds'],R['threads'],R['top_m'],R['total_wall_s'])
for arm,pts in (('SCL',R['points']),('SC',R['sc_reference'])):
  for p in pts:
    rec=p['records'];n=len(rec)
    c={k:sum(bool(r.get(k,False)) for r in rec) for k in ('exact','verify_failed','undetected','decode_failed','resource_abort')}
    tot=round(p['f_nominal']*H*N/5);k1=round(.0469*tot)
    fer=(n-c['exact'])/n
    ok=(n==p['n_blocks']==32,tot==p['total'],k1==p['k1'],tot-k1==p['k2'],
        abs(p['f_book_no_crc']-5*tot/HN)<1e-12, abs(fer-p['FER_not_exact'])<1e-12,
        all(abs(a-b)<1e-9 for a,b in zip(wil(n-c['exact'],n),p['wilson95_FER'])),
        all(c[k]==p['counts'][k] for k in c))
    seeds=sorted({(r['seed'],r['block']) for r in rec})
    # consistency: exact+verify_failed+undetected+decode_failed+abort==n ; outcome flags
    part=sum(c.values())
    print(arm,p.get('L'),p['f_nominal'],tot,k1,p['k2'],'fbook %.4f'%p['f_book_no_crc'],'wCRC %.4f'%((5*tot+16)/HN),c,'sum',part,'FER %.4f'%fer,[round(x,3) for x in wil(n-c['exact'],n)],'uniq',len(seeds),all(ok),ok if not all(ok) else '', 'undet_rec',sum(r['outcome']=='undetected' for r in rec))
# pairing check
sc=R['sc_reference']
sset={(r['seed'],r['block']) for r in R['points'][0]['records']}
for p in R['points']+sc: assert {(r['seed'],r['block']) for r in p['records']}==sset
print('same block set all arms', len(sset), sorted({s for s,_ in sset}))
# paired: SC vs SCL16 at 1.20,1.25
for s in sc:
    f=s['f_nominal']; a={(r['seed'],r['block']):r['exact'] for r in s['records']}
    for L in (16,32):
        m=[p for p in R['points'] if p['L']==L and p['f_nominal']==f]
        if m:
            b={(r['seed'],r['block']):r['exact'] for r in m[0]['records']}
            print(f,'SC vs L',L,'both',sum(a[k] and b[k] for k in a),'scOnly',sum(a[k] and not b[k] for k in a),'sclOnly',sum(b[k] and not a[k] for k in a),'neither',sum(not a[k] and not b[k] for k in a))
# failed block ids per point for L16
for p in R['points']:
    print(p['L'],p['f_nominal'],'fail',[(r['seed']%100,r['block']) for r in p['records'] if not r['exact']], 'walls',round(p['wall_per_block_mean_s'],1))
print(R['points'][0]['records'][0].keys(), sc[0]['records'][0].keys())
print('sum walls',sum(p['wall_per_block_mean_s']*32 for p in R['points'])+sum(s['wall_per_block_mean_s']*32 for s in sc))

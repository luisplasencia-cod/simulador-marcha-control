import re,glob,numpy as np,sys
def parse(f):
    rows=[];day=0;prev=None
    for l in open(f):
        m=re.match(r'(\d\d):(\d\d):(\d\d) n=(\d+) Fz=(-?[\d.]+)/(-?[\d.]+)/(-?[\d.]+) V=([+-][\d.]+) RTT=(\S+) pos=(\S+)',l)
        if not m: continue
        h,mi,s=map(int,m.groups()[:3]);t=h*3600+mi*60+s
        if prev is not None and t<prev-3600: day+=1
        prev=t
        n,mn,me,mx=int(m[4]),float(m[5]),float(m[6]),float(m[7])
        rows.append((day*86400+t,n,mn,me,mx,float(m[8]),m[9],m[10]))
    return rows
for f in sorted(glob.glob('logs/monitor_2026*.log')):
    r=parse(f)
    if not r: continue
    a=np.array([x[:6] for x in r]);ok=a[:,1]>=90
    a=a[ok]
    rng=a[:,4]-a[:,2]
    print(f, 'int',len(a),'rango N med %.1f p10 %.1f p90 %.1f | media rango en mV %.1f'%(np.median(rng),*np.percentile(rng,[10,90]),np.median(rng)*1.7665), 'RTT/pos ej:',r[len(r)//2][6:],'std medias %.1f'%a[:,3].std())

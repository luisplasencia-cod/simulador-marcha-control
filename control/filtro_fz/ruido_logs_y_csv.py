# Uso: .venv/bin/python control/filtro_fz/ruido_logs_y_csv.py (desde la raiz del repo). Ver reportes/2026-11-05_ruido_fz.md
import numpy as np,sys
exec(open('control/filtro_fz/ruido_logs_parse.py').read().split('for f in sorted')[0])
d=np.genfromtxt('pruebas/lecturas_fz_20261102_175759.csv',delimiter=',',skip_header=1);n=d[:,2];fs=1000.
segs=[(0,1000),(1500,4500),(5500,7000),(8000,8500),(14500,16200)]
L=256;w=np.hanning(L);U=(w**2).sum()*fs;P=0;k=0
allq=[]
for a,b in segs:
    s=n[a:b];allq.append(s)
    for i in range(0,len(s)-L,L//2):
        x=s[i:i+L];x=x-np.polyval(np.polyfit(np.arange(L),x,1),np.arange(L))
        P=P+np.abs(np.fft.rfft(x*w))**2/U;k+=1
P=P/k;P[1:-1]*=2;f=np.fft.rfftfreq(L,1/fs);df=f[1]
q=np.concatenate(allq);print('reposo 11-02: n',len(q),'std %.3f pp %.1f'%(q.std(),q.max()-q.min()),'segmentos Welch',k,'df %.2f'%df)
for lo,hi in [(4,10),(10,30),(30,60),(60,100),(100,200),(200,500)]:
    m=(f>=lo)&(f<hi);print('%4d-%3d Hz: rms %.3f N  ASD %.4f N/rtHz'%(lo,hi,np.sqrt(P[m].sum()*df),np.sqrt(P[m].mean())))
tot=P[f>0].sum()*df
for fc in (5,10,20,50,100,200):
    m=(f<=fc)&(f>0);print('fraccion de varianza hasta %d Hz: %.1f %%  (rms %.3f N)'%(fc,100*P[m].sum()*df/tot,np.sqrt(P[m].sum()*df)))
print('autocorr lag1/2/5/20:',[round(np.dot(q[:-k]-q.mean(),q[k:]-q.mean())/np.dot(q-q.mean(),q-q.mean()),3) for k in (1,2,5,20)])
print('pico max |ASD| bins:',[(round(f[i],1),round(np.sqrt(P[i]),3)) for i in np.argsort(P)[::-1][:6]])
# 11-05
r=parse('logs/monitor_20261105_105214.log');a=np.array([x[:6] for x in r]);a=a[a[:,1]>=90]
t0=a[0,0];print('11-05: intervalos',len(a),'dur s',a[-1,0]-a[0,0])
rng=a[:,4]-a[:,2];print('rango N: med %.2f p10 %.2f p90 %.2f max %.2f; media_n %.2f std_medias %.3f (esperado ruido blanco sigma/sqrt(104)= %.3f si sigma=rango/5)'%(np.median(rng),*np.percentile(rng,[10,90]),rng.max(),a[:,3].mean(),a[:,3].std(),np.median(rng)/5/104**.5))
sig=np.median(rng)/5.0;print('sigma estimada (rango/5.0, gaussiano n~104) = %.2f N'%sig)
print('deriva media entre primer y ultimo 10 intervalos: %.2f -> %.2f'%(a[:10,3].mean(),a[-10:,3].mean()))
# 11-03 173707 por tramos
r=parse('logs/monitor_20261103_173707.log');a=np.array([x[:6] for x in r]);a=a[a[:,1]>=90]
tt=a[:,0]%86400;day=a[:,0]//86400
print('dia0 desde',a[0,0]%86400/3600,'dias',np.unique(day))
rng=a[:,4]-a[:,2]
# tramos de 10 min
import math
start=a[0,0]
for k in range(int((a[-1,0]-start)//1800)+1):
    m=(a[:,0]>=start+k*1800)&(a[:,0]<start+(k+1)*1800)
    if m.sum()>5:
        h=((start+k*1800)%86400)/3600; print('dia%d %05.2fh  n=%4d rango mediano %.1f  min %.1f'%(day[m][0],h,m.sum(),np.median(rng[m]),rng[m].min()))
m=(a[:,0]%86400>=10*3600+51*60)&(day==day.max());print('11-05 >=10:51:',m.sum(),'rango med %.2f'%np.median(rng[m]) if m.sum() else '')
m=(a[:,0]%86400>=10*3600+44*60)&(a[:,0]%86400<10*3600+51*60)&(day==day.max());print('11-05 10:44-10:51:',m.sum(),'rango med %.2f'%np.median(rng[m]))
print('---- transicion 11-05')
m0=(day==day.max())
for s in range(10*3600+37*60,10*3600+52*60,60):
    m=m0&(a[:,0]%86400>=s)&(a[:,0]%86400<s+60)
    if m.sum(): print('%02d:%02d  n=%3d rango med %.1f  min %.1f  media_Fz %.1f'%(s//3600,s%3600//60,m.sum(),np.median(rng[m]),rng[m].min(),np.median(a[m,3])))
print('---- post-fix')
sec=a[:,0]%86400
m=m0&(sec>=10*3600+50*60+10)
A=a[m];R=A[:,4]-A[:,2]
r2=parse('logs/monitor_20261105_105214.log');B=np.array([x[:6] for x in r2]);B=B[B[:,1]>=90];RB=B[:,4]-B[:,2]
print('log 173707 tramo 10:50:10-10:52:11: n',len(A),'rango med %.2f p10 %.2f p90 %.2f'%(np.median(R),*np.percentile(R,[10,90])),'max',R.max())
print('log 105214 completo: n',len(B),'rango med %.2f p10 %.2f p90 %.2f'%(np.median(RB),*np.percentile(RB,[10,90])))
allR=np.concatenate([R,RB]);ok=allR<10;print('conjunto, intervalos con rango<10 (descarta transitorios de carga):',ok.sum(),'de',len(allR),'rango med %.2f -> sigma %.2f N'%(np.median(allR[ok]),np.median(allR[ok])/5.0))
M=np.concatenate([A[:,3],B[:,3]]);dm=np.diff(M);dm=dm[np.abs(dm)<2]
print('std de diferencias consecutivas de medias(0.1 s) en reposo, /sqrt2: %.3f N (blanco puro daria %.3f)'%(dm.std()/2**.5,0.82/104**.5))
print('V pp: %.2f mV (rango N*1.7665)'%(np.median(allR[ok])*1.7665))

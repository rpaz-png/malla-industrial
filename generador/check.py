import runpy, sys, re
sys.argv=['x']
g = runpy.run_path('malla.py')
CYCLES, ORDER = g['CYCLES'], g['ORDER']

def polys(svg):
    out=[]
    for m in re.finditer(r'data-src="([^"]+)" data-dst="([^"]+)" d="([^"]+)"', svg):
        P=[]
        for t in re.finditer(r'([MLQ]) ([-\d.]+) ([-\d.]+)(?: ([-\d.]+) ([-\d.]+))?', m.group(3)):
            P.append((float(t.group(2)),float(t.group(3))))
            if t.group(4): P.append((float(t.group(4)),float(t.group(5))))
        out.append((m.group(1),m.group(2),P))
    return out

def seg_x(p,q,r,s):
    def d(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    d1,d2,d3,d4 = d(r,s,p), d(r,s,q), d(p,q,r), d(p,q,s)
    return ((d1>0)!=(d2>0)) and ((d3>0)!=(d4>0))

for mode in ("A","B"):
    G = g['generate'](mode)
    BW,BH,MX,GUT = G["BW"],G["BH"],G["MX"],G["GUT"]
    BOX_TOP, VG = G["BOX_TOP"], G["VG"]
    boxes=[(k, MX+CYCLES.index(c)*(BW+GUT), BOX_TOP+i*(BH+VG))
           for c in CYCLES for i,k in enumerate(ORDER[c])]
    E = polys(G["svg"])
    # colisiones flecha-cuadro
    hits=set()
    for src,dst,P in E:
        for i in range(len(P)-1):
            x0,y0=P[i]; x1,y1=P[i+1]
            for t in range(41):
                x=x0+(x1-x0)*t/40; y=y0+(y1-y0)*t/40
                for k,bx,by in boxes:
                    if k in (src,dst): continue
                    if bx+4<x<bx+BW-4 and by+4<y<by+BH-4: hits.add((src,dst,k))
    # cruces geométricos entre flechas
    X=[]
    for a in range(len(E)):
        for b in range(a+1,len(E)):
            (s1,d1,P),(s2,d2,Q) = E[a],E[b]
            if {s1,d1} & {s2,d2}: continue
            n=0
            for i in range(len(P)-1):
                for j in range(len(Q)-1):
                    if seg_x(P[i],P[i+1],Q[j],Q[j+1]): n+=1
            if n: X.append((s1+"→"+d1, s2+"→"+d2, n))
    print("%s | flechas %d | colisiones con cuadros %d | cruces reales %d"
          % (mode, len(E), len(hits), sum(x[2] for x in X)))
    for x in sorted(X, key=lambda z:-z[2])[:12]: print("     ", x)

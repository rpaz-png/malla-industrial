# -*- coding: utf-8 -*-
"""Malla curricular Ingeniería Industrial PUCP (ciclos 5-10).

Versión A: todas las relaciones como flechas ortogonales.
Versión B: sin flechas de salto largo; esos requisitos van como claves en el cuadro.

Orden vertical calculado con barrido de baricentro + transposiciones sobre un grafo
por capas con nodos ficticios (Sugiyama), para minimizar cruces de flechas.
"""
import re, html, itertools, copy, random, json, os

# ---------------------------------------------------------------- DATOS
COURSES = [
 (5,"1EST21","Análisis Cuantitativo para la Toma de Decisiones",2.75,["EST145"]),
 (5,"1INF23","Introducción a la Programación",3.00,["1IND65"]),
 (5,"1IND45","Control Estadístico de Calidad",3.50,["[1EST21]","1IND65"]),
 (5,"1IND44","Gestión Empresarial",3.50,["70 créditos aprobados"]),
 (5,"ECO204","Economía General",4.50,["70 créditos aprobados"]),
 (5,"1MEC39","Introducción a la Termodinámica",2.50,["1FIS04","1MAT07","1QUI02"]),
 (5,"MEC266","Dibujo Mecánico",2.75,["1ING02"]),

 (6,"1IND47","Modelos Determinísticos",3.50,["1EST21"]),
 (6,"1IND48","Analytics 1",3.00,["1INF23","1EST21"]),
 (6,"1IND49","Fundamentos de la Cadena de Suministros y Operaciones",4.00,["(1IND45)"]),
 (6,"1IND46","Habilidades Directivas",3.00,["1IND44"]),
 (6,"IND231","Ingeniería Económica",3.50,["80 créditos aprobados"]),
 (6,"MEC245","Laboratorio de Termodinámica General",1.00,["1MEC39"]),
 (6,"ING217","Resistencia de Materiales 1A",3.50,["1IND64","1MAT23","[MEC266]"]),

 (7,"1IND51","Analytics 2",3.00,["1IND48"]),
 (7,"1IND52","Diseño de la Cadena de Suministros y Operaciones",4.00,["1IND45","(1IND49)"]),
 (7,"1IND50","Gestión del Talento Humano",3.00,["1IND46"]),
 (7,"IND275","Control de Gestión Industrial",4.50,["IND231","ECO204"]),
 (7,"IND270","Procesos Industriales",3.00,["1MEC39"]),
 (7,"1MEC09","Taller de Procesos de Manufactura",1.00,["[ING217]"]),
 (7,"1MEC07","Ingeniería de Materiales",3.00,["1FIS04","1QUI02"]),
 (7,"IDM201","Idioma Extranjero (inglés)",0.00,["Acreditar capacidad de lectura"]),

 (8,"1IND59","Simulación",3.50,["1IND47"]),
 (8,"1IND53","Dinámica de la Cadena de Suministro Esbelta",4.00,["1IND49","(1IND52)"]),
 (8,"IND283","Mercadotecnia Industrial",3.50,["1IND44","1EST21"]),
 (8,"IND284","Finanzas Industriales",3.50,["IND275"]),
 (8,"IND277","Laboratorio de Procesos Industriales",1.00,["(IND270)"]),
 (8,"IEE272","Electricidad Industrial",2.50,["1FIS06"]),
 (8,"1MEC10","Procesos de Manufactura",3.00,["MEC266","1MEC09","[1MEC07]"]),
 (8,"1IND43","Práctica Supervisada Preprofesional",0.50,["130 créditos aprobados"]),

 (9,"1IND61","Análisis y Diseño de Sistemas",3.00,["1IND53"]),
 (9,"1IND55","Proyecto de Mejora",2.00,["1IND51","1IND53"]),
 (9,"IND318","Gestión Ambiental",3.50,["IND270","[IND277]"]),
 (9,"1IND91","Elaboración y Evaluación de Proyectos",3.75,["IND283","IND284","1IND52","[IND318]"]),
 (9,"1IND56","Proyecto de Ingeniería Industrial 1",2.00,["[1IND43]","[1IND55]","{1IND91}"]),
 (9,"1IND54","Automatización e Industria 4.0",4.00,["IEE272","1MEC10","[IND277]"]),
 (9,"ELEC9","Electivo de especialidad o libre disponibilidad",4.00,[]),

 (10,"IND201","Ética Profesional en Ingeniería Industrial",3.00,["[1IND91]"]),
 (10,"IND328","Gestión de Proyectos",3.00,["[1IND91]"]),
 (10,"1IND58","Proyecto de Ingeniería Industrial 2",3.00,["1IND56"]),
 (10,"1IND57","Gestión de la Innovación",3.00,["170 créditos aprobados"]),
 (10,"ELEC10","Electivo de especialidad o libre disponibilidad",8.00,[]),
]

REL = {                       # colores tomados de la identidad Made Easy
 "aprobado": ("#1B4F72", "Requiere el curso APROBADO"),
 "sim":      ("#5E9B37", "[ ]  Aprobado O cursar en paralelo"),
 "nota08":   ("#C98A1E", "( )  Haber cursado con nota 08 o más"),
 "cursado":  ("#A91E36", "{ }  Haber cursado O cursar en paralelo"),
}
SLATE, VERDE, ARENA = "#1F2C34", "#70AD47", "#EBC97E"
CHIP_ONLY = {"IND283"}          # sus requisitos van como clave, sin flecha
CYCLES  = [5,6,7,8,9,10]
CYC_COL = {5:"#1F2C34",6:"#17607F",7:"#12847A",8:"#5F901F",9:"#C1841A",10:"#97365F"}

CYC_OF  = {c[1]: c[0] for c in COURSES}
NAME_OF = {c[1]: c[2] for c in COURSES}
CRD_OF  = {c[1]: c[3] for c in COURSES}
REQ_OF  = {c[1]: c[4] for c in COURSES}

def parse_req(r):
    r = r.strip()
    for pat, tipo in ((r'^\[(.+)\]$',"sim"), (r'^\((.+)\)$',"nota08"), (r'^\{(.+)\}$',"cursado")):
        m = re.match(pat, r)
        if m: return tipo, m.group(1)
    return "aprobado", r

# aristas y etiquetas "externas" (ciclos 1-4 / créditos)
EDGES, CHIPS = [], {k: [] for k in CYC_OF}
for clave in CYC_OF:
    for r in REQ_OF[clave]:
        t, code = parse_req(r)
        if code in CYC_OF:
            EDGES.append(dict(id=len(EDGES), src=code, dst=clave, tipo=t,
                              span=CYC_OF[clave]-CYC_OF[code]))
        elif "créditos" in code:
            CHIPS[clave].append(("cred", code.replace(" aprobados","").replace("créditos","cr.")+" aprob."))
        elif "Acreditar" in code:
            CHIPS[clave].append(("cred", "Acreditar lectura"))
        else:
            CHIPS[clave].append(("prev", code))

# ============================================================ ORDEN VERTICAL
INIT = {c: [x[1] for x in COURSES if x[0]==c] for c in CYCLES}

def layered(order):
    """Grafo por capas con nodos ficticios. Devuelve (capas, enlaces)."""
    L = [[("n",k) for k in order[c]] for c in CYCLES]
    links = [[] for _ in range(len(CYCLES)-1)]
    for e in EDGES:
        li, lj = CYCLES.index(CYC_OF[e["src"]]), CYCLES.index(CYC_OF[e["dst"]])
        if lj <= li or e["dst"] in CHIP_ONLY: continue   # intraciclo / sin flecha
        chain = [("n", e["src"])]
        for m in range(li+1, lj):
            dm = ("d", e["id"], m); L[m].append(dm); chain.append(dm)
        chain.append(("n", e["dst"]))
        for k in range(len(chain)-1):
            links[li+k].append((chain[k], chain[k+1]))
    return L, links

def inversions(seq):
    n, c = len(seq), 0
    for i in range(n):
        for j in range(i+1, n):
            if seq[i] > seq[j]: c += 1
    return c

def crossings(L, links):
    tot = 0
    for i, lk in enumerate(links):
        pa = {it: p for p, it in enumerate(L[i])}
        pb = {it: p for p, it in enumerate(L[i+1])}
        tot += inversions([b for _, b in sorted((pa[a], pb[b]) for a, b in lk)])
    return tot

def optimize():
    L, links = layered(INIT)
    # los ficticios arrancan cerca de la media de sus vecinos
    for i in range(1, len(L)-0):
        pass
    best, bestc = copy.deepcopy(L), crossings(L, links)
    for sweep in range(80):
        rng = range(1, len(L)) if sweep % 2 == 0 else range(len(L)-2, -1, -1)
        for i in rng:
            j, lk = (i-1, links[i-1]) if sweep % 2 == 0 else (i+1, links[i])
            pj = {it: p for p, it in enumerate(L[j])}
            cur = {it: p for p, it in enumerate(L[i])}
            bary = {}
            for it in L[i]:
                ns = [pj[a if sweep % 2 == 0 else b]
                      for a, b in lk if (b if sweep % 2 == 0 else a) == it]
                bary[it] = sum(ns)/len(ns) if ns else cur[it]
            L[i].sort(key=lambda it: (bary[it], cur[it]))
        c = crossings(L, links)
        if c < bestc: best, bestc = copy.deepcopy(L), c
    # refinamiento por transposición de adyacentes
    L = copy.deepcopy(best)
    improved = True
    while improved:
        improved = False
        for i in range(len(L)):
            for k in range(len(L[i])-1):
                L[i][k], L[i][k+1] = L[i][k+1], L[i][k]
                c = crossings(L, links)
                if c < bestc: bestc = c; improved = True
                else:         L[i][k], L[i][k+1] = L[i][k+1], L[i][k]
    return L, bestc, crossings(*layered(INIT))

LAY, NCROSS, NCROSS0 = optimize()
ORDER = {CYCLES[i]: [it[1] for it in LAY[i] if it[0]=="n"] for i in range(len(CYCLES))}
# posición del nodo ficticio de cada arista en cada capa intermedia
DUMMY = {}      # (edge_id, layer) -> (hueco, carril, carril_max_del_hueco)
gapof, seq = {}, {}
for i, layer in enumerate(LAY):
    r, n = 0, 0
    for it in layer:
        if it[0] == "n": r += 1
        else: gapof[(it[1], i)] = r; seq[(it[1], i)] = n; n += 1
# un carril por hueco, sin chocar con los corredores de columnas vecinas
byg = {}
for (eid, lay), g in gapof.items(): byg.setdefault(g, []).append((lay, seq[(eid, lay)], eid))
lane = {}
for g, lst in byg.items():
    for lay, _, eid in sorted(lst):
        usados = {lane[(e2, l2)] for l2, _, e2 in lst
                  if (e2, l2) in lane and abs(l2 - lay) <= 1}
        k = 0
        while k in usados: k += 1
        lane[(eid, lay)] = k
for g, lst in byg.items():
    gmax = max(lane[(e2, l2)] for l2, _, e2 in lst)
    for lay, _, eid in lst:
        DUMMY[(eid, lay)] = (g, lane[(eid, lay)], gmax)

# ============================================================ RENDER
def esc(t): return html.escape(t)

def rounded(pts, r=13):
    pts = [pts[0]] + [p for i, p in enumerate(pts[1:], 1) if p != pts[i-1]]
    if len(pts) == 2: return "M %.1f %.1f L %.1f %.1f" % (pts[0]+pts[1])
    d = "M %.1f %.1f" % pts[0]
    for i in range(1, len(pts)-1):
        (x0,y0),(x1,y1),(x2,y2) = pts[i-1], pts[i], pts[i+1]
        rr = min(r, max(abs(x1-x0),abs(y1-y0))/2, max(abs(x2-x1),abs(y2-y1))/2)
        ax = x1 - (0 if x1==x0 else rr*(1 if x1>x0 else -1))
        ay = y1 - (0 if y1==y0 else rr*(1 if y1>y0 else -1))
        bx = x1 + (0 if x2==x1 else rr*(1 if x2>x1 else -1))
        by = y1 + (0 if y2==y1 else rr*(1 if y2>y1 else -1))
        d += " L %.1f %.1f Q %.1f %.1f %.1f %.1f" % (ax,ay,x1,y1,bx,by)
    return d + " L %.1f %.1f" % pts[-1]


def generate(mode):
    """mode 'A' = todas las flechas · mode 'B' = sin saltos largos (claves en el cuadro)"""
    MX, BW, GUT = 96, 366, 196
    BH, VG = (188, 58) if mode == "A" else (222, 34)
    BAR_H, HDR_Y, HDR_H = 208, 254, 66
    BOX_TOP = 418 if mode == "A" else 368

    maxn    = max(len(v) for v in ORDER.values())
    COL_BOT = BOX_TOP + maxn*BH + (maxn-1)*VG
    LEG_Y   = COL_BOT + (95 if mode == "A" else 80)
    W = MX*2 + len(CYCLES)*BW + (len(CYCLES)-1)*GUT

    colx  = lambda c: MX + CYCLES.index(c)*(BW+GUT)
    nodes = {}
    for c in CYCLES:
        for i, k in enumerate(ORDER[c]):
            nodes[k] = dict(clave=k, cyc=c, idx=i, x=colx(c), y=BOX_TOP + i*(BH+VG))

    def gap_y(r):
        return BOX_TOP - VG/2 if r == 0 else BOX_TOP + (r-1)*(BH+VG) + BH + VG/2

    # ---- aristas de esta versión + claves extra en los cuadros -------------
    chips = {k: list(v) for k, v in CHIPS.items()}
    oculta = (lambda e: e["dst"] in CHIP_ONLY or e["span"] >= 2) if mode == "B" \
             else (lambda e: e["dst"] in CHIP_ONLY)
    use = [e for e in EDGES if not oculta(e)]
    for e in sorted((x for x in EDGES if oculta(x)),
                    key=lambda x: (x["dst"], CYC_OF[x["src"]], x["src"])):
        chips[e["dst"]].append(("rel-"+e["tipo"], e["src"]))

    # ---- y de cada nodo ficticio ------------------------------------------
    dy = {}
    for e in use:
        if e["span"] < 2: continue
        li = CYCLES.index(CYC_OF[e["src"]])
        for m in range(li+1, CYCLES.index(CYC_OF[e["dst"]])):
            g, k, gmax = DUMMY[(e["id"], m)]
            step = min(14.0, (VG - 8) / (gmax + 1))
            dy[(e["id"], m)] = gap_y(g) + (k - gmax/2) * step

    # ---- anclas en los bordes (3 pasadas: la geometría real reordena) -----
    ain, aout = {}, {}
    for e in use:
        s_, d_ = nodes[e["src"]], nodes[e["dst"]]
        li, lj = CYCLES.index(s_["cyc"]), CYCLES.index(d_["cyc"])
        aout[e["id"]] = dy.get((e["id"], li+1), d_["y"] + BH/2)
        ain[e["id"]]  = dy.get((e["id"], lj-1), s_["y"] + BH/2)
    lazo_izq = lambda e: e["span"] == 0 and CYCLES.index(CYC_OF[e["src"]]) == 0
    for _ in range(3):
        side = {k: {"R": [], "L": []} for k in nodes}
        for e in use:
            side[e["src"]]["L" if lazo_izq(e) else "R"].append((aout[e["id"]], e["id"], "out"))
            side[e["dst"]]["L" if (e["span"] or lazo_izq(e)) else "R"].append(
                (ain[e["id"]], e["id"], "in"))
        anc = {}
        for k, n in nodes.items():
            for sd in ("R", "L"):
                lst = sorted(side[k][sd]); m = len(lst)
                for j, (_, eid, kind) in enumerate(lst):
                    anc[(eid, kind)] = (n["x"] + BW if sd == "R" else n["x"],
                                        n["y"] + BH*(j+1)/(m+1))
        for e in use:                      # la y de aproximación real de los saltos de 1 ciclo
            if e["span"] == 1:
                ain[e["id"]]  = anc[(e["id"], "out")][1]
                aout[e["id"]] = anc[(e["id"], "in")][1]

    # ---- segmentos verticales por canal ------------------------------------
    verts = {}
    plan  = {}
    for e in use:
        sx, sy = anc[(e["id"], "out")]; tx, ty = anc[(e["id"], "in")]
        s_, d_ = nodes[e["src"]], nodes[e["dst"]]
        li, lj = CYCLES.index(s_["cyc"]), CYCLES.index(d_["cyc"])
        if e["span"] == 0:
            if lazo_izq(e):
                plan[e["id"]] = ("intraL", sx, sy, tx, ty, [])
            else:
                verts.setdefault(CYCLES.index(s_["cyc"]), []).append(((e["id"], 0), sy, ty, "intra"))
                plan[e["id"]] = ("intra", sx, sy, tx, ty, [])
            continue
        ys = [sy] + [dy[(e["id"], m)] for m in range(li+1, lj)] + [ty]
        segs = []
        for k in range(lj - li):
            gdx = li + k
            if abs(ys[k+1] - ys[k]) > 0.5:
                verts.setdefault(gdx, []).append(((e["id"], k), ys[k], ys[k+1], "norm"))
            segs.append((gdx, ys[k], ys[k+1]))
        plan[e["id"]] = ("orto", sx, sy, tx, ty, segs)

    # ---- orden de carriles que minimiza cruces dentro de cada canal --------
    def pair_cross(a, b):                  # a queda a la IZQUIERDA de b
        _, sa, ta, ka = a; _, sb, tb, kb = b
        loa, hia = min(sa, ta) - 1, max(sa, ta) + 1
        lob, hib = min(sb, tb) - 1, max(sb, tb) + 1
        c = 0
        if loa < sb < hia: c += 1                       # b entra por la izquierda
        if kb == "intra" and loa < tb < hia: c += 1     # el lazo vuelve por la izquierda
        if ka == "norm" and lob < ta < hib: c += 1      # a sale por la derecha
        return c
    lane_x = {}
    for gdx, lst in verts.items():
        tot = lambda o: sum(pair_cross(o[i], o[j])
                            for i in range(len(o)) for j in range(i+1, len(o)))
        def pulir(o):
            b, moved = tot(o), True
            while moved:                                # intercambios + reinserciones
                moved = False
                for i in range(len(o)-1):
                    o[i], o[i+1] = o[i+1], o[i]
                    t = tot(o)
                    if t < b: b, moved = t, True
                    else: o[i], o[i+1] = o[i+1], o[i]
                for i in range(len(o)):
                    it = o.pop(i); cand, pos = b, i
                    for j in range(len(o)+1):
                        o.insert(j, it); t = tot(o); o.pop(j)
                        if t < cand: cand, pos = t, j
                    o.insert(pos, it)
                    if cand < b: b, moved = cand, True
            return b
        rnd = random.Random(7)
        order = sorted(lst, key=lambda v: (min(v[1], v[2]), v[2]))
        best = pulir(order)
        for _ in range(120):                            # reinicios aleatorios
            cand = lst[:]; rnd.shuffle(cand)
            c = pulir(cand)
            if c < best: best, order = c, cand
            if best == 0: break
        x0 = MX + gdx*(BW+GUT) + BW; x1 = MX + (gdx+1)*(BW+GUT)
        m = len(order); spanx = min(GUT - 56, 15*m)
        for i, (key, _, _, _) in enumerate(order):
            lane_x[key] = (x0 + x1)/2 - spanx/2 + (spanx*i/(m-1) if m > 1 else 0)

    # ---- construir los paths ----------------------------------------------
    for e in use:
        kind, sx, sy, tx, ty, segs = plan[e["id"]]
        if kind in ("intra", "intraL"):
            vx = (MX - 34) if kind == "intraL" else lane_x[(e["id"], 0)]
            e["d"] = rounded([(sx,sy),(vx,sy),(vx,ty),(tx,ty)], 11)
            e["head"] = "right" if kind == "intraL" else "left"; continue
        pts = [(sx, sy)]
        for k, (g, ya, yb) in enumerate(segs):
            if abs(yb - ya) > 0.5:
                vx = lane_x[(e["id"], k)]
                pts += [(vx, ya), (vx, yb)]
        pts.append((tx, ty))
        e["d"] = rounded(pts, 12); e["head"] = "right"

    # ---- SVG ---------------------------------------------------------------
    H_placeholder = LEG_Y + 300
    svg = ['<svg class="wires" width="%d" height="%d" viewBox="0 0 %d %d">' %
           (W, H_placeholder, W, H_placeholder), "<defs>"]
    for k, (c, _) in REL.items():
        for sd in ("right", "left"):
            p = "M0,0 L11,4 L0,8 Z" if sd == "right" else "M11,0 L0,4 L11,8 Z"
            svg.append('<marker id="a-%s-%s" markerWidth="11" markerHeight="8" refX="%s" refY="4" '
                       'orient="auto"><path d="%s" fill="%s"/></marker>'
                       % (k, sd, "10.5" if sd == "right" else "0.5", p, c))
    svg.append("</defs>")
    for e in use:
        c = REL[e["tipo"]][0]
        svg.append('<path class="wire w-%s" data-src="%s" data-dst="%s" d="%s" fill="none" '
                   'stroke="%s" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" '
                   'marker-end="url(#a-%s-%s)"/>'
                   % (e["tipo"], e["src"], e["dst"], e["d"], c, e["tipo"], e["head"]))
    svg.append("</svg>")

    # ---- cuadros -----------------------------------------------------------
    bx = []
    for c in CYCLES:
        tot = sum(CRD_OF[k] for k in ORDER[c])
        bx.append('<div class="cyc" style="left:%dpx;top:%dpx;width:%dpx;--k:%s">'
                  '<b>CICLO %d</b><span>%.2f créditos</span></div>'
                  % (colx(c), HDR_Y, BW, CYC_COL[c], c, tot))
    for k, n in nodes.items():
        elec = k.startswith("ELEC")
        ch = ""
        for t, v in chips[k]:
            if t.startswith("rel-"):
                col = REL[t[4:]][0]
                ch += '<i class="ch rel" style="--c:%s">%s</i>' % (col, esc(v))
            else:
                ch += '<i class="ch %s">%s</i>' % (t, esc(v))
        cr = ('<span class="cr">%.2f cr</span>' % CRD_OF[k]) if CRD_OF[k] > 0 else '<span class="cr">sin créditos</span>'
        bx.append('<div class="box%s" id="b-%s" data-c="%s" style="left:%dpx;top:%dpx;--k:%s">'
                  '<div class="hd"><span class="cd">%s</span>%s</div>'
                  '<div class="nm">%s</div><div class="ft">%s</div></div>'
                  % (" elec" if elec else "", k, k, n["x"], n["y"], CYC_COL[n["cyc"]],
                     "ELECTIVO" if elec else k, cr, esc(NAME_OF[k]), ch))

    legend = "".join(
        '<div class="li"><svg width="104" height="20"><line x1="2" y1="10" x2="82" y2="10" '
        'stroke="%s" stroke-width="4" stroke-linecap="round"/><path d="M82,4 L96,10 L82,16 Z" '
        'fill="%s"/></svg><span>%s</span></div>' % (c, c, esc(t)) for k, (c, t) in REL.items())

    hay_rel = any(t.startswith("rel-") for v in chips.values() for t, _ in v)
    nota_b = ('<div class="note n2">Las <b>claves con recuadro de color</b> son requisitos dibujados sin flecha; '
              'el color indica el tipo de relación.</div>' if hay_rel else "") + \
             ('<div class="note n2">Los electivos deben sumar 12 créditos o más entre electivos de '
              'especialidad y de libre disponibilidad.</div>')

    me_w = 262
    me_x = MX + 5*(BW+GUT) + BW - me_w
    me_y = COL_BOT - 400
    return dict(W=W, LEG_Y=LEG_Y, MX=MX, BW=BW, BH=BH, HDR_H=HDR_H, BAR_H=BAR_H,
                ME=(me_x, me_y, me_w),
                BOX_TOP=BOX_TOP, VG=VG, GUT=GUT,
                svg="\n".join(svg), boxes="\n".join(bx), legend=legend, nota_b=nota_b,
                nedges=len(use), mode=mode,
                vlinks=[[e["src"], e["dst"], e["tipo"]] for e in EDGES if oculta(e)])


CSS = """
@font-face{font-family:MEHead;src:url(data:font/woff2;base64,__P6__) format('woff2');font-weight:600}
@font-face{font-family:MEHead;src:url(data:font/woff2;base64,__P7__) format('woff2');font-weight:700}
@font-face{font-family:MEBody;src:url(data:font/woff2;base64,__I4__) format('woff2');font-weight:400}
@font-face{font-family:MEBody;src:url(data:font/woff2;base64,__I6__) format('woff2');font-weight:600}
@font-face{font-family:MEBody;src:url(data:font/woff2;base64,__I7__) format('woff2');font-weight:700}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:MEBody,'DejaVu Sans',sans-serif;background:#F2F4F3;color:#1F2C34}
#stage{position:relative;width:%(W)dpx;height:%(H)dpx;background:#F2F4F3}
.topbar{position:absolute;left:0;top:0;width:100%%;height:%(BARH)dpx;background:#1F2C34;
  display:flex;align-items:center;justify-content:space-between;padding:0 %(MX)dpx}
.topbar h1{font-family:MEHead;font-weight:700;font-size:54px;color:#fff;letter-spacing:-.5px}
.topbar .marca{display:flex;align-items:center;gap:34px}
.topbar .marca img.mklogo{height:108px}
.topbar .marca img.eq{height:140px}
.wires{position:absolute;left:0;top:0;pointer-events:none}
.mreasy{position:absolute;left:%(MEX)dpx;top:%(MEY)dpx;width:%(MEW)dpx}
.cyc{position:absolute;height:%(HDRH)dpx;border-radius:8px;background:var(--k);
  display:flex;align-items:center;justify-content:space-between;padding:0 20px;color:#fff}
.cyc b{font-family:MEHead;font-weight:600;font-size:27px;letter-spacing:.6px}
.cyc span{font-size:18.5px;color:rgba(255,255,255,.82);font-weight:600}
.box{position:absolute;width:%(BW)dpx;height:%(BH)dpx;background:#fff;border:1.5px solid #D8DEDC;
  border-left:9px solid var(--k);border-radius:9px;padding:14px 18px 13px 19px;
  box-shadow:0 1px 3px rgba(31,44,52,.10);display:flex;flex-direction:column}
.box.elec{background:#EBEEEC;border-style:dashed;border-left-style:solid}
.hd{display:flex;justify-content:space-between;align-items:baseline}
.cd{font-family:MEHead;font-weight:700;font-size:26px;color:var(--k);letter-spacing:.3px}
.cr{font-size:19px;color:#6A737A;font-weight:600}
.nm{font-size:24px;line-height:1.27;margin-top:9px;flex:1;font-weight:400;color:#22303A}
.ft{display:flex;flex-wrap:wrap;gap:7px;align-content:flex-end;overflow:hidden}
.ch{font-style:normal;font-size:17.5px;padding:2px 9px;border-radius:5px;background:#EBEEEC;
  color:#5F696F;white-space:nowrap;font-weight:600}
.ch.cred{background:#FBF0D8;color:#8A6410}
.ch.rel{background:#fff;color:var(--c);border:2px solid var(--c);font-weight:700;padding:1px 8px}
.lg{position:absolute;left:%(MX)dpx;top:%(LEGY)dpx;width:%(LW)dpx;background:#fff;
  border:1.5px solid #D8DEDC;border-radius:10px;padding:26px 32px 34px;border-top:5px solid #70AD47}
.lg h3{font-family:MEHead;font-weight:600;font-size:21px;letter-spacing:1.4px;color:#1F2C34;margin-bottom:18px}
.lgrid{display:flex;gap:44px;flex-wrap:wrap}
.li{display:flex;align-items:center;gap:14px;font-size:23px}
.note{margin-top:20px;font-size:24px;color:#3D4A52;line-height:1.5;white-space:nowrap}
.note b{color:#1F2C34}
.note i{font-style:normal;background:#E4E9E6;color:#3D4A52;padding:2px 9px;border-radius:4px;
  font-size:21px;font-weight:600}
.note i.cred{background:#FBF0D8;color:#7A5709}
.note.n2{margin-top:10px}
"""

INTER = """
html,body{height:100%;overflow:hidden}
body{display:flex;flex-direction:column}
.box{transition:opacity .12s, box-shadow .12s;cursor:pointer}
.wire{transition:opacity .12s, stroke-width .12s}
body.focus .box{opacity:.15}
body.focus .wire{opacity:.05}
body.focus .box.on{opacity:1;box-shadow:0 6px 18px rgba(31,44,52,.22)}\nbody.focus .box.on .ch.rel,body.focus .box.hero .ch.rel{box-shadow:0 0 0 3px rgba(112,173,71,.35)}
body.focus .box.hero{opacity:1;box-shadow:0 0 0 3px #70AD47,0 8px 22px rgba(31,44,52,.30)}
body.focus .wire.on{opacity:1;stroke-width:4.5}
.bar{flex:0 0 auto;z-index:9;background:#fff;border-bottom:2px solid #70AD47;padding:8px 16px;
  display:flex;gap:14px;align-items:center;flex-wrap:wrap;font-size:13.5px}
.bar label{display:flex;gap:7px;align-items:center;cursor:pointer;white-space:nowrap;color:#1F2C34}
.bar .sw{width:26px;height:4px;border-radius:2px;display:inline-block}
.bar .hint{color:#68717E}
.bar .sep{width:1px;height:22px;background:#D8DEDC}
.zoom{display:flex;align-items:center;gap:6px}
.zoom button{font:inherit;font-size:14px;border:1.4px solid #D8DEDC;background:#fff;border-radius:7px;
  padding:4px 11px;cursor:pointer;color:#14181F;line-height:1.3}
.zoom button:hover{background:#EEF1F5}
.zoom button.act{background:#1F2C34;color:#fff;border-color:#1F2C34}
.zoom #zl{font-variant-numeric:tabular-nums;color:#68717E;min-width:46px;text-align:right}
#wrap{flex:1 1 auto;overflow:auto;background:#F2F4F3;cursor:grab}
#wrap.drag{cursor:grabbing}
#sizer{position:relative}
#stage{transform-origin:0 0}
"""

JS = """
const A={},B={};
document.querySelectorAll('.wire').forEach(w=>{
  (A[w.dataset.dst]=A[w.dataset.dst]||[]).push(w);
  (B[w.dataset.src]=B[w.dataset.src]||[]).push(w);});
function clr(){document.body.classList.remove('focus');
  document.querySelectorAll('.on,.hero').forEach(e=>e.classList.remove('on','hero'));}
function foc(c){clr();document.body.classList.add('focus');
  document.getElementById('b-'+c).classList.add('hero');
  (A[c]||[]).forEach(w=>{if(!w)return;w.classList.add('on');document.getElementById('b-'+w.dataset.src).classList.add('on');});
  (B[c]||[]).forEach(w=>{if(!w)return;w.classList.add('on');document.getElementById('b-'+w.dataset.dst).classList.add('on');});
  vlink(c);}
const VL=__VL__;                       // relaciones sin flecha (clave en el cuadro)
VL.forEach(([s,d])=>{(A[d]=A[d]||[]).push(null);(B[s]=B[s]||[]).push(null);});
function vlink(c){
  VL.forEach(([s,d])=>{
    if(d===c) document.getElementById('b-'+s).classList.add('on');
    if(s===c) document.getElementById('b-'+d).classList.add('on');});}
document.querySelectorAll('.box').forEach(b=>{
  b.addEventListener('mouseenter',()=>foc(b.dataset.c));b.addEventListener('mouseleave',clr);});
document.querySelectorAll('.bar input').forEach(i=>i.addEventListener('change',()=>{
  document.querySelectorAll('.w-'+i.dataset.t).forEach(w=>w.style.display=i.checked?'':'none');}));
const SW=__W__,SH=__H__;
const wrap=document.getElementById('wrap'),sizer=document.getElementById('sizer'),
      stage=document.getElementById('stage'),zl=document.getElementById('zl'),
      bF=document.getElementById('bfit'),b1=document.getElementById('b100');
let z=1,mode='fit';
function ap(s){z=Math.min(2.5,Math.max(.12,s));stage.style.transform='scale('+z+')';
  sizer.style.width=(SW*z)+'px';sizer.style.height=(SH*z)+'px';
  zl.textContent=Math.round(z*100)+'%';
  bF.classList.toggle('act',mode==='fit');b1.classList.toggle('act',mode==='100');}
function fit(){mode='fit';ap((wrap.clientWidth-6)/SW);
  requestAnimationFrame(()=>ap((wrap.clientWidth-6)/SW));}
bF.onclick=fit;b1.onclick=()=>{mode='100';ap(1);};
document.getElementById('bin').onclick=()=>{mode='free';ap(z*1.25);};
document.getElementById('bout').onclick=()=>{mode='free';ap(z/1.25);};
addEventListener('resize',()=>{if(mode==='fit')fit();});fit();
let dg=null;
wrap.addEventListener('mousedown',e=>{if(e.target.closest('.box'))return;
  dg={x:e.clientX,y:e.clientY,l:wrap.scrollLeft,t:wrap.scrollTop};wrap.classList.add('drag');});
addEventListener('mousemove',e=>{if(!dg)return;
  wrap.scrollLeft=dg.l-(e.clientX-dg.x);wrap.scrollTop=dg.t-(e.clientY-dg.y);});
addEventListener('mouseup',()=>{dg=null;wrap.classList.remove('drag');});
"""

SHORT = {"aprobado":"Aprobado","sim":"[ ] Paralelo","nota08":"( ) Nota 08+","cursado":"{ } Cursado/paralelo"}

ASSETS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets.json")))

def page(G, H, interactive):
    css = CSS % dict(W=G["W"], H=H, MX=G["MX"], BW=G["BW"], BH=G["BH"], BARH=G["BAR_H"],
                     HDRH=G["HDR_H"], LEGY=G["LEG_Y"], LW=G["W"]-2*G["MX"],
                     MEX=G["ME"][0], MEY=G["ME"][1], MEW=G["ME"][2])
    for k in ("P6", "P7", "I4", "I6", "I7"):
        css = css.replace("__%s__" % k, ASSETS[k])
    bar = pre = post = js = ""
    if interactive:
        sw = "".join('<label><input type="checkbox" data-t="%s" checked>'
                     '<span class="sw" style="background:%s"></span>%s</label>'
                     % (k, c, esc(SHORT[k])) for k, (c, t) in REL.items())
        bar = ('<div class="bar"><div class="zoom"><button id="bout">−</button><button id="bin">+</button>'
               '<button id="bfit">Ajustar</button><button id="b100">100%</button>'
               '<span id="zl">100%</span></div><div class="sep"></div>' + sw +
               '<div class="sep"></div><span class="hint">Cursor sobre un curso = aislar sus dependencias</span></div>')
        pre, post = '<div id="wrap"><div id="sizer">', '</div></div>'
        js = "<script>%s</script>" % (JS.replace("__W__", str(G["W"])).replace("__H__", str(H))
                                        .replace("__VL__", json.dumps(G["vlinks"])))
    top = ('<div class="topbar"><h1>Ingeniería Industrial - Plan de Estudio 26.2</h1>'
           '<div class="marca"><img class="mklogo" src="data:image/png;base64,%s">'
           '<img class="eq" src="data:image/png;base64,%s"></div></div>' % (ASSETS["LOGO"], ASSETS["ENG"]))
    mre = '<img class="mreasy" src="data:image/png;base64,%s">' % ASSETS["MREASY"]
    head = ('<meta name="description" content="Malla de requisitos de Ingeniería Industrial PUCP, '
            'ciclos 5 al 10. Plan de estudios vigente 2026-2. Made Easy.">'
            '<link rel="icon" type="image/png" href="data:image/png;base64,%s">'
            '<meta property="og:type" content="website">'
            '<meta property="og:title" content="Ingeniería Industrial - Plan de Estudio 26.2">'
            '<meta property="og:description" content="Malla interactiva de requisitos, ciclos 5 al 10.">'
            '<meta property="og:image" content="malla-plan-estudio-26-2.png">'
            '<meta name="twitter:card" content="summary_large_image">' % ASSETS["FAV"])
    return ("""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ingeniería Industrial - Plan de Estudio 26.2</title>""" + head + """<style>%s%s</style></head><body>%s%s
<div id="stage">
%s
%s
%s
%s
<div class="lg"><h3>TIPO DE RELACIÓN ENTRE CURSOS</h3><div class="lgrid">%s</div>
<div class="note">Etiquetas dentro del recuadro: <i>1FIS04</i> = curso aprobado de ciclos 1–4 &nbsp;·&nbsp; <i class="cred">70 cr. aprob.</i> = créditos aprobados del plan.</div>
%s</div></div>%s%s</body></html>"""
            % (css, INTER if interactive else "", bar, pre, top,
               G["svg"], G["boxes"], mre, G["legend"], G["nota_b"], post, js))


if __name__ == "__main__":
    import json, sys
    print("cruces: %d -> %d" % (NCROSS0, NCROSS))
    out = {}
    for m in ("A", "B"):
        G = generate(m)
        tmp = page(G, G["LEG_Y"] + 300, False)
        open("probe_%s.html" % m, "w", encoding="utf-8").write(
            tmp.replace("</body>", '<script>document.title="H:"+Math.ceil('
                        'document.querySelector(".lg").getBoundingClientRect().bottom+48)</script></body>'))
        out[m] = G
    
    print({m: (out[m]["W"], out[m]["LEG_Y"], out[m]["nedges"]) for m in out})

def emit(m, H):
    G = generate(m)
    tag = "A_flechas" if m == "A" else "B_claves"
    open("print_%s.html" % m, "w", encoding="utf-8").write(page(G, H, False))
    open("Malla_%s.html" % tag, "w", encoding="utf-8").write(page(G, H, True))
    return G["W"], H

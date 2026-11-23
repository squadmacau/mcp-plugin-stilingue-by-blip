#!/usr/bin/env python3
"""
Central de Influenciadores — motor de enriquecimento e score.

Uso:
  python3 build_central.py prepare <pasta_trabalho>
      Lê config.json + raw/, gera candidatos.md (para curadoria) e lookups.md
      (lotes de handles sem seguidores para buscar no Radar).
  python3 build_central.py build <pasta_trabalho> [--template caminho.html]
      Lê config.json + raw/ + curadoria.json, gera out/data.json e
      out/central.html (template + dados).

Estrutura da pasta de trabalho:
  config.json               categoria, período, subnichos, cidades, marca, concorrentes
  raw/trend__<slug>.json    resultado de radar(data_type=trend_users) por subnicho
  raw/lookup__<n>.json      resultado de radar(trend_users) com handles em OR
  raw/posts__<janela>__<k>.json   resultado de radar(data_type=posts)
  raw/statistics.json       radar(statistics) da query principal (opcional)
  raw/linechart.json        radar(linechart) da query principal (opcional)
  raw/warroom__<painel>__<recorte>.json  warroom_query path=top_influenciadores de um painel
                            (recorte: marca-<x>, conc-<x>, cat-<x>, cat-<x>-pessoas, geral)
  raw/painelposts__<painel>__<n>.json    warroom_query path=publicacoes com uids em lote
  curadoria.json            ajustes manuais/pesquisa online por perfil (opcional)

Nada aqui inventa dado: campo sem fonte fica vazio e aparece como "a confirmar".
"""
import json, math, os, re, sys, glob, html, unicodedata, statistics, datetime, collections

# ----------------------------------------------------------------- utilidades
def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return s.lower()

TAG_RE = re.compile(r"<[^>]+>")
def clean_text(t):
    t = TAG_RE.sub("", str(t or "")).replace("&nbsp;", " ")
    return html.unescape(re.sub(r"\s+", " ", t)).strip()

def load(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def unwrap(d):
    """Aceita a resposta crua da tool ou {data:[...]} / {influencers_list:[...]}."""
    if isinstance(d, dict):
        for k in ("data", "influencers_list", "influencers", "posts", "result"):
            if k in d and isinstance(d[k], list):
                v = d[k]
                if v and isinstance(v[0], dict) and "influencers" in v[0]:
                    return [i for blk in v for i in blk.get("influencers", [])]
                return v
    return d if isinstance(d, list) else []

def parse_date(s):
    for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%d", "%Y/%m/%d %H:%M", "%Y%m%d%H%M"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except Exception:
            pass
    return None

def median(xs, default=None):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else default

def pct_rank(value, population):
    pop = sorted(p for p in population if p is not None)
    if value is None or not pop:
        return None
    below = sum(1 for p in pop if p < value)
    equal = sum(1 for p in pop if p == value)
    return (below + 0.5 * equal) / len(pop)

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def key_of(channel, name):
    return f"{norm(channel)}:{norm(name).strip().lstrip('@')}"

def handle_from_url(url, fallback):
    m = re.search(r"(instagram|twitter|x|tiktok)\.com/@?([^/?#]+)", url or "")
    return m.group(2) if m else fallback

# ----------------------------------------------------------------- tiers
TIERS = [("nano", 1_000, 10_000), ("micro", 10_000, 100_000), ("mid", 100_000, 500_000),
         ("macro", 500_000, 1_000_000), ("mega", 1_000_000, float("inf"))]
TIER_ORDER = {"comunidade": 0, "nano": 1, "micro": 2, "mid": 3, "macro": 4, "mega": 5}

def tier_of(followers):
    if not followers:
        return None
    if followers < 1_000:
        return "comunidade"
    for name, lo, hi in TIERS:
        if lo <= followers < hi:
            return name
    return "mega"

# ----------------------------------------------------------------- tipo de perfil
TIPO_PATTERNS = [
    ("midia", r"(jornal|news|noticia|online$|\btv\b|tv[a-z]|radio|revista|portal|magazine|folha|gazeta|correio|diario|blog ?do|imprensa|podcast oficial|urgente|^canal|fofoca|famosos)"),
    ("varejo", r"(loja|lojas|store|shop|shopping|drog|farma|market|atacad|outlet|e-?commerce)"),
    ("marca", r"(oficial|official|cosmetic|cosmetico|ceutical|\blab\b|labs|industria|brasil$|_br$|group|grupo|agency|agencia|clinica|clinic|instituto|academy|escola)"),
    ("agregador", r"(memes?|videos|virais?|dicas ?de|curiosidades|resenha|melted|humor|promo|ofertas|achadinhos|cupons?)"),
    ("especialista", r"(^dr[a]?[._ ]|^dr[a]?[a-z]|dermato|medic|nutri|farmaceut|cientista|prof[._ ]|biomedic|esteticista|terapeuta|enferm)"),
]

def guess_tipo(name, url=""):
    n = (norm(name) + " " + norm(handle_from_url(url, ""))).strip()
    for tipo, pat in TIPO_PATTERNS:
        if re.search(pat, n):
            return tipo
    return "criador"

CREATOR_TYPES = {"criador", "especialista"}

# ----------------------------------------------------------------- texto
STOP = set(norm("""a o e é de da do das dos em no na nos nas um uma uns umas para pra por com sem
que se sua seu suas seus ao aos à às mais muito muita como mas ou já também isso essa esse esta
este aqui ali lá eu você vocês voce voces ele ela eles elas nós nos meu minha meus minhas te
me lhe só so tem ter foi ser são sao vai vou está esta estão estao quando onde porque pq tudo
todo toda todos todas cada sobre entre até ate depois antes hoje dia dias vez nao não sim ja
the and of to in for is on with your you my this that it at be are link bio aqui comenta
salva siga segue post video vídeo reels""").split())
HASH_RE = re.compile(r"#([\wÀ-ÿ]+)")
MENTION_RE = re.compile(r"@([A-Za-z0-9_.]{3,30})")
PUBLI_RE = re.compile(r"(#publi\b|#publicidade|#ad\b|#parceria|parceria paga|publipost|#recebido|#publi[a-z]*|\bpubli\b)", re.I)
AFIL_RE = re.compile(r"(comente?\s+[\"“']?\w+[\"”']?\s+que\s+(eu\s+)?te\s+(envio|mando)|link\s+(na|da)\s+bio|cupo(m|ns)|c[oó]digo\s+de\s+desconto|link\s+de\s+afiliad|achadinhos?|shopee|amazon\.com\.br|mercado\s*livre)", re.I)

def tokens(text):
    t = norm(HASH_RE.sub(" ", MENTION_RE.sub(" ", text)))
    return [w for w in re.findall(r"[a-z][a-z0-9\-]{2,}", t) if w not in STOP]

def term_regex(term):
    # aceita termos simples ou expressões do Radar ('"pele negra" AND (manchas OR ...)'):
    # para marcar subnicho usa só o primeiro termo da expressão
    t = re.split(r"\s+(?:AND|OR|AND NOT)\s+", str(term).strip())[0]
    t = norm(t.strip().strip("()").strip().strip('"'))
    if t.endswith("*"):
        return re.compile(r"\b" + re.escape(t[:-1]) + r"\w*")
    return re.compile(r"\b" + re.escape(t) + r"\b")

# ----------------------------------------------------------------- carregamento
def load_inputs(wd):
    cfg = load(os.path.join(wd, "config.json"), {}) or {}
    raw = os.path.join(wd, "raw")
    trends = {}
    for f in sorted(glob.glob(os.path.join(raw, "trend__*.json"))):
        slug = os.path.basename(f)[len("trend__"):-5]
        trends[slug] = unwrap(load(f, []))
    lookups = [i for f in sorted(glob.glob(os.path.join(raw, "lookup__*.json"))) for i in unwrap(load(f, []))]
    posts, windows = {}, set()
    for f in sorted(glob.glob(os.path.join(raw, "posts__*.json"))):
        parts = os.path.basename(f)[:-5].split("__")
        win = parts[1] if len(parts) > 1 else "w"
        windows.add(win)
        for p in unwrap(load(f, [])):
            if isinstance(p, dict) and p.get("pid"):
                p = dict(p); p["_win"] = win
                posts.setdefault(p["pid"], p)
    warroom = []
    for f in sorted(glob.glob(os.path.join(raw, "warroom__*.json"))):
        parts = os.path.basename(f)[:-5].split("__")
        painel = parts[1] if len(parts) > 2 else "painel"
        recorte = parts[2] if len(parts) > 2 else (parts[1] if len(parts) > 1 else "geral")
        for i in unwrap(load(f, [])):
            if isinstance(i, dict):
                i = dict(i); i["_painel"] = painel; i["_recorte"] = recorte
                warroom.append(i)
    # publicações do painel (uids em lote): sentimento do Warroom 1/-1/0 → polaridade do Radar 1/2/3
    for f in sorted(glob.glob(os.path.join(raw, "painelposts__*.json"))):
        parts = os.path.basename(f)[:-5].split("__")
        painel = parts[1] if len(parts) > 1 else "painel"
        for p in unwrap(load(f, [])):
            if not isinstance(p, dict) or not p.get("author"):
                continue
            key = p.get("pid") or p.get("post_url") or (p.get("author", "") + p.get("date", "") + str(p.get("text", ""))[:40])
            d = parse_date(p.get("date", ""))
            q = dict(p); q["pid"] = key; q["_painel"] = painel
            q["polarity"] = {1: 1, -1: 2, 0: 3}.get(p.get("sentiment"), p.get("polarity"))
            q["_win"] = "pw" + (d.strftime("%G%V") if d else "x")
            q["channel"] = p.get("channel") or "Instagram"
            windows.add(q["_win"])
            if key not in posts:
                posts[key] = q
            else:
                for k2 in ("videoplays", "groups"):
                    if q.get(k2) and not posts[key].get(k2):
                        posts[key][k2] = q[k2]
    stats = load(os.path.join(raw, "statistics.json"))
    line = load(os.path.join(raw, "linechart.json"))
    cur = load(os.path.join(wd, "curadoria.json"), {}) or {}
    return cfg, trends, lookups, list(posts.values()), sorted(windows), warroom, stats, line, cur

# ----------------------------------------------------------------- marcas do painel
def group_label(g):
    """'[M] Sallve_7103508' → 'Sallve' ; '[C] Rosto_980206' → ('Rosto', categoria)"""
    g = re.sub(r"_\d+$", "", str(g)).strip()
    kind = "categoria" if re.match(r"^\[(C|CAT|PROD|Cat)\]", g) else "marca"
    name = re.sub(r"^(\[[^\]]+\]\s*)+", "", g).strip(" -")
    name = re.sub(r"\s*-+\s*(TENT|POSTS?|COMENT[AÁ]RIOS?|Comments)\s*$", "", name, flags=re.I).strip(" -")
    return name, kind

def brand_match(name, terms):
    n = norm(name)
    return any(norm(t) and (norm(t) in n or n in norm(t)) for t in terms)

# ----------------------------------------------------------------- núcleo
def build_profiles(cfg, trends, lookups, posts, windows, warroom, cur):
    subn = {name: [term_regex(t) for t in terms] for name, terms in (cfg.get("subnichos") or {}).items()}
    cities = [(c, term_regex(c)) for c in (cfg.get("cidades") or [])]
    brand_terms = [term_regex(t) for t in (cfg.get("marca_cliente_termos") or ([cfg["marca_cliente"]] if cfg.get("marca_cliente") else []))]
    comps_cfg = cfg.get("concorrentes") or []
    comps_cfg = comps_cfg if isinstance(comps_cfg, dict) else {c: [c] for c in comps_cfg}
    comp_terms = {c: [term_regex(t) for t in ts] for c, ts in comps_cfg.items()}
    end = parse_date((cfg.get("periodo") or {}).get("fim", ""))
    end = end.replace(hour=23, minute=59) if end else max(
        (parse_date(p.get("date", "")) for p in posts if parse_date(p.get("date", ""))), default=datetime.datetime.now())

    P = {}
    def get(channel, name, url=None):
        k = key_of(channel, name)
        if k not in P:
            P[k] = {"id": re.sub(r"[^a-z0-9]+", "-", k).strip("-"), "nome": name, "canal": channel,
                    "handle": handle_from_url(url, name) if url else name, "url": url or "",
                    "seguidores": None, "seguidores_fonte": None, "rankings": {}, "best_score": 0.0,
                    "posts": [], "origem": set(), "warroom": None, "painel_recortes": set(), "painel_grupos": collections.Counter()}
        if url and not P[k]["url"]:
            P[k]["url"] = url
        return P[k]

    def set_followers(pr, value, fonte):
        try:
            v = int(float(value or 0))
        except Exception:
            v = 0
        if v > 0 and v > (pr["seguidores"] or 0):  # -1/0 = desconhecido; diverge entre coletas → maior valor
            pr["seguidores"] = v; pr["seguidores_fonte"] = fonte

    def usable(i):
        ch = i.get("channel", "")
        return ch and not ch.lower().endswith("comments")  # comentaristas não são candidatos

    for slug, items in trends.items():
        for i in items:
            if not usable(i):
                continue
            pr = get(i.get("channel", ""), i.get("name", ""), i.get("url"))
            set_followers(pr, i.get("followers"), "Radar")
            pr["rankings"][slug] = round(float(i.get("score") or 0), 4)
            pr["best_score"] = max(pr["best_score"], float(i.get("score") or 0))
            pr["origem"].add("ranking")
    for i in lookups:
        if not usable(i):
            continue
        pr = get(i.get("channel", ""), i.get("name", ""), i.get("url"))
        set_followers(pr, i.get("followers"), "Radar")
        pr["origem"].add("lookup")
    for w in warroom:
        ch, nm = w.get("channel", ""), w.get("username") or w.get("name", "")
        pr = get(ch, nm, w.get("url"))
        set_followers(pr, w.get("followers"), "Painel")
        prev = pr["warroom"] or {}
        rk = float(w.get("ranking_3as") or w.get("ranking_harmonic_mean") or 0)
        pr["warroom"] = {"posts": max(prev.get("posts") or 0, w.get("posts_count") or 0), "ranking": max(prev.get("ranking") or 0, rk),
                         "verificado": w.get("is_verified"), "genero": w.get("gender") if w.get("gender") not in (None, "undefined") else prev.get("genero"),
                         "ocupacao": w.get("occupation") or prev.get("ocupacao") or "", "grupos": sorted(set(prev.get("grupos", [])) | set(w.get("groups", [])))}
        pr["painel_recortes"].add(f'{w.get("_painel","painel")}:{w.get("_recorte","geral")}')
        pr["origem"].add("painel")
    for p in posts:
        pr = get(p.get("channel", ""), p.get("author", ""))
        pr["posts"].append(p); pr["origem"].add("posts" if not p.get("_painel") else "painel")
        for g in p.get("groups") or []:
            pr["painel_grupos"][g] += 1

    # aplica curadoria antes do score (tipo, seguidores, local, exclusão)
    for k, pr in P.items():
        c = cur.get(k) or cur.get(pr["handle"]) or cur.get(norm(pr["handle"])) or {}
        pr["_cur"] = c
        if c.get("seguidores"):
            pr["seguidores"] = int(c["seguidores"]); pr["seguidores_fonte"] = c.get("seguidores_fonte", "Pesquisa online")
        wr = pr.get("warroom") or {}
        occ = norm(wr.get("ocupacao", ""))
        auto = "marca" if wr.get("genero") == "Marca" else "midia" if re.search(r"(imprensa|midia|jornal|portal|blog, site)", occ) else None
        _comps = cfg.get("concorrentes") or []
        _comps = [t for c, ts in _comps.items() for t in [c] + list(ts)] if isinstance(_comps, dict) else list(_comps)
        brand_terms_all = list(cfg.get("marca_cliente_termos") or ([cfg["marca_cliente"]] if cfg.get("marca_cliente") else [])) + _comps
        hn = re.sub(r"[^a-z0-9]", "", norm(pr["handle"]))
        own = any(len(re.sub(r"[^a-z0-9]", "", norm(t))) >= 4 and re.sub(r"[^a-z0-9]", "", norm(t)) in hn and len(hn) <= len(re.sub(r"[^a-z0-9]", "", norm(t))) + 12 for t in brand_terms_all)
        pr["tipo"] = c.get("tipo") or ("marca" if own else None) or auto or guess_tipo(pr["nome"], pr["url"])
        pr["tipo_fonte"] = "curadoria" if c.get("tipo") else "heurística"

    # métricas por perfil
    for pr in P.values():
        ps = pr["posts"]
        eng = [(p.get("likes") or 0) + (p.get("comments") or 0) + (p.get("shares") or 0) for p in ps]
        likes = [p.get("likes") or 0 for p in ps]
        hots = [float(p.get("hot") or 0) for p in ps if p.get("hot")]
        comms = [p.get("comments") or 0 for p in ps]
        dates = [d for d in (parse_date(p.get("date", "")) for p in ps) if d]
        pol = collections.Counter(p.get("polarity") for p in ps)
        texts = [clean_text(p.get("text")) for p in ps]
        ntext = [norm(t) for t in texts]
        sn = collections.Counter()
        for t in ntext:
            for name, regs in subn.items():
                if any(r.search(t) for r in regs):
                    sn[name] += 1
        for slug in pr["rankings"]:
            sn[slug] += 0  # garante presença
        hashtags = collections.Counter(norm(h) for t in texts for h in HASH_RE.findall(t))
        own = norm(pr["handle"])
        mentions = collections.Counter(norm(m).rstrip(".") for t in texts for m in MENTION_RE.findall(t) if norm(m).rstrip(".") != own)
        kw = collections.Counter(w for t in texts for w in tokens(t))
        city_hits = collections.Counter(c for t in ntext for c, r in cities if r.search(t))
        brand_hits = sum(1 for t in ntext if any(r.search(t) for r in brand_terms)) if brand_terms else 0
        comp_hits = {c: sum(1 for t in ntext if any(r.search(t) for r in rs)) for c, rs in comp_terms.items()}
        is_publi = [bool(PUBLI_RE.search(t) or re.search(r"\bcupo(m|ns)\b|\bcodigos?\b", norm(t))) for t in texts]
        def _hasb(t): return bool(brand_terms) and any(r.search(t) for r in brand_terms)
        def _ncomp(t): return sum(1 for rs in comp_terms.values() if any(r.search(t) for r in rs))
        # publi/cupom da marca SEM concorrente no mesmo post = parceria; com concorrentes = lista de cupons (afiliação multimarcas)
        publi_marca = sum(1 for t, pb in zip(ntext, is_publi) if pb and _hasb(t) and _ncomp(t) == 0)
        cupom_multimarca = sum(1 for t, pb in zip(ntext, is_publi) if pb and _hasb(t) and _ncomp(t) >= 1)
        publi_conc = {c: sum(1 for t, pb in zip(ntext, is_publi) if pb and any(r.search(t) for r in rs) and not _hasb(t)) for c, rs in comp_terms.items()}
        publi_posts = [{"url": p.get("post_url"), "data": (parse_date(p.get("date", "")) or end).strftime("%Y-%m-%d")}
                       for p, t, pb in zip(ps, ntext, is_publi) if pb and brand_terms and any(r.search(t) for r in brand_terms)][:3]
        publis = sum(1 for t in texts if PUBLI_RE.search(t))
        afiliado = sum(1 for t in texts if AFIL_RE.search(t))
        n = len(ps)
        views = [p.get("videoplays") for p in ps if p.get("videoplays")]
        er = (median(eng) / pr["seguidores"]) if (n and pr["seguidores"]) else None
        rwin = [w for w in windows if not w.startswith("pw")]
        pweeks = sorted({w for w in windows if w.startswith("pw")})
        c_radar = len({p["_win"] for p in ps if not p["_win"].startswith("pw")}) / len(rwin) if rwin else 0
        c_painel = len({p["_win"] for p in ps if p["_win"].startswith("pw")}) / len(pweeks) if pweeks else 0
        # marcas citadas: grupos do painel (por post e do ranking) + texto
        mcount, labels = collections.Counter(), {}
        def addm(nm, k):
            key = re.sub(r"[^a-z0-9]", "", norm(nm))
            labels.setdefault(key, nm); mcount[labels[key]] += k
        for g, k in pr["painel_grupos"].items():
            nm, kind = group_label(g)
            if kind == "marca": addm(nm, k)
        seen_rank = set()
        for g in (pr.get("warroom") or {}).get("grupos", []):
            nm, kind = group_label(g)
            key = re.sub(r"[^a-z0-9]", "", norm(nm))
            if kind == "marca" and key not in seen_rank and mcount.get(labels.get(key, nm), 0) == 0:
                seen_rank.add(key); addm(nm, 1)
        cats = sorted({group_label(g)[0] for g in list(pr["painel_grupos"]) + list((pr.get("warroom") or {}).get("grupos", [])) if group_label(g)[1] == "categoria"})
        top = sorted(ps, key=lambda p: (p.get("likes") or 0) + (p.get("comments") or 0), reverse=True)[:4]
        pr["m"] = {
            "posts": n,
            "constancia": round(max(c_radar, c_painel), 2) if n else 0,
            "views_med": median(views) if views else None,
            "likes_med": median(likes, 0), "comentarios_med": median(comms, 0), "eng_med": median(eng, 0),
            "er": round(er, 5) if er is not None else None,
            "conversa": round(median([c / l for c, l in zip(comms, likes) if l], 0) or 0, 4) if n else None,
            "pos": round(pol.get(1, 0) / n, 2) if n else None, "neg": round(pol.get(2, 0) / n, 2) if n else None,
            "ultimo_post": max(dates).strftime("%Y-%m-%d") if dates else None,
            "dias_desde_ultimo": max(0, (end - max(dates)).days) if dates else None,
            "hot_med": round(median(hots), 3) if hots else None,
            "publis": publis, "afiliado": afiliado, "cita_marca": brand_hits,
            "publi_marca": publi_marca, "cupom_multimarca": cupom_multimarca, "publi_concorrentes": {c: v for c, v in publi_conc.items() if v}, "publi_marca_posts": publi_posts, "cita_concorrentes": {c: v for c, v in comp_hits.items() if v},
        }
        pr["marcas_citadas"] = dict(mcount.most_common(12))
        pr["categorias_painel"] = cats
        pr["subnichos"] = [s for s, _ in sn.most_common() ][:6]
        pr["subnichos_contagem"] = dict(sn.most_common(8))
        pr["hashtags"] = [h for h, _ in hashtags.most_common(10)]
        pr["mencoes"] = [m for m, _ in mentions.most_common(10)]
        pr["kw"] = kw
        pr["cidades_citadas"] = dict(city_hits)
        pr["top_posts"] = [{"url": p.get("post_url"), "data": (parse_date(p.get("date", "")) or end).strftime("%Y-%m-%d"),
                            "texto": clean_text(p.get("text"))[:280], "likes": p.get("likes") or 0,
                            "comentarios": p.get("comments") or 0, "sentimento": {1: "positivo", 2: "negativo", 3: "neutro"}.get(p.get("polarity"), "")}
                           for p in top]
        pr["tier"] = tier_of(pr["seguidores"])
    return P

def score_profiles(P, cfg):
    creators = [p for p in P.values() if p["tipo"] in CREATOR_TYPES and not p["_cur"].get("excluir")]
    # benchmark interno de ER por canal+tier (mín. 5 perfis), depois por canal, depois geral
    groups = collections.defaultdict(list)
    for p in creators:
        if p["m"]["er"] is not None:
            groups[(p["canal"], p["tier"])].append(p["m"]["er"]); groups[(p["canal"], None)].append(p["m"]["er"]); groups[(None, None)].append(p["m"]["er"])
    def bench(p):
        for g in ((p["canal"], p["tier"]), (p["canal"], None), (None, None)):
            if len(groups.get(g, [])) >= 5:
                return statistics.median(groups[g]), g
        return None, None
    eng_by_channel = collections.defaultdict(list)
    for p in creators:
        if p["m"]["posts"]:
            eng_by_channel[p["canal"]].append(p["m"]["eng_med"])
    conv_pop = [p["m"]["conversa"] for p in creators if p["m"]["conversa"] is not None and p["m"]["posts"]]
    best_pop = [p["best_score"] for p in creators if p["best_score"] > 0]
    hot_by_channel = collections.defaultdict(list)
    for p in creators:
        if p["m"].get("hot_med") is not None:
            hot_by_channel[p["canal"]].append(p["m"]["hot_med"])
    n_sub = max(1, len(cfg.get("subnichos") or {}))

    for p in P.values():
        m = p["m"]; alerts = list(p["_cur"].get("alertas", []))
        wr = p.get("warroom") or {}
        npost = max(m["posts"], int(wr.get("posts") or 0))  # posts no painel contam como aderência
        m["posts_painel"] = int(wr.get("posts") or 0)
        # Aderência: volume na categoria + constância entre janelas + presença em rankings de subnicho
        ader = clamp(math.log1p(npost) / math.log1p(12)) * 0.55 + m["constancia"] * 0.30 + clamp(len(p["rankings"]) / min(3, n_sub)) * 0.15
        # Engajamento relativo ao benchmark do mesmo canal+tier
        b, g = bench(p)
        er_idx = (m["er"] / b) if (m["er"] is not None and b) else None
        if er_idx is not None:
            eng = clamp(er_idx / 2)
            if er_idx >= 3:
                alerts.append("Engajamento muito acima do grupo — checar autenticidade (pods, sorteios, post patrocinado impulsionado)")
            if er_idx <= 0.25 and (p["seguidores"] or 0) >= 10_000:
                alerts.append("Engajamento muito abaixo do grupo — checar qualidade da audiência")
        elif m["posts"]:
            eng = (pct_rank(m["eng_med"], eng_by_channel.get(p["canal"], [])) or 0) * 0.8  # sem seguidores: só volume
        else:
            eng = 0.0
        # Conversa: proporção comentário/curtida + sentimento
        conv = 0.0
        if m["posts"]:
            conv = 0.6 * (pct_rank(m["conversa"], conv_pop) or 0) + 0.4 * clamp((m["pos"] or 0) + 0.5 * (1 - (m["pos"] or 0) - (m["neg"] or 0)))
            if (m["neg"] or 0) >= 0.4 and m["posts"] >= 3:
                alerts.append("Parte relevante das publicações classificada como negativa — ler amostra antes de propor")
        # Relevância no Radar (score proprietário nos rankings)
        # Relevância: presença nos rankings de subnicho + força (hot) das publicações vs. o mesmo canal.
        # O hot entra para não punir micro/nano, que raramente aparecem nos rankings do Radar.
        hot_pct = pct_rank(m.get("hot_med"), hot_by_channel.get(p["canal"], [])) or 0
        rank_part = 0.5 * clamp(len(p["rankings"]) / min(3, n_sub)) + 0.5 * ((pct_rank(p["best_score"], best_pop) or 0) if p["best_score"] > 0 else 0)
        rel = max(rank_part, 0.45 * rank_part + 0.55 * hot_pct)
        if p.get("warroom") and p["warroom"].get("ranking"):
            rel = max(rel, clamp(float(p["warroom"]["ranking"]) * 3))
        # Recência
        d = m["dias_desde_ultimo"]
        rec = (0.8 if wr.get("posts") else 0) if d is None else (1 if d <= 14 else 0.8 if d <= 30 else 0.5 if d <= 60 else 0.2)
        if not m["posts"] and wr.get("ranking"):
            eng = max(eng, 0.4 * clamp(float(wr["ranking"]) * 4))  # sem posts lidos: proxy pelo ranking do painel
        for c, v in m["cita_concorrentes"].items():
            alerts.append(f"Citou o concorrente {c} em {v} publicação(ões) — checar exclusividade")
        if m["publis"] >= max(3, 0.6 * m["posts"]) and m["posts"]:
            alerts.append("Alta proporção de conteúdo publicitário na categoria — avaliar saturação")
        total = 100 * (0.30 * ader + 0.25 * eng + 0.15 * conv + 0.15 * rel + 0.15 * rec)
        # Confiança: poucas publicações na amostra = leitura frágil
        conf = 0.7 if npost == 0 else 0.78 if npost == 1 else 0.9 if npost == 2 else 1.0
        if not m["posts"] and npost:
            conf *= 0.9  # métricas vieram só do ranking do painel
        if p["seguidores"] is None:
            conf *= 0.92
        total *= conf
        p["score"] = {"total": round(total), "confianca": round(conf, 2), "aderencia": round(ader * 100), "engajamento": round(eng * 100),
                      "conversa": round(conv * 100), "relevancia": round(rel * 100), "recencia": round(rec * 100)}
        # fora do nicho: tem posts lidos, nenhum casa com os subnichos nem com categoria do painel
        if (cfg.get("subnichos") and m["posts"] >= 2 and not any(p["subnichos_contagem"].values())
                and not p["_cur"].get("subnichos")):
            total *= 0.7 if p.get("categorias_painel") else 0.5
            alerts.append("Nenhuma publicação lida trata da categoria — provável perfil de outro nicho que caiu na busca por uma palavra ambígua")
        p["score"]["total"] = round(total)
        m["er_idx"] = round(er_idx, 2) if er_idx is not None else None
        m["er_benchmark"] = round(b, 5) if b else None
        m["benchmark_grupo"] = (f"{g[0] or 'todos os canais'} · {g[1] or 'todos os tiers'}") if g else None
        p["alertas"] = list(dict.fromkeys(alerts))

def brand_relation(P, cfg):
    """Relação com a marca. Com posts lidos, vale o TEXTO (termos da marca/concorrentes):
    grupo de marca do painel pode ter ruído ('creamy' em receita, 'salve' como saudação).
    Sem posts lidos, o grupo do painel vira sinal 'a confirmar'."""
    marca = cfg.get("marca_cliente")
    mterms = cfg.get("marca_cliente_termos") or ([marca] if marca else [])
    comps = cfg.get("concorrentes") or []
    comps = comps if isinstance(comps, dict) else {c: [c] for c in comps}
    for p in P.values():
        m = p["m"]; mc = p.get("marcas_citadas", {})
        sinal_m = sum(v for k, v in mc.items() if marca and brand_match(k, [marca] + list(mterms)))
        sinal_c = {}
        for k, v in mc.items():
            for c, ts in comps.items():
                if brand_match(k, [c] + list(ts)):
                    sinal_c[c] = max(sinal_c.get(c, 0), v)
        lidos = m["posts"] > 0
        if lidos:
            cita_m, cita_c, conf = m["cita_marca"], {k: v for k, v in m["cita_concorrentes"].items() if v}, True
            m["ruido_grupo"] = bool((sinal_m and not cita_m) or any(v and not cita_c.get(c) for c, v in sinal_c.items()))
        else:
            cita_m, cita_c, conf = sinal_m, {k: v for k, v in sinal_c.items() if v}, False
            m["ruido_grupo"] = False
        m["cita_marca"], m["cita_concorrentes"] = cita_m, cita_c
        if not marca:
            rel = None
        elif lidos and m.get("publi_marca"):
            rel = "parceira"
        elif cita_m and cita_c:
            rel = "multimarcas"
        elif cita_m:
            rel = "defensor"
        elif cita_c:
            rel = "concorrente"
        else:
            rel = "categoria"
        p["relacao"], p["relacao_confirmada"] = rel, conf
        for c, v in (m.get("publi_concorrentes") or {}).items():
            p["alertas"].append(f"Fez publicidade para {c} no período ({v} post(s)) — checar exclusividade antes de propor")
        if conf and rel == "defensor":
            p["score"]["total"] = min(100, p["score"]["total"] + 6)
        elif conf and rel == "multimarcas":
            p["score"]["total"] = min(100, p["score"]["total"] + 3)
        if rel in ("concorrente", "multimarcas"):
            p["alertas"] = [a for a in p["alertas"] if not a.startswith("Citou o concorrente")]
        if m["ruido_grupo"]:
            p["alertas"].append("O painel associou este perfil a uma marca, mas o texto das publicações não cita a marca (provável ruído do grupo) — relação desconsiderada")

ESPEC = re.compile(r"(dermato|derm|medic|dr[a]?\b|nutri|farmac|biomed|esteticista|cientista)")

def motivos(P, cfg, rotulos):
    marca = cfg.get("marca_cliente")
    for p in P.values():
        m, sc = p["m"], p["score"]; out = []
        conf = p.get("relacao_confirmada", True)
        tag = "" if conf else " — sinal do painel, confirmar lendo os posts"
        if p.get("relacao") == "parceira":
            esp = m["cita_marca"] - m["publi_marca"]
            out.append((11, f"Já é parceira de {marca}: {m['publi_marca']} publi(s) no período" + (f" e cita a marca espontaneamente em outros {esp} post(s)" if esp > 0 else "") + " — candidata a renovar ou ampliar o contrato"))
        if m.get("cupom_multimarca"):
            out.append((8, f"Tem cupom de {marca} listado junto com concorrentes: perfil de cupons/afiliação multimarcas — bom para performance, não para exclusividade"))
        if p.get("relacao") in ("defensor", "multimarcas") and m["cita_marca"] and not m.get("cupom_multimarca"):
            out.append((10 if conf else 6, f"Já fala de {marca} espontaneamente ({m['cita_marca']} publicação(ões) no período){tag or ' — collab tende a soar natural'}"))
        pc = m.get("publi_concorrentes") or {}
        if p.get("relacao") in ("concorrente", "multimarcas") and pc:
            cs = ", ".join(f"{k} ({v} publi)" for k, v in sorted(pc.items(), key=lambda x: -x[1]))
            out.append((9, f"Hoje é parceira paga de {cs}: conquista só depois do fim do contrato — vale acompanhar, não abordar agora"))
        elif p.get("relacao") == "concorrente":
            cs = ", ".join(f"{k} ({v})" for k, v in sorted(m["cita_concorrentes"].items(), key=lambda x: -x[1]))
            out.append((9 if conf else 5, f"Fala de {cs} por conta própria e ainda não de {marca}: oportunidade de conquista{tag}"))
        if p.get("relacao") == "multimarcas":
            out.append((5, "Testa várias marcas da categoria: bom para comparativos e resenhas, menor risco de exclusividade"))
        if p["tipo"] == "especialista":
            out.append((8, "Especialista: dá credibilidade técnica ao produto (atenção às regras de publicidade do conselho profissional)"))
        sn = [rotulos.get(s, s) for s in p["subnichos"][:2]]
        if m["posts"] >= 3 and sn:
            out.append((7, f"Publica sobre {', '.join(sn)} com constância ({m['posts']} posts na amostra, presença em {round(100*m['constancia'])}% das janelas)"))
        if m.get("er_idx") and m["er_idx"] >= 1.3:
            out.append((7, f"Engajamento {str(round(m['er_idx'],1)).replace('.',',')}× a mediana de perfis do mesmo canal e porte"))
        if m.get("views_med") and m["views_med"] >= 1000:
            out.append((5, f"Vídeos com mediana de {int(m['views_med']):,} visualizações por post na categoria".replace(",", ".")))
        if m.get("conversa") and m["conversa"] >= 0.05 and m["posts"] >= 2:
            out.append((5, f"Audiência conversa: {str(round(100*m['conversa'],1)).replace('.',',')} comentários a cada 100 curtidas"))
        if m.get("afiliado"):
            out.append((4, "Trabalha com link/cupom de produto: encaixa em campanha de performance e afiliados"))
        if p["tier"] in ("nano", "micro"):
            out.append((3, "Porte micro: custo menor por post e comunidade mais próxima — bom para ativar vários em paralelo"))
        if (p["_cur"].get("local") or {}).get("cidade"):
            out.append((6, f"Base em {p['_cur']['local']['cidade']}: serve para ação local"))
        if m.get("dias_desde_ultimo") is not None and m["dias_desde_ultimo"] <= 7:
            out.append((2, "Postou sobre a categoria na última semana"))
        p["motivos"] = [t for _, t in sorted(out, key=lambda x: -x[0])][:5]

def lookalikes(P, k=6):
    pool = [p for p in P.values() if p["tipo"] in CREATOR_TYPES and not p["_cur"].get("excluir")]
    vec = {}
    for p in pool:
        v = collections.Counter()
        for s, c in p["subnichos_contagem"].items():
            v["sn:" + s] += 3 * (c or 1)
        for h in p["hashtags"]:
            v["h:" + h] += 2
        for w, c in p["kw"].most_common(40):
            v["w:" + w] += c
        vec[p["id"]] = v
    def cos(a, b):
        common = set(a) & set(b)
        num = sum(a[x] * b[x] for x in common)
        den = math.sqrt(sum(x * x for x in a.values())) * math.sqrt(sum(x * x for x in b.values()))
        return num / den if den else 0
    by_handle = {norm(p["handle"]): p for p in pool}
    for p in pool:
        res = []
        for q in pool:
            if q is p:
                continue
            c = cos(vec[p["id"]], vec[q["id"]])
            ti = TIER_ORDER.get(p["tier"]); tq = TIER_ORDER.get(q["tier"])
            tsim = 1 if ti == tq and ti is not None else 0.5 if (ti is not None and tq is not None and abs(ti - tq) == 1) else 0
            mutual = norm(q["handle"]) in p["mencoes"] or norm(p["handle"]) in q["mencoes"]
            loc_p, loc_q = (p["_cur"].get("local") or {}).get("cidade"), (q["_cur"].get("local") or {}).get("cidade")
            sim = 0.55 * c + 0.15 * tsim + 0.10 * (p["canal"] == q["canal"]) + 0.08 * (p["tipo"] == q["tipo"]) + 0.07 * bool(loc_p and loc_p == loc_q) + 0.05 * mutual
            if sim < 0.2:
                continue
            why = []
            shared = [s for s in p["subnichos"] if s in q["subnichos"]][:2]
            if shared: why.append("mesmo subnicho: " + ", ".join(shared))
            sh = [h for h in p["hashtags"] if h in q["hashtags"]][:2]
            if sh: why.append("usa as mesmas hashtags: " + ", ".join("#" + h for h in sh))
            if tsim == 1: why.append(f"mesmo porte ({q['tier']})")
            elif tsim == 0.5: why.append(f"porte vizinho ({q['tier']})")
            if p["tipo"] == q["tipo"] == "especialista": why.append("também é especialista")
            if loc_p and loc_p == loc_q: why.append(f"também é de {loc_q}")
            if mutual: why.append("se citam nas publicações")
            res.append({"id": q["id"], "sim": round(sim, 3), "motivos": why[:3]})
        p["parecidos"] = sorted(res, key=lambda r: -r["sim"])[:k]

def assemble(cfg, P, stats, line, cur):
    infl, outras = [], []
    for p in P.values():
        c = p["_cur"]
        if c.get("excluir"):
            continue
        base = {"id": p["id"], "nome": c.get("nome") or p["nome"], "handle": p["handle"], "canal": p["canal"], "url": p["url"],
                "seguidores": p["seguidores"], "seguidores_fonte": p["seguidores_fonte"], "tier": p["tier"], "tipo": p["tipo"],
                "tipo_fonte": p["tipo_fonte"]}
        if p["tipo"] not in CREATOR_TYPES:
            if p["seguidores"] or p["m"]["posts"]:
                outras.append({**base, "posts": p["m"]["posts"]})
            continue
        if not p["m"]["posts"] and not p["rankings"] and "painel" not in p["origem"]:
            continue  # só apareceu citando alguém em lookup: não é candidato da categoria
        # perfil de 1 post sem seguidores e sem curadoria = ruído de amostra
        if not c and p["seguidores"] is None and p["m"]["posts"] < 2 and not p["rankings"] and "painel" not in p["origem"]:
            continue
        local = c.get("local") or None
        if not local and p["cidades_citadas"]:
            cidade = max(p["cidades_citadas"], key=p["cidades_citadas"].get)
            hits = p["cidades_citadas"][cidade]
            if hits >= 2 and hits / max(1, p["m"]["posts"]) >= 0.3:
                local = {"cidade": cidade, "confianca": "provável", "fonte": f"cita {cidade} em {hits} de {p['m']['posts']} publicações"}
        infl.append({**base,
            "resumo": c.get("resumo", ""), "bio": c.get("bio", ""), "local": local,
            "subnichos": c.get("subnichos") or [s for s in p["subnichos"] if p["subnichos_contagem"].get(s)] or p.get("categorias_painel", []) or p["subnichos"], "hashtags": p["hashtags"], "mencoes": p["mencoes"],
            "metricas": p["m"], "score": p["score"], "alertas": p["alertas"], "top_posts": p["top_posts"],
            "rankings": p["rankings"], "painel": p["warroom"], "origem": sorted(p["origem"]),
            "relacao": p.get("relacao"), "relacao_confirmada": p.get("relacao_confirmada", True), "marcas_citadas": p.get("marcas_citadas", {}), "categorias_painel": p.get("categorias_painel", []),
            "motivos": p.get("motivos", []), "por_que": c.get("por_que", ""), "ideia_collab": c.get("ideia_collab", ""),
            "painel_recortes": sorted(p["painel_recortes"]),
            "parcerias": c.get("parcerias", []), "contatos": c.get("contatos", []), "redes": c.get("redes", []),
            "brand_safety": c.get("brand_safety", []), "fontes": c.get("fontes", []), "parecidos": p.get("parecidos", []),
            "destaque": bool(c.get("destaque")), "pesquisado": bool(c)})
    infl.sort(key=lambda x: (not x["pesquisado"], -x["score"]["total"]))
    cap = int(cfg.get("max_perfis") or 200)
    infl = sorted(infl[:cap], key=lambda x: -x["score"]["total"])  # curados sempre entram
    keep = {i["id"] for i in infl}
    for i in infl:
        i["parecidos"] = [s for s in i["parecidos"] if s["id"] in keep][:6]
    outras.sort(key=lambda x: -(x["seguidores"] or 0))
    pan = {}
    if isinstance(stats, dict):
        pan["total_mencoes"] = stats.get("total_mentions")
        pan["canais"] = sorted([{"canal": k, "pct": round(v.get("percentage", 0), 1), "n": v.get("mentions_collected", 0)}
                                for k, v in (stats.get("channels") or {}).items()], key=lambda x: -x["n"])
        try:
            pol = dict(stats["talking_about"]["polarities"][1]); tot = sum(pol.values()) or 1
            pan["sentimento"] = {"positivo": round(100 * pol.get("Positivo", 0) / tot), "neutro": round(100 * pol.get("Neutro", 0) / tot), "negativo": round(100 * pol.get("Negativo", 0) / tot)}
            gen = dict(stats["talking_about"]["gender"][1]); tg = sum(gen.values()) or 1
            pan["autores"] = {k: round(100 * v / tg) for k, v in gen.items()}
        except Exception:
            pass
    if isinstance(line, dict) and line.get("points"):
        pan["serie"] = [{"d": pt["date"][:10].replace("/", "-"), "n": pt["count"]} for pt in line["points"]]
    tiers = collections.Counter(i["tier"] or "a confirmar" for i in infl)
    pan["por_tier"] = {t: tiers.get(t, 0) for t in ["nano", "micro", "mid", "macro", "mega", "comunidade", "a confirmar"]}
    pan["subnichos"] = collections.Counter(s for i in infl for s in i["subnichos"][:2]).most_common(12)
    meta = {k: cfg.get(k) for k in ("categoria", "titulo", "periodo", "marca_cliente", "concorrentes", "cidades", "objetivo", "tema", "painel")}
    meta["subnichos"] = {k: v for k, v in (cfg.get("subnichos") or {}).items()}
    meta["rotulos"] = cfg.get("rotulos") or {}
    meta["queries"] = cfg.get("queries", [])
    meta["notas"] = cfg.get("notas", [])
    meta["gerado_em"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    meta["fonte"] = cfg.get("fonte") or "Radar Stilingue" + (" + painel" if any(i.get("painel") for i in infl) else "") + (" + pesquisa online" if any(i["pesquisado"] for i in infl) else "")
    return {"meta": meta, "panorama": pan, "influenciadores": infl, "outras_vozes": outras[:60]}

# ----------------------------------------------------------------- comandos
def fmt_n(n):
    if n is None: return "?"
    return f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}k" if n >= 1e3 else str(n)

def cmd_prepare(wd):
    cfg, trends, lookups, posts, windows, warroom, stats, line, cur = load_inputs(wd)
    P = build_profiles(cfg, trends, lookups, posts, windows, warroom, cur)
    score_profiles(P, cfg)
    brand_relation(P, cfg)
    cands = sorted([p for p in P.values() if (p["m"]["posts"] or p["rankings"] or p["warroom"])], key=lambda p: -p["score"]["total"])
    lines = [f"# Candidatos — {cfg.get('categoria','')}", "", f"{len(posts)} publicações · {len(windows)} janelas · {len(cands)} perfis", "",
             "| # | chave (use em curadoria.json) | tipo (heurística) | canal | seguidores | tier | posts | ER | score | relação c/ marca | marcas citadas | subnichos |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, p in enumerate(cands[:120], 1):
        er = f"{100*p['m']['er']:.1f}%" if p["m"]["er"] is not None else "—"
        lines.append(f"| {i} | `{key_of(p['canal'], p['handle'])}` | {p['tipo']} | {p['canal']} | {fmt_n(p['seguidores'])} | {p['tier'] or '?'} | {p['m']['posts']} | {er} | {p['score']['total']} | {p.get('relacao') or '—'} | {', '.join(list(p.get('marcas_citadas',{}))[:4])} | {', '.join(p['subnichos'][:3])} |")
    with open(os.path.join(wd, "candidatos.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    missing = [p for p in cands if not p["seguidores"] and p["tipo"] in CREATOR_TYPES and p["m"]["posts"] >= 2]
    batches = [missing[i:i + 4] for i in range(0, min(len(missing), 40), 4)]
    out = ["# Lotes para completar seguidores (radar trend_users, 1 chamada por lote)", ""]
    for n, b in enumerate(batches, 1):
        q = " OR ".join(f'"{p["handle"].strip()}"' if re.search(r"[._ ]", p["handle"].strip()) else p["handle"].strip() for p in b)
        out.append(f"- lookup__{n:02d}.json → `{q}`")
    with open(os.path.join(wd, "lookups.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"{len(cands)} candidatos · {sum(1 for p in cands if p['tipo'] in CREATOR_TYPES)} criadores/especialistas · {len(missing)} sem seguidores ({len(batches)} lotes)")
    print("Gerado: candidatos.md, lookups.md")

def cmd_build(wd, template):
    cfg, trends, lookups, posts, windows, warroom, stats, line, cur = load_inputs(wd)
    P = build_profiles(cfg, trends, lookups, posts, windows, warroom, cur)
    score_profiles(P, cfg)
    brand_relation(P, cfg)
    motivos(P, cfg, cfg.get("rotulos") or {})
    lookalikes(P)
    data = assemble(cfg, P, stats, line, cur)
    os.makedirs(os.path.join(wd, "out"), exist_ok=True)
    with open(os.path.join(wd, "out", "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(template, encoding="utf-8") as f:
        tpl = f.read()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(cfg.get("titulo") or f"Central de Influenciadores · {cfg.get('categoria','')}")
    page = tpl.replace("/*__CENTRAL_DATA__*/null", payload).replace("__TITLE__", title)
    with open(os.path.join(wd, "out", "central.html"), "w", encoding="utf-8") as f:
        f.write(page)
    infl = data["influenciadores"]
    print(f"{len(infl)} influenciadores na Central · {len(data['outras_vozes'])} outras vozes")
    print("Top 10:")
    for i in infl[:10]:
        print(f"  {i['score']['total']:>3}  {i['canal']:<9} {i['handle']:<28} {fmt_n(i['seguidores']):>6} {i['tier'] or '?':<6} posts={i['metricas']['posts']}")
    print("Gerado: out/data.json, out/central.html")

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("prepare", "build"):
        print(__doc__); sys.exit(1)
    wd = sys.argv[2]
    if sys.argv[1] == "prepare":
        cmd_prepare(wd)
    else:
        tpl = sys.argv[sys.argv.index("--template") + 1] if "--template" in sys.argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "central-template.html")
        cmd_build(wd, tpl)

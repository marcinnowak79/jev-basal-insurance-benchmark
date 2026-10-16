# Krok 3 (bez API): składa rekordy z ukrytych faktów (odtworzonych z ziarna), tekstów piszących i odczytu sędziów.
# Użycie: python zloz.py [prefiks]  → dane_v2/<rodzina>.jsonl, dane_v2/odrzucone.jsonl, raport na ekranie
import sys, json, random, glob, os
from collections import Counter
import nnw, dom
from wspolne import rekord

RODZINY = nnw.RODZINY | dom.RODZINY
ZGODNY = {r: nnw.zgodny for r in nnw.RODZINY} | dom.ZGODNY
PRE = sys.argv[1] if len(sys.argv) > 1 else "p"
os.makedirs("dane_v2", exist_ok=True)
ODRZUC = set(open("odrzuc_reczne.txt").read().split()) if os.path.exists("odrzuc_reczne.txt") else set()  # teksty wadliwe po przeglądzie (group#wariant)
out, odrz, braki = {}, [], 0
for zf in sorted(glob.glob(f"zadania/{PRE}_*.json")):
    nr = os.path.basename(zf)
    tf, sf = f"teksty/{nr}", f"sedzia/{nr}"
    if not (os.path.exists(tf) and os.path.exists(sf)): print("brak", nr); continue
    T, S = json.load(open(tf)), json.load(open(sf))
    for z in json.load(open(zf)):
        R = random.Random(z["seed"])
        gfun, rfun = RODZINY[z["rodzina"]]
        gr = gfun(R, z["group"])
        teksty = T.get(z["group"])
        if not teksty or len(teksty) != len(gr["warianty"]): braki += 1; continue
        for j, (w, t) in enumerate(zip(gr["warianty"], teksty)):
            odp = S.get(f"{z['group']}#{j}")
            meta_w = {k: v for k, v in w.items() if k not in ("fakty", "ukryte")}
            if odp is None: braki += 1; continue
            if f"{z['group']}#{j}" in ODRZUC: odrzuc_r = True; continue
            if not ZGODNY[z["rodzina"]](gr, w, odp):
                odrz.append(dict(group=z["group"], wariant=j, ukryte=meta_w, sedzia=odp, tekst=t)); continue
            for k, (reg, pytania, mreg) in enumerate(rfun(gr, w, R)):
                out.setdefault(z["rodzina"], []).append(rekord(f"{z['group']}-{j}-{k}", z["group"], z["rodzina"], reg, gr["styl"], t, pytania,
                                                               {"fakty": meta_w, "regula": mreg, "wiek": gr["wiek"], "split": "train"}, R))
for r, L in out.items():
    with open(f"dane_v2/{r}.jsonl", "w") as f:
        for x in L: f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(r, len(L), {k: dict(Counter(x["questions"][k]["gold"] for x in L)) for k in L[0]["questions"]})
with open("dane_v2/odrzucone.jsonl", "w") as f:
    for x in odrz: f.write(json.dumps(x, ensure_ascii=False) + "\n")
print("razem", sum(map(len, out.values())), "| odrzucone teksty", len(odrz), "| braki", braki)

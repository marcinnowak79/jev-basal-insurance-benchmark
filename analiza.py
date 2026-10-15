# Zestawia wynik_*.json: trafność w podziale na rodziny, kalibracja (ECE), kaskada przy progach 0,8 i 0,95,
# bliźniaki (para trafiona w całości) i najpewniejsze pomyłki. Użycie: python analiza.py [wynik_A.json wynik_B.json ...]
import json, sys, glob
from statistics import median

pliki = sys.argv[1:] or sorted(glob.glob("wyniki/wynik_*.json") + glob.glob("wynik_*.json"))
W = {json.load(open(p))["label"]: json.load(open(p))["wyniki"] for p in pliki}


def ece(x, kosze=10):
    s = 0
    for i in range(kosze):
        b = [r for r in x if i / kosze < r["conf"] <= (i + 1) / kosze or (i == 0 and r["conf"] == 0)]
        if b: s += len(b) / len(x) * abs(sum(r["conf"] for r in b) / len(b) - sum(r["pred"] == r["gold"] for r in b) / len(b))
    return s


def kaskada(x, p):
    w = [r for r in x if r["conf"] >= p]; return f"{len(w)}/{sum(r['pred'] != r['gold'] for r in w)}"


def blizniaki(x):
    g = {}
    for r in x: g.setdefault(r["group"], []).append(r["pred"] == r["gold"])
    pary = [v for v in g.values() if len(v) >= 2]
    return f"{sum(all(v) for v in pary)}/{len(pary)}"


rodziny = sorted({r["family"] for x in W.values() for r in x})
etyk = list(W)
print("Trafność (w nawiasie: kaskada 0,8 bierze/błędy | 0,95 bierze/błędy | bliźniaki trafione w całości)\n")
print(f"{'rodzina':48}" + "".join(f"{e:>34}" for e in etyk))
for f in rodziny + ["RAZEM"]:
    wiersz = f"{f:48}"
    for e in etyk:
        x = [r for r in W[e] if (f == "RAZEM" or r["family"] == f) and r["pred"] is not None]
        wiersz += f"{f'{sum(r[chr(112)+chr(114)+chr(101)+chr(100)] == r[chr(103)+chr(111)+chr(108)+chr(100)] for r in x)}/{len(x)} ({kaskada(x, .8)} | {kaskada(x, .95)} | {blizniaki(x)})':>34}"
    print(wiersz)
print()
for e in etyk:
    x = [r for r in W[e] if r["pred"] is not None]
    print(f"{e}: ECE {ece(x):.3f}, mediana {median(r['ms'] for r in x):.0f} ms, błędy wywołań {len(W[e]) - len(x)}")
print("\nNajpewniejsze pomyłki:")
for e in etyk:
    zle = sorted([r for r in W[e] if r["pred"] is not None and r["pred"] != r["gold"]], key=lambda r: -r["conf"])[:8]
    print(f"\n== {e}")
    for r in zle: print(f"  {r['family']:44} wzorzec {r['gold']:14} model {r['pred']:14} p={r['conf']:.2f}  {r['meta']}")

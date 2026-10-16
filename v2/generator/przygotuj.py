# Krok 1 (bez API): kod losuje grupy z ukrytymi faktami i zapisuje zadania dla piszących i dla sędziów.
# Użycie: python przygotuj.py <grup_na_rodzine> <grup_na_partie> [prefiks]  → zadania/<prefiks>_NN.json
import sys, json, random, os
import nnw, dom
from wspolne import STYLE

RODZINY = nnw.RODZINY | dom.RODZINY
N, NP = int(sys.argv[1]), int(sys.argv[2]); PRE = sys.argv[3] if len(sys.argv) > 3 else "p"
SEED = os.environ.get("SEED", "v2")
grupy = []
for rodz in RODZINY:
    for i in range(N):
        seed = f"{SEED}-{rodz}-{i}"
        gr = RODZINY[rodz][0](random.Random(seed), f"{PRE}-{rodz}-{i:04d}")
        grupy.append(dict(group=gr["group"], seed=seed, rodzina=rodz, styl=STYLE[gr["styl"]], osoba=gr["osoba"],
                          warianty=[dict(fakty=w["fakty"], ukryte=w["ukryte"]) for w in gr["warianty"]],
                          pola={k: {"pytanie": q, "wartosci": list(v) + ["nie_wynika"]} for k, (q, v) in gr["pola"].items()}))
random.Random(SEED).shuffle(grupy)
for p in range(0, len(grupy), NP):
    json.dump(grupy[p:p + NP], open(f"zadania/{PRE}_{p // NP:02d}.json", "w"), ensure_ascii=False, indent=1)
print(len(grupy), "grup,", sum(len(g["warianty"]) for g in grupy), "tekstów,", (len(grupy) + NP - 1) // NP, "partii")

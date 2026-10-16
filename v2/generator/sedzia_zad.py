# Krok 2b: z tekstów robi zadania dla sędziego (bez faktów). Użycie: python sedzia_zad.py <partia>
import sys, json
p = sys.argv[1]
Z = json.load(open(f"zadania/{p}.json")); T = json.load(open(f"teksty/{p}.json"))
out = [dict(id=f"{z['group']}#{j}", tekst=t, pola=z["pola"]) for z in Z for j, t in enumerate(T[z["group"]])]
json.dump(out, open(f"sedzia/zad_{p}.json", "w"), ensure_ascii=False, indent=1); print(len(out), "pozycji")

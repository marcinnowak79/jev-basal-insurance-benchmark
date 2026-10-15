# Puszcza zestaw.jsonl na serwerze z interfejsem /v1/systemone (Basal lub Jev) i zapisuje wynik_<etykieta>.json.
# FACTS=auto dodaje do zapytania "facts": "auto" (Basal liczy polskie daty i kwoty i dopisuje je do stanu).
# Użycie: python uruchom.py <etykieta> <url> [plik_z_kluczem] [wątki]
#   Basal: python uruchom.py Basal20-mini http://127.0.0.1:8000/v1/systemone
#   Jev:   python uruchom.py Jev https://api.typesafe.ai/v1/systemone <plik_z_kluczem> 4
import json, sys, time, urllib.request, os
from concurrent.futures import ThreadPoolExecutor

label, url = sys.argv[1], sys.argv[2]
key = open(os.path.expanduser(sys.argv[3])).read().strip() if len(sys.argv) > 3 and sys.argv[3] else ""
watki = int(sys.argv[4]) if len(sys.argv) > 4 else 1
Z = [json.loads(l) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zestaw.jsonl"))]


def call(z):
    q = {k: {kk: vv for kk, vv in v.items() if kk != "gold"} for k, v in z["questions"].items()}
    body = {"state": z["state"], "questions": q}
    if os.environ.get("FACTS"): body["facts"] = os.environ["FACTS"]   # Basal: "auto" dolicza daty i kwoty
    h = {"content-type": "application/json"}
    if key: body["model"] = "jev-latest"; h["Authorization"] = f"Bearer {key}"
    for proba in range(4):
        try:
            t = time.time()
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, json.dumps(body).encode(), h), timeout=120))
            ms = (time.time() - t) * 1000
            a = r["answers"]["a"]
            return dict(id=z["id"], family=z["family"], group=z["group"], gold=z["questions"]["a"]["gold"],
                        pred=a["choice"], conf=a["confidence"], probs=a["probabilities"], ms=ms, meta=z.get("meta"))
        except Exception as e:
            err = e; time.sleep(2 * (proba + 1))
    return dict(id=z["id"], family=z["family"], group=z["group"], gold=z["questions"]["a"]["gold"], pred=None, conf=0,
                probs={}, ms=None, error=str(err), meta=z.get("meta"))


call(Z[0]); call(Z[1])  # rozgrzewka
with ThreadPoolExecutor(watki) as ex: res = list(ex.map(call, Z))
json.dump(dict(label=label, url=url, wyniki=res), open(f"wynik_{label}.json", "w"), ensure_ascii=False, indent=1)
ok = [r for r in res if r["pred"] is not None]
print(f"{label}: {sum(r['pred'] == r['gold'] for r in ok)}/{len(res)} trafnych, błędy wywołań {len(res) - len(ok)}")

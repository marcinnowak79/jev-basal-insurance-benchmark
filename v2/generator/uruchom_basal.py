# Puszcza dane_v2/wszystko.jsonl na /v1/systemone (Basal lub Jev); wiele pytań na stan. → wynik_<etykieta>.jsonl (wznawialne)
# Użycie: python uruchom_basal.py <etykieta> <url> <plik_zestawu> [wątki] [plik_z_kluczem]
import json, sys, time, urllib.request, os
from concurrent.futures import ThreadPoolExecutor
label, url, plik = sys.argv[1], sys.argv[2], sys.argv[3]
watki = int(sys.argv[4]) if len(sys.argv) > 4 else 4
key = open(os.path.expanduser(sys.argv[5])).read().strip() if len(sys.argv) > 5 else ""
WY = f"wynik_{label}.jsonl"
gotowe = {json.loads(l)["id"] for l in open(WY)} if os.path.exists(WY) else set()
Z = [json.loads(l) for l in open(plik)]
Z = [z for z in Z if z["id"] not in gotowe]


def call(z):
    body = {"state": z["state"], "questions": {k: {kk: vv for kk, vv in q.items() if kk != "gold"} for k, q in z["questions"].items()}}
    h = {"content-type": "application/json"}
    if key: body["model"] = "jev-latest"; h["Authorization"] = f"Bearer {key}"
    err = None
    for proba in range(4):
        try:
            t = time.time()
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, json.dumps(body).encode(), h), timeout=180))
            ms = (time.time() - t) * 1000
            return dict(id=z["id"], family=z["family"], ms=ms,
                        odp={k: dict(gold=q["gold"], pred=r["answers"][k]["choice"], conf=r["answers"][k]["confidence"], probs=r["answers"][k]["probabilities"])
                             for k, q in z["questions"].items()})
        except Exception as e:
            err = str(e); time.sleep(2 * (proba + 1))
    return dict(id=z["id"], family=z["family"], ms=None, error=err, odp=None)


with open(WY, "a") as f, ThreadPoolExecutor(watki) as ex:
    for i, r in enumerate(ex.map(call, Z)):
        f.write(json.dumps(r, ensure_ascii=False) + "\n"); f.flush()
        if i % 250 == 0: print(i, time.strftime("%T"), flush=True)
L = [json.loads(l) for l in open(WY)]
ok = sum(o["pred"] == o["gold"] for r in L if r["odp"] for o in r["odp"].values()); n = sum(len(r["odp"]) for r in L if r["odp"])
print(f"{label}: {ok}/{n} trafnych, błędy wywołań {sum(1 for r in L if not r['odp'])}")

# Kontrola krzyżowa: model ogólny odpowiada na pytania z dane_v2/wszystko.jsonl (tylko ocena, nic nie trafia do danych).
# Użycie: GEMINI_API_KEY=... python kontrola_gemini.py [model] [wątki] → dane_v2/kontrola_<model>.jsonl (wznawialne)
import json, sys, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
model = sys.argv[1] if len(sys.argv) > 1 else "gemini-3.8-flash"; watki = int(sys.argv[2]) if len(sys.argv) > 2 else 16
KEY = os.environ["GEMINI_API_KEY"]
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
WY = f"dane_v2/kontrola_{model}.jsonl"
gotowe = {json.loads(l)["id"] for l in open(WY)} if os.path.exists(WY) else set()
Z = [json.loads(l) for l in open("dane_v2/wszystko.jsonl")]
Z = [z for z in Z if z["id"] not in gotowe]


def call(z):
    pyt = "\n\n".join(f"Pytanie {k}: {q['instructions']}\nMożliwe odpowiedzi:\n" + "\n".join(f"- {o}: {d}" for o, d in q["criteria"].items())
                      for k, q in z["questions"].items())
    prompt = f"{z['state']}\n\n{pyt}\n\nNa każde pytanie odpowiedz wyłącznie kluczem jednej odpowiedzi, opierając się tylko na podanym fragmencie warunków i dokumencie."
    schema = {"type": "OBJECT", "properties": {k: {"type": "STRING", "enum": list(q["criteria"])} for k, q in z["questions"].items()}, "required": list(z["questions"])}
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json", "responseSchema": schema}}
    for proba in range(6):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(), {"content-type": "application/json", "x-goog-api-key": KEY}), timeout=180))
            pred = json.loads("".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"] if not p.get("thought")))
            return dict(id=z["id"], family=z["family"], pred=pred, gold={k: q["gold"] for k, q in z["questions"].items()})
        except Exception as e:
            err = str(e); time.sleep(4 * (proba + 1))
    return dict(id=z["id"], family=z["family"], pred=None, error=err, gold={k: q["gold"] for k, q in z["questions"].items()})


with open(WY, "a") as f, ThreadPoolExecutor(watki) as ex:
    for i, r in enumerate(ex.map(call, Z)):
        f.write(json.dumps(r, ensure_ascii=False) + "\n"); f.flush()
        if i % 200 == 0: print(i, flush=True)
L = [json.loads(l) for l in open(WY)]
from collections import Counter
ok, n, bl = Counter(), Counter(), 0
for r in L:
    if not r["pred"]: bl += 1; continue
    for k, g in r["gold"].items():
        n[r["family"]] += 1; ok[r["family"]] += r["pred"].get(k) == g
for f in sorted(n): print(f, f"{ok[f]}/{n[f]}", f"{100 * ok[f] / n[f]:.1f}%")
print("razem", f"{sum(ok.values())}/{sum(n.values())}", "błędy wywołań", bl)

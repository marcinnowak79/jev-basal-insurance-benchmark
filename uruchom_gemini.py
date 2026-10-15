# Ten sam zestaw na modelu Gemini przez API (punkt odniesienia: model ogólny, nie decyzyjny).
# Model dostaje stan, pytanie i opisy opcji, a odpowiada jednym kluczem opcji (schemat JSON z enum).
# Modele ogólne nie zwracają rozkładu prawdopodobieństw, więc conf = 1 (kaskady i ECE dla nich nie liczymy).
# Użycie: GEMINI_API_KEY=... python uruchom_gemini.py <model> [wątki]   → wynik_<model>.json
import json, sys, time, os, urllib.request
from concurrent.futures import ThreadPoolExecutor

model = sys.argv[1]; watki = int(sys.argv[2]) if len(sys.argv) > 2 else 8
key = os.environ["GEMINI_API_KEY"]
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
Z = [json.loads(l) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zestaw.jsonl"))]


def prompt(z):
    q = z["questions"]["a"]
    opcje = "\n".join(f"- {k}: {v}" for k, v in q["criteria"].items())
    return (f"{z['state']}\n\nPytanie: {q['instructions']}\n\nMożliwe odpowiedzi:\n{opcje}\n\n"
            "Odpowiedz wyłącznie kluczem jednej odpowiedzi, opierając się tylko na podanym fragmencie OWU i faktach.")


def call(z):
    q = z["questions"]["a"]
    body = {"contents": [{"role": "user", "parts": [{"text": prompt(z)}]}],
            "generationConfig": {"responseMimeType": "application/json",
                                 "responseSchema": {"type": "OBJECT", "properties": {"odpowiedz": {"type": "STRING", "enum": list(q["criteria"])}},
                                                    "required": ["odpowiedz"]}}}
    err = None
    for proba in range(5):
        try:
            t = time.time()
            r = json.load(urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(),
                                                                        {"content-type": "application/json", "x-goog-api-key": key}), timeout=180))
            ms = (time.time() - t) * 1000
            pred = json.loads(r["candidates"][0]["content"]["parts"][-1]["text"])["odpowiedz"]
            return dict(id=z["id"], family=z["family"], group=z["group"], gold=q["gold"], pred=pred, conf=1.0, probs={},
                        ms=ms, meta=z.get("meta"), usage=r.get("usageMetadata"))
        except Exception as e:
            err = e; time.sleep(3 * (proba + 1))
    return dict(id=z["id"], family=z["family"], group=z["group"], gold=q["gold"], pred=None, conf=0, probs={}, ms=None,
                error=str(err), meta=z.get("meta"))


with ThreadPoolExecutor(watki) as ex: res = list(ex.map(call, Z))
json.dump(dict(label=model, url=URL, wyniki=res), open(f"wynik_{model}.json", "w"), ensure_ascii=False, indent=1)
ok = [r for r in res if r["pred"] is not None]
print(f"{model}: {sum(r['pred'] == r['gold'] for r in ok)}/{len(res)} trafnych, błędy wywołań {len(res) - len(ok)}")

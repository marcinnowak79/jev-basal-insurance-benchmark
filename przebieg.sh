#!/usr/bin/env bash
# Zestaw OWU na Basalu 2.0, jeden model po drugim na jednej karcie NVIDIA.
# MODELE: lista model:tryb:flagi (domyślnie mini w bf16 i max w porcie FP8). Wagi są kasowane po teście.
# WORKDIR: katalog z uruchom.py i zestaw.jsonl; BASAL_ENV: środowisko z basal[fp8] v2.0.0 i torch 2.11.0 cu128.
# Gdy karta jest zajęta przez inną usługę, zatrzymaj ją przed startem (u nas: vLLM z Gemmą).
set -u
cd "${WORKDIR:-$(dirname "$0")}"; . "${BASAL_ENV:?ustaw BASAL_ENV}/bin/activate"
HUB=${HF_HOME:-$HOME/.cache/huggingface}/hub
for SPEC in ${MODELE:-mini:fast: max-FP8:fp8:}; do
  IFS=: read M TRYB FLAGI <<< "$SPEC"; FLAGI=${FLAGI/=/ }
  touch .znacznik
  python -c "from huggingface_hub import snapshot_download as s;print(s('Remek/basal-2.0-$M'))" || continue
  basal-serve --model Remek/basal-2.0-$M --mode $TRYB $FLAGI --host 127.0.0.1 --port 8000 > serve_$M.log 2>&1 &
  PID=$!; t0=$(date +%s); OK=0
  while [ $(( $(date +%s)-t0 )) -lt 1500 ]; do
    curl -sf localhost:8000/health >/dev/null && { OK=1; break; }
    kill -0 $PID 2>/dev/null || break; sleep 5
  done
  echo "serwer $M ok=$OK po $(( $(date +%s)-t0 )) s"
  [ $OK = 1 ] && python uruchom.py Basal20-$M http://127.0.0.1:8000/v1/systemone "" 4
  kill $PID 2>/dev/null; wait $PID 2>/dev/null; sleep 5
  # cache HF może trzymać wagi we wspólnym hub/blobs — kasujemy bloby pobrane w tym przebiegu
  [ -d "$HUB/blobs" ] && find "$HUB/blobs" -newer .znacznik -type f -delete
  rm -rf "$HUB/models--Remek--basal-2.0-$M"
done
rm -f .znacznik

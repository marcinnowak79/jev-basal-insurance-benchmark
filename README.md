# Jev vs Basal na decyzjach ubezpieczeniowych

> **v2 (16.10.2026): dane treningowe z odczytu dokumentów** — 3042 rekordy (3636 pytań) w 8 rodzinach NNW i szkód domowych, tylko pytania, których nie da się policzyć kodem; wyniki Basal-2.0 max-FP8 (87,2%) i gemini-3.8-flash (98,8%). Szczegóły: [`v2/README.md`](v2/README.md).

## Wyniki (trafne decyzje na 325)

| Rodzina | n | gemini-3.8-flash | gemini-3.1-pro-preview | gemini-3.5-flash-lite | Jev | Basal-2.0 max-FP8 | Basal-2.0 max-FP8 + `facts: auto` | Basal-2.0 mini |
|---|---|---|---|---|---|---|---|---|
| Kradzież: policja w 12 h | 50 | 50 | 50 | 35 | 35 | 37 | 36 | 33 |
| Kradzież: zgłoszenie do ubezpieczyciela, bez dnia tygodnia | 30 | 30 | 30 | 22 | 23 | 27 | 30 | 15 |
| Kradzież: zgłoszenie do ubezpieczyciela, z dniem tygodnia | 30 | 30 | 30 | 23 | 26 | 30 | 30 | 15 |
| Początek ochrony | 50 | 50 | 50 | 50 | 50 | 35 | 41 | 28 |
| Szkoda całkowita 70% | 50 | 50 | 50 | 36 | 28 | 21 | 23 | 22 |
| Zgłoszenie w 7 dni | 55 | 55 | 55 | 55 | 43 | 53 | 55 | 40 |
| Wyłączenia § 4 | 60 | 60 | 60 | 57 | 57 | 57 | 57 | 40 |
| **Razem** | **325** | **325** | **325** | **278** | **262** | **260** | **272** | **193** |
| Mediana czasu | | 3,4 s | 5,7 s | 0,7 s | 227 ms | 136 ms | 132 ms | 27 ms |

**Na czym mierzyliśmy czasy (15.10.2026):**

| Model | Sprzęt i dostęp | Równoległe zapytania |
|---|---|---|
| Basal-2.0 mini, max-FP8 (także z `facts: auto`) | lokalnie, jedna karta NVIDIA RTX PRO 6000 Blackwell Server Edition (96 GB), silnik basal v2.0.0; mini w bf16 (`--mode fast`), max w porcie FP8 (`--mode fp8`), jedna kolejność opcji; klient na tym samym serwerze | 4 |
| Jev (`jev-latest`) | API TypeSafe (`api.typesafe.ai`) przez internet z Polski; sprzęt dostawcy nieznany | 4 |
| Gemini 3.5 flash-lite, 3.8 flash, 3.1 pro | API Google (Gemini API) przez internet z Polski; domyślne rozumowanie modeli | 8 |

`facts: auto` to opcja zapytania Basala: silnik dolicza do polskiego stanu fakty kalendarzowe i kwotowe (dzień tygodnia, dni wolne, odstępy między datami, porównania kwot), bez reguł i bez odpowiedzi.

Czasy API zawierają opóźnienie sieci, czasy Basala nie. Na karcie z Basalem działały w tle inne usługi (około 13 GB pamięci karty), Gemma była na czas pomiaru zatrzymana. Mediana liczona na wszystkich 325 zapytaniach.

> **EN summary.** A Polish insurance decision benchmark: 325 typed decisions built from the public terms and conditions of a Polish motor own-damage (autocasco) policy, with labels computed by code from the policy rules (deadlines, start of cover, 70% total-loss threshold, exclusions). Compares the decision models Jev (TypeSafe) and Basal 2.0 (mini, max) against Gemini 3.5 flash-lite, 3.8 flash and 3.1 pro. All data is synthetic. Requests use the `/v1/systemone` format with `gold`, `group` and `family`, so the file works directly with `basal-calibrate`.

Porównanie z 15.10.2026: modele decyzyjne kontra modele ogólne

325 decyzji na regułach z publicznych OWU autocasco polskiego ubezpieczyciela. Etykiety liczy kod z reguł OWU. Dane są w całości syntetyczne (osoby, pojazdy i daty wymyślone), więc zestaw można wysyłać do zewnętrznych API i przekazać dalej.

## Pliki

| Plik | Do czego |
|---|---|
| `zbuduj.py` | Generator zestawu (stałe ziarno, wynik powtarzalny) → `zestaw.jsonl` |
| `zestaw.jsonl` | Jedno zapytanie `/v1/systemone` na linię, pytanie z polem `gold`, plus `group` (bliźniaki) i `family`. Format `basal-calibrate`. |
| `uruchom.py <etykieta> <url> [plik_z_kluczem] [wątki]` | Basal lub Jev → `wynik_<etykieta>.json` |
| `uruchom_gemini.py <model> [wątki]` | Model Gemini przez API, odpowiedź jako klucz opcji (schemat JSON z enum). Klucz w zmiennej `GEMINI_API_KEY`. |
| `analiza.py [wynik_*.json]` | Trafność per rodzina, kaskada przy progach 0,8 i 0,95, bliźniaki, ECE, najpewniejsze pomyłki |
| `przebieg.sh` | Przebieg Basala na jednej karcie NVIDIA: pobiera wagi, startuje `basal-serve`, puszcza zestaw, kasuje wagi. Katalog roboczy w `WORKDIR`, środowisko z silnikiem basal v2.0.0 w `BASAL_ENV`. |
| `wyniki/wynik_*.json` | Surowe wyniki wszystkich modeli (skrypty zapisują `wynik_*.json` w bieżącym katalogu) |

Jev: `uruchom.py Jev https://api.typesafe.ai/v1/systemone <plik_z_kluczem> 4`.

## Rodziny

| Rodzina | n | Reguła | Etykieta |
|---|---|---|---|
| Zgłoszenie w 7 dni | 55 | § 12 ust. 1 pkt 3 | dni od szkody ≤ 7 (art. 111 KC; przypadki, gdy koniec terminu wypada w dzień wolny, pominięte ze względu na art. 115 KC); 5 bez daty → brak danych |
| Kradzież: policja w 12 h | 50 | § 12 ust. 2 pkt 1 | minuty ≤ 720; pary 11 h 40 / 12 h 25; 6 bez godziny → brak danych |
| Kradzież: zgłoszenie do ubezpieczyciela do następnego dnia roboczego | 60 | § 12 ust. 2 pkt 2 | data ≤ następny dzień roboczy (święta 2026 z Wigilią); połowa z dniem tygodnia w stanie, połowa bez |
| Początek ochrony | 50 | § 6 ust. 1 i 4 | szkoda ≥ max(zawarcie, zapłata) + 1 dzień; 6 bez daty zapłaty → brak danych |
| Szkoda całkowita 70% | 50 | § 14 ust. 1 | koszt > 70% min(wartość, suma ubezpieczenia); pary 68/72% i pułapka między 70% sumy a 70% wartości |
| Wyłączenia § 4 i terytorium | 60 | § 3 ust. 5, § 4 | 10 par bliźniaków (wyłączenie / ten sam opis z faktem, który je znosi) × 3 |

Każde pytanie to `choice` z opisami opcji po polsku, a stan zawiera cytowany fragment OWU i fakty sprawy.

## Wpływ `facts: auto` na Basala 2.0

| Rodzina | n | max-FP8 | max-FP8 + facts | mini | mini + facts |
|---|---|---|---|---|---|
| Kradzież: policja w 12 h | 50 | 37 | 36 | 33 | 29 |
| Kradzież: zgłoszenie do ubezpieczyciela, bez dnia tygodnia | 30 | 27 | **30** | 15 | 15 |
| Kradzież: zgłoszenie do ubezpieczyciela, z dniem tygodnia | 30 | 30 | 30 | 15 | 15 |
| Początek ochrony | 50 | 35 | **41** | 28 | 27 |
| Szkoda całkowita 70% | 50 | 21 | 23 | 22 | 22 |
| Zgłoszenie w 7 dni | 55 | 53 | **55** | 40 | 42 |
| Wyłączenia § 4 | 60 | 57 | 57 | 40 | 40 |
| **Razem** | **325** | **260** | **272** | **193** | **190** |
| Kaskada przy 0,95: bierze / błędy | | 113 / 3 | 149 / 3 | 1 / 1 | 24 / 2 |
| ECE | | 0,063 | 0,048 | 0,154 | 0,201 |

Fakty pomagają max na regułach z datami (początek ochrony, terminy w dniach i dniach roboczych) i poprawiają jego kalibrację. Nie pomagają na progu 70% (fakty porównują kwoty, ale nie liczą procentu wartości) ani na terminie 12 godzin. Mini z faktów nie korzysta. Przebieg mini z faktami szedł obok innej usługi na tej samej karcie, przebieg max z faktami na karcie bez Gemmy.

## Kaskada i kalibracja

Ile decyzji model bierze sam przy danym progu pewności i ile z nich jest błędnych:

| Model | Próg 0,8 | Próg 0,95 | ECE |
|---|---|---|---|
| Jev | 136 / 5 | 77 / 3 | 0,115 |
| Basal-2.0 max-FP8 | 210 / 18 | 113 / 3 | 0,063 |
| Basal-2.0 max-FP8 + `facts: auto` | 244 / 20 | 149 / 3 | 0,048 |
| Basal-2.0 mini | 144 / 44 | 1 / 1 | 0,154 |

## Wnioski

- Z `facts: auto` Basal max wyprzedza Jev: 272 wobec 262 na 325. Bez faktów są równi (260 i 262).

- Oba duże Gemini mają komplet, więc pytania i etykiety są poprawne, a stan wystarcza do odpowiedzi.
- Na regułach z datami i kwotami Jev i Basal max są równe (około 80%) i oba ustępują nawet flash-lite (86%).
- Basal max przegrywa z Jev na początku ochrony (35 wobec 50: reguła z trzema datami) i na szkodzie całkowitej (21/50, poniżej losowania; Jev 28/50). Wygrywa na terminach kradzieży i zgłoszenia.
- Jev myli terminy prawie zawsze na korzyść klienta („w terminie” po 8 dniach albo po 14 godzinach).
- Dzień tygodnia w stanie pomaga Basalowi max (27 → 30) i Jev (23 → 26). Mini nic.
- Wyłączenia: wszystkie modele poza mini 57/60, a trzy pomyłki to za każdym razem Ankara uznana za teren objęty ochroną (azjatycka część Turcji; u Jev p = 0,99). Ten przypadek wymaga wiedzy o świecie, nie samego OWU.
- Basal max ma lepszą kalibrację niż Jev, ale przy progu 0,8 przepuszcza 18 błędów; przy 0,95 obaj po 3.

## Licencja

Skrypty: MIT (`LICENSE`). Zestaw i wyniki: CC BY 4.0 (`LICENSE-DATA`). Zestaw cytuje krótkie fragmenty OWU Autocasco Standard (C6205) TUiR WARTA S.A. jako źródło reguł; prawa do tekstu OWU należą do ich właściciela.

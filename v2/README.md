# Decyzje ubezpieczeniowe z odczytu dokumentów — dane treningowe v2

## Wyniki (trafne odpowiedzi na 3636 pytań)

| Rodzina | n | Basal-2.0 max-FP8 | gemini-3.8-flash |
|---|---|---|---|
| dom_okno | 408 | 403 (99%) | 408 (100%) |
| dom_pusty | 408 | 386 (95%) | 408 (100%) |
| nnw_pojazd / kto | 200 | 190 (95%) | 200 (100%) |
| nnw_sport / wyczyn | 394 | 373 (95%) | 371 (94%) |
| nnw_bojka | 408 | 364 (89%) | 404 (99%) |
| nnw_przyczyna | 408 | 355 (87%) | 408 (100%) |
| nnw_sport / ryzyko | 394 | 341 (87%) | 394 (100%) |
| nnw_pojazd / przyczyna | 200 | 168 (84%) | 200 (100%) |
| dom_definicja | 408 | 338 (83%) | 402 (99%) |
| nnw_alkohol | 408 | 251 (62%) | 397 (97%) |
| **Razem** | **3636** | **3169 (87,2%)** | **3592 (98,8%)** |
| Mediana czasu | | 100 ms | |

Basal 2.0 max-FP8: lokalnie, jedna karta NVIDIA RTX PRO 6000 Blackwell Server Edition, silnik basal v2.0.0, `--mode fp8`, 4 równoległe zapytania, 16.10.2026. Kaskada Basala: przy progu pewności 0,95 bierze 44% pytań z 19 błędami (1,2%), przy 0,8 — 79% pytań ze 144 błędami.
Gemini: API Google, odpowiedź jako klucz opcji (schemat JSON z enum), bez rozkładu prawdopodobieństw.

Najwięcej błędów Basala: alkohol (ucieka w „brak danych”, gdy z opisu przebiegu wynika wpływ albo jego brak), lista sportów wysokiego ryzyka (ścianka ≠ skałki, trasa ≠ poza trasą), bójka (wyjątek, którego reguła nie przewiduje), definicje zdarzeń domowych („nie spełnia warunku” vs „inne zdarzenie”).

> **EN summary.** 3,042 Polish insurance decision requests (3,636 questions) in `/v1/systemone` format with `gold`, `group` and `family` (works with `basal-calibrate`). Each state is a rule fragment in the style of Polish general terms and conditions plus one case document (police note, ER card, school accident report, claim form, adjuster note). The questions cover only what code cannot compute: reading a document against a concept from the terms (external cause vs illness, role in a fight, influence of alcohol, high-risk sport, event definitions, supervision of an empty home). Dates, thresholds, blood-alcohol levels, ages and registry checks are left to code. Labels are computed by code from hidden facts; rules are synthetic with explicit parameters; every story comes with twins that differ in one fact. All data is synthetic. Results of Basal 2.0 max-FP8 and Gemini 3.8 flash are included per record.

## Zasada: model decyzyjny tylko tam, gdzie kod nie wystarczy

Wszystko, co da się policzyć — daty i terminy, progi kwotowe, promile, wiek, liczba dni nieobecności, prędkość wiatru z IMGW, uprawnienia z rejestru — liczy kod. Model dostaje wyłącznie pytania o **odczyt dokumentu względem pojęcia z warunków**. Gdy pytanie zakłada fakt policzony przez kod, mówi to wprost (np. „Wynik badania przekracza próg stanu po użyciu alkoholu (ustalone na podstawie wyniku badania). Czy stan Ubezpieczonego miał wpływ na zajście wypadku?”).

## Jak powstały dane

1. **Ukryte fakty losuje kod** (`generator/nnw.py`, `generator/dom.py`): co się stało, kto kierował, kto zaczął bójkę, czy ktoś wchodził do mieszkania. Z faktów i parametrów reguły kod liczy etykietę.
2. **Bliźniaki:** każda historia (`group`) ma 2–4 warianty różniące się jednym faktem; ten sam tekst trafia zwykle pod dwa warianty reguły (z wyjątkiem i bez, różne listy, różne definicje), więc etykieta zmienia się razem z regułą.
3. **Dokument pisze model językowy** według `generator/PISZACY.md`: zadany rodzaj dokumentu, fakty do oddania językiem tego dokumentu, fakty, których nie wolno ujawnić (dla odpowiedzi „brak danych”), zakaz dopisywania okoliczności zmieniających ocenę i zakaz słów-wniosków („wyłączenie”, „obrona konieczna”, „miało wpływ”).
4. **Sędzia** (`generator/SEDZIA.md`) czyta sam tekst, bez faktów, i odpowiada, co z niego wynika; rekord wchodzi, gdy odczyt zgadza się z ukrytymi faktami.
5. **Kontrola krzyżowa** na gemini-3.8-flash; rozbieżności przejrzane ręcznie — tam, gdzie etykieta była sporna, reguła albo opis opcji zostały doprecyzowane, a 4 teksty odrzucone.

Opcje każdej odpowiedzi mają opisy po polsku, wzajemnie się wykluczają, kolejność jest losowana. W każdej rodzinie 15–30% etykiet to „brak danych”.

## Rodziny

| Rodzina | Rekordy | Grupy | Pytanie | Etykiety |
|---|---|---|---|---|
| `nnw_przyczyna` | 408 | 68 | Przyczyna zewnętrzna czy stan zdrowia (padaczka, omdlenie, niedocukrzenie, zawał) wobec definicji NW z rozszerzeniami lub bez | objete_nw / objete_zrownane / nieobjete / brak_danych |
| `nnw_alkohol` | 408 | 68 | Czy stan Ubezpieczonego miał wpływ na zajście wypadku | mial_wplyw / nie_mial_wplywu / brak_danych |
| `nnw_bojka` | 408 | 68 | Rola w zajściu (zaczął, umówiona bójka, bronił się, bity, bronił innej osoby) wobec reguły z wyjątkami lub bez | wylaczona / wyjatek_znosi / brak_przeslanki / brak_danych |
| `nnw_sport` | 394 | 68 | Dwa pytania: czy aktywność mieści się w liście sportów wysokiego ryzyka; czy okoliczności mieszczą się w definicji wyczynu | z_listy / spoza_listy / brak_danych; wyczyn / nie_wyczyn / brak_danych |
| `nnw_pojazd` | 200 | 68 | Dwa pytania: kto kierował; czy przyczyna leżała po stronie kierującego | ubezpieczony / inna_osoba / brak_danych; po_stronie_kierujacego / zewnetrzna / brak_danych |
| `dom_definicja` | 408 | 68 | Czy szkoda powstała wskutek silnego wiatru / zalania / uderzenia pioruna / kradzieży z włamaniem w rozumieniu definicji | spelnia / nie_spelnia_warunku / inne_zdarzenie / brak_danych |
| `dom_pusty` | 408 | 68 | Czy doglądanie niezamieszkałego lokalu spełniało warunek z warunków | spelniony / niespelniony / brak_danych |
| `dom_okno` | 408 | 68 | Deszcz przez niezamknięty otwór a wyjątki (otwór po gradzie, woda z innego źródła) | wylaczona / wyjatek_znosi / brak_przeslanki / brak_danych |

Rodzaje dokumentów: notatka policji, karta SOR, protokół powypadkowy szkoły, zgłoszenie rodzica lub poszkodowanego, oświadczenie świadka, notatka likwidatora z rozmowy lub z oględzin.

## Pliki

| Plik | Do czego |
|---|---|
| `dane/<rodzina>.jsonl` | Rekordy jednej rodziny: `id`, `group` (bliźniaki), `family`, `state`, `questions` (z `gold`), `meta` (ukryte fakty i parametry reguły) |
| `dane/wszystko.jsonl` | Wszystkie rodziny razem (3042 rekordy) |
| `dane/wszystko_z_wynikami.jsonl` | To samo plus pole `wyniki`: odpowiedź Gemini oraz odpowiedź i pewność Basala dla każdego pytania |
| `wyniki/wynik_Basal20-max-FP8.jsonl` | Surowe odpowiedzi Basala (wybór, pewność, rozkład, czas) |
| `wyniki/kontrola_gemini-3.8-flash.jsonl` | Surowe odpowiedzi Gemini |
| `generator/` | Kod rodzin i składania, instrukcje dla piszącego i sędziego, skrypty uruchomieniowe |

Uruchomienie na serwerze `/v1/systemone`: `python generator/uruchom_basal.py <etykieta> http://127.0.0.1:8000/v1/systemone dane/wszystko.jsonl 4`.
Nowa partia: `python generator/przygotuj.py <grup_na_rodzinę> <grup_na_partię> <prefiks>` → teksty według `PISZACY.md` → `sedzia_zad.py` + `SEDZIA.md` → `python generator/zloz.py <prefiks>`. Etykiety po zmianie reguły przelicza `zloz.py` bez pisania tekstów od nowa (ziarno odtwarza ukryte fakty).

## Licencja

Skrypty: MIT (`LICENSE`). Dane i wyniki: CC BY 4.0 (`LICENSE-DATA`).

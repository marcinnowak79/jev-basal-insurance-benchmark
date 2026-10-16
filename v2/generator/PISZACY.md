# Instrukcja dla piszącego dokumenty (dane treningowe, NNW i szkody domowe)

Wejście: plik `zadania/<partia>.json` — lista grup. Każda grupa ma: `styl` (jaki to dokument), `osoba` (poszkodowany/właściciel),
`warianty` (lista; każdy ma `fakty` i `ukryte`).

Dla każdej grupy napisz po jednym dokumencie na każdy wariant, po polsku.

1. **Wariant 0** piszesz od zera jako dokument w zadanym stylu (notatka policji, karta SOR, zgłoszenie, protokół szkolny…).
   Wymyśl fikcyjne szczegóły tła: miejscowość, datę z lat 2024–2026, nazwiska świadków i funkcjonariuszy, numery — ale tylko neutralne.
2. **Każdy następny wariant** to ten sam dokument z wariantu 0, w którym zmieniasz WYŁĄCZNIE to, czym jego `fakty`/`ukryte` różnią się
   od wariantu 0. Ta sama data, miejsce, osoby, układ i reszta zdań. Usuń wszystko, co po zmianie stałoby w sprzeczności (np. inne miejsce,
   liczba sprawców, okoliczności z wersji 0 niepasujące do nowej wersji). Tekst ma być spójny sam w sobie.
3. **`fakty`** muszą jednoznacznie wynikać z tekstu, ale oddaj je językiem danego dokumentu — nie przepisuj zdań z listy. Policjant pisze
   „w/w”, „ustalono”, lekarz „w wywiadzie”, „neguje”, rodzic pisze potocznie. Świadek w 1. osobie mówi, co sam widział.
   Liczby (promile, mg/l, m/s, czas nieobecności, wiek) podawaj dokładnie tak jak w faktach (forma zapisu może być naturalna dla dokumentu).
4. **`ukryte`** — tego z tekstu NIE może się dać ustalić. Dokument może wprost powiedzieć, że tego nie ustalono, albo milczeć.
5. **Nie dodawaj** okoliczności, które mogłyby zmienić ocenę ubezpieczyciela, a których nie ma w faktach: alkoholu, chorób, sportu, bójki,
   pojazdów, uprawnień, wcześniejszych urazów, pogody, otwartych okien, nieobecności domowników itp.
6. **Nie oceniaj prawnie** i nie używaj słów: wyłączenie, odpowiedzialność ubezpieczyciela, nieszczęśliwy wypadek, obrona konieczna,
   „miało wpływ”, „nie miało wpływu”, „definicja”, „warunki ubezpieczenia”. Opisuj zdarzenia, nie wnioski.
7. Długość 70–180 słów. Bez nagłówków typu „Wariant 1”, bez komentarzy. Różnicuj styl i budowę między grupami.
8. Płeć: osoba ma dopisek (kobieta)/(mężczyzna) — odmieniaj zgodnie z nim (fakty piszą „poszkodowany” rodzajowo ogólnie).
   Jeśli zawód nie pasuje do płci (np. „księgowa” u mężczyzny), użyj formy pasującej do płci.

Wyjście: `teksty/<partia>.json` — obiekt `{ "<group>": ["tekst wariantu 0", "tekst wariantu 1", ...], ... }` — dokładnie tyle tekstów,
ile wariantów, w tej samej kolejności, dla każdej grupy z pliku. Zapisz poprawny JSON (sprawdź `python3 -c "import json;json.load(open(...))"`).

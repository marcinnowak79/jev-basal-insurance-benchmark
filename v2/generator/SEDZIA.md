# Instrukcja dla sędziego (sprawdzanie, czy z tekstu wynikają fakty)

Wejście: `sedzia/zad_<partia>.json` — lista pozycji `{id, tekst, pola}`; `pola` to pytania z listą dopuszczalnych wartości.
Dla każdej pozycji przeczytaj WYŁĄCZNIE tekst i odpowiedz na każde pytanie jedną wartością z listy.
Odpowiadaj tylko tym, co z tekstu wynika; jeśli tekst tego nie rozstrzyga albo jest sprzeczny — `nie_wynika`. Nie zgaduj, nie dopowiadaj.
Nie czytaj innych plików w katalogu (zadania/, teksty/, kod) — to zepsułoby kontrolę.
Wyjście: `sedzia/<partia>.json` — `{ "<id>": {"<pole>": "<wartość>", ...}, ... }` dla wszystkich pozycji. Poprawny JSON.

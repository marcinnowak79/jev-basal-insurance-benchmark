# Buduje zestaw decyzji na OWU Warta Autocasco Standard (C6205, od 17.05.2026). Etykiety liczy kod z reguł OWU.
# Wynik: zestaw.jsonl — jedno zapytanie /v1/systemone na linię, pytanie z polem "gold", plus "group" i "family"
# (format basal-calibrate). Dane w całości syntetyczne: osoby, pojazdy i daty są wymyślone.
# Użycie: python zbuduj.py  → zestaw.jsonl
import json, random
from datetime import date, datetime, timedelta

R = random.Random(20261015)

# Dni ustawowo wolne w Polsce, 2026 (Wigilia wolna od 2025).
SWIETA = {date(2026, m, d) for m, d in [(1, 1), (1, 6), (4, 5), (4, 6), (5, 1), (5, 3), (5, 24), (6, 4), (8, 15),
                                         (11, 1), (11, 11), (12, 24), (12, 25), (12, 26)]}
DNI = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"]
MIES = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października",
        "listopada", "grudnia"]


def roboczy(d): return d.weekday() < 5 and d not in SWIETA
def nastepny_roboczy(d):
    d += timedelta(days=1)
    while not roboczy(d): d += timedelta(days=1)
    return d
def fd(d, tydzien=False): return f"{d.day} {MIES[d.month - 1]} {d.year} r." + (f" ({DNI[d.weekday()]})" if tydzien else "")
def fdt(t): return f"{fd(t.date())}, godz. {t:%H:%M}"
def zl(x): return f"{x:,.0f}".replace(",", " ") + " zł"
def losowa_data(od=date(2026, 5, 20), do=date(2026, 12, 10)): return od + timedelta(days=R.randrange((do - od).days))

IMIONA = ["Anna Kowalska", "Piotr Nowak", "Katarzyna Wiśniewska", "Tomasz Wójcik", "Magdalena Kamińska", "Michał Lewandowski",
          "Agnieszka Zielińska", "Krzysztof Szymański", "Joanna Woźniak", "Paweł Dąbrowski", "Ewa Kozłowska", "Marcin Jankowski"]
AUTA = ["Toyota Corolla 1.8 Hybrid", "Skoda Octavia 2.0 TDI", "Volkswagen Golf 1.5 TSI", "Kia Sportage 1.6 T-GDI",
        "Hyundai Tucson 1.6", "Opel Astra 1.2", "Ford Focus 1.0 EcoBoost", "Renault Clio 1.0 TCe", "Mazda CX-5 2.0",
        "Dacia Duster 1.5 dCi", "BMW 320d", "Audi A4 35 TFSI"]
MIASTA = ["Warszawie", "Krakowie", "Poznaniu", "Wrocławiu", "Gdańsku", "Łodzi", "Lublinie", "Katowicach", "Szczecinie", "Rzeszowie"]
def osoba(): return R.choice(IMIONA)
def auto(): return R.choice(AUTA)
def miasto(): return R.choice(MIASTA)

OWU_P12_1 = ("§ 12 ust. 1 pkt 3 OWU: W razie zaistnienia szkody innej niż kradzież pojazdu Ubezpieczający lub Ubezpieczony "
             "zobowiązani są szkodę zgłosić niezwłocznie do WARTY kontaktując się z Centrum Obsługi Klienta (…) – nie później "
             "jednak niż w ciągu 7 dni od powstania szkody.")
OWU_P12_2 = ("§ 12 ust. 2 OWU: W razie kradzieży pojazdu Ubezpieczający lub Ubezpieczony zobowiązani są niezwłocznie: "
             "1) powiadomić o kradzieży pojazdu policję, nie później niż w ciągu 12 godzin od powzięcia informacji o kradzieży "
             "pojazdu, 2) zgłosić szkodę polegającą na kradzieży pojazdu do WARTY kontaktując się z COK – nie później niż "
             "w ciągu następnego dnia roboczego od powzięcia informacji o kradzieży pojazdu.")
OWU_P6 = ("§ 6 ust. 1 OWU: Jeżeli nie umówiono się inaczej, odpowiedzialność WARTY rozpoczyna się od dnia następnego po zawarciu "
          "umowy ubezpieczenia, nie wcześniej jednak niż od dnia następnego po zapłaceniu składki lub jej pierwszej raty. "
          "§ 6 ust. 4: (…) jako termin zapłacenia składki, w przypadku jej opłacania przelewem bankowym, przyjmuje się datę "
          "potwierdzenia przez bank przyjęcia do realizacji polecenia przelewu.")
OWU_P14 = ("§ 14 ust. 1 OWU: Szkoda jest kwalifikowana jako całkowita, gdy koszt naprawy wyliczony w oparciu o maksymalne "
           "akceptowane przez WARTĘ koszty części, materiałów i robocizny przekracza 70% wartości tego pojazdu bezpośrednio przed "
           "zaistnieniem szkody lub przekracza 70% sumy ubezpieczenia z dnia zawarcia umowy ubezpieczenia, jeśli jej wysokość "
           "jest niższa od wartości pojazdu bezpośrednio przed zaistnieniem szkody.")
OWU_P4 = """Fragmenty OWU Autocasco Standard WARTA (C6205):
§ 3 ust. 3: Z tytułu umowy ubezpieczenia przysługuje odszkodowanie w razie uszkodzenia, całkowitego zniszczenia lub kradzieży pojazdu (…) wskutek wszelkich zdarzeń powstałych niezależnie od woli Ubezpieczonego lub osoby upoważnionej do korzystania z pojazdu z wyłączeniem szkód wymienionych w § 4.
§ 3 ust. 5: Umową ubezpieczenia objęte są szkody powstałe na terytorium RP oraz pozostałych krajów europejskich (Rosja i Turcja w europejskich częściach ich terytoriów), a także Maroka, Tunezji i Izraela. Szkody powstałe na terytorium Gruzji nie są objęte ochroną ubezpieczeniową.
§ 4 ust. 1: WARTA nie odpowiada za szkody:
2) spowodowane przez (…) osoby upoważnione do korzystania z pojazdu, kierujące pojazdem w stanie nietrzeźwości lub po użyciu alkoholu, narkotyków (…), chyba że nie miało to wpływu na powstanie szkody,
3) powstałe podczas kierowania pojazdem przez (…) osoby upoważnione do korzystania z pojazdu, bez wymaganych prawem kraju zajścia zdarzenia uprawnień do kierowania ubezpieczonym pojazdem, chyba że nie miało to wpływu na powstanie szkody,
4) gdy (…) osoby upoważnione do korzystania z pojazdu, kierujące pojazdem zbiegły z miejsca zdarzenia, pomimo prawnego obowiązku pozostania na miejscu zdarzenia,
8) polegające na uszkodzeniu silnika wskutek zassania wody podczas jego pracy lub próby uruchomienia silnika w warunkach stwarzających takie zagrożenie,
10) polegające na awarii,
14) polegające na uszkodzeniu lub zniszczeniu ogumienia, chyba że powstały one wskutek działania osób trzecich lub powstały jednocześnie z uszkodzeniem lub zniszczeniem innych części pojazdu, objętych ochroną ubezpieczeniową ACS,
17) powstałe podczas jazd wyścigowych, konkursowych, rajdowych oraz treningów do tych jazd.
§ 4 ust. 2: WARTA nie odpowiada za szkody polegające na utracie ubezpieczonego pojazdu w wyniku kradzieży: (…) 2) w przypadku pozostawienia bez nadzoru w pojeździe lub w miejscu, do którego mają dostęp osoby nieupoważnione do korzystania z pojazdu, klucza, karty lub innego urządzenia służącego do jego otwarcia lub uruchomienia.
§ 2: Awaria – przypadek losowy wynikający z przyczyn wewnętrznych ubezpieczonego pojazdu powodujących, że pojazd, jego część lub element wyposażenia, nie mogą być aktualnie użytkowane zgodnie z jego przeznaczeniem."""

TERMIN = {"w_terminie": "obowiązek dopełniony w terminie wskazanym w OWU",
          "po_terminie": "obowiązek dopełniony po upływie terminu wskazanego w OWU",
          "brak_danych": "z podanych faktów nie da się ustalić, czy termin został dotrzymany"}

zestaw = []
def dodaj(family, group, owu, fakty, instr, criteria, gold, meta):
    assert gold in criteria
    zestaw.append({"id": f"{family}-{len(zestaw):04d}", "group": group, "family": family,
                   "state": f"{owu}\n\nFakty sprawy:\n{fakty}",
                   "questions": {"a": {"type": "choice", "instructions": instr, "criteria": criteria, "gold": gold}},
                   "meta": meta})


# 1. Termin zgłoszenia szkody innej niż kradzież (7 dni od powstania szkody).
# Liczenie wg art. 111 § 2 KC (dnia zdarzenia nie wlicza się). Gdy ostatni dzień terminu wypada w dzień wolny,
# art. 115 KC przesuwa go — takie przypadki pomijamy, żeby etykieta była jednoznaczna.
SZKODY = ["kolizja z innym pojazdem na skrzyżowaniu", "uszkodzenie zderzaka podczas parkowania", "uszkodzenie lakieru przez nieznanego sprawcę",
          "stłuczenie przedniej szyby przez kamień", "uszkodzenie karoserii przez gałąź podczas burzy", "zderzenie z sarną na drodze krajowej"]
n = 0
while n < 25:
    d = losowa_data(); koniec = d + timedelta(days=7)
    if not roboczy(koniec): continue
    g = f"T7-{n}"; kto, a, m, s = osoba(), auto(), miasto(), R.choice(SZKODY)
    for opoz in (7, 8) if n % 2 == 0 else (R.choice([1, 2, 3, 5]), R.choice([10, 12, 15, 21])):
        z = d + timedelta(days=opoz)
        fakty = (f"Ubezpieczony: {kto}, pojazd {a}.\nZdarzenie: {s} w {m}, {fd(d)}.\n"
                 f"Zgłoszenie szkody do Centrum Obsługi Klienta WARTY: {fd(z)}.")
        dodaj("termin_zgloszenia_7dni", g, OWU_P12_1, fakty, "Czy szkoda została zgłoszona do WARTY w terminie wymaganym przez OWU?",
              TERMIN, "w_terminie" if opoz <= 7 else "po_terminie", {"dni": opoz})
    if n % 5 == 0:
        fakty = (f"Ubezpieczony: {kto}, pojazd {a}.\nZdarzenie: {s} w {m}, w ubiegłym tygodniu (dokładna data nieznana).\n"
                 f"Zgłoszenie szkody do Centrum Obsługi Klienta WARTY: {fd(d + timedelta(days=9))}.")
        dodaj("termin_zgloszenia_7dni", g, OWU_P12_1, fakty, "Czy szkoda została zgłoszona do WARTY w terminie wymaganym przez OWU?",
              TERMIN, "brak_danych", {"dni": None})
    n += 1

# 2. Kradzież: policja w ciągu 12 godzin od powzięcia informacji.
for n in range(22):
    d = losowa_data(); g = f"P12-{n}"; kto, a, m = osoba(), auto(), miasto()
    t0 = datetime(d.year, d.month, d.day, R.choice([6, 7, 8, 14, 18, 21, 22, 23]), R.choice([0, 10, 25, 40, 55]))
    pary = [(11 * 60 + 40, 12 * 60 + 25)] if n % 2 == 0 else [(R.choice([30, 90, 200, 400]), R.choice([14 * 60, 20 * 60, 30 * 60]))]
    for przed, po in pary:
        for minuty in (przed, po):
            t1 = t0 + timedelta(minutes=minuty)
            fakty = (f"Ubezpieczony: {kto}, pojazd {a}.\nUbezpieczony zauważył brak pojazdu na parkingu w {m}: {fdt(t0)}.\n"
                     f"Zawiadomienie o kradzieży złożone na policji: {fdt(t1)}.")
            dodaj("kradziez_policja_12h", g, OWU_P12_2, fakty,
                  "Czy ubezpieczony powiadomił policję o kradzieży pojazdu w terminie wymaganym przez OWU?",
                  TERMIN, "w_terminie" if minuty <= 12 * 60 else "po_terminie", {"minuty": minuty})
    if n % 4 == 0:
        fakty = (f"Ubezpieczony: {kto}, pojazd {a}.\nUbezpieczony zauważył brak pojazdu na parkingu w {m}: {fdt(t0)}.\n"
                 f"Zawiadomienie o kradzieży złożone na policji: później tego samego dnia lub następnego dnia (godzina nieznana).")
        dodaj("kradziez_policja_12h", g, OWU_P12_2, fakty,
              "Czy ubezpieczony powiadomił policję o kradzieży pojazdu w terminie wymaganym przez OWU?", TERMIN, "brak_danych", {"minuty": None})

# 3. Kradzież: zgłoszenie do WARTY najpóźniej następnego dnia roboczego. Dwa warianty: z dniem tygodnia i bez.
n = 0
while n < 30:
    d = losowa_data()
    nr = nastepny_roboczy(d)
    # celowo dużo piątków, sobót i dni przed świętami — tam reguła jest trudna
    if n % 3 == 0 and not (d.weekday() >= 4 or (d + timedelta(days=1)) in SWIETA): continue
    g = f"W1-{n}"; kto, a, m = osoba(), auto(), miasto()
    pozniej = nr + timedelta(days=1)
    while not roboczy(pozniej): pozniej += timedelta(days=1)
    for z in (nr, pozniej):
        tyg = n % 2 == 0
        fakty = (f"Ubezpieczony: {kto}, pojazd {a}.\nUbezpieczony dowiedział się o kradzieży pojazdu z parkingu w {m}: {fd(d, tyg)}.\n"
                 f"Policję powiadomiono tego samego dnia, w ciągu 2 godzin.\nZgłoszenie kradzieży do Centrum Obsługi Klienta WARTY: {fd(z, tyg)}.")
        dodaj("kradziez_warta_dzien_roboczy" + ("_z_dniem_tygodnia" if tyg else "_bez_dnia_tygodnia"), g, OWU_P12_2, fakty,
              "Czy ubezpieczony zgłosił kradzież pojazdu do WARTY w terminie wymaganym przez OWU?",
              TERMIN, "w_terminie" if z <= nr else "po_terminie", {"dzien": str(d), "termin": str(nr), "zgloszenie": str(z)})
    n += 1

# 4. Początek ochrony: dzień po zawarciu umowy, nie wcześniej niż dzień po zapłacie składki.
OCHRONA = {"objeta": "szkoda powstała w okresie odpowiedzialności WARTY",
           "przed_ochrona": "szkoda powstała przed rozpoczęciem odpowiedzialności WARTY",
           "brak_danych": "z podanych faktów nie da się ustalić, czy odpowiedzialność WARTY już się rozpoczęła"}
for n in range(22):
    zaw = losowa_data(); g = f"O-{n}"; kto, a, m = osoba(), auto(), miasto()
    zap = zaw + timedelta(days=R.choice([0, 0, 1, 2, 3, 5]))
    start = max(zaw, zap) + timedelta(days=1)
    for szk in (start - timedelta(days=1), start):
        fakty = (f"Ubezpieczający: {kto}, pojazd {a}. W polisie nie ustalono innego początku odpowiedzialności.\n"
                 f"Data zawarcia umowy ubezpieczenia AC: {fd(zaw)}.\nPierwsza rata składki zapłacona przelewem; bank przyjął "
                 f"polecenie przelewu do realizacji: {fd(zap)}.\nData szkody (kolizja w {m}): {fd(szk)}.")
        dodaj("poczatek_ochrony", g, OWU_P6, fakty, "Czy szkoda powstała w okresie odpowiedzialności WARTY?",
              OCHRONA, "objeta" if szk >= start else "przed_ochrona", {"zawarcie": str(zaw), "zaplata": str(zap), "szkoda": str(szk)})
    if n % 4 == 0:
        fakty = (f"Ubezpieczający: {kto}, pojazd {a}. W polisie nie ustalono innego początku odpowiedzialności.\n"
                 f"Data zawarcia umowy ubezpieczenia AC: {fd(zaw)}.\nPierwsza rata składki: płatna przelewem, data zapłaty nieznana.\n"
                 f"Data szkody (kolizja w {m}): {fd(zaw + timedelta(days=2))}.")
        dodaj("poczatek_ochrony", g, OWU_P6, fakty, "Czy szkoda powstała w okresie odpowiedzialności WARTY?", OCHRONA, "brak_danych", {})

# 5. Szkoda całkowita: koszt naprawy > 70% podstawy (wartość pojazdu albo niższa suma ubezpieczenia).
CALK = {"calkowita": "szkoda całkowita w rozumieniu OWU", "czesciowa": "szkoda częściowa (nie jest szkodą całkowitą)"}
for n in range(25):
    g = f"C-{n}"; a = auto()
    W = R.randrange(24, 160) * 1000
    S = W if n % 3 else int(W * R.choice([0.8, 0.85, 0.9]) / 100) * 100
    baza = min(W, S)
    if n % 3 == 0:  # pułapka: między 70% sumy ubezpieczenia a 70% wartości pojazdu
        koszty = [int((0.7 * S + (0.7 * W - 0.7 * S) / 2) / 100) * 100, int(0.66 * S / 100) * 100]
    else:
        koszty = [int(baza * 0.68 / 100) * 100, int(baza * 0.72 / 100) * 100]
    for K in koszty:
        su = f"Suma ubezpieczenia z dnia zawarcia umowy: {zl(S)}."
        fakty = (f"Pojazd {a}. Wartość pojazdu bezpośrednio przed szkodą: {zl(W)}. {su}\n"
                 f"Koszt naprawy wyliczony w oparciu o maksymalne akceptowane przez WARTĘ koszty: {zl(K)}.")
        dodaj("szkoda_calkowita_70", g, OWU_P14, fakty, "Czy szkoda jest szkodą całkowitą w rozumieniu OWU?",
              CALK, "calkowita" if K > 0.7 * baza else "czesciowa", {"W": W, "S": S, "K": K, "proc": round(K / baza * 100, 1)})

# 6. Wyłączenia z § 4 i terytorium (§ 3 ust. 5). Każda para to bliźniaki: ten sam opis, jeden fakt zmienia odpowiedź.
WYL = {"objeta": "szkoda objęta ochroną, żadne wyłączenie nie ma zastosowania",
       "alkohol": "wyłączenie: kierowanie po alkoholu lub środkach odurzających, które miało wpływ na szkodę",
       "uprawnienia": "wyłączenie: kierowanie bez wymaganych uprawnień, które miało wpływ na szkodę",
       "ucieczka": "wyłączenie: kierujący zbiegł z miejsca zdarzenia",
       "woda": "wyłączenie: uszkodzenie silnika wskutek zassania wody podczas pracy lub próby uruchomienia",
       "awaria": "wyłączenie: awaria pojazdu",
       "ogumienie": "wyłączenie: samo uszkodzenie ogumienia",
       "wyscigi": "wyłączenie: jazda wyścigowa, konkursowa, rajdowa lub trening",
       "kluczyki": "wyłączenie: kradzież przy kluczyku pozostawionym bez nadzoru w pojeździe",
       "terytorium": "szkoda poza terytorium objętym ochroną"}
PARY = [
    ("alkohol", "Kierujący {kto} wjechał na łuku drogi do rowu. Badanie wykazało 1,1 promila alkoholu we krwi; policja ustaliła, że przyczyną było niedostosowanie prędkości przez nietrzeźwego kierowcę.",
     "objeta", "Pojazd prowadzony przez {kto} stał na czerwonym świetle i został uderzony w tył przez inny samochód, którego kierowca przyznał się do winy. Badanie wykazało u {kto} 0,3 promila alkoholu; policja ustaliła, że stan kierującego nie miał wpływu na zdarzenie."),
    ("uprawnienia", "Pojazd prowadziła 16-letnia córka ubezpieczonego, która nie ma prawa jazdy. Na pustym parkingu straciła panowanie nad autem i uderzyła w latarnię.",
     "objeta", "Pojazd prowadził {kto}, któremu tydzień wcześniej upłynęła ważność prawa jazdy (nie wymienił dokumentu). Auto stało zaparkowane prawidłowo, gdy uderzyła w nie śmieciarka cofająca bez asekuracji; policja wskazała winę kierowcy śmieciarki i brak wpływu kierującego na zdarzenie."),
    ("ucieczka", "Kierujący {kto} uderzył w ogrodzenie posesji, po czym odjechał z miejsca zdarzenia, nie czekając na policję mimo prawnego obowiązku pozostania. Ustalono go następnego dnia na podstawie monitoringu.",
     "objeta", "Kierujący {kto} uderzył w ogrodzenie posesji, pozostał na miejscu, wezwał policję i spisał oświadczenie z właścicielem posesji."),
    ("woda", "Podczas ulewy {kto} wjechał w zalany przejazd pod wiaduktem. Silnik zgasł w trakcie jazdy, a próba ponownego uruchomienia w wodzie zakończyła się uszkodzeniem silnika (zassanie wody).",
     "objeta", "Podczas nocnej ulewy zalany został parking podziemny, na którym stał zaparkowany pojazd. Woda sięgnęła wysokości maski; silnika nikt nie uruchamiał. Rzeczoznawca stwierdził zalanie wnętrza i elektroniki."),
    ("awaria", "W trakcie jazdy po autostradzie w pojeździe pękł pasek rozrządu z powodu zużycia, co doprowadziło do uszkodzenia silnika. Żadne zdarzenie zewnętrzne nie miało miejsca.",
     "objeta", "W trakcie jazdy po autostradzie spod kół ciężarówki wyleciał metalowy element, który przebił miskę olejową; po utracie oleju doszło do uszkodzenia silnika."),
    ("ogumienie", "Podczas jazdy w lewej przedniej oponie powstało pęknięcie boku opony po najechaniu na krawężnik. Felga ani inne części pojazdu nie zostały uszkodzone.",
     "objeta", "Podczas jazdy pojazd wpadł w głęboką wyrwę w jezdni; pękła lewa przednia opona, a jednocześnie wygięła się felga i uszkodzony został wahacz."),
    ("wyscigi", "{kto} wziął udział pojazdem w amatorskim treningu przed rajdem na zamkniętym torze; na zakręcie pojazd wypadł z toru i uderzył w bandę.",
     "objeta", "{kto} jechał pojazdem na tor wyścigowy jako widz zawodów; na drodze dojazdowej, w normalnym ruchu, uderzył w tył innego auta podczas hamowania przed światłami."),
    ("kluczyki", "{kto} zostawił samochód z kluczykiem w stacyjce i uruchomionym silnikiem pod sklepem, wchodząc na kilka minut do środka. W tym czasie nieznany sprawca odjechał pojazdem; pojazdu nie odnaleziono.",
     "objeta", "Pojazd zamknięty i zabezpieczony alarmem skradziono nocą z parkingu przed blokiem; oba kluczyki znajdowały się w zamkniętym mieszkaniu ubezpieczonego i zostały przekazane do WARTY. Pojazdu nie odnaleziono."),
    ("terytorium", "Do kolizji doszło podczas wakacji w Gruzji, w Tbilisi, gdzie inny pojazd wymusił pierwszeństwo.",
     "objeta", "Do kolizji doszło podczas wakacji w Turcji, w europejskiej części Stambułu, gdzie inny pojazd wymusił pierwszeństwo."),
    ("terytorium", "Do kolizji doszło podczas podróży służbowej w Turcji, w Ankarze, gdzie inny pojazd wymusił pierwszeństwo.",
     "objeta", "Do kolizji doszło podczas wakacji w Maroku, w Marrakeszu, gdzie inny pojazd wymusił pierwszeństwo."),
]
for n in range(3):
    for i, (g1, t1, g2, t2) in enumerate(PARY):
        kto, a = osoba(), auto(); grp = f"X-{i}-{n}"
        for gold, t in ((g1, t1), (g2, t2)):
            fakty = f"Ubezpieczony: {kto}, pojazd {a}.\n" + t.format(kto=kto)
            dodaj("wylaczenia_par4", grp, OWU_P4, fakty, "Czy WARTA odpowiada za tę szkodę, a jeśli nie, które wyłączenie z OWU ma zastosowanie?",
                  WYL, gold, {})

R.shuffle(zestaw)
with open("zestaw.jsonl", "w") as f:
    for z in zestaw: f.write(json.dumps(z, ensure_ascii=False) + "\n")
from collections import Counter
c = Counter(z["family"] for z in zestaw); g = Counter((z["family"], z["questions"]["a"]["gold"]) for z in zestaw)
print(len(zestaw), "decyzji"); [print(f"  {k}: {v}  ", {o: n for (fa, o), n in g.items() if fa == k}) for k, v in sorted(c.items())]

# Rodziny NNW. Podział pracy: wszystko, co da się policzyć (daty, progi, promile, wiek, rejestr uprawnień), liczy kod;
# Basal dostaje tylko pytania o odczyt dokumentu względem pojęć z warunków (przyczyna, rola w zajściu, wpływ, kategoria aktywności).
# Każda grupa = jedna historia + bliźniaki różniące się jednym faktem; reguły syntetyczne z jawnymi parametrami.
from wspolne import *

IM_M = ["Kacper", "Bartosz", "Igor", "Adam", "Jan", "Szymon", "Filip", "Mikołaj", "Wojciech", "Antoni", "Dawid", "Krzysztof", "Paweł", "Łukasz", "Grzegorz", "Marek", "Oskar", "Tymon"]
IM_K = ["Zuzanna", "Natalia", "Oliwia", "Monika", "Ewa", "Karolina", "Julia", "Maja", "Hanna", "Agata", "Magdalena", "Joanna", "Weronika", "Alicja", "Lena", "Beata", "Iwona", "Patrycja"]
NAZ = [("Malinowski", "Malinowska"), ("Pawlak", "Pawlak"), ("Górski", "Górska"), ("Sikora", "Sikora"), ("Baran", "Baran"), ("Krajewski", "Krajewska"), ("Wróbel", "Wróbel"),
       ("Lis", "Lis"), ("Mazur", "Mazur"), ("Czarnecki", "Czarnecka"), ("Kubiak", "Kubiak"), ("Duda", "Duda"), ("Jabłoński", "Jabłońska"), ("Wieczorek", "Wieczorek"),
       ("Ostrowski", "Ostrowska"), ("Zając", "Zając"), ("Kołodziej", "Kołodziej"), ("Szewczyk", "Szewczyk"), ("Tomaszewski", "Tomaszewska"), ("Nowicki", "Nowicka")]
ZAWODY = ["magazynier", "księgowa", "kierowca", "pielęgniarka", "elektryk", "nauczycielka", "programista", "sprzedawczyni", "mechanik", "fryzjerka", "rolnik", "kucharz"]


def osoba(R, min_wiek=0, max_wiek=99):
    k = R.random() < .5
    imie = R.choice(IM_K if k else IM_M) + " " + R.choice(NAZ)[1 if k else 0]
    wiek = R.randint(max(min_wiek, 7), min(max_wiek, 70))
    rola = ("uczennica" if k else "uczeń") if wiek < 19 else ("studentka" if k else "student") if wiek < 24 and R.random() < .6 else R.choice(ZAWODY)
    return (imie, wiek, rola), f"{imie}, {wiek} lat, {rola}" + (" (kobieta)" if k else " (mężczyzna)")


# ───────────── 1. Przyczyna zdarzenia: przyczyna zewnętrzna czy stan zdrowia ─────────────
DEF_NW = ("nieszczęśliwy wypadek – nagłe zdarzenie wywołane przyczyną zewnętrzną, w następstwie którego Ubezpieczony, niezależnie "
          "od swojej woli, doznał uszkodzenia ciała, rozstroju zdrowia lub zmarł.")
ROZSZ = {
    "padaczka_omdlenie": "Za nieszczęśliwy wypadek uważa się również napad padaczki oraz omdlenie, jeżeli w ich następstwie Ubezpieczony doznał uszkodzenia ciała.",
    "zawal": "Za nieszczęśliwy wypadek uważa się również zawał serca i udar mózgu.",
    "omdlenie": "Za nieszczęśliwy wypadek uważa się również omdlenie, jeżeli w jego następstwie Ubezpieczony doznał uszkodzenia ciała.",
}
MECH = {  # mechanizm → (fakty dla piszącego, ukryte)
    "zewn": (["upadek spowodował czynnik zewnętrzny: {zew}", "przed upadkiem poszkodowany czuł się dobrze, nie tracił przytomności"], []),
    "zewn_wywiad": (["upadek spowodował czynnik zewnętrzny: {zew}", "poszkodowany choruje na {chor} (leczony od kilku lat), ale świadkowie i on sam potwierdzają, że przed upadkiem nie miał napadu ani zasłabnięcia, był przytomny"], []),
    "padaczka": (["poszkodowany choruje na padaczkę", "upadek nastąpił w trakcie napadu padaczkowego: drgawki i utrata przytomności poprzedziły upadek"], []),
    "omdlenie": (["poszkodowany zasłabł i stracił przytomność (omdlenie), a następnie upadł; nie potknął się ani nikt go nie popchnął"], []),
    "hipoglikemia": (["poszkodowany choruje na cukrzycę typu 1", "przed upadkiem miał bardzo niski poziom cukru (zmierzony glukometrem zaraz po zdarzeniu), był oszołomiony i osunął się na ziemię; nikt go nie popchnął, nie potknął się"], []),
    "zawal": (["poszkodowany nagle poczuł silny ból w klatce piersiowej i upadł; w szpitalu rozpoznano zawał serca", "wcześniej nie miał urazu ani kontaktu z czynnikiem zewnętrznym"], []),
    "nieustalone": (["poszkodowanego znaleziono leżącego na ziemi z urazem", "nikt nie widział, jak doszło do upadku, a poszkodowany nie pamięta zdarzenia"],
                    ["czy przyczyną był czynnik zewnętrzny, czy stan zdrowia (napad, zasłabnięcie)"]),
}
ZEW = ["potknął się o nierówną płytę chodnikową", "poślizgnął się na mokrej posadzce na korytarzu", "został uderzony piłką w głowę podczas przerwy",
       "został popchnięty przez kolegę na schodach", "spadł z drabinki, gdy pękł szczebel", "przytrzasnął palce drzwiami szafki"]
CHOR = ["padaczkę", "cukrzycę typu 1", "astmę"]
OPC_PRZ = {"objete_nw": "zdarzenie wywołane przyczyną zewnętrzną – nieszczęśliwy wypadek w rozumieniu definicji",
           "objete_zrownane": "zdarzenie wywołane stanem zdrowia, który warunki wprost zrównują z nieszczęśliwym wypadkiem",
           "nieobjete": "zdarzenie wywołane stanem zdrowia Ubezpieczonego, którego warunki nie zrównują z nieszczęśliwym wypadkiem",
           "brak_danych": "z dokumentów nie da się ustalić, czy przyczyną był czynnik zewnętrzny, czy stan zdrowia"}


def przyczyna_gold(mech, rozsz):
    if mech in ("zewn", "zewn_wywiad"): return "objete_nw"
    if mech == "nieustalone": return "brak_danych"
    if mech == "padaczka": return "objete_zrownane" if rozsz == "padaczka_omdlenie" else "nieobjete"
    if mech == "omdlenie": return "objete_zrownane" if rozsz in ("padaczka_omdlenie", "omdlenie") else "nieobjete"
    if mech == "zawal": return "objete_zrownane" if rozsz == "zawal" else "nieobjete"
    return "nieobjete"  # hipoglikemia nie jest zrównana w żadnym wariancie


def grupa_przyczyna(R, g):
    rdzen = R.choice([["zewn", "padaczka", "zewn_wywiad"], ["zewn", "omdlenie", "nieustalone"], ["zewn_wywiad", "hipoglikemia", "zewn"],
                      ["zawal", "zewn", "nieustalone"], ["padaczka", "omdlenie", "zewn_wywiad"]])
    o, opis = osoba(R, 9, 17) if "zawal" not in rdzen else osoba(R, 35, 68)
    zew, chor = R.choice(ZEW), R.choice(CHOR)
    if "zewn_wywiad" in rdzen and "padaczka" in rdzen: chor = "padaczkę"
    styl = R.choice(["zgloszenie_rodzica", "protokol_szkolny", "karta_sor", "oswiadczenie_swiadka"] if o[1] < 18 else ["zgloszenie_wlasne", "karta_sor", "notatka_likwidatora"])
    w = []
    for mech in rdzen:
        f, u = MECH[mech]
        w.append(dict(mech=mech, fakty=[x.format(zew=zew, chor=chor) for x in f] + ["skutek: uraz wymagający pomocy lekarskiej (np. złamanie, rana głowy)"], ukryte=u))
    return dict(rodzina="nnw_przyczyna", group=g, osoba=opis, wiek=o[1], styl=styl, warianty=w,
                pola={"mech": ("Co spowodowało upadek/zdarzenie?", ["przyczyna_zewnetrzna", "napad_padaczki", "omdlenie", "niedocukrzenie", "zawal"])})


MECH_SEDZIA = {"zewn": "przyczyna_zewnetrzna", "zewn_wywiad": "przyczyna_zewnetrzna", "padaczka": "napad_padaczki", "omdlenie": "omdlenie",
               "hipoglikemia": "niedocukrzenie", "zawal": "zawal", "nieustalone": "nie_wynika"}


def rekordy_przyczyna(gr, w, R):
    return [(DEF_NW + (" " + ROZSZ[r] if r else ""), {"a": ("Jak zakwalifikować zdarzenie według definicji z warunków ubezpieczenia?", OPC_PRZ, przyczyna_gold(w["mech"], r))},
             {"rozszerzenie": r}) for r in R.sample([None, "padaczka_omdlenie", "zawal", "omdlenie"], 2)]


# ───────────── 2. Alkohol: wynik badania i próg porównuje kod; Basal ocenia tylko wpływ na zajście wypadku ─────────────
REG_ALK = ["Ubezpieczyciel nie odpowiada za następstwa nieszczęśliwych wypadków, którym Ubezpieczony uległ w stanie po użyciu alkoholu lub w stanie nietrzeźwości, chyba że stan ten nie miał wpływu na zajście wypadku.",
           "Wyłączona jest odpowiedzialność za następstwa wypadków powstałych, gdy Ubezpieczony znajdował się pod wpływem alkoholu, jeżeli stan ten przyczynił się do zajścia wypadku."]
WPLYW = {
    "tak": ["poszkodowany szedł chwiejnym krokiem, potknął się o własne nogi na schodach i spadł",
            "poszkodowany wtargnął na jezdnię poza przejściem prosto pod nadjeżdżający samochód, nie rozglądając się",
            "poszkodowany wszedł na balustradę balkonu, żeby pokazać znajomym, że utrzyma równowagę, i spadł"],
    "nie": ["poszkodowany stał na przystanku autobusowym, gdy samochód, którego kierowca zasłabł, wjechał na chodnik i go potrącił",
            "poszkodowany siedział na ławce w parku, gdy złamany wiatrem konar spadł mu na ramię",
            "poszkodowany siedział jako pasażer w autobusie miejskim, który na skrzyżowaniu uderzył w ciężarówkę wjeżdżającą na czerwonym świetle"],
    "nieustalone": ["poszkodowany został potrącony przez samochód na przejściu dla pieszych; kierowca twierdzi, że pieszy wbiegł nagle na czerwonym, pieszy – że szedł na zielonym; świadków ani monitoringu brak",
                    "poszkodowany został potrącony przez rowerzystę na chodniku; rowerzysta twierdzi, że pieszy zatoczył się nagle pod koła, pieszy – że stał spokojnie przy witrynie sklepu; świadków ani monitoringu brak"],
}
OPC_ALK = {"mial_wplyw": "z dokumentu wynika, że stan Ubezpieczonego przyczynił się do zajścia wypadku",
           "nie_mial_wplywu": "z dokumentu wynika, że do wypadku doszłoby niezależnie od stanu Ubezpieczonego",
           "brak_danych": "z dokumentu nie da się ustalić, czy stan Ubezpieczonego przyczynił się do zajścia wypadku"}
WYNIK_ALK = ["badanie krwi wykazało 1,4‰ alkoholu", "badanie alkomatem wykazało 0,62 mg/l", "badanie krwi wykazało 0,9‰ alkoholu", "badanie alkomatem wykazało 1,05 mg/l"]


def grupa_alkohol(R, g):
    o, opis = osoba(R, 19, 65)
    wyn = R.choice(WYNIK_ALK)
    wp = R.sample(list(WPLYW), 3)
    w = [dict(wplyw=x, fakty=[f"przebieg zdarzenia: {R.choice(WPLYW[x])}", f"po zdarzeniu {wyn}", "skutek: złamanie, pobyt w szpitalu"],
              ukryte=["czy zachowanie poszkodowanego przyczyniło się do wypadku"] if x == "nieustalone" else []) for x in wp]
    return dict(rodzina="nnw_alkohol", group=g, osoba=opis, wiek=o[1], styl=R.choice(["notatka_policji", "karta_sor", "notatka_likwidatora"]), warianty=w,
                pola={"wplyw": ("Czy zachowanie poszkodowanego przyczyniło się do zdarzenia?", ["tak", "nie"])})


def rekordy_alkohol(gr, w, R):
    pyt = "Wynik badania przekracza próg stanu po użyciu alkoholu (ustalone na podstawie wyniku badania). Czy stan Ubezpieczonego miał wpływ na zajście wypadku?"
    return [(reg, {"a": (pyt, OPC_ALK, {"tak": "mial_wplyw", "nie": "nie_mial_wplywu", "nieustalone": "brak_danych"}[w["wplyw"]])}, {}) for reg in REG_ALK]


# ───────────── 3. Bójka ─────────────
REG_BOJKA = {
    None: "Ubezpieczyciel nie odpowiada za następstwa nieszczęśliwych wypadków powstałe w wyniku czynnego udziału Ubezpieczonego w bójce lub pobiciu, także wtedy, gdy Ubezpieczony działał w obronie własnej lub innej osoby.",
    "obrona": "Ubezpieczyciel nie odpowiada za następstwa nieszczęśliwych wypadków powstałe w wyniku czynnego udziału Ubezpieczonego w bójce lub pobiciu, z wyjątkiem działania w obronie koniecznej.",
    "obrona_pomoc": "Ubezpieczyciel nie odpowiada za następstwa nieszczęśliwych wypadków powstałe w wyniku czynnego udziału Ubezpieczonego w bójce lub pobiciu, z wyjątkiem działania w obronie koniecznej oraz udzielania pomocy osobie znajdującej się w niebezpieczeństwie.",
}
ROLA = {
    "inicjator": "poszkodowany pierwszy zaatakował rówieśnika (uderzył go pięścią po wymianie wyzwisk), ten oddał i doszło do szarpaniny, w której poszkodowany doznał urazu",
    "wzajemna": "poszkodowany umówił się z rówieśnikiem „na solo”; obaj zadawali sobie ciosy, poszkodowany doznał urazu",
    "obrona": "poszkodowany został niespodziewanie zaatakowany przez nieznanego mężczyznę; odpychał go i zasłaniał się, a gdy napastnik nie przestawał, uderzył go raz, żeby uciec; w trakcie szarpaniny doznał urazu",
    "ofiara": "poszkodowany został pobity przez dwóch nieznanych sprawców; nie oddawał ciosów, skulił się i próbował uciec",
    "pomoc": "poszkodowany zobaczył, jak dwóch starszych chłopaków bije młodszego kolegę; podbiegł, odciągał napastników i osłaniał kolegę, wtedy został uderzony",
    "nieustalone": "doszło do szarpaniny z udziałem poszkodowanego i rówieśnika, w której poszkodowany doznał urazu; obaj obwiniają się nawzajem o rozpoczęcie, świadków nie ma",
}
OPC_BOJ = {"wylaczona": "Ubezpieczony czynnie uczestniczył w bójce lub pobiciu i nie zachodzi wyjątek z warunków",
           "wyjatek_znosi": "Ubezpieczony uczestniczył w zajściu, ale jego działanie mieści się w wyjątku przewidzianym w warunkach",
           "brak_przeslanki": "Ubezpieczony nie brał czynnego udziału w bójce ani pobiciu",
           "brak_danych": "z dokumentów nie da się ustalić roli Ubezpieczonego w zajściu"}


def bojka_gold(rola, wyj):
    if rola == "nieustalone": return "brak_danych"
    if rola == "ofiara": return "brak_przeslanki"
    if rola in ("inicjator", "wzajemna"): return "wylaczona"
    return "wyjatek_znosi" if wyj else "wylaczona"  # obrona konieczna obejmuje też obronę cudzego dobra


def grupa_bojka(R, g):
    o, opis = osoba(R, 13, 23)
    role = R.sample(list(ROLA), 3)
    styl = R.choice(["notatka_policji", "protokol_szkolny" if o[1] < 19 else "notatka_likwidatora", "karta_sor", "oswiadczenie_swiadka"])
    return dict(rodzina="nnw_bojka", group=g, osoba=opis, wiek=o[1], styl=styl,
                warianty=[dict(rola=r, fakty=[ROLA[r], "skutek: złamanie nosa i stłuczenia"], ukryte=([] if r != "nieustalone" else ["kto rozpoczął zajście i czy poszkodowany zadawał ciosy"])) for r in role],
                pola={"rola": ("Jaka była rola poszkodowanego w zajściu?", ["zaatakowal_pierwszy", "wzajemna_umowiona_bojka", "bronil_sie_przed_atakiem", "bity_nie_oddawal", "bronil_innej_osoby"])})


ROLA_SEDZIA = {"inicjator": "zaatakowal_pierwszy", "wzajemna": "wzajemna_umowiona_bojka", "obrona": "bronil_sie_przed_atakiem", "ofiara": "bity_nie_oddawal",
               "pomoc": "bronil_innej_osoby", "nieustalone": "nie_wynika"}


def rekordy_bojka(gr, w, R):
    return [(REG_BOJKA[x], {"a": ("Czy zachodzi wyłączenie odpowiedzialności związane z bójką lub pobiciem?", OPC_BOJ, bojka_gold(w["rola"], x))}, {"wyjatek": x})
            for x in R.sample([None, "obrona", "obrona_pomoc"], 2)]


# ───────────── 4. Sport: wiek liczy kod; Basal klasyfikuje aktywność wobec listy i okoliczności wobec definicji wyczynu ─────────────
SPORTY_RYZ = ["wspinaczka skałkowa", "kolarstwo górskie (downhill)", "jazda na nartach poza oznakowanymi trasami", "skoki spadochronowe", "nurkowanie z aparatem oddechowym",
              "parkour", "sporty walki w formule kontaktowej (MMA, kick-boxing)", "jazda na motocyklu crossowym"]
ZAJECIA = {  # nazwa → (opis, pozycja listy, która ją obejmuje)
    "scianka": ("wspinaczka na sztucznej ściance wspinaczkowej w centrum sportowym, z asekuracją liną", None),
    "skalki": ("wspinaczka na skałkach w Jurze Krakowsko-Częstochowskiej", "wspinaczka skałkowa"),
    "narty_trasa": ("jazda na nartach po oznakowanej, otwartej trasie zjazdowej", None),
    "narty_poza": ("jazda na nartach w lesie poza oznakowanymi trasami, obok wyciągu", "jazda na nartach poza oznakowanymi trasami"),
    "pilka": ("gra w piłkę nożną", None),
    "rower_park": ("jazda rowerem po asfaltowej ścieżce w parku", None),
    "downhill": ("zjazd rowerem po stromej leśnej trasie downhillowej z przeszkodami", "kolarstwo górskie (downhill)"),
    "mma": ("sparing MMA w pełnym kontakcie", "sporty walki w formule kontaktowej (MMA, kick-boxing)"),
}
KONTEKST = {"rekreacja": "dla przyjemności, ze znajomymi, poza jakimkolwiek klubem i bez zawodów",
            "wf": "podczas obowiązkowej lekcji wychowania fizycznego w szkole",
            "zawody_szkolne": "podczas międzyszkolnych zawodów organizowanych przez szkołę",
            "klub": "podczas treningu w klubie sportowym, do którego należy i w barwach którego startuje w rozgrywkach ligowych"}
MOZLIWE = {"scianka": ["rekreacja", "wf", "zawody_szkolne", "klub"], "skalki": ["rekreacja", "klub"], "narty_trasa": ["rekreacja", "zawody_szkolne", "klub"],
           "narty_poza": ["rekreacja"], "pilka": ["rekreacja", "wf", "zawody_szkolne", "klub"], "rower_park": ["rekreacja"], "downhill": ["rekreacja", "klub"],
           "mma": ["rekreacja", "klub"]}


def regula_sport(lista, szkola):
    return ("Ubezpieczyciel nie odpowiada za następstwa nieszczęśliwych wypadków powstałe podczas: 1) uprawiania sportów wysokiego ryzyka, "
            f"tj.: {', '.join(lista)}; 2) wyczynowego uprawiania sportu, tj. udziału w zawodach lub rozgrywkach sportowych oraz w treningach w klubach sportowych"
            + (", przy czym za wyczynowe uprawianie sportu nie uważa się zawodów organizowanych przez szkołę" if szkola else "") + ".")


OPC_RYZ = {"z_listy": "aktywność, podczas której doszło do wypadku, mieści się w jednej z pozycji listy sportów wysokiego ryzyka",
           "spoza_listy": "aktywność nie mieści się w żadnej pozycji listy sportów wysokiego ryzyka",
           "brak_danych": "z dokumentu nie da się ustalić, jaką aktywność uprawiano"}
OPC_WYCZ = {"wyczyn": "okoliczności mieszczą się w definicji wyczynowego uprawiania sportu z warunków",
            "nie_wyczyn": "okoliczności nie mieszczą się w definicji wyczynowego uprawiania sportu z warunków",
            "brak_danych": "z dokumentu nie da się ustalić okoliczności, w jakich uprawiano aktywność"}


def grupa_sport(R, g):
    o, opis = osoba(R, 12, 18) if R.random() < .6 else osoba(R, 19, 35)
    szkolny = o[1] < 19
    MOZ = {k: [c for c in v if szkolny or c not in ("wf", "zawody_szkolne")] for k, v in MOZLIWE.items()}
    zaj = R.choice(list(ZAJECIA))
    zaj2 = {"scianka": "skalki", "skalki": "scianka", "narty_trasa": "narty_poza", "narty_poza": "narty_trasa", "rower_park": "downhill", "downhill": "rower_park"}.get(zaj, R.choice(list(ZAJECIA)))
    zaj2 = zaj2 if set(MOZ[zaj]) & set(MOZ[zaj2]) else zaj
    kont = R.choice([k for k in MOZ[zaj] if k in MOZ[zaj2]])
    kont2 = R.choice([k for k in MOZ[zaj] if k != kont] or [kont])
    w = [dict(zaj=a, kont=b) for a, b in dict.fromkeys([(zaj, kont), (zaj2, kont), (zaj, kont2)])]
    if R.random() < .3: w.append(dict(zaj=zaj, kont=None))
    for x in w:
        x["fakty"] = [f"do urazu doszło podczas aktywności: {ZAJECIA[x['zaj']][0]}"] + ([f"okoliczności: {KONTEKST[x['kont']]}"] if x["kont"] else []) + ["skutek: złamanie kości"]
        x["ukryte"] = [] if x["kont"] else ["czy działo się to w klubie, w szkole czy rekreacyjnie"]
    styl = R.choice(["zgloszenie_rodzica" if o[1] < 18 else "zgloszenie_wlasne", "karta_sor", "notatka_likwidatora"])
    return dict(rodzina="nnw_sport", group=g, osoba=opis, wiek=o[1], styl=styl, warianty=w,
                pola={"kont": ("W jakich okolicznościach uprawiano aktywność?", ["rekreacja", "lekcja_wf", "zawody_szkolne", "klub_sportowy"]),
                      "zaj": ("Jaką aktywność uprawiano?", ["scianka_wspinaczkowa", "skalki", "narty_na_trasie", "narty_poza_trasa", "pilka_nozna", "rower_rekreacyjnie", "rower_downhill", "mma"])})


KONT_SEDZIA = {"rekreacja": "rekreacja", "wf": "lekcja_wf", "zawody_szkolne": "zawody_szkolne", "klub": "klub_sportowy", None: "nie_wynika"}
ZAJ_SEDZIA = {"scianka": "scianka_wspinaczkowa", "skalki": "skalki", "narty_trasa": "narty_na_trasie", "narty_poza": "narty_poza_trasa", "pilka": "pilka_nozna",
              "rower_park": "rower_rekreacyjnie", "downhill": "rower_downhill", "mma": "mma"}


def rekordy_sport(gr, w, R):
    out = []
    for _ in range(2):
        lista = R.sample(SPORTY_RYZ, R.randint(3, 6))
        if ZAJECIA[w["zaj"]][1] and R.random() < .6 and ZAJECIA[w["zaj"]][1] not in lista:
            lista[0] = ZAJECIA[w["zaj"]][1]
        R.shuffle(lista)
        sz = R.random() < .5
        ryz = "z_listy" if ZAJECIA[w["zaj"]][1] in lista else "spoza_listy"
        wycz = "brak_danych" if w["kont"] is None else "wyczyn" if (w["kont"] == "klub" or (w["kont"] == "zawody_szkolne" and not sz)) else "nie_wyczyn"
        out.append((regula_sport(lista, sz), {"ryzyko": ("Czy aktywność, podczas której doszło do wypadku, jest sportem wysokiego ryzyka w rozumieniu warunków?", OPC_RYZ, ryz),
                                              "wyczyn": ("Czy wypadek nastąpił podczas wyczynowego uprawiania sportu w rozumieniu warunków?", OPC_WYCZ, wycz)},
                    {"lista": lista, "szkola": sz}))
    return out


# ───────────── 5. Kierowanie pojazdem: uprawnienia sprawdza kod w rejestrze; Basal ustala, kto kierował i czy przyczyna leżała po stronie kierującego ─────────────
POJAZD = {"skuter": "motorowerem (skuterem 50 cm³)", "samochod": "samochodem osobowym", "motocykl": "motocyklem 600 cm³"}
ZDARZ = {"kierujacy": ["na łuku drogi stracił panowanie nad pojazdem przy zbyt dużej prędkości i uderzył w drzewo",
                       "nie zauważył znaku STOP, wjechał na skrzyżowanie i zderzył się z innym pojazdem"],
         "zewnetrzna": ["stał prawidłowo na czerwonym świetle, gdy w tył pojazdu z dużą prędkością uderzył inny kierowca, który – jak ustaliła policja – zasnął za kierownicą",
                        "jechał prawidłowo swoim pasem, gdy z przeciwka na jego pas zjechała ciężarówka, której kierowca zasłabł"],
         "nieustalone": ["pojazd wypadł z drogi na prostym odcinku; kierujący nie pamięta zdarzenia, świadków nie było, opinia biegłego jeszcze nie powstała"]}
OPC_KTO = {"ubezpieczony": "pojazdem kierował Ubezpieczony", "inna_osoba": "pojazdem kierowała inna osoba, a Ubezpieczony był pasażerem", "brak_danych": "z dokumentu nie da się ustalić, kto kierował"}
OPC_PRZYCZ = {"po_stronie_kierujacego": "wypadek spowodował sposób prowadzenia pojazdu przez kierującego",
              "zewnetrzna": "wypadek spowodowała okoliczność niezależna od kierującego (np. inny uczestnik ruchu)",
              "brak_danych": "z dokumentu nie da się ustalić przyczyny wypadku"}
REG_POJ = "Ubezpieczyciel nie odpowiada za następstwa nieszczęśliwych wypadków powstałe podczas kierowania przez Ubezpieczonego pojazdem bez wymaganych uprawnień, chyba że brak uprawnień nie miał wpływu na zajście wypadku."


def grupa_pojazd(R, g):
    poj = R.choice(list(POJAZD))
    o, opis = osoba(R, 15, 17) if poj == "skuter" else osoba(R, 19, 45)
    prz = R.choice(["kierujacy", "zewnetrzna"])
    inna = "zewnetrzna" if prz == "kierujacy" else R.choice(["kierujacy", "nieustalone"])
    w = []
    for kto, p in [("ubezpieczony", prz), ("ubezpieczony", inna), (R.choice(["inna_osoba", "nieustalone"]), prz)]:
        z = R.choice(ZDARZ[p]) if p != prz or not w else w[0]["_z"]
        if kto == "inna_osoba":
            f = [f"poszkodowany jechał jako pasażer; pojazdem ({POJAZD[poj]}) kierował jego znajomy", f"kierujący {z}"]
            u = []
        elif kto == "nieustalone":
            f = [f"poszkodowany i jego znajomy jechali razem {POJAZD[poj]}; poszkodowany twierdzi, że kierował znajomy, a znajomy – że kierował poszkodowany; świadków nie ma", f"pojazd {z.replace('stał', 'stał').replace('jechał', 'jechał')}"]
            u = ["kto kierował pojazdem"]
        else:
            f, u = [f"poszkodowany kierował {POJAZD[poj]}", f"kierujący {z}"], []
        w.append(dict(kto=kto, przycz=p, _z=z, fakty=f + ["skutek: złamanie, pobyt w szpitalu"], ukryte=u + (["przyczyna wypadku"] if p == "nieustalone" else [])))
    for x in w: x.pop("_z")
    return dict(rodzina="nnw_pojazd", group=g, osoba=opis, wiek=o[1], styl=R.choice(["notatka_policji", "notatka_likwidatora"]), warianty=w,
                pola={"kto": ("Kto kierował pojazdem?", ["poszkodowany", "inna_osoba"]),
                      "przycz": ("Co było przyczyną wypadku?", ["blad_kierujacego", "inny_uczestnik_ruchu_lub_okolicznosc_zewnetrzna"])})


def rekordy_pojazd(gr, w, R):
    return [(REG_POJ, {"kto": ("Kto kierował pojazdem w chwili wypadku?", OPC_KTO, {"nieustalone": "brak_danych"}.get(w["kto"], w["kto"])),
                       "przyczyna": ("Co było przyczyną wypadku?", OPC_PRZYCZ, {"kierujacy": "po_stronie_kierujacego", "zewnetrzna": "zewnetrzna", "nieustalone": "brak_danych"}[w["przycz"]])},
             {"uwaga": "uprawnienia sprawdza kod w rejestrze; łączy odpowiedzi z regułą"})]


# ───────────── zgodność odczytu sędziego z ukrytymi faktami ─────────────
def zgodny(gr, w, odp):
    r = gr["rodzina"]
    if r == "nnw_przyczyna": return odp["mech"] == MECH_SEDZIA[w["mech"]]
    if r == "nnw_alkohol": return odp["wplyw"] == {"tak": "tak", "nie": "nie", "nieustalone": "nie_wynika"}[w["wplyw"]]
    if r == "nnw_bojka": return odp["rola"] == ROLA_SEDZIA[w["rola"]]
    if r == "nnw_sport": return odp["kont"] == KONT_SEDZIA[w["kont"]] and odp["zaj"] == ZAJ_SEDZIA[w["zaj"]]
    if r == "nnw_pojazd":
        return (odp["kto"] == {"ubezpieczony": "poszkodowany", "inna_osoba": "inna_osoba", "nieustalone": "nie_wynika"}[w["kto"]]
                and odp["przycz"] == {"kierujacy": "blad_kierujacego", "zewnetrzna": "inny_uczestnik_ruchu_lub_okolicznosc_zewnetrzna", "nieustalone": "nie_wynika"}[w["przycz"]])


RODZINY = {"nnw_przyczyna": (grupa_przyczyna, rekordy_przyczyna), "nnw_alkohol": (grupa_alkohol, rekordy_alkohol), "nnw_bojka": (grupa_bojka, rekordy_bojka),
           "nnw_sport": (grupa_sport, rekordy_sport), "nnw_pojazd": (grupa_pojazd, rekordy_pojazd)}

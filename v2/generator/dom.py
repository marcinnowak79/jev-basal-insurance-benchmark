# Rodziny majątkowe (dom/mieszkanie): definicja zdarzenia z OWU i wyłączenia oceniane z opisu.
# Reguły syntetyczne z parametrami wzorowanymi na rozrzucie między OWU (reguly_dom.json → roznice); etykietę liczy kod z ukrytych faktów.
from wspolne import *

STYLE.update({
    "zgloszenie_wlasciciela": "zgłoszenie szkody majątkowej wpisane przez właściciela domu lub mieszkania w formularzu internetowym (pierwsza osoba, potocznie)",
    "notatka_ogledzin": "notatka likwidatora z oględzin miejsca szkody (trzecia osoba, rzeczowo, z opisem stwierdzonych uszkodzeń)",
    "notatka_policji_wlam": "notatka urzędowa policjanta z oględzin miejsca kradzieży (styl urzędowy, trzecia osoba)",
})
WLASC = ["Tomasz Zieliński, właściciel domu jednorodzinnego", "Agnieszka Wójcik, właścicielka mieszkania w bloku", "Robert Kaczmarek, właściciel domu z garażem",
         "Beata Szulc, właścicielka mieszkania w kamienicy", "Marek Pietrzak, właściciel domu na wsi", "Dorota Michalska, właścicielka segmentu"]
OPC_DEF = {"spelnia": "zdarzenie spełnia definicję z warunków ubezpieczenia",
           "nie_spelnia_warunku": "zaszło zjawisko opisane w definicji (wiatr, wyładowanie, wyciek z instalacji, wejście sprawcy), ale bez spełnienia dodatkowego warunku z definicji (np. szkód w sąsiedztwie, sposobu wejścia, przyczyny wycieku)",
           "inne_zdarzenie": "szkodę spowodowało zjawisko innego rodzaju niż opisane w definicji, w tym takie, które definicja wprost wyłącza (np. wody gruntowe, deszcz przez dach, spróchnienie drzewa, awaria sieci)",
           "brak_danych": "z dokumentów nie da się ustalić, czy zdarzenie spełnia definicję"}

# ── wiatr (bez progów m/s – pomiar IMGW porównuje kod) ──
def def_wiatr(sasiedztwo):
    return ("silny wiatr – wiatr, którego działanie wyrządziło szkody w miejscu ubezpieczenia"
            + (" oraz – w tym samym czasie – szkody w sąsiedztwie miejsca ubezpieczenia." if sasiedztwo else "."))
WIATR = {
    "sasiedztwo": ["podczas wichury drzewo przewróciło się na dach i uszkodziło pokrycie", "wiatr zerwał też fragmenty dachów i ogrodzeń u kilku sąsiadów na tej samej ulicy"],
    "tylko_u_nas": ["podczas wichury drzewo przewróciło się na dach i uszkodziło pokrycie", "u sąsiadów nic się nie stało, szkody były tylko na tej posesji"],
    "spruchniale": ["w bezwietrzny, spokojny dzień drzewo przewróciło się na dach", "pień drzewa był od środka spróchniały, co stwierdził arborysta"],
    "nieustalone": ["w nocy drzewo przewróciło się na dach; właściciel spał i nie wie, czy wiało", "sąsiedzi szkód nie zgłaszali i nikt nie pamięta pogody tej nocy; stanu pnia nikt nie sprawdzał"],
}


def gold_wiatr(sc, sasiedztwo):
    return {"sasiedztwo": "spelnia", "tylko_u_nas": "nie_spelnia_warunku" if sasiedztwo else "spelnia", "spruchniale": "inne_zdarzenie", "nieustalone": "brak_danych"}[sc]


# ── zalanie ──
def def_zalanie(krany):
    return ("zalanie – wydostanie się wody lub pary z przewodów albo urządzeń instalacji wodociągowej, kanalizacyjnej lub centralnego ogrzewania na skutek ich awarii"
            + (" albo pozostawienia otwartych kranów lub zaworów przez osoby trzecie" if krany else "")
            + "; za zalanie nie uważa się przenikania wód gruntowych ani wody opadowej przez dach, ściany lub okna.")
ZAL = {
    "rura": ["w łazience pękła rura doprowadzająca wodę (stwierdzono pęknięcie na złączce)", "woda zalała podłogę i ściany"],
    "sasiad_kran": ["sąsiad z góry zostawił odkręcony kran w wannie i wyszedł z domu", "woda przeciekła przez strop i zalała sufit oraz ściany"],
    "dach": ["podczas ulewy woda przeciekała przez nieszczelne pokrycie dachu", "zalany sufit i ściany na poddaszu; instalacje wodne sprawne"],
    "grunt": ["po długotrwałych roztopach w piwnicy pojawiła się woda przesączająca się przez ściany fundamentowe", "instalacje wodne i kanalizacyjne sprawne, sprawdzone przez hydraulika"],
    "nieustalone": ["na suficie pojawiła się duża mokra plama, która po kilku dniach wyschła", "hydraulik nie znalazł nieszczelności, a sąsiad z góry nie wpuścił nikogo do mieszkania"],
}


def gold_zal(sc, krany):
    return {"rura": "spelnia", "sasiad_kran": "spelnia" if krany else "nie_spelnia_warunku", "dach": "inne_zdarzenie", "grunt": "inne_zdarzenie",
            "nieustalone": "brak_danych"}[sc]


# ── piorun ──
def def_piorun(posr):
    return ("uderzenie pioruna – " + ("bezpośrednie lub pośrednie" if posr else "bezpośrednie") + " przejście ładunku elektrycznego z atmosfery do ziemi przez ubezpieczone mienie"
            + ("; za uderzenie pioruna uważa się także uszkodzenie urządzeń elektrycznych wskutek przepięcia wywołanego wyładowaniem atmosferycznym w pobliżu miejsca ubezpieczenia" if posr else
               "; za uderzenie pioruna nie uważa się uszkodzeń urządzeń elektrycznych wskutek przepięcia w sieci, nawet jeśli wywołał je piorun") + ".")
PIOR = {
    "bezposr": ["podczas burzy piorun uderzył w komin domu", "komin pękł, dachówki wokół zostały strzaskane, osmalone ślady na murze"],
    "posr": ["podczas burzy piorun uderzył w słup energetyczny ok. 50 m od domu", "w domu spaliły się telewizor i router; sam budynek nie został trafiony"],
    "awaria": ["przy bezchmurnej pogodzie w sieci energetycznej doszło do awarii transformatora", "w domu spaliły się telewizor i router"],
    "nieustalone": ["po powrocie z urlopu właściciel stwierdził, że spalił się telewizor i router", "nie wiadomo, kiedy ani dlaczego doszło do uszkodzenia; zakład energetyczny nie odnotował awarii"],
}


def gold_pior(sc, posr):
    # przy definicji tylko bezpośredniej przepięcie od pioruna jest wprost wyłączone → „inne zdarzenie” (jak wody gruntowe przy zalaniu)
    return {"bezposr": "spelnia", "posr": "spelnia" if posr else "inne_zdarzenie", "awaria": "inne_zdarzenie", "nieustalone": "brak_danych"}[sc]


# ── kradzież z włamaniem ──
def def_wlam(klucz):
    return ("kradzież z włamaniem – zabór mienia z zamkniętego lokalu po usunięciu zabezpieczeń przy użyciu siły lub narzędzi albo po otwarciu zamka podrobionym kluczem"
            + (" lub kluczem oryginalnym, który sprawca zdobył w wyniku rabunku" if klucz else "") + "; za kradzież z włamaniem nie uważa się zaboru mienia z lokalu niezamkniętego "
            "ani wejścia przez otwarte okno.")
WLAM = {
    "wywazone": ["drzwi wejściowe zostały wyważone łomem – wyrwana framuga, ślady narzędzia na skrzydle", "skradziono laptopa i biżuterię"],
    "okno_otwarte": ["sprawca wszedł przez uchylone okno na parterze, którego nikt nie zamknął przed wyjściem", "okno i drzwi bez śladów uszkodzeń; skradziono laptopa i biżuterię"],
    "klucz_rabunek": ["dzień wcześniej właścicielce na ulicy siłą wyrwano torebkę z kluczami do mieszkania", "sprawca otworzył drzwi tymi kluczami, zamek bez uszkodzeń; skradziono laptopa i biżuterię"],
    "drzwi_niezamkniete": ["domownicy wyszli do ogrodu, zostawiając drzwi wejściowe niezamknięte na klucz", "w tym czasie ktoś wszedł i zabrał laptopa i biżuterię"],
    "nieustalone": ["po powrocie właściciel zauważył brak laptopa i biżuterii", "drzwi i okna były zamknięte, bez widocznych śladów; policja nie ustaliła, jak sprawca dostał się do środka"],
}


def gold_wlam(sc, klucz):
    return {"wywazone": "spelnia", "okno_otwarte": "nie_spelnia_warunku", "klucz_rabunek": "spelnia" if klucz else "nie_spelnia_warunku",
            "drzwi_niezamkniete": "nie_spelnia_warunku", "nieustalone": "nie_spelnia_warunku"}[sc]  # brak śladów usunięcia zabezpieczeń = brak przesłanki włamania


ZDARZENIA = {  # nazwa → (scenariusze, generator parametrów, definicja, gold, styl, pytanie sędziego)
    "wiatr": (list(WIATR), lambda R: R.random() < .5, def_wiatr, gold_wiatr, ["zgloszenie_wlasciciela", "notatka_ogledzin"],
              ("Co przewróciło drzewo i czy wiatr wyrządził szkody także u sąsiadów?", ["wiatr_szkody_tez_u_sasiadow", "wiatr_szkody_tylko_tu", "sprochnialy_pien_bez_wiatru"])),
    "zalanie": (list(ZAL), lambda R: R.random() < .5, def_zalanie, gold_zal, ["zgloszenie_wlasciciela", "notatka_ogledzin"],
                ("Skąd pochodziła woda?", ["pekniecie_rury", "kran_u_sasiada", "dach_podczas_deszczu", "wody_gruntowe"])),
    "piorun": (list(PIOR), lambda R: R.random() < .5, def_piorun, gold_pior, ["zgloszenie_wlasciciela", "notatka_ogledzin"],
               ("Co spowodowało szkodę?", ["piorun_trafil_w_budynek", "piorun_w_poblizu_przepiecie", "awaria_sieci_bez_burzy"])),
    "wlamanie": (list(WLAM), lambda R: R.random() < .5, def_wlam, gold_wlam, ["zgloszenie_wlasciciela", "notatka_policji_wlam"],
                 ("Jak sprawca dostał się do środka?", ["wywazyl_drzwi", "otwarte_okno", "klucz_zdobyty_w_rabunku", "drzwi_niezamkniete"])),
}
SEDZIA_DOM = {"wiatr": {"sasiedztwo": "wiatr_szkody_tez_u_sasiadow", "tylko_u_nas": "wiatr_szkody_tylko_tu", "spruchniale": "sprochnialy_pien_bez_wiatru", "nieustalone": "nie_wynika"},
              "zalanie": {"rura": "pekniecie_rury", "sasiad_kran": "kran_u_sasiada", "dach": "dach_podczas_deszczu", "grunt": "wody_gruntowe", "nieustalone": "nie_wynika"},
              "piorun": {"bezposr": "piorun_trafil_w_budynek", "posr": "piorun_w_poblizu_przepiecie", "awaria": "awaria_sieci_bez_burzy", "nieustalone": "nie_wynika"},
              "wlamanie": {"wywazone": "wywazyl_drzwi", "okno_otwarte": "otwarte_okno", "klucz_rabunek": "klucz_zdobyty_w_rabunku", "drzwi_niezamkniete": "drzwi_niezamkniete", "nieustalone": "nie_wynika"}}
NAZWA = {"wiatr": "silnego wiatru", "zalanie": "zalania", "piorun": "uderzenia pioruna", "wlamanie": "kradzieży z włamaniem"}


def grupa_definicja(R, g):
    zd = R.choice(list(ZDARZENIA))
    wyb = R.sample(ZDARZENIA[zd][0], 3)
    src = {"wiatr": WIATR, "zalanie": ZAL, "piorun": PIOR, "wlamanie": WLAM}[zd]
    w = [dict(zd=zd, sc=sc, fakty=list(src[sc]), ukryte=["przyczyna szkody"] if sc == "nieustalone" else []) for sc in wyb]
    return dict(rodzina="dom_definicja", group=g, osoba=R.choice(WLASC), wiek=99, styl=R.choice(ZDARZENIA[zd][4]), warianty=w, pola={"sc": ZDARZENIA[zd][5]})


def rekordy_definicja(gr, w, R):
    zd = w["zd"]
    return [(ZDARZENIA[zd][2](p), {"a": (f"Czy szkoda powstała wskutek {NAZWA[zd]} w rozumieniu definicji z warunków ubezpieczenia?", OPC_DEF, ZDARZENIA[zd][3](w["sc"], p))},
             {"zdarzenie": zd, "param": p}) for p in [True, False]]


def zgodny_def(gr, w, odp):
    return odp["sc"] == SEDZIA_DOM[w["zd"]][w["sc"]]


# ── wyłączenie: lokal pozostawiony bez nadzoru (liczbę dni liczy kod z dat; Basal ocenia tylko doglądanie) ──
def regula_pusty(dni, czest):
    return (f"Ubezpieczyciel nie odpowiada za szkody powstałe w lokalu, który w chwili szkody pozostawał niezamieszkały przez okres dłuższy niż {dni} kolejnych dni, "
            f"chyba że w tym czasie lokal był doglądany przez osobę upoważnioną przez Ubezpieczonego, która {czest} wchodziła do lokalu i sprawdzała jego stan.")
CZEST = {"tydzien": "nie rzadziej niż raz w tygodniu", "dwa_tyg": "nie rzadziej niż raz na dwa tygodnie"}
DOGLAD = {"co_kilka_dni": "w tym czasie sąsiadka co kilka dni wchodziła do mieszkania, podlewała kwiaty i sprawdzała, czy wszystko w porządku",
          "co_10_dni": "w tym czasie syn zaglądał do mieszkania mniej więcej co dziesięć dni, wietrzył i sprawdzał, czy wszystko w porządku",
          "raz": "w tym czasie syn zajrzał do mieszkania tylko raz, mniej więcej w połowie wyjazdu",
          "skrzynka": "w tym czasie sąsiad co dwa–trzy dni wyjmował listy ze skrzynki pocztowej, ale do mieszkania nie wchodził",
          "nieustalone": "właściciel twierdzi, że ktoś z rodziny „doglądał” mieszkania, ale nie potrafi powiedzieć kto ani jak często"}
OPC_DOGL = {"spelniony": "lokal był doglądany w sposób i z częstotliwością wymaganą przez warunki",
            "niespelniony": "lokal nie był doglądany w sposób lub z częstotliwością wymaganą przez warunki",
            "brak_danych": "z dokumentu nie da się ustalić, czy lokal był doglądany zgodnie z warunkami"}


def gold_dogl(d, czest):
    if d == "nieustalone": return "brak_danych"
    if d == "co_kilka_dni": return "spelniony"
    if d == "co_10_dni": return "spelniony" if czest == "dwa_tyg" else "niespelniony"
    return "niespelniony"


def grupa_pusty(R, g):
    wyj = R.choice(["wyjazd za granicę", "wyjazd do sanatorium", "kontrakt w Norwegii", "pobyt u córki w Anglii", "pobyt w szpitalu i rehabilitacja"])
    w = [dict(doglad=d, fakty=["podczas nieobecności mieszkańców pękł wąż przy pralce i woda zalała mieszkanie; szkodę zauważono po powrocie",
                               f"mieszkańcy byli kilka miesięcy nieobecni z powodu: {wyj}; przez ten czas nikt w lokalu nie mieszkał", DOGLAD[d]],
              ukryte=["kto i jak często doglądał mieszkania"] if d == "nieustalone" else []) for d in R.sample(list(DOGLAD), 3)]
    return dict(rodzina="dom_pusty", group=g, osoba=R.choice(WLASC), wiek=99, styl=R.choice(["zgloszenie_wlasciciela", "notatka_ogledzin"]), warianty=w,
                pola={"doglad": ("Czy ktoś wchodził do lokalu podczas nieobecności i jak często?", ["co_kilka_dni", "co_okolo_10_dni", "jeden_raz", "nikt_nie_wchodzil_do_srodka"])})


def zgodny_pusty(gr, w, odp):
    return odp["doglad"] == {"co_kilka_dni": "co_kilka_dni", "co_10_dni": "co_okolo_10_dni", "raz": "jeden_raz", "skrzynka": "nikt_nie_wchodzil_do_srodka", "nieustalone": "nie_wynika"}[w["doglad"]]


def rekordy_pusty(gr, w, R):
    pyt = "Z dat wynika, że lokal pozostawał niezamieszkały dłużej niż okres wskazany w warunkach. Czy spełniono warunek doglądania lokalu, który znosi wyłączenie?"
    return [(regula_pusty(dni, CZEST[c]), {"a": (pyt, OPC_DOGL, gold_dogl(w["doglad"], c))}, {"dni": dni, "czest": c})
            for dni, c in [(R.choice([30, 45, 60, 90]), c) for c in R.sample(list(CZEST), 2)]]


# ── wyłączenie: deszcz przez niezamknięte okno ──
def regula_okno(furtka):
    return ("Ubezpieczyciel nie odpowiada za szkody wyrządzone przez deszcz lub grad, które dostały się do wnętrza budynku przez niezamknięte okna, drzwi lub inne otwory"
            + (", chyba że otwór powstał wskutek zdarzenia objętego ubezpieczeniem albo pozostawienie niezamkniętego okna nie miało wpływu na powstanie szkody." if furtka else
               ", w tym przez otwory powstałe wskutek uszkodzenia okien lub dachu, niezależnie od przyczyny, dla której otwór pozostawał niezamknięty."))
OKNO = {"uchylone": ["domownicy wyjechali na weekend, zostawiając uchylone okno dachowe", "podczas ulewy woda wlała się przez to okno i zalała podłogę oraz meble"],
        "wybite": ["podczas burzy grad wybił szybę w oknie dachowym", "deszcz wlewał się przez wybitą szybę i zalał podłogę oraz meble"],
        "inne_zrodlo": ["domownicy zostawili uchylone okno w kuchni", "szkodę w salonie spowodowała woda z pękniętego grzejnika – kuchnia i okno pozostały suche"],
        "nieustalone": ["po ulewie podłoga i meble przy oknie dachowym były zalane", "nie wiadomo, czy okno było zamknięte, bo w domu nikogo nie było, a po powrocie domownicy nie pamiętają"]}
OPC_OKNO = {"wylaczona": "szkodę wyrządził deszcz, który dostał się przez niezamknięty otwór, i nie zachodzi wyjątek",
            "wyjatek_znosi": "deszcz dostał się przez otwór, ale zachodzi wyjątek przewidziany w warunkach",
            "brak_przeslanki": "szkody nie wyrządził deszcz ani grad, który dostał się przez niezamknięty otwór",
            "brak_danych": "z dokumentów nie da się ustalić, jak woda dostała się do wnętrza"}


def gold_okno(sc, furtka):
    return {"uchylone": "wylaczona", "wybite": "wyjatek_znosi" if furtka else "wylaczona", "inne_zrodlo": "brak_przeslanki", "nieustalone": "brak_danych"}[sc]


def grupa_okno(R, g):
    wyb = R.sample(list(OKNO), 3)
    w = [dict(sc=sc, fakty=OKNO[sc], ukryte=["czy okno było otwarte"] if sc == "nieustalone" else []) for sc in wyb]
    return dict(rodzina="dom_okno", group=g, osoba=R.choice(WLASC), wiek=99, styl=R.choice(["zgloszenie_wlasciciela", "notatka_ogledzin"]), warianty=w,
                pola={"sc": ("Jak woda dostała się do pomieszczenia?", ["przez_pozostawione_otwarte_okno", "przez_szybe_wybita_przez_grad", "z_instalacji_grzewczej"])})


def zgodny_okno(gr, w, odp):
    return odp["sc"] == {"uchylone": "przez_pozostawione_otwarte_okno", "wybite": "przez_szybe_wybita_przez_grad", "inne_zrodlo": "z_instalacji_grzewczej", "nieustalone": "nie_wynika"}[w["sc"]]


def rekordy_okno(gr, w, R):
    return [(regula_okno(f), {"a": ("Czy zachodzi wyłączenie odpowiedzialności za szkody wyrządzone przez opady przez niezamknięte otwory?", OPC_OKNO, gold_okno(w["sc"], f))}, {"furtka": f})
            for f in R.sample([True, False], 2)]


RODZINY = {"dom_definicja": (grupa_definicja, rekordy_definicja), "dom_pusty": (grupa_pusty, rekordy_pusty), "dom_okno": (grupa_okno, rekordy_okno)}
ZGODNY = {"dom_definicja": zgodny_def, "dom_pusty": zgodny_pusty, "dom_okno": zgodny_okno}

# Wspólne: style dokumentów i budowa rekordu /v1/systemone. Teksty piszą subagenci (PISZACY.md), odczyt sprawdzają sędziowie (SEDZIA.md);
# etykietę zawsze liczy kod z ukrytych faktów i parametrów reguły.

STYLE = {
    "zgloszenie_rodzica": "zgłoszenie szkody wpisane przez rodzica w formularzu internetowym ubezpieczyciela (pierwsza osoba, potocznie, bez wiedzy prawniczej)",
    "zgloszenie_wlasne": "zgłoszenie szkody napisane przez samego poszkodowanego w e-mailu do ubezpieczyciela (pierwsza osoba, potocznie)",
    "protokol_szkolny": "protokół powypadkowy szkoły sporządzony przez dyrektora lub nauczyciela (styl urzędowy, trzecia osoba)",
    "notatka_policji": "notatka urzędowa policjanta z interwencji (styl urzędowy, skróty typowe dla policji, trzecia osoba)",
    "karta_sor": "karta informacyjna z SOR (wywiad, badanie, rozpoznanie; styl medyczny, skróty lekarskie)",
    "oswiadczenie_swiadka": "oświadczenie świadka zdarzenia spisane na formularzu (pierwsza osoba, potocznie)",
    "notatka_likwidatora": "notatka likwidatora z rozmowy telefonicznej z poszkodowanym (trzecia osoba, zwięźle)",
}


def rekord(rid, group, family, regula, styl, tekst, pytania, meta, R):
    """pytania: {klucz: (instrukcja, opcje {klucz_opcji: opis}, gold)} – kolejność opcji losowana."""
    q = {}
    for k, (instr, opcje, gold) in pytania.items():
        assert gold in opcje, (gold, opcje)
        kl = list(opcje); R.shuffle(kl)
        q[k] = {"type": "choice", "instructions": instr, "criteria": {x: opcje[x] for x in kl}, "gold": gold}
    state = f"Fragment warunków ubezpieczenia:\n{regula}\n\nDokument w aktach sprawy ({STYLE[styl].split(' (')[0]}):\n{tekst}"
    return {"id": rid, "group": group, "family": family, "state": state, "questions": q, "meta": meta}



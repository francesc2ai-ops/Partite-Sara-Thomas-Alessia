#!/usr/bin/env python3
"""Genera data/sara.json, data/thomas.json, data/alessia.json dai calendari in data/."""
import json, re, subprocess
from datetime import date, datetime
from pathlib import Path
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
CASA_MANDELLO = ("Palestra Polifunzionale Ing. Luigi Buzzi", "Via Pra Magno 8, Mandello del Lario (LC)")

def bello(s):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    s = s.title()
    for a, b in [("'S", "'s"), ("Asd", "ASD"), (" Di ", " di "), (" Del ", " del "), (" Della ", " della "), (" Dello ", " dello "),
                 (" Degli ", " degli "), (" Al ", " al "), (" E ", " e "), ("Rasta'", "Rastà"), ("Barzano'", "Barzanò"), ("Xxiii", "XXIII"),
                 ("Paolo Vi", "Paolo VI"), ("Ics ", "ICS "), ("Gbg ", "GBG "), ("Pvv-Vavv", "PVV-VAVV"), ("Vavv", "VAVV"), ("V36", "V36"),
                 ("Ac ", "AC "), ("Gsv", "GSV"), ("Tml ", "TML "), ("Dao ", "DAO "), ("Duec", "DUEC"), ("Di.R.El.", "DI.R.EL."),
                 ("Pol.C.G.", "Pol. C.G."), ("G.S.Rast", "G.S. Rast"), ("G.S.Cagliero", "G.S. Cagliero"), ("Artigianelli-", "Artigianelli -")]:
        s = s.replace(a, b)
    s = re.sub(r"\b(Df|Bs|Bg|Lc|Co|Tn|Cr|Pg|V\.Bs)\b", lambda m: m.group(1).upper(), s)
    return s.replace("(PG) (PG)", "(PG)").replace("PG (PG)", "PG")

def scrivi(nome, partite, nota):
    partite.sort(key=lambda p: p["inizio"])
    out = {"_nota": nota, "partite": partite}
    (D / f"{nome}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(nome, len(partite), "partite")

# ---------- Alessia: Serie B2 F girone C (Excel FIPAV), squadra CARTIERA DELL'ADDA LC ----------
ws = load_workbook(D / "calendario_alessia_B2.xlsx", data_only=True)["Calendario"]
ale = []
for r in ws.iter_rows(values_only=True):
    if not isinstance(r[2], datetime) or not r[6]:
        continue
    casa_t, osp_t = str(r[6]), str(r[7])
    if "CARTIERA" not in (casa_t + osp_t).upper():
        continue
    in_casa = "CARTIERA" in casa_t.upper()
    impianto, _, via = str(r[4]).partition(" - ")
    citta = bello(r[5])
    if in_casa:
        campo, ind = CASA_MANDELLO
    else:
        campo = bello(impianto)
        via = re.sub(r"\s*-\s*$", "", via).strip(" -")
        ind = ", ".join(x for x in [bello(via.split(" - ")[0]), citta] if x)
    ale.append({"inizio": r[2].strftime("%Y-%m-%d") + "T" + r[3].strftime("%H:%M"), "casa": in_casa,
                "avversario": bello(osp_t if in_casa else casa_t), "campo": campo, "indirizzo": ind})
scrivi("alessia", ale, "Serie B2 femminile girone C, Cartiera dell'Adda (Mandello). Fonte: calendario FIPAV in Excel.")

# ---------- Sara: Serie D F (PDF della Polisportiva Mandello) ----------
txt = subprocess.run(["pdftotext", "-layout", str(D / "calendario_sara_serieD.pdf"), "-"], capture_output=True, text=True).stdout.splitlines()
# nomi palestre dal calendario FIPAV ufficiale (pagina Mandello Serie D), per data
fipav = {}
fj = Path("/home/claude/partite-mandello-serie-d-2026-2027/data/partite.json")
if fj.exists():
    for p in json.loads(fj.read_text())["partite"]:
        fipav[p["inizio"][:10]] = p
sara = []
for i, l in enumerate(txt):
    m = re.match(r"\s*(\d\d/\d\d/\d{4})\s{2,}(.+?)\s{2,}(.+?)\s*$", l)
    if not m:
        continue
    dstr, a, b = m.groups()
    d = datetime.strptime(dstr, "%d/%m/%Y").date()
    via = txt[i - 1].strip(); citta = txt[i + 1].strip()
    ora = next((re.search(r"ORE (\d\d:\d\d)", x).group(1) for x in txt[i + 1:i + 4] if "ORE" in x), "21:00")
    in_casa = "MANDELLO" in a.upper()
    f = fipav.get(d.isoformat())
    if in_casa:
        campo, ind = CASA_MANDELLO
    else:
        campo = bello(f["impianto"]) if f else "Palestra"
        via_ok = via.replace("E MIGRANTI", "EMIGRANTI")
        ind = bello(via_ok) + ", " + bello(citta)
    sara.append({"inizio": d.isoformat() + "T" + ora, "casa": in_casa, "avversario": bello(b if in_casa else a),
                 "campo": campo, "indirizzo": ind})
scrivi("sara", sara, "Serie D femminile girone C, Polisportiva Mandello. Fonte: calendario della società (PDF); nomi palestre dal calendario FIPAV.")

# ---------- Thomas: DR3 basket (PDF), squadra DC MANDELLO ----------
txt = subprocess.run(["pdftotext", "-layout", str(D / "calendario_thomas_DR3.pdf"), "-"], capture_output=True, text=True).stdout.splitlines()
tom = []
for i, l in enumerate(txt):
    m = re.match(r"\s*(\d+)\s+\w+\.?\s+(\d{1,2})/(\d{1,2})\s+–\s+(\d{1,2})\.(\d\d)\s{2,}(.+?)\s{2,}(.+?)\s{2,}(.*?)\s*$", l)
    if not m:
        continue
    g, gg, mm, hh, mi, a, b, ind = m.groups()
    gg, mm = int(gg), int(mm)
    anno = 2026 if mm >= 8 else 2027
    # indirizzo spezzato su due righe: riga sopra o sotto con solo testo nella colonna indirizzo
    pre = txt[i - 1].strip() if i > 0 and txt[i - 1].startswith(" " * 40) else ""
    post = txt[i + 1].strip() if i + 1 < len(txt) and txt[i + 1].startswith(" " * 40) and not re.search(r"\d+\s+\w+\.", txt[i + 1]) else ""
    ind = " ".join(x for x in [pre, ind, post] if x).strip()
    in_casa = "MANDELLO" in a.upper()
    if in_casa:
        campo, indir = CASA_MANDELLO
    else:
        parti = [x.strip() for x in ind.split(",")]
        if parti[0].lower().startswith(("pal", "scuole")):
            campo, indir = parti[0], ", ".join(parti[1:])
        else:
            campo, indir = "Palestra", ind
    tom.append({"inizio": f"{anno}-{mm:02d}-{gg:02d}T{int(hh):02d}:{mi}", "casa": in_casa,
                "avversario": (b if in_casa else a).strip(), "campo": campo, "indirizzo": indir})
scrivi("thomas", tom, "Serie DR3 basket, DC Mandello. Fonte: calendario provvisorio (PDF).")

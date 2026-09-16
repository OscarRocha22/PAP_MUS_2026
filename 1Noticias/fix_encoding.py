# Imports
from __future__ import annotations
import argparse
import glob
import re
from pathlib import Path
import ftfy
import pandas as pd

# Columns checked/repaired if present. Extend if your CSVs use other names.
TEXT_COLUMNS = ["texto", "titulo", "medio", "error"]

# Tras el paso de ftfy, cualquier "Ã"/"Â" restante ya es el residuo huérfano
# (el segundo byte se perdió río arriba), no un par mojibake sin corregir.
_LONE_A_TILDE = re.compile(r"Ã")
_LONE_A_CIRC = re.compile(r"Â")
_LONE_A_LOWER_CIRC = re.compile(r"â")  # comilla curva huérfana -> comilla recta
# ftfy a veces "arregla" el mismo residuo huérfano de otra forma, dejando
# "à" (con acento grave) en vez de "Ã". El español no usa acento grave en
# la "a", así que cualquier "à" en este corpus es, con certeza, el mismo
# residuo de "í" perdida.
_LONE_A_GRAVE = re.compile(r"à")


def reparar_texto(valor: str) -> str:
    """Applies ftfy's mojibake repair, then the two disclosed heuristics
    for the small residue that ftfy can't reconstruct because the second
    byte was already deleted upstream."""
    if not isinstance(valor, str) or not valor:
        return valor
    arreglado = ftfy.fix_text(valor)
    arreglado = _LONE_A_TILDE.sub("í", arreglado)
    arreglado = _LONE_A_CIRC.sub("", arreglado)
    arreglado = _LONE_A_LOWER_CIRC.sub('"', arreglado)
    arreglado = _LONE_A_GRAVE.sub("í", arreglado)
    return arreglado


def contar_artefactos(serie: pd.Series) -> int:
    s = serie.fillna("")
    return int(
        s.str.count("Ã").sum() + s.str.count("Â").sum()
        + s.str.count("â").sum() + s.str.count("à").sum()
    )


def procesar_archivo(ruta: Path) -> Path:
    df = pd.read_csv(ruta, dtype=str)
    columnas_presentes = [c for c in TEXT_COLUMNS if c in df.columns]
    if not columnas_presentes:
        print(f"  (sin columnas de texto reconocibles en {ruta.name}, se omite)")
        return ruta

    antes = sum(contar_artefactos(df[c]) for c in columnas_presentes)
    for col in columnas_presentes:
        df[col] = df[col].map(reparar_texto)
    despues = sum(contar_artefactos(df[c]) for c in columnas_presentes)

    salida = ruta.with_suffix(".corregido.csv")
    df.to_csv(salida, index=False)
    print(f"{ruta.name}: artefactos Ã/Â {antes} -> {despues}  ->  {salida.name}")
    return salida


def parse_args():
    p = argparse.ArgumentParser(description="Repara mojibake en CSVs de corpus ya descargados.")
    p.add_argument("archivos", nargs="*", help="Rutas de CSV a reparar")
    p.add_argument("--glob", dest="patron", help="Patrón glob alternativo, ej. 'salidas/*.csv'")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rutas = [Path(a) for a in args.archivos]
    if args.patron:
        rutas += [Path(p) for p in glob.glob(args.patron)]
    if not rutas:
        raise SystemExit("Da al menos un archivo CSV o --glob 'patrón/*.csv'")
    for ruta in rutas:
        procesar_archivo(ruta)
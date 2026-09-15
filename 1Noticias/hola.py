with open('./data/raw/Medios_MiBici(2026).csv', 'rb') as f:
    crudo = f.read()

print("tamaño en bytes:", len(crudo))
print("primeros 120 bytes:", crudo[:120])
print()

import pandas as pd
df = pd.read_csv('./data/raw/Medios_MiBici(2026).csv', dtype=str, encoding='utf-8-sig', sep=None, engine='python')
print("columnas detectadas:", repr(df.columns.tolist()))
print("forma (filas, columnas):", df.shape)
print()
print(df.head(3).to_string())
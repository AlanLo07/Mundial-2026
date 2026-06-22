from Mundial_2026_Standings import MundialTracker
from matriz495 import RAW

# Parse RAW into list of lists
matriz = []
for line in RAW.splitlines():
    line=line.strip()
    if not line:
        continue
    parts=line.split()
    # skip lines that are not starting with a number
    if not parts[0].isdigit():
        continue
    etiquetas=[p for p in parts[1:] if p.startswith('3')]
    if len(etiquetas)==8:
        matriz.append(etiquetas)

tracker = MundialTracker()
# registrar resultados (usar la función incluida si existe)
try:
    from Mundial_2026_Standings import registrar_resultados
    registrar_resultados()
except Exception:
    # si no existe, asumimos que el __main__ ya registró en el script
    pass

ok = tracker.set_matriz_list(matriz)
print('Matriz cargada:', ok, 'opciones cargadas=', len(tracker.matriz_terceros_list))
idx = tracker.encontrar_opcion_por_terceros_actuales()
print('Índice encontrado (0-based):', idx)
print('Opción encontrada (1-based):', idx+1 if idx is not None else None)

# Mostrar octavos (si se encontró, se aplicará)
tracker.mostrar_octavos_final()

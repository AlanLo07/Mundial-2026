import random
from collections import Counter

from equipo import Equipo, Jugador, Partido


def construir_equipo(configuracion):
    equipo = Equipo(configuracion['nombre'], configuracion.get('tactica', '4-4-2'))
    titulares = [
        Jugador(
            jugador['nombre'],
            jugador['posicion'],
            jugador['ataque'],
            jugador['defensa'],
            jugador['definicion'],
        )
        for jugador in configuracion.get('titulares', [])
    ]
    equipo.cargar_titulares(titulares)
    return equipo


def simular_partido_detallado(local, visitante, n_simulaciones=1000, minutos=90):
    resultados = []
    historial_marcadores = []
    historial_goleadores = Counter()
    ejemplo_partido = None

    for indice in range(n_simulaciones):
        partido = Partido(local, visitante, minutos=minutos)
        resumen = partido.simular_partido_completo(mostrar_resultado=False)
        marcador = (resumen['goles_local'], resumen['goles_visitante'])

        historial_marcadores.append(marcador)
        for goleador in resumen['goleadores']:
            historial_goleadores[goleador['jugador']] += 1

        if resumen['goles_local'] > resumen['goles_visitante']:
            resultados.append('Victoria Local')
        elif resumen['goles_local'] < resumen['goles_visitante']:
            resultados.append('Victoria Visitante')
        else:
            resultados.append('Empate')

        if ejemplo_partido is None or indice == 0:
            ejemplo_partido = resumen

    total = len(resultados)
    conteo_resultados = Counter(resultados)
    conteo_marcadores = Counter(historial_marcadores)

    return {
        'simulaciones': total,
        'probabilidades': {
            'local': round((conteo_resultados['Victoria Local'] / total) * 100, 2),
            'empate': round((conteo_resultados['Empate'] / total) * 100, 2),
            'visitante': round((conteo_resultados['Victoria Visitante'] / total) * 100, 2),
        },
        'marcadores_frecuentes': [
            {
                'marcador': marcador,
                'veces': veces,
                'porcentaje': round((veces / total) * 100, 2),
            }
            for marcador, veces in conteo_marcadores.most_common(5)
        ],
        'goleadores_frecuentes': [
            {
                'jugador': nombre,
                'veces': veces,
                'porcentaje': round((veces / total) * 100, 2),
            }
            for nombre, veces in historial_goleadores.most_common(5)
        ],
        'ejemplo_partido': ejemplo_partido,
    }


def simular_partido_detallado_desde_config(local_config, visitante_config, n_simulaciones=1000, minutos=90):
    equipo_local = construir_equipo(local_config)
    equipo_visitante = construir_equipo(visitante_config)
    return simular_partido_detallado(equipo_local, equipo_visitante, n_simulaciones=n_simulaciones, minutos=minutos)


def imprimir_resumen_simulacion(resultado, nombre_local, nombre_visitante):
    print(f"=== RESULTADOS DE {resultado['simulaciones']:,} SIMULACIONES MONTECARLO ===")
    print(f"Victoria {nombre_local}: {resultado['probabilidades']['local']:.2f}%")
    print(f"Empate:              {resultado['probabilidades']['empate']:.2f}%")
    print(f"Victoria {nombre_visitante}: {resultado['probabilidades']['visitante']:.2f}%")

    print("\n--- Top 5 Marcadores Más Frecuentes ---")
    for item in resultado['marcadores_frecuentes']:
        goles_local, goles_visitante = item['marcador']
        print(f"  Marcador: {goles_local} - {goles_visitante} | Ocurrió: {item['veces']} veces ({item['porcentaje']:.2f}%)")

    print("\n--- Top 5 Goleadores Más Frecuentes ---")
    if not resultado['goleadores_frecuentes']:
        print("  Sin goleadores registrados en la muestra")
    else:
        for item in resultado['goleadores_frecuentes']:
            print(f"  {item['jugador']}: {item['veces']} partidos ({item['porcentaje']:.2f}%)")


if __name__ == '__main__':
    local_config = {
        'nombre': 'Local',
        'tactica': '4-3-3',
        'titulares': [
            {'nombre': 'POR L', 'posicion': 'POR', 'ataque': 20, 'defensa': 78, 'definicion': 5},
            {'nombre': 'DEF L1', 'posicion': 'DEF', 'ataque': 35, 'defensa': 75, 'definicion': 20},
            {'nombre': 'DEF L2', 'posicion': 'DEF', 'ataque': 34, 'defensa': 74, 'definicion': 18},
            {'nombre': 'DEF L3', 'posicion': 'DEF', 'ataque': 33, 'defensa': 73, 'definicion': 19},
            {'nombre': 'DEF L4', 'posicion': 'DEF', 'ataque': 32, 'defensa': 72, 'definicion': 17},
            {'nombre': 'MED L1', 'posicion': 'MED', 'ataque': 72, 'defensa': 60, 'definicion': 45},
            {'nombre': 'MED L2', 'posicion': 'MED', 'ataque': 70, 'defensa': 58, 'definicion': 42},
            {'nombre': 'MED L3', 'posicion': 'MED', 'ataque': 68, 'defensa': 57, 'definicion': 40},
            {'nombre': 'DEL L1', 'posicion': 'DEL', 'ataque': 82, 'defensa': 30, 'definicion': 78},
            {'nombre': 'DEL L2', 'posicion': 'DEL', 'ataque': 80, 'defensa': 28, 'definicion': 74},
            {'nombre': 'DEL L3', 'posicion': 'DEL', 'ataque': 79, 'defensa': 29, 'definicion': 72},
        ],
    }

    visitante_config = {
        'nombre': 'Visitante',
        'tactica': '4-4-2',
        'titulares': [
            {'nombre': 'POR V', 'posicion': 'POR', 'ataque': 20, 'defensa': 76, 'definicion': 5},
            {'nombre': 'DEF V1', 'posicion': 'DEF', 'ataque': 34, 'defensa': 74, 'definicion': 18},
            {'nombre': 'DEF V2', 'posicion': 'DEF', 'ataque': 35, 'defensa': 75, 'definicion': 20},
            {'nombre': 'DEF V3', 'posicion': 'DEF', 'ataque': 33, 'defensa': 73, 'definicion': 19},
            {'nombre': 'DEF V4', 'posicion': 'DEF', 'ataque': 32, 'defensa': 72, 'definicion': 17},
            {'nombre': 'MED V1', 'posicion': 'MED', 'ataque': 69, 'defensa': 59, 'definicion': 41},
            {'nombre': 'MED V2', 'posicion': 'MED', 'ataque': 67, 'defensa': 57, 'definicion': 39},
            {'nombre': 'MED V3', 'posicion': 'MED', 'ataque': 66, 'defensa': 56, 'definicion': 38},
            {'nombre': 'MED V4', 'posicion': 'MED', 'ataque': 64, 'defensa': 55, 'definicion': 36},
            {'nombre': 'DEL V1', 'posicion': 'DEL', 'ataque': 78, 'defensa': 28, 'definicion': 71},
            {'nombre': 'DEL V2', 'posicion': 'DEL', 'ataque': 76, 'defensa': 27, 'definicion': 69},
        ],
    }

    resultado = simular_partido_detallado_desde_config(local_config, visitante_config, n_simulaciones=1000)
    imprimir_resumen_simulacion(resultado, local_config['nombre'], visitante_config['nombre'])
    print(resultado['ejemplo_partido'])
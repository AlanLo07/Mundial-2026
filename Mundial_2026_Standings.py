#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de seguimiento del Mundial 2026
"""

from collections import defaultdict
from datetime import datetime
from hashlib import sha256
import random

from equipo import Equipo, Jugador, Partido
from datos_selecciones import SELECCIONES_REALES


class MundialTracker:
    def __init__(self):
        # Estructura de grupos del Mundial 2026
        self.grupos = {
            'A': ['México', 'Corea del Sur', 'Chequia', 'Sudáfrica'],
            'B': ['Canadá', 'Suiza', 'Boznia Herzegovina', 'Qatar'],
            'C': ['Brasil', 'Marruecos', 'Escocia', 'Haití'],
            'D': ['Estados Unidos', 'Australia', 'Paraguay', 'Turquía'],
            'E': ['Alemania', 'Costa de Marfil', 'Ecuador', 'Curacao'],
            'F': ['Suecia', 'Japón', 'Paises Bajos', 'Túnez'],
            'G': ['Nueva Zelanda', 'Irán', 'Bélgica', 'Egipto'],
            'H': ['Uruguay', 'Arabia Saudí', 'España', 'Cabo Verde'],
            'I': ['Noruega', 'Francia', 'Senegal', 'Irak'],
            'J': ['Argentina', 'Austria', 'Jordania', 'Argelia'],
            'K': ['Colombia', 'Congo', 'Portugal', 'Uzbekistán'],
            'L': ['Inglaterra', 'Ghana', 'Panamá', 'Croacia']
        }
        
        # Estadísticas por equipo
        self.stats = {}
        self._inicializar_stats()
        
        # Historial de partidos
        self.partidos = []
        # Matriz de combinaciones de mejores terceros (opción_number -> list de 8 etiquetas)
        self.matriz_terceros = {}
        # Opción seleccionada (int) para asignar terceros explícitamente
        self.terceros_opcion = None
        # Matriz como lista de opciones (lista de listas), p.ej. 495 combinaciones
        self.matriz_terceros_list = []
        # Índice (0-based) de la opción encontrada al buscar según terceros actuales
        self.matriz_terceros_matched_index = None
    
    def _inicializar_stats(self):
        """Inicializa las estadísticas de todos los equipos"""
        for grupo, equipos in self.grupos.items():
            for equipo in equipos:
                self.stats[equipo] = {
                    'grupo': grupo,
                    'pj': 0,  # Partidos jugados
                    'pg': 0,  # Partidos ganados
                    'pe': 0,  # Partidos empatados
                    'pp': 0,  # Partidos perdidos
                    'gf': 0,  # Goles a favor
                    'gc': 0,  # Goles en contra
                    'dg': 0,  # Diferencia de goles
                    'pts': 0,  # Puntos
                    'tarjetas_amarillas': 0,  # Conducta deportiva
                    'tarjetas_rojas_dobles': 0,  # Tarjetas rojas por doble amonestación
                    'tarjetas_rojas_directas': 0,  # Tarjetas rojas directas
                    'puntos_conducta': 0  # Puntos por conducta deportiva
                }
    
    def registrar_partido(self, equipo_local, goles_local, equipo_visitante, goles_visitante, 
                         amarillas_local=None, amarillas_visitante=None, 
                         rojas_dobles_local=None, rojas_dobles_visitante=None,
                         rojas_directas_local=None, rojas_directas_visitante=None):
        """Registra un resultado de partido y actualiza estadísticas
        
        Parámetros opcionales para tarjetas (conducta deportiva):
        - amarillas_local/visitante: cantidad de tarjetas amarillas
        - rojas_dobles_local/visitante: cantidad de tarjetas rojas por doble amonestación
        - rojas_directas_local/visitante: cantidad de tarjetas rojas directas
        """
        
        # Validar que los equipos existan
        if equipo_local not in self.stats or equipo_visitante not in self.stats:
            print(f"❌ Error: Uno de los equipos no existe")
            return False
        
        # Validar que sean del mismo grupo
        if self.stats[equipo_local]['grupo'] != self.stats[equipo_visitante]['grupo']:
            print(f"❌ Error: Los equipos no pertenecen al mismo grupo")
            return False
        
        # Valores por defecto para tarjetas
        amarillas_local = amarillas_local or 0
        amarillas_visitante = amarillas_visitante or 0
        rojas_dobles_local = rojas_dobles_local or 0
        rojas_dobles_visitante = rojas_dobles_visitante or 0
        rojas_directas_local = rojas_directas_local or 0
        rojas_directas_visitante = rojas_directas_visitante or 0
        
        # Registrar partido
        self.partidos.append({
            'local': equipo_local,
            'goles_local': goles_local,
            'visitante': equipo_visitante,
            'goles_visitante': goles_visitante,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'amarillas_local': amarillas_local,
            'amarillas_visitante': amarillas_visitante,
            'rojas_dobles_local': rojas_dobles_local,
            'rojas_dobles_visitante': rojas_dobles_visitante,
            'rojas_directas_local': rojas_directas_local,
            'rojas_directas_visitante': rojas_directas_visitante
        })
        
        # Actualizar estadísticas de tarjetas
        self.stats[equipo_local]['tarjetas_amarillas'] += amarillas_local
        self.stats[equipo_local]['tarjetas_rojas_dobles'] += rojas_dobles_local
        self.stats[equipo_local]['tarjetas_rojas_directas'] += rojas_directas_local
        
        self.stats[equipo_visitante]['tarjetas_amarillas'] += amarillas_visitante
        self.stats[equipo_visitante]['tarjetas_rojas_dobles'] += rojas_dobles_visitante
        self.stats[equipo_visitante]['tarjetas_rojas_directas'] += rojas_directas_visitante
        
        # Calcular puntos por conducta
        self._actualizar_puntos_conducta()
        
        # Actualizar estadísticas de goles
        # Equipo local
        self.stats[equipo_local]['pj'] += 1
        self.stats[equipo_local]['gf'] += goles_local
        self.stats[equipo_local]['gc'] += goles_visitante
        
        # Equipo visitante
        self.stats[equipo_visitante]['pj'] += 1
        self.stats[equipo_visitante]['gf'] += goles_visitante
        self.stats[equipo_visitante]['gc'] += goles_local
        
        # Determinar ganador y actualizar puntos
        if goles_local > goles_visitante:
            self.stats[equipo_local]['pg'] += 1
            self.stats[equipo_local]['pts'] += 3
            self.stats[equipo_visitante]['pp'] += 1
        elif goles_visitante > goles_local:
            self.stats[equipo_visitante]['pg'] += 1
            self.stats[equipo_visitante]['pts'] += 3
            self.stats[equipo_local]['pp'] += 1
        else:
            self.stats[equipo_local]['pe'] += 1
            self.stats[equipo_local]['pts'] += 1
            self.stats[equipo_visitante]['pe'] += 1
            self.stats[equipo_visitante]['pts'] += 1
        
        # Actualizar diferencia de goles
        self.stats[equipo_local]['dg'] = self.stats[equipo_local]['gf'] - self.stats[equipo_local]['gc']
        self.stats[equipo_visitante]['dg'] = self.stats[equipo_visitante]['gf'] - self.stats[equipo_visitante]['gc']
        
        print(f"✅ Partido registrado: {equipo_local} {goles_local} - {goles_visitante} {equipo_visitante}")
        return True
    
    def _actualizar_puntos_conducta(self):
        """Recalcula los puntos por conducta deportiva de todos los equipos"""
        for equipo in self.stats:
            amarillas = self.stats[equipo]['tarjetas_amarillas']
            rojas_dobles = self.stats[equipo]['tarjetas_rojas_dobles']
            rojas_directas = self.stats[equipo]['tarjetas_rojas_directas']
            
            puntos = 0
            puntos -= amarillas * 1
            puntos -= rojas_dobles * 3
            puntos -= rojas_directas * 4
            
            self.stats[equipo]['puntos_conducta'] = puntos
    
    def _obtener_partidos_entre_equipos(self, equipos_grupo):
        """Obtiene los partidos jugados entre equipos específicos del mismo grupo"""
        partidos_entre = []
        equipos_set = set(equipos_grupo)
        
        for partido in self.partidos:
            if partido['local'] in equipos_set and partido['visitante'] in equipos_set:
                partidos_entre.append(partido)
        
        return partidos_entre
    
    def _calcular_stats_entre_equipos(self, equipos, partidos):
        """Calcula estadísticas entre equipos específicos"""
        stats_entre = {}
        
        for equipo in equipos:
            stats_entre[equipo] = {
                'pts': 0,
                'dg': 0,
                'gf': 0,
                'gc': 0,
                'pj': 0
            }
        
        for partido in partidos:
            local = partido['local']
            visitante = partido['visitante']
            gl = partido['goles_local']
            gv = partido['goles_visitante']
            
            # Actualizar goles
            stats_entre[local]['gf'] += gl
            stats_entre[local]['gc'] += gv
            stats_entre[visitante]['gf'] += gv
            stats_entre[visitante]['gc'] += gl
            stats_entre[local]['pj'] += 1
            stats_entre[visitante]['pj'] += 1
            
            # Actualizar puntos
            if gl > gv:
                stats_entre[local]['pts'] += 3
            elif gv > gl:
                stats_entre[visitante]['pts'] += 3
            else:
                stats_entre[local]['pts'] += 1
                stats_entre[visitante]['pts'] += 1
            
            # Diferencia de goles
            stats_entre[local]['dg'] = stats_entre[local]['gf'] - stats_entre[local]['gc']
            stats_entre[visitante]['dg'] = stats_entre[visitante]['gf'] - stats_entre[visitante]['gc']
        
        return stats_entre
    
    def _aplicar_criterios_desempate(self, equipos_empatados):
        """Aplica los criterios de desempate FIFA para equipos con los mismos puntos
        
        Criterios por orden:
        1. Diferencia de goles en partidos entre ellos
        2. Goles marcados en partidos entre ellos
        3. Diferencia de goles en todos los partidos
        4. Goles marcados en todos los partidos
        5. Puntos por conducta deportiva
        """
        
        if len(equipos_empatados) <= 1:
            return equipos_empatados
        
        # Obtener grupo de los equipos
        grupo = self.stats[equipos_empatados[0]]['grupo']
        
        # Primer paso: Partidos entre ellos
        partidos_entre = self._obtener_partidos_entre_equipos(equipos_empatados)
        
        if partidos_entre:
            stats_entre = self._calcular_stats_entre_equipos(equipos_empatados, partidos_entre)
            
            # Ordenar por: pts en partidos entre ellos, dg entre ellos, gf entre ellos
            equipos_ordenados = sorted(equipos_empatados, key=lambda x: (
                -stats_entre[x]['pts'],
                -stats_entre[x]['dg'],
                -stats_entre[x]['gf']
            ))
            
            # Si el primero se diferencia claramente, lo dejamos
            if stats_entre[equipos_ordenados[0]]['pts'] > stats_entre[equipos_ordenados[1]]['pts']:
                return [equipos_ordenados[0]] + self._aplicar_criterios_desempate(equipos_ordenados[1:])
            
            if stats_entre[equipos_ordenados[0]]['dg'] != stats_entre[equipos_ordenados[1]]['dg']:
                return [equipos_ordenados[0]] + self._aplicar_criterios_desempate(equipos_ordenados[1:])
            
            if stats_entre[equipos_ordenados[0]]['gf'] != stats_entre[equipos_ordenados[1]]['gf']:
                return [equipos_ordenados[0]] + self._aplicar_criterios_desempate(equipos_ordenados[1:])
        
        # Segundo paso: Todos los partidos (dg general, gf general, conducta)
        equipos_ordenados = sorted(equipos_empatados, key=lambda x: (
            -self.stats[x]['dg'],
            -self.stats[x]['gf'],
            -self.stats[x]['puntos_conducta']  # Mayor (menos negativo) es mejor
        ))
        
        return equipos_ordenados
    
    def mostrar_posiciones(self, grupo=None):
        """Muestra las posiciones de un grupo o todos los grupos"""
        
        if grupo:
            self._mostrar_grupo(grupo)
        else:
            for g in sorted(self.grupos.keys()):
                self._mostrar_grupo(g)
                print()
    
    def _mostrar_grupo(self, grupo):
        """Muestra las posiciones de un grupo específico"""
        
        if grupo not in self.grupos:
            print(f"❌ Grupo {grupo} no existe")
            return
        
        # Obtener equipos del grupo
        equipos = self.grupos[grupo]
        
        # Primero, agrupar equipos por puntos
        equipos_por_puntos = defaultdict(list)
        for equipo in equipos:
            puntos = self.stats[equipo]['pts']
            equipos_por_puntos[puntos].append(equipo)
        
        # Aplicar criterios de desempate para cada grupo de puntos
        equipos_sorted = []
        for puntos in sorted(equipos_por_puntos.keys(), reverse=True):
            equipos_con_puntos = equipos_por_puntos[puntos]
            equipos_desempatados = self._aplicar_criterios_desempate(equipos_con_puntos)
            equipos_sorted.extend(equipos_desempatados)
        
        print(f"\n{'='*80}")
        print(f"GRUPO {grupo}")
        print(f"{'='*80}")
        print(f"{'POS':<5} {'EQUIPO':<25} {'PJ':<4} {'PG':<4} {'PE':<4} {'PP':<4} {'GF':<4} {'GC':<4} {'DG':<4} {'PTS':<4}")
        print(f"{'-'*80}")
        
        for pos, equipo in enumerate(equipos_sorted, 1):
            s = self.stats[equipo]
            print(f"{pos:<5} {equipo:<25} {s['pj']:<4} {s['pg']:<4} {s['pe']:<4} {s['pp']:<4} {s['gf']:<4} {s['gc']:<4} {s['dg']:<4} {s['pts']:<4}")
    
    def mostrar_historial_partidos(self, grupo=None):
        """Muestra el historial de partidos"""
        
        if not self.partidos:
            print("❌ No hay partidos registrados")
            return
        
        print(f"\n{'='*80}")
        print("HISTORIAL DE PARTIDOS")
        print(f"{'='*80}")
        
        for partido in self.partidos:
            if grupo is None or self.stats[partido['local']]['grupo'] == grupo:
                print(f"{partido['fecha']} | {partido['local']:<25} {partido['goles_local']} - {partido['goles_visitante']} {partido['visitante']:<25}")
    
    def _obtener_clasificados_grupo(self, grupo):
        """Obtiene los dos primeros clasificados de un grupo con su posición"""
        
        equipos = self.grupos[grupo]
        
        # Agrupar por puntos y desempatar
        equipos_por_puntos = defaultdict(list)
        for equipo in equipos:
            puntos = self.stats[equipo]['pts']
            equipos_por_puntos[puntos].append(equipo)
        
        equipos_sorted = []
        for puntos in sorted(equipos_por_puntos.keys(), reverse=True):
            equipos_con_puntos = equipos_por_puntos[puntos]
            equipos_desempatados = self._aplicar_criterios_desempate(equipos_con_puntos)
            equipos_sorted.extend(equipos_desempatados)
        
        # Retorna los dos primeros con etiquetas (ej: A1, A2)
        return [
            {
                'equipo': equipos_sorted[0],
                'etiqueta': f"{grupo}1",
                'pts': self.stats[equipos_sorted[0]]['pts'],
                'dg': self.stats[equipos_sorted[0]]['dg'],
                'gf': self.stats[equipos_sorted[0]]['gf'],
                'conducta': self.stats[equipos_sorted[0]]['puntos_conducta']
            },
            {
                'equipo': equipos_sorted[1],
                'etiqueta': f"{grupo}2",
                'pts': self.stats[equipos_sorted[1]]['pts'],
                'dg': self.stats[equipos_sorted[1]]['dg'],
                'gf': self.stats[equipos_sorted[1]]['gf'],
                'conducta': self.stats[equipos_sorted[1]]['puntos_conducta']
            }
        ]
    
    def _obtener_tercer_lugar(self, grupo):
        """Obtiene el tercer clasificado de un grupo"""
        
        equipos = self.grupos[grupo]
        
        # Agrupar por puntos y desempatar
        equipos_por_puntos = defaultdict(list)
        for equipo in equipos:
            puntos = self.stats[equipo]['pts']
            equipos_por_puntos[puntos].append(equipo)
        
        equipos_sorted = []
        for puntos in sorted(equipos_por_puntos.keys(), reverse=True):
            equipos_con_puntos = equipos_por_puntos[puntos]
            equipos_desempatados = self._aplicar_criterios_desempate(equipos_con_puntos)
            equipos_sorted.extend(equipos_desempatados)
        
        return {
            'equipo': equipos_sorted[2],
            'grupo': grupo,
            'pts': self.stats[equipos_sorted[2]]['pts'],
            'dg': self.stats[equipos_sorted[2]]['dg'],
            'gf': self.stats[equipos_sorted[2]]['gf'],
            'conducta': self.stats[equipos_sorted[2]]['puntos_conducta']
        }
    
    def obtener_clasificados_octavos(self):
        """Obtiene los clasificados para octavos de final:
        - Los 2 primeros de cada grupo (A1, A2, B1, B2, ...)
        - Los 8 mejores terceros lugares ordenados por criterios FIFA"""
        
        clasificados = {
            'primeros_y_segundos': [],
            'terceros_seleccionados': []
        }
        
        # Obtener los 2 primeros de cada grupo
        for grupo in sorted(self.grupos.keys()):
            clasificados_grupo = self._obtener_clasificados_grupo(grupo)
            clasificados['primeros_y_segundos'].extend(clasificados_grupo)
        
        # Obtener todos los terceros lugares
        todos_terceros = []
        for grupo in sorted(self.grupos.keys()):
            tercero = self._obtener_tercer_lugar(grupo)
            todos_terceros.append(tercero)
        
        # Agrupar terceros por puntos para aplicar criterios de desempate
        terceros_por_puntos = defaultdict(list)
        for tercero in todos_terceros:
            puntos = tercero['pts']
            terceros_por_puntos[puntos].append(tercero['equipo'])
        
        # Desempatar terceros lugares
        terceros_desempatados = []
        for puntos in sorted(terceros_por_puntos.keys(), reverse=True):
            equipos_con_puntos = terceros_por_puntos[puntos]
            equipos_desempatados = self._aplicar_criterios_desempate(equipos_con_puntos)
            
            for equipo in equipos_desempatados:
                # Buscar los datos del tercero
                tercero_data = next(t for t in todos_terceros if t['equipo'] == equipo)
                terceros_desempatados.append(tercero_data)

        
        # Seleccionar los 8 mejores terceros
        for tercero in terceros_desempatados[:8]:
            tercero['etiqueta'] = f"{tercero['grupo']}3"
            clasificados['terceros_seleccionados'].append(tercero)
        
        return clasificados
    
    def mostrar_clasificados_octavos(self):
        """Muestra los equipos clasificados para octavos de final"""
        
        clasificados = self.obtener_clasificados_octavos()
        
        print(f"\n{'='*80}")
        print("CLASIFICADOS A OCTAVOS DE FINAL")
        print(f"{'='*80}\n")
        
        # Mostrar primeros y segundos
        print("PRIMEROS Y SEGUNDOS DE GRUPO:")
        print(f"{'ETIQUETA':<10} {'EQUIPO':<25} {'PTS':<4} {'DG':<4} {'GF':<4} {'COND.':<6}")
        print("-" * 80)
        for clasificado in clasificados['primeros_y_segundos']:
            cond = clasificado['conducta'] if clasificado['conducta'] < 0 else 0
            print(f"{clasificado['etiqueta']:<10} {clasificado['equipo']:<25} {clasificado['pts']:<4} {clasificado['dg']:<4} {clasificado['gf']:<4} {cond:<6}")
        
        # Mostrar terceros seleccionados
        print(f"\n{'='*80}")
        print("8 MEJORES TERCEROS LUGARES:")
        print(f"{'ETIQUETA':<10} {'EQUIPO':<25} {'GRUPO':<7} {'PTS':<4} {'DG':<4} {'GF':<4} {'COND.':<6}")
        print("-" * 80)
        for tercero in clasificados['terceros_seleccionados']:
            cond = tercero['conducta'] if tercero['conducta'] < 0 else 0
            print(f"{tercero['etiqueta']:<10} {tercero['equipo']:<25} {tercero['grupo']:<7} {tercero['pts']:<4} {tercero['dg']:<4} {tercero['gf']:<4} {cond:<6}")
        
        print(f"\n{'='*80}")
        print("TOTAL: 16 EQUIPOS CLASIFICADOS A OCTAVOS DE FINAL")
        print(f"{'='*80}\n")
        print("Leyenda:")
        print("  PTS = Puntos | DG = Diferencia de goles | GF = Goles a favor")
        print("  COND. = Puntos por conducta (si es negativo indica descuentos por tarjetas)")
        print(f"{'='*80}")
    
    def _obtener_equipo_clasificado(self, etiqueta):
        """Obtiene el equipo clasificado por su etiqueta (ej: A1, 2A, B2, 1I)
        
        Acepta ambos formatos:
        - Formato estándar: A1, B2, C3 (grupo + posición)
        - Formato alternativo: 1A, 2B, 3C (posición + grupo)
        """
        clasificados = self.obtener_clasificados_octavos()
        
        # Convertir formato alternativo (2A) a estándar (A2)
        if len(etiqueta) == 2 and etiqueta[0].isdigit():
            etiqueta = etiqueta[1] + etiqueta[0]  # Cambiar '2A' a 'A2'
        
        # Buscar en primeros y segundos
        for clasificado in clasificados['primeros_y_segundos']:
            if clasificado['etiqueta'] == etiqueta:
                return clasificado['equipo']
        
        # Buscar en terceros
        for tercero in clasificados['terceros_seleccionados']:
            if tercero['etiqueta'] == etiqueta:
                return tercero['equipo']
        
        return None
    
    def _obtener_mejor_tercero_de(self, grupos):
        """Obtiene el mejor tercero lugar entre los grupos especificados
        
        Parámetros:
        grupos: string con letras de grupos (ej: 'ABCDF')
        
        Retorna: etiqueta del tercer lugar (ej: 'C3') o None si no existe
        """
        clasificados = self.obtener_clasificados_octavos()
        terceros = clasificados['terceros_seleccionados']
        
        # Buscar terceros de los grupos especificados en el orden en que aparecen en terceros_seleccionados
        for tercero in terceros:
            if tercero['grupo'] in grupos:
                return tercero['etiqueta']
        
        return None

    def cargar_matriz_desde_texto(self, texto):
        """Carga la matriz de combinaciones desde un texto con líneas.

        Formato esperado por línea:
        <num> <3X> <3Y> <3Z> <3...> (8 etiquetas de tercero separadas por espacios)
        Ejemplo: "1 3E 3J 3I 3F 3H 3G 3L 3K"
        """
        matriz = {}
        for line in texto.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            # Línea válida debe empezar con un número y luego 8 tokens
            try:
                num = int(parts[0])
            except Exception:
                continue
            etiquetas = [p for p in parts[1:] if p.startswith('3')]
            if len(etiquetas) >= 8:
                matriz[num] = etiquetas[:8]
        self.matriz_terceros = matriz
        return matriz

    def set_matriz_list(self, matriz_list):
        """Carga la matriz proporcionada como lista de opciones.

        Cada opción debe ser una lista/tupla de 8 etiquetas de terceros (ej '3E' o 'E3').
        """
        # Validar formato básico
        valid = True
        for opt in matriz_list:
            if not isinstance(opt, (list, tuple)) or len(opt) != 8:
                valid = False
                break
        if not valid:
            print("❌ Matriz inválida: cada opción debe ser una lista/tupla de 8 etiquetas")
            return False
        self.matriz_terceros_list = [list(opt) for opt in matriz_list]
        self.matriz_terceros_matched_index = None
        return True

    def _normalizar_etiqueta_3X(self, etiqueta):
        """Normaliza etiquetas a formato '3X' (digito primero), independientemente de 'X3' o '3X'."""
        if not etiqueta or len(etiqueta) != 2:
            return etiqueta
        a, b = etiqueta[0], etiqueta[1]
        if a == '3' and b.isalpha():
            return etiqueta.upper()
        if b == '3' and a.isalpha():
            return ('3' + a).upper()
        # Fallback: return upper
        return etiqueta.upper()

    def encontrar_opcion_por_terceros_actuales(self):
        """Busca en `matriz_terceros_list` la opción cuyo conjunto de 8 etiquetas
        coincide exactamente con los 8 mejores terceros actuales. Retorna índice 0-based o None.
        """
        if not self.matriz_terceros_list:
            return None

        clasificados = self.obtener_clasificados_octavos()
        terceros = [t['etiqueta'] for t in clasificados['terceros_seleccionados']]
        # Normalizar a formato '3X'
        terceros_norm = {self._normalizar_etiqueta_3X(t) for t in terceros}

        for idx, opcion in enumerate(self.matriz_terceros_list):
            opcion_norm = {self._normalizar_etiqueta_3X(tag) for tag in opcion}
            if opcion_norm == terceros_norm:
                self.matriz_terceros_matched_index = idx
                # Guardar también en el dict de compatibilidad (1-based)
                self.matriz_terceros[idx + 1] = [self._normalizar_etiqueta_3X(t) for t in opcion]
                return idx

        self.matriz_terceros_matched_index = None
        return None

    def set_opcion_terceros(self, opcion_num):
        """Selecciona la opción (número) de la matriz para usar en octavos."""
        if opcion_num is None:
            self.terceros_opcion = None
            return True
        if opcion_num not in self.matriz_terceros:
            print(f"❌ Opción {opcion_num} no encontrada en la matriz de terceros")
            return False
        self.terceros_opcion = opcion_num
        return True
    
    def generar_octavos_final(self):
        """Genera los 16 partidos de octavos de final según el esquema FIFA 2026"""
        
        octavos = []
        print("Inicio")
        # Definición de los 16 partidos según el esquema FIFA
        partidos_config = [
            # (número, equipo_a, equipo_b, descripción)
            (73, '2A', '2B', 'Segunda A vs Segunda B'),
            (74, '1E', self.matriz_terceros[opcion_num][3], 'Ganadora E vs Mejor 3ro ABCDF'),
            (75, '1F', '2C', 'Ganadora F vs Segunda C'),
            (76, '1C', '2F', 'Ganadora C vs Segunda F'),
            (77, '1I', self.matriz_terceros[opcion_num][5], 'Ganadora I vs Mejor 3ro CDFGH'),
            (78, '2E', '2I', 'Segunda E vs Segunda I'),
            (79, '1A', self.matriz_terceros[opcion_num][0], 'Ganadora A vs Mejor 3ro CEFHI'),
            (80, '1L', self.matriz_terceros[opcion_num][7], 'Ganadora L vs Mejor 3ro EHIJK'),
            (81, '1D', self.matriz_terceros[opcion_num][2], 'Primera D vs Mejor 3ro BEFIJ'),
            (82, '1G', self.matriz_terceros[opcion_num][4], 'Ganadora G vs Mejor 3ro AEHIJ'),
            (83, '2K', '2L', 'Segunda K vs Segunda L'),
            (84, '1H', '2J', 'Ganadora H vs Segunda J'),
            (85, '1B', self.matriz_terceros[opcion_num][1], 'Ganadora B vs Mejor 3ro EFGIJ'),
            (86, '1J', '2H', 'Ganadora J vs Segunda H'),
            (87, '1K', self.matriz_terceros[opcion_num][6], 'Ganadora K vs Mejor 3ro DEIJL'),
            (88, '2D', '2G', 'Segunda D vs Segunda G'),
        ]
        # Si el usuario ha cargado una matriz y seleccionado una opción, usarla
        # Prioridad 1: si hay matriz_list, intentar encontrar la opción que coincide
        if self.matriz_terceros_list:
            print("Intentando encontrar opción en matriz_list...")
            found_idx = self.encontrar_opcion_por_terceros_actuales()
            if found_idx is not None:
                # Usar la opción encontrada (lista normalizada en self.matriz_terceros[found_idx+1])
                opcion_etiquetas = self.matriz_terceros[found_idx + 1]
                # Mapeo por orden de winners: 1A,1B,1D,1E,1G,1I,1K,1L
                winners_order = ['1A','1B','1D','1E','1G','1I','1K','1L']
                # Construir un dict mapping winner -> etiqueta tercero (en formato '3X')
                winner_to_tercero = {winners_order[i]: opcion_etiquetas[i] for i in range(8)}
                # Reutilizar partidos_config base y reemplazar los oponentes correspondientes
                partidos_config = [
                    (73, '2A', '2B', 'Segunda A vs Segunda B'),
                    (74, '1E', self.matriz_terceros[opcion_num][3], 'Ganadora E vs Mejor 3ro'),
                    (75, '1F', '2C', 'Ganadora F vs Segunda C'),
                    (76, '1C', '2F', 'Ganadora C vs Segunda F'),
                    (77, '1I', self.matriz_terceros[opcion_num][5], 'Ganadora I vs Mejor 3ro'),
                    (78, '2E', '2I', 'Segunda E vs Segunda I'),
                    (79, '1A', self.matriz_terceros[opcion_num][0], 'Ganadora A vs Mejor 3ro'),
                    (80, '1L', self.matriz_terceros[opcion_num][7], 'Ganadora L vs Mejor 3ro'),
                    (81, '1D', self.matriz_terceros[opcion_num][2], 'Primera D vs Mejor 3ro'),
                    (82, '1G', self.matriz_terceros[opcion_num][4], 'Ganadora G vs Mejor 3ro'),
                    (83, '2K', '2L', 'Segunda K vs Segunda L'),
                    (84, '1H', '2J', 'Ganadora H vs Segunda J'),
                    (85, '1B', self.matriz_terceros[opcion_num][1], 'Ganadora B vs Mejor 3ro'),
                    (86, '1J', '2H', 'Ganadora J vs Segunda H'),
                    (87, '1K', self.matriz_terceros[opcion_num][6], 'Ganadora K vs Mejor 3ro'),
                    (88, '2D', '2G', 'Segunda D vs Segunda G'),
                ]
            else:
                # No se encontró opción exacta; seguir con otras lógicas
                pass
        if self.terceros_opcion and self.terceros_opcion in self.matriz_terceros:
            print("Usando opción seleccionada por el usuario en matriz_terceros...")
            # Orden de partidos que requieren un mejor tercero
            partidos_con_terceros = [74, 77, 79, 80, 81, 82, 85, 87]
            terceros_etiquetas = self.matriz_terceros[self.terceros_opcion]
            # Mapear match number -> etiqueta de tercero
            mapping_terceros = {partidos_con_terceros[i]: terceros_etiquetas[i] for i in range(len(partidos_con_terceros))}
            partidos_config = [
                (73, '2A', '2B', 'Segunda A vs Segunda B'),
                (74, '1E', self.matriz_terceros[self.terceros_opcion][3], 'Ganadora E vs Mejor 3ro ABCDF'),
                (75, '1F', '2C', 'Ganadora F vs Segunda C'),
                (76, '1C', '2F', 'Ganadora C vs Segunda F'),
                (77, '1I', self.matriz_terceros[self.terceros_opcion][5], 'Ganadora I vs Mejor 3ro CDFGH'),
                (78, '2E', '2I', 'Segunda E vs Segunda I'),
                (79, '1A', self.matriz_terceros[self.terceros_opcion][0], 'Ganadora A vs Mejor 3ro CEFHI'),
                (80, '1L', self.matriz_terceros[self.terceros_opcion][7], 'Ganadora L vs Mejor 3ro EHIJK'),
                (81, '1D', self.matriz_terceros[self.terceros_opcion][2], 'Primera D vs Mejor 3ro BEFIJ'),
                (82, '1G', self.matriz_terceros[self.terceros_opcion][4], 'Ganadora G vs Mejor 3ro AEHIJ'),
                (83, '2K', '2L', 'Segunda K vs Segunda L'),
                (84, '1H', '2J', 'Ganadora H vs Segunda J'),
                (85, '1B', self.matriz_terceros[self.terceros_opcion][1], 'Ganadora B vs Mejor 3ro EFGIJ'),
                (86, '1J', '2H', 'Ganadora J vs Segunda H'),
                (87, '1K', self.matriz_terceros[self.terceros_opcion][6], 'Ganadora K vs Mejor 3ro DEIJL'),
                (88, '2D', '2G', 'Segunda D vs Segunda G'),
            ]
        else:
            print("No se ha seleccionado una opción de matriz de terceros. Asignando mejores terceros según criterios FIFA sin repetir...")
            # Obtener terceros y rastrear cuáles ya han sido asignados
            clasificados = self.obtener_clasificados_octavos()
            terceros_disponibles = [t['etiqueta'] for t in clasificados['terceros_seleccionados']]
            terceros_usados = set()
            
            def obtener_mejor_tercero_asignado(grupos_str):
                """Obtiene el mejor tercero del conjunto especificado, excluyendo ya asignados"""
                for tercero_etiqueta in terceros_disponibles:
                    if tercero_etiqueta in terceros_usados:
                        continue
                    grupo = tercero_etiqueta[0]  # El grupo es la primera letra
                    if grupo in grupos_str:
                        terceros_usados.add(tercero_etiqueta)
                        return tercero_etiqueta
                return None
            
            # Construir config dinámicamente con terceros sin repetir
            partidos_config = [
                (73, '2A', '2B', 'Segunda A vs Segunda B'),
                (74, '1E', self.matriz_terceros[self.terceros_opcion][3], 'Ganadora E vs Mejor 3ro ABCDF'),
                (75, '1F', '2C', 'Ganadora F vs Segunda C'),
                (76, '1C', '2F', 'Ganadora C vs Segunda F'),
                (77, '1I', self.matriz_terceros[self.terceros_opcion][5], 'Ganadora I vs Mejor 3ro CDFGH'),
                (78, '2E', '2I', 'Segunda E vs Segunda I'),
                (79, '1A', self.matriz_terceros[self.terceros_opcion][0], 'Ganadora A vs Mejor 3ro CEFHI'),
                (80, '1L', self.matriz_terceros[self.terceros_opcion][7], 'Ganadora L vs Mejor 3ro EHIJK'),
                (81, '1D', self.matriz_terceros[self.terceros_opcion][2], 'Primera D vs Mejor 3ro BEFIJ'),
                (82, '1G', self.matriz_terceros[self.terceros_opcion][4], 'Ganadora G vs Mejor 3ro AEHIJ'),
                (83, '2K', '2L', 'Segunda K vs Segunda L'),
                (84, '1H', '2J', 'Ganadora H vs Segunda J'),
                (85, '1B', self.matriz_terceros[self.terceros_opcion][1], 'Ganadora B vs Mejor 3ro EFGIJ'),
                (86, '1J', '2H', 'Ganadora J vs Segunda H'),
                (87, '1K', self.matriz_terceros[self.terceros_opcion][6], 'Ganadora K vs Mejor 3ro DEIJL'),
                (88, '2D', '2G', 'Segunda D vs Segunda G'),
            ]
        for num, equipo_a_label, equipo_b_label, desc in partidos_config:
            equipo_a = self._obtener_equipo_clasificado(equipo_a_label)
            
            # Si equipo_b_label es un número, es un tercero seleccionado
            if isinstance(equipo_b_label, str) and equipo_b_label[0].isdigit():
                equipo_b = self._obtener_equipo_clasificado(equipo_b_label)
            else:
                equipo_b = equipo_b_label  # Es la etiqueta del mejor tercero
                if equipo_b:
                    equipo_b = self._obtener_equipo_clasificado(equipo_b)
            
            octavos.append({
                'numero_partido': num,
                'codigo_partido': f'M{num}',
                'codigo_ganador': f'W{num}',
                'equipo_a_label': equipo_a_label,
                'equipo_b_label': equipo_b_label if isinstance(equipo_b_label, str) and len(equipo_b_label) <= 2 else 'Mejor 3ro',
                'equipo_a': equipo_a,
                'equipo_b': equipo_b,
                'descripcion': desc
            })
        
        return octavos
    
    def mostrar_octavos_final(self):
        """Muestra los 16 partidos de octavos de final"""
        
        octavos = self.generar_octavos_final()
        
        print(f"\n{'='*100}")
        print("DIECISEISAVOS DE FINAL - OCTAVOS DE FINAL")
        print(f"{'='*100}\n")
        print(f"{'PARTIDO':<12} {'EQUIPO A':<30} {'vs':<4} {'EQUIPO B':<30} {'GANADOR':<12}")
        print("-" * 100)
        
        for partido in octavos:
            print(f"{partido['codigo_partido']:<12} {(partido['equipo_a'] or 'TBD'):<30} {'vs':<4} {(partido['equipo_b'] or 'TBD'):<30} {partido['codigo_ganador']:<12}")
        
        print(f"\n{'='*100}")
        print("Códigos de equipos: 1A/2A/3A (Primero/Segundo/Tercero del Grupo A), etc.")
        print("M73-M88 = Números de partido | W73-W88 = Códigos de ganador para siguientes rondas")
        print(f"{'='*100}")

    def _resolver_referencia_llave(self, codigo_partido, ganadores=None, perdedores=None, tipo='ganadora'):
        """Resuelve referencias de llaves por código de partido.

        - tipo='ganadora' usa `ganadores` y fallback a 'Ganadora Mxx (Wxx)'.
        - tipo='perdedora' usa `perdedores` y fallback a 'Perdedora Mxx'.
        """
        ganadores = ganadores or {}
        perdedores = perdedores or {}

        if tipo == 'ganadora':
            if codigo_partido in ganadores:
                return ganadores[codigo_partido]
            sufijo = codigo_partido[1:]
            return f"Ganadora {codigo_partido} (W{sufijo})"

        if codigo_partido in perdedores:
            return perdedores[codigo_partido]
        return f"Perdedora {codigo_partido}"

    def generar_llaves_fases_finales(self, ganadores=None, perdedores=None):
        """Genera llaves desde M89 hasta M104 usando las reglas del usuario.

        `ganadores` y `perdedores` son opcionales y permiten reemplazar
        las referencias por equipos concretos tras simular cada ronda.
        """
        cuartos_previos = [
            ('M89', 'M74', 'M77', 'Cuartos (17)'),
            ('M90', 'M73', 'M75', 'Cuartos (18)'),
            ('M91', 'M76', 'M78', 'Cuartos (19)'),
            ('M92', 'M79', 'M80', 'Cuartos (20)'),
            ('M93', 'M83', 'M84', 'Cuartos (21)'),
            ('M94', 'M81', 'M82', 'Cuartos (22)'),
            ('M95', 'M86', 'M88', 'Cuartos (23)'),
            ('M96', 'M85', 'M87', 'Cuartos (24)'),
        ]

        cuartos = []
        for codigo, ref_a, ref_b, fase in cuartos_previos:
            cuartos.append({
                'codigo_partido': codigo,
                'fase': fase,
                'equipo_a': self._resolver_referencia_llave(ref_a, ganadores=ganadores, perdedores=perdedores, tipo='ganadora'),
                'equipo_b': self._resolver_referencia_llave(ref_b, ganadores=ganadores, perdedores=perdedores, tipo='ganadora'),
                'codigo_ganador': f"W{codigo[1:]}",
            })

        semis_previas = [
            ('M97', 'M89', 'M90', 'Semifinal (A)'),
            ('M98', 'M93', 'M94', 'Semifinal (B)'),
            ('M99', 'M91', 'M92', 'Semifinal (C)'),
            ('M100', 'M95', 'M96', 'Semifinal (D)'),
        ]

        semis = []
        for codigo, ref_a, ref_b, fase in semis_previas:
            semis.append({
                'codigo_partido': codigo,
                'fase': fase,
                'equipo_a': self._resolver_referencia_llave(ref_a, ganadores=ganadores, perdedores=perdedores, tipo='ganadora'),
                'equipo_b': self._resolver_referencia_llave(ref_b, ganadores=ganadores, perdedores=perdedores, tipo='ganadora'),
                'codigo_ganador': f"W{codigo[1:]}",
            })

        semifinales = [
            {
                'codigo_partido': 'M101',
                'fase': 'Semifinal (SF1)',
                'equipo_a': self._resolver_referencia_llave('M97', ganadores=ganadores, perdedores=perdedores, tipo='ganadora'),
                'equipo_b': self._resolver_referencia_llave('M98', ganadores=ganadores, perdedores=perdedores, tipo='ganadora'),
                'codigo_ganador': 'W101',
            },
            {
                'codigo_partido': 'M102',
                'fase': 'Semifinal (SF2)',
                'equipo_a': self._resolver_referencia_llave('M99', ganadores=ganadores, perdedores=perdedores, tipo='ganadora'),
                'equipo_b': self._resolver_referencia_llave('M100', ganadores=ganadores, perdedores=perdedores, tipo='ganadora'),
                'codigo_ganador': 'W102',
            },
        ]

        tercer_puesto = {
            'codigo_partido': 'M103',
            'fase': 'Tercer Puesto',
            'equipo_a': self._resolver_referencia_llave('M101', ganadores=ganadores, perdedores=perdedores, tipo='perdedora'),
            'equipo_b': self._resolver_referencia_llave('M102', ganadores=ganadores, perdedores=perdedores, tipo='perdedora'),
            'codigo_ganador': 'W103',
        }

        final = {
            'codigo_partido': 'M104',
            'fase': 'Final',
            'equipo_a': self._resolver_referencia_llave('M101', ganadores=ganadores, perdedores=perdedores, tipo='ganadora'),
            'equipo_b': self._resolver_referencia_llave('M102', ganadores=ganadores, perdedores=perdedores, tipo='ganadora'),
            'codigo_ganador': 'W104',
        }

        return {
            'cuartos_previos': cuartos,
            'cuartos': semis,
            'semifinales': semifinales,
            'tercer_puesto': tercer_puesto,
            'final': final,
        }

    def mostrar_llaves_fases_finales(self, llaves=None):
        """Muestra las llaves desde M89 hasta M104."""
        if llaves is None:
            llaves = self.generar_llaves_fases_finales()

        print(f"\n{'='*100}")
        print("FASE FINAL - LLAVES DESDE M89")
        print(f"{'='*100}")

        print("\nCUARTOS (M89-M96):")
        print(f"{'PARTIDO':<10} {'EQUIPO A':<35} {'vs':<4} {'EQUIPO B':<35} {'GANADOR':<8}")
        print("-" * 100)
        for partido in llaves['cuartos_previos']:
            print(f"{partido['codigo_partido']:<10} {partido['equipo_a']:<35} {'vs':<4} {partido['equipo_b']:<35} {partido['codigo_ganador']:<8}")

        print("\nCUARTOS DE FINAL (M97-M100):")
        print(f"{'PARTIDO':<10} {'EQUIPO A':<35} {'vs':<4} {'EQUIPO B':<35} {'GANADOR':<8}")
        print("-" * 100)
        for partido in llaves['cuartos']:
            print(f"{partido['codigo_partido']:<10} {partido['equipo_a']:<35} {'vs':<4} {partido['equipo_b']:<35} {partido['codigo_ganador']:<8}")

        print("\nSEMIFINALES (M101-M102):")
        print(f"{'PARTIDO':<10} {'EQUIPO A':<35} {'vs':<4} {'EQUIPO B':<35} {'GANADOR':<8}")
        print("-" * 100)
        for partido in llaves['semifinales']:
            print(f"{partido['codigo_partido']:<10} {partido['equipo_a']:<35} {'vs':<4} {partido['equipo_b']:<35} {partido['codigo_ganador']:<8}")

        print("\nTERCER PUESTO (M103):")
        tp = llaves['tercer_puesto']
        print(f"{tp['codigo_partido']:<10} {tp['equipo_a']:<35} {'vs':<4} {tp['equipo_b']:<35} {tp['codigo_ganador']:<8}")

        print("\nFINAL (M104):")
        fn = llaves['final']
        print(f"{fn['codigo_partido']:<10} {fn['equipo_a']:<35} {'vs':<4} {fn['equipo_b']:<35} {fn['codigo_ganador']:<8}")
        print(f"{'='*100}")

    def simular_fases_finales(self, n_simulaciones_por_partido=250):
        """Simula llaves eliminatorias con regla de desempate: prórroga y penales."""
        ganadores = {}
        perdedores = {}
        partidos_resueltos = []

        # 1) Resolver octavos (M73-M88)
        for partido in self.generar_octavos_final():
            equipo_a = partido.get('equipo_a')
            equipo_b = partido.get('equipo_b')
            codigo = partido.get('codigo_partido')
            if not equipo_a or not equipo_b or not codigo:
                continue

            resultado = _simular_partido_eliminatorio(
                equipo_a,
                equipo_b,
                f"Eliminatoria|{codigo}",
                n_simulaciones=n_simulaciones_por_partido,
            )
            resultado['codigo_partido'] = codigo
            resultado['fase'] = 'Octavos'
            partidos_resueltos.append(resultado)
            ganadores[codigo] = resultado['ganador']
            perdedores[codigo] = resultado['perdedor']

        # 2) Resolver M89-M102 con el árbol indicado
        arbol = [
            ('M89', 'M74', 'M77', 'Ronda M89-M96'),
            ('M90', 'M73', 'M75', 'Ronda M89-M96'),
            ('M91', 'M76', 'M78', 'Ronda M89-M96'),
            ('M92', 'M79', 'M80', 'Ronda M89-M96'),
            ('M93', 'M83', 'M84', 'Ronda M89-M96'),
            ('M94', 'M81', 'M82', 'Ronda M89-M96'),
            ('M95', 'M86', 'M88', 'Ronda M89-M96'),
            ('M96', 'M85', 'M87', 'Ronda M89-M96'),
            ('M97', 'M89', 'M90', 'Cuartos'),
            ('M98', 'M93', 'M94', 'Cuartos'),
            ('M99', 'M91', 'M92', 'Cuartos'),
            ('M100', 'M95', 'M96', 'Cuartos'),
            ('M101', 'M97', 'M98', 'Semifinales'),
            ('M102', 'M99', 'M100', 'Semifinales'),
        ]

        for codigo, ref_a, ref_b, fase in arbol:
            equipo_a = ganadores.get(ref_a)
            equipo_b = ganadores.get(ref_b)
            if not equipo_a or not equipo_b:
                continue

            resultado = _simular_partido_eliminatorio(
                equipo_a,
                equipo_b,
                f"Eliminatoria|{codigo}",
                n_simulaciones=n_simulaciones_por_partido,
            )
            resultado['codigo_partido'] = codigo
            resultado['fase'] = fase
            partidos_resueltos.append(resultado)
            ganadores[codigo] = resultado['ganador']
            perdedores[codigo] = resultado['perdedor']

        # 3) Tercer puesto (M103) y final (M104)
        if perdedores.get('M101') and perdedores.get('M102'):
            resultado_tercer = _simular_partido_eliminatorio(
                perdedores['M101'],
                perdedores['M102'],
                'Eliminatoria|M103',
                n_simulaciones=n_simulaciones_por_partido,
            )
            resultado_tercer['codigo_partido'] = 'M103'
            resultado_tercer['fase'] = 'Tercer Puesto'
            partidos_resueltos.append(resultado_tercer)
            ganadores['M103'] = resultado_tercer['ganador']
            perdedores['M103'] = resultado_tercer['perdedor']

        if ganadores.get('M101') and ganadores.get('M102'):
            resultado_final = _simular_partido_eliminatorio(
                ganadores['M101'],
                ganadores['M102'],
                'Eliminatoria|M104',
                n_simulaciones=n_simulaciones_por_partido,
            )
            resultado_final['codigo_partido'] = 'M104'
            resultado_final['fase'] = 'Final'
            partidos_resueltos.append(resultado_final)
            ganadores['M104'] = resultado_final['ganador']
            perdedores['M104'] = resultado_final['perdedor']

        return {
            'partidos': partidos_resueltos,
            'ganadores': ganadores,
            'perdedores': perdedores,
            'llaves_resueltas': self.generar_llaves_fases_finales(ganadores=ganadores, perdedores=perdedores),
        }

    def mostrar_resultados_fases_finales(self, resultados):
        """Muestra resultados simulados de llaves eliminatorias."""
        print(f"\n{'='*100}")
        print('RESULTADOS SIMULADOS - FASES FINALES')
        print(f"{'='*100}")
        print(f"{'PARTIDO':<8} {'FASE':<18} {'LOCAL':<24} {'RES':<16} {'VISITA':<24} {'VIA':<10}")
        print('-' * 100)

        for partido in resultados.get('partidos', []):
            res = f"{partido['goles_local_120']} - {partido['goles_visitante_120']}"
            via = partido.get('via', 'REG')
            if via == 'PEN':
                res = f"{res} ({partido['penales_local']}-{partido['penales_visitante']} pen)"

            print(
                f"{partido['codigo_partido']:<8} {partido['fase']:<18} "
                f"{partido['equipo_local']:<24} {res:<16} {partido['equipo_visitante']:<24} {via:<10}"
            )

        if resultados.get('ganadores', {}).get('M104'):
            print(f"\n🏆 Campeona: {resultados['ganadores']['M104']}")
        if resultados.get('ganadores', {}).get('M103'):
            print(f"🥉 Tercer puesto: {resultados['ganadores']['M103']}")
        print(f"{'='*100}")

# Crear instancia
tracker = MundialTracker()

TACTICAS_SELECCION = {
    'México': '4-3-3',
    'Corea del Sur': '4-2-3-1',
    'Chequia': '4-4-2',
    'Sudáfrica': '4-4-2',
    'Canadá': '4-2-3-1',
    'Suiza': '3-5-2',
    'Boznia Herzegovina': '4-3-3',
    'Qatar': '5-4-1',
    'Brasil': '4-3-3',
    'Marruecos': '4-1-4-1',
    'Escocia': '3-4-2-1',
    'Haití': '4-4-2',
    'Estados Unidos': '4-3-3',
    'Australia': '4-2-3-1',
    'Paraguay': '4-4-2',
    'Turquía': '4-2-3-1',
    'Alemania': '4-2-3-1',
    'Costa de Marfil': '4-3-3',
    'Ecuador': '4-4-2',
    'Curacao': '5-4-1',
    'Suecia': '4-4-2',
    'Japón': '4-2-3-1',
    'Paises Bajos': '4-3-3',
    'Túnez': '4-3-3',
    'Nueva Zelanda': '4-4-2',
    'Irán': '4-3-3',
    'Bélgica': '4-2-3-1',
    'Egipto': '4-3-3',
    'Uruguay': '4-3-3',
    'Arabia Saudí': '4-3-3',
    'España': '4-3-3',
    'Cabo Verde': '4-2-3-1',
    'Argentina': '4-4-2',
    'Austria': '4-2-3-1',
    'Jordania': '3-4-3',
    'Argelia': '4-3-3',
    'Francia': '4-2-3-1',
    'Irak': '4-5-1',
    'Noruega': '4-1-2-3',
    'Senegal': '4-3-3',
    'Portugal': '4-2-3-1',
    'Uzbekistán': '3-4-3',
    'Colombia': '4-2-3-1',
    'Congo': '4-4-2',
    'Inglaterra': '4-3-3',
    'Ghana': '4-2-3-1',
    'Panamá': '5-4-1',
    'Croacia': '4-3-3',
}

FUERZA_SELECCION = {
    'México': 82,
    'Corea del Sur': 76,
    'Chequia': 74,
    'Sudáfrica': 72,
    'Canadá': 78,
    'Suiza': 80,
    'Boznia Herzegovina': 70,
    'Qatar': 68,
    'Brasil': 90,
    'Marruecos': 79,
    'Escocia': 76,
    'Haití': 66,
    'Estados Unidos': 82,
    'Australia': 77,
    'Paraguay': 74,
    'Turquía': 75,
    'Alemania': 88,
    'Costa de Marfil': 78,
    'Ecuador': 75,
    'Curacao': 67,
    'Suecia': 80,
    'Japón': 82,
    'Paises Bajos': 87,
    'Túnez': 72,
    'Nueva Zelanda': 69,
    'Irán': 78,
    'Bélgica': 84,
    'Egipto': 77,
    'Uruguay': 83,
    'Arabia Saudí': 71,
    'España': 88,
    'Cabo Verde': 70,
    'Argentina': 88,
    'Austria': 78,
    'Jordania': 68,
    'Argelia': 73,
    'Francia': 90,
    'Irak': 67,
    'Noruega': 84,
    'Senegal': 79,
    'Portugal': 86,
    'Uzbekistán': 74,
    'Colombia': 82,
    'Congo': 71,
    'Inglaterra': 89,
    'Ghana': 76,
    'Panamá': 72,
    'Croacia': 80,
}


def _acotar_atributo(valor, minimo=5, maximo=95):
    return max(minimo, min(maximo, int(round(valor))))


def _crear_jugador(nombre, posicion, ataque, defensa, definicion):
    return Jugador(
        nombre,
        posicion,
        _acotar_atributo(ataque, 20, 95),
        _acotar_atributo(defensa, 20, 95),
        _acotar_atributo(definicion, 5, 95),
    )


def _crear_equipo_simulado(nombre_seleccion):
    tactica = TACTICAS_SELECCION.get(nombre_seleccion, '4-4-2')
    fuerza = FUERZA_SELECCION.get(nombre_seleccion, 74)
    lineas_tacticas = [int(parte) for parte in tactica.split('-')]
    defensas = lineas_tacticas[0]
    delanteros = lineas_tacticas[-1]
    medios = sum(lineas_tacticas[1:-1]) if len(lineas_tacticas) > 2 else lineas_tacticas[1]

    titulares = [
        _crear_jugador(f'{nombre_seleccion} POR', 'POR', 20, fuerza + 7, 5),
    ]

    for indice in range(defensas):
        ajuste = indice - (defensas / 2)
        titulares.append(
            _crear_jugador(
                f'{nombre_seleccion} DEF {indice + 1}',
                'DEF',
                fuerza - 19 + ajuste,
                fuerza + 4 - (ajuste * 0.3),
                fuerza - 22 + ajuste,
            )
        )

    for indice in range(medios):
        ajuste = indice - (medios / 2)
        titulares.append(
            _crear_jugador(
                f'{nombre_seleccion} MED {indice + 1}',
                'MED',
                fuerza + 1 - (ajuste * 0.6),
                fuerza - 4 + (abs(ajuste) * 0.4),
                fuerza - 11 + indice,
            )
        )

    for indice in range(delanteros):
        ajuste = indice - (delanteros / 2)
        titulares.append(
            _crear_jugador(
                f'{nombre_seleccion} DEL {indice + 1}',
                'DEL',
                fuerza + 8 - (ajuste * 0.5),
                fuerza - 28,
                fuerza + 6 - indice,
            )
        )

    equipo = Equipo(nombre_seleccion, tactica)
    equipo.cargar_titulares(titulares)
    return equipo


def _crear_equipo_desde_config(configuracion):
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


def _obtener_configuracion_real(nombre_seleccion):
    configuracion = SELECCIONES_REALES.get(nombre_seleccion)
    if not configuracion:
        return None

    titulares = configuracion.get('titulares', [])
    if len(titulares) != 11:
        raise ValueError(
            f"La selección {nombre_seleccion} debe tener exactamente 11 titulares en datos_selecciones.py"
        )

    return configuracion


def _crear_equipo_para_simulacion(nombre_seleccion):
    configuracion_real = _obtener_configuracion_real(nombre_seleccion)
    if configuracion_real is not None:
        return _crear_equipo_desde_config(configuracion_real)
    return _crear_equipo_simulado(nombre_seleccion)


def _simular_marcador(nombre_local, nombre_visitante, contexto, n_simulaciones=250):
    semilla_texto = f'{contexto}|{nombre_local}|{nombre_visitante}'
    semilla = int(sha256(semilla_texto.encode('utf-8')).hexdigest()[:16], 16)
    estado_random = random.getstate()
    random.seed(semilla)

    try:
        equipo_local = _crear_equipo_para_simulacion(nombre_local)
        equipo_visitante = _crear_equipo_para_simulacion(nombre_visitante)
        conteo_marcadores = defaultdict(int)

        for _ in range(n_simulaciones):
            partido = Partido(equipo_local, equipo_visitante)
            resumen = partido.simular_partido_completo(mostrar_resultado=False)
            marcador = (resumen['goles_local'], resumen['goles_visitante'])
            conteo_marcadores[marcador] += 1

        marcador_mas_probable = max(
            conteo_marcadores.items(),
            key=lambda item: (item[1], item[0][0] - item[0][1], item[0][0], -item[0][1]),
        )[0]
        return marcador_mas_probable
    finally:
        random.setstate(estado_random)


def _acotar_probabilidad(valor, minimo=0.05, maximo=0.95):
    return max(minimo, min(maximo, valor))


def _simular_tanda_penales(equipo_local, equipo_visitante):
    fuerza_local = equipo_local.obtener_fuerza_definicion()
    fuerza_visitante = equipo_visitante.obtener_fuerza_definicion()

    portero_local = equipo_local.obtener_portero()
    portero_visitante = equipo_visitante.obtener_portero()
    defensa_portero_local = portero_local.defensa if portero_local else 50
    defensa_portero_visitante = portero_visitante.defensa if portero_visitante else 50

    prob_local = _acotar_probabilidad(0.72 + ((fuerza_local - defensa_portero_visitante) / 300), 0.58, 0.90)
    prob_visitante = _acotar_probabilidad(0.72 + ((fuerza_visitante - defensa_portero_local) / 300), 0.58, 0.90)

    pen_local = 0
    pen_visitante = 0

    for _ in range(5):
        if random.random() < prob_local:
            pen_local += 1
        if random.random() < prob_visitante:
            pen_visitante += 1

    rondas_extra = 0
    while pen_local == pen_visitante and rondas_extra < 10:
        rondas_extra += 1
        if random.random() < prob_local:
            pen_local += 1
        if random.random() < prob_visitante:
            pen_visitante += 1

    if pen_local == pen_visitante:
        if random.random() < 0.5:
            pen_local += 1
        else:
            pen_visitante += 1

    if pen_local > pen_visitante:
        return equipo_local.nombre, equipo_visitante.nombre, pen_local, pen_visitante
    return equipo_visitante.nombre, equipo_local.nombre, pen_local, pen_visitante


def _simular_partido_eliminatorio(nombre_local, nombre_visitante, contexto, n_simulaciones=250):
    semilla_texto = f'{contexto}|{nombre_local}|{nombre_visitante}|KO'
    semilla = int(sha256(semilla_texto.encode('utf-8')).hexdigest()[:16], 16)
    estado_random = random.getstate()
    random.seed(semilla)

    try:
        equipo_local = _crear_equipo_para_simulacion(nombre_local)
        equipo_visitante = _crear_equipo_para_simulacion(nombre_visitante)

        conteo = defaultdict(int)
        ejemplos = {}

        for _ in range(n_simulaciones):
            partido_regular = Partido(equipo_local, equipo_visitante, minutos=90)
            regular = partido_regular.simular_partido_completo(mostrar_resultado=False)
            goles_local_90 = regular['goles_local']
            goles_visitante_90 = regular['goles_visitante']

            goles_local_120 = goles_local_90
            goles_visitante_120 = goles_visitante_90
            penales_local = None
            penales_visitante = None
            via = 'REG'

            if goles_local_90 == goles_visitante_90:
                prorroga = Partido(equipo_local, equipo_visitante, minutos=30).simular_partido_completo(mostrar_resultado=False)
                goles_local_120 += prorroga['goles_local']
                goles_visitante_120 += prorroga['goles_visitante']
                via = 'ET'

                if goles_local_120 == goles_visitante_120:
                    via = 'PEN'
                    ganador, perdedor, penales_local, penales_visitante = _simular_tanda_penales(equipo_local, equipo_visitante)
                else:
                    ganador = nombre_local if goles_local_120 > goles_visitante_120 else nombre_visitante
                    perdedor = nombre_visitante if ganador == nombre_local else nombre_local
            else:
                ganador = nombre_local if goles_local_90 > goles_visitante_90 else nombre_visitante
                perdedor = nombre_visitante if ganador == nombre_local else nombre_local

            clave = (
                ganador,
                perdedor,
                goles_local_120,
                goles_visitante_120,
                via,
                penales_local if penales_local is not None else -1,
                penales_visitante if penales_visitante is not None else -1,
            )
            conteo[clave] += 1
            ejemplos[clave] = {
                'equipo_local': nombre_local,
                'equipo_visitante': nombre_visitante,
                'ganador': ganador,
                'perdedor': perdedor,
                'goles_local_90': goles_local_90,
                'goles_visitante_90': goles_visitante_90,
                'goles_local_120': goles_local_120,
                'goles_visitante_120': goles_visitante_120,
                'via': via,
                'penales_local': penales_local,
                'penales_visitante': penales_visitante,
            }

        mejor_clave = max(
            conteo.items(),
            key=lambda item: (item[1], item[0][2] - item[0][3], item[0][2], -item[0][3]),
        )[0]
        return ejemplos[mejor_clave]
    finally:
        random.setstate(estado_random)


def _registrar_partidos_simulados(partidos, contexto):
    for equipo_local, equipo_visitante in partidos:
        goles_local, goles_visitante = _simular_marcador(equipo_local, equipo_visitante, contexto)
        tracker.registrar_partido(equipo_local, goles_local, equipo_visitante, goles_visitante)

# Registrar resultados de los primeros partidos del torneo
def registrar_resultados():
    """Registra todos los resultados de los partidos"""
    
    # Grupo A
    tracker.registrar_partido('México', 2, 'Sudáfrica', 0, rojas_directas_local=1, rojas_directas_visitante=2,amarillas_local=1, amarillas_visitante=2)
    tracker.registrar_partido('Canadá', 1, 'Boznia Herzegovina', 1,amarillas_local=2, amarillas_visitante=3)
    tracker.registrar_partido('Canadá', 6, 'Qatar', 0,amarillas_local=1, amarillas_visitante=1, rojas_directas_visitante=1)
    tracker.registrar_partido('México', 1, 'Corea del Sur', 0,amarillas_visitante=2)
    
    # Grupo B
    tracker.registrar_partido('Corea del Sur', 2, 'Chequia', 1,amarillas_local=1)
    tracker.registrar_partido('Chequia', 1, 'Sudáfrica', 1,amarillas_local=1, amarillas_visitante=2)
    tracker.registrar_partido('Suiza', 4, 'Boznia Herzegovina', 1, amarillas_local=1, amarillas_visitante=2,rojas_directas_visitante=1)
    
    # Grupo C
    tracker.registrar_partido('Brasil', 1, 'Marruecos', 1,amarillas_local=2)
    tracker.registrar_partido('Qatar', 1, 'Suiza', 1,amarillas_local=2, amarillas_visitante=1)
    tracker.registrar_partido('Brasil', 3, 'Haití', 0,amarillas_local=1, amarillas_visitante=3)
    tracker.registrar_partido('Escocia', 0, 'Marruecos', 1,amarillas_local=1, amarillas_visitante=1)
    
    # Grupo D
    tracker.registrar_partido('Estados Unidos', 4, 'Paraguay', 1,amarillas_local=1, amarillas_visitante=5)
    tracker.registrar_partido('Haití', 0, 'Escocia', 1,amarillas_local=1, amarillas_visitante=3)
    tracker.registrar_partido('Estados Unidos', 2, 'Australia', 0,amarillas_local=3, amarillas_visitante=4)
    tracker.registrar_partido('Turquía', 0, 'Paraguay', 1, amarillas_visitante=1)
    
    # Grupo E
    tracker.registrar_partido('Australia', 2, 'Turquía', 0,amarillas_visitante=1)
    tracker.registrar_partido('Paises Bajos', 2, 'Japón', 2,amarillas_local=3)
    
    # Grupo F
    tracker.registrar_partido('Alemania', 7, 'Curacao', 1)
    tracker.registrar_partido('Suecia', 5, 'Túnez', 1,amarillas_visitante=1)
    tracker.registrar_partido('Costa de Marfil', 1, 'Ecuador', 0,amarillas_local=3, amarillas_visitante=1)
    
    # Grupo G
    tracker.registrar_partido('España', 0, 'Cabo Verde', 0,amarillas_local=1,amarillas_visitante=1)
    tracker.registrar_partido('Bélgica', 1, 'Egipto', 1, amarillas_local=2, amarillas_visitante=2)
    
    # Grupo H
    tracker.registrar_partido('Arabia Saudí', 1, 'Uruguay', 1,amarillas_local=1)
    
    # Grupo I
    tracker.registrar_partido('Irán', 2, 'Nueva Zelanda', 2,amarillas_local=1)
    tracker.registrar_partido('Francia', 3, 'Senegal', 1)
    
    # Grupo J
    tracker.registrar_partido('Irak', 1, 'Noruega', 4,amarillas_local=1)
    tracker.registrar_partido('Argentina', 3, 'Argelia', 0)
    
    # Grupo K
    tracker.registrar_partido('Austria', 3, 'Jordania', 1,amarillas_local=1)
    tracker.registrar_partido('Portugal', 1, 'Congo', 1,amarillas_local=3,amarillas_visitante=1)
    tracker.registrar_partido('Uzbekistán', 1, 'Colombia', 3,amarillas_local=1,amarillas_visitante=1)
    
    # Grupo L
    tracker.registrar_partido('Inglaterra', 4, 'Croacia', 2)
    tracker.registrar_partido('Ghana', 1, 'Panamá', 0,amarillas_local=1,amarillas_visitante=2)

    # Jornada 2
    tracker.registrar_partido("Paises Bajos",5,"Suecia",1,amarillas_visitante=3)
    tracker.registrar_partido("Alemania",2,"Costa de Marfil",1)
    tracker.registrar_partido("Ecuador",0,"Curacao",0,amarillas_local=1,amarillas_visitante=5)
    tracker.registrar_partido("Túnez",0,"Japón",4)

    tracker.registrar_partido("España",4,"Arabia Saudí",0,amarillas_visitante=2)
    tracker.registrar_partido("Bélgica",0,"Irán",0,amarillas_local=1,amarillas_visitante=1,rojas_directas_local=1)
    tracker.registrar_partido('Uruguay', 2, 'Cabo Verde', 2,amarillas_local=2,amarillas_visitante=2)
    tracker.registrar_partido("Nueva Zelanda",1, "Egipto",3,amarillas_local=2,amarillas_visitante=1)

    tracker.registrar_partido("Argentina",2,"Austria",0,amarillas_local=2,amarillas_visitante=2)
    tracker.registrar_partido("Francia",3,"Irak",0,amarillas_visitante=1)
    tracker.registrar_partido("Noruega",3,"Senegal",2)
    tracker.registrar_partido("Jordania",1,"Argelia",2,amarillas_local=1,amarillas_visitante=1)

    tracker.registrar_partido("Portugal",5,"Uzbekistán",0,amarillas_local=1,amarillas_visitante=1)
    _registrar_partidos_simulados([
        ('Inglaterra', 'Ghana'),
        ('Panamá', 'Croacia'),
        ('Colombia', 'Congo'),
    ], 'Jornada 2 Grupos I-L')

    # Jornada 3
    _registrar_partidos_simulados([
        ('México', 'Chequia'),
        ('Corea del Sur', 'Sudáfrica'),
        ('Canadá', 'Suiza'),
        ('Boznia Herzegovina', 'Qatar'),
        ('Brasil', 'Escocia'),
        ('Marruecos', 'Haití'),
        ('Estados Unidos', 'Turquía'),
        ('Australia', 'Paraguay'),
        ('Alemania', 'Ecuador'),
        ('Costa de Marfil', 'Curacao'),
        ('Suecia', 'Japón'),
        ('Paises Bajos', 'Túnez'),
        ('Nueva Zelanda', 'Bélgica'),
        ('Irán', 'Egipto'),
        ('Uruguay', 'España'),
        ('Arabia Saudí', 'Cabo Verde'),
    ], 'Jornada 3 Grupos A-H')

    _registrar_partidos_simulados([
        ('Francia', 'Noruega'),
        ('Senegal', 'Irak'),
        ('Argentina', 'Jordania'),
        ('Austria', 'Argelia'),
        ('Portugal', 'Colombia'),
        ('Congo', 'Uzbekistán'),
        ('Inglaterra', 'Panamá'),
        ('Ghana', 'Croacia'),
    ], 'Jornada 3 Grupos I-L')

# Ejemplo de uso:
if __name__ == "__main__":
    print("🌍 MUNDIAL 2026 - SISTEMA DE SEGUIMIENTO")
    print("="*80)
    
    # Registrar todos los resultados
    print("\n📊 Registrando resultados de partidos...")
    registrar_resultados()
    
    # Mostrar posiciones
    print("\n📋 POSICIONES ACTUALES:")
    tracker.mostrar_posiciones()
    
    # Mostrar clasificados a octavos
    tracker.mostrar_clasificados_octavos()

    # Intentar cargar la matriz de 495 opciones desde matriz495.py y seleccionar opción
    try:
        from matriz495 import RAW as _RAW495
        matriz_list = []
        for line in _RAW495.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if not parts[0].isdigit():
                continue
            etiquetas = [p for p in parts[1:] if p.startswith('3')]
            if len(etiquetas) == 8:
                matriz_list.append(etiquetas)

        if matriz_list:
            tracker.set_matriz_list(matriz_list)
            found_idx = tracker.encontrar_opcion_por_terceros_actuales()
            if found_idx is not None:
                opcion_num = found_idx + 1
                tracker.set_opcion_terceros(opcion_num)
                print(f"\n✅ Opción encontrada y seleccionada automáticamente: {opcion_num} (índice {found_idx})")
                print(f"   Etiquetas de terceros para esta opción: {tracker.matriz_terceros[opcion_num]}")
            else:
                print("\n⚠️ No se encontró una opción exacta entre las 495 opciones cargadas.")
    except Exception as e:
        print("\n⚠️ No se pudo cargar la matriz desde matriz495.py:", e)

    # Mostrar octavos de final
    tracker.mostrar_octavos_final()

    # Mostrar llaves de fases siguientes (M89-M104) según reglamento
    tracker.mostrar_llaves_fases_finales()

    # Simulación de fases finales (desactivada por ahora)
    # Regla aplicada: si hay empate -> prórroga (30') y si persiste -> penales.
    #
    resultados_fases = tracker.simular_fases_finales(n_simulaciones_por_partido=250)
    tracker.mostrar_resultados_fases_finales(resultados_fases)
    tracker.mostrar_llaves_fases_finales(resultados_fases['llaves_resueltas'])

    print("\n\n💡 Para registrar más partidos, usa:")
    print("   tracker.registrar_partido('Equipo 1', goles1, 'Equipo 2', goles2)")
    print("\nPara ver posiciones de un grupo:")
    print("   tracker.mostrar_posiciones('A')")
    print("\nPara ver historial de partidos:")
    print("   tracker.mostrar_historial_partidos()")

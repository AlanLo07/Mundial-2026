import random

class Jugador:
    def __init__(self, nombre, posicion, ataque, defensa, definicion):
        self.nombre = nombre
        self.posicion = posicion  # 'DEL', 'MED', 'DEF', 'POR'
        self.ataque = ataque      # Atributo de 1 a 100
        self.defensa = defensa    # Atributo de 1 a 100
        self.definicion = definicion # Capacidad de meter gol

class Equipo:
    def __init__(self, nombre, tactica):
        self.nombre = nombre
        self.tactica = tactica  # Ej: '4-3-3', '5-4-1'
        self.titulares = []

    def agregar_titular(self, jugador):
        self.titulares.append(jugador)

    def cargar_titulares(self, jugadores):
        self.titulares = list(jugadores)

    def obtener_jugadores_por_posicion(self, posicion):
        return [jugador for jugador in self.titulares if jugador.posicion == posicion]

    def obtener_portero(self):
        porteros = self.obtener_jugadores_por_posicion('POR')
        return porteros[0] if porteros else None

    def obtener_tiradores(self):
        tiradores = self.obtener_jugadores_por_posicion('DEL') + self.obtener_jugadores_por_posicion('MED')
        return tiradores if tiradores else list(self.titulares)

    def obtener_creadores(self):
        creadores = self.obtener_jugadores_por_posicion('MED') + self.obtener_jugadores_por_posicion('DEL')
        return creadores if creadores else list(self.titulares)

    def obtener_modificadores_tacticos(self):
        tacticas = {
            '4-3-3': {'posesion': 1.05, 'ataque': 1.12, 'defensa': 0.96},
            '4-4-2': {'posesion': 1.00, 'ataque': 1.00, 'defensa': 1.00},
            '4-2-3-1': {'posesion': 1.08, 'ataque': 1.05, 'defensa': 1.02},
            '3-5-2': {'posesion': 1.10, 'ataque': 1.06, 'defensa': 0.94},
            '5-4-1': {'posesion': 0.96, 'ataque': 0.88, 'defensa': 1.15},
        }
        return tacticas.get(self.tactica, {'posesion': 1.00, 'ataque': 1.00, 'defensa': 1.00})
        
    def obtener_fuerza_linea(self, posicion):
        # Suma el atributo de los jugadores en esa posición específica
        jugadores_linea = [j for j in self.titulares if j.posicion == posicion]
        if not jugadores_linea:
            return 0
        return sum(j.ataque if posicion == 'MED' or posicion == 'DEL' else j.defensa for j in jugadores_linea) / len(jugadores_linea)

    def obtener_fuerza_creacion(self):
        mediocampo = self.obtener_fuerza_linea('MED')
        delanteros = self.obtener_fuerza_linea('DEL')
        return (mediocampo * 0.55) + (delanteros * 0.45)

    def obtener_fuerza_defensiva(self):
        defensa = self.obtener_fuerza_linea('DEF')
        mediocampo = self.obtener_fuerza_linea('MED')
        portero = self.obtener_portero()
        fuerza_portero = portero.defensa if portero else 50
        return (defensa * 0.55) + (mediocampo * 0.15) + (fuerza_portero * 0.30)

    def obtener_fuerza_definicion(self):
        tiradores = self.obtener_tiradores()
        if not tiradores:
            return 0
        return sum(jugador.definicion for jugador in tiradores) / len(tiradores)

    def obtener_intensidad_ofensiva(self):
        creacion = self.obtener_fuerza_creacion()
        definicion = self.obtener_fuerza_definicion()
        return (creacion * 0.65) + (definicion * 0.35)
    
class Partido:
    def __init__(self, local, visitante, minutos=90):
        self.local = local
        self.visitante = visitante
        self.minutos = minutos
        self.goles_local = 0
        self.goles_visitante = 0
        self.tiros_local = 0
        self.tiros_visitante = 0
        self.tiros_arco_local = 0
        self.tiros_arco_visitante = 0
        self.posesion_local = 0
        self.posesion_visitante = 0
        self.eventos = []
        self.goleadores = []

    def _probabilidad_acotada(self, valor, minimo, maximo):
        return max(minimo, min(maximo, valor))

    def _obtener_factor_posicion_tiro(self, jugador):
        factores = {
            'DEL': 1.10,
            'MED': 1.00,
            'DEF': 0.72,
            'POR': 0.20,
        }
        return factores.get(jugador.posicion, 1.00)

    def _obtener_factor_posicion_definicion(self, jugador):
        factores = {
            'DEL': 1.03,
            'MED': 1.01,
            'DEF': 0.70,
            'POR': 0.20,
        }
        return factores.get(jugador.posicion, 1.00)

    def _elegir_creador(self, equipo):
        creadores = equipo.obtener_creadores()
        if not creadores:
            return None

        pesos = []
        for jugador in creadores:
            peso = max(1, (jugador.ataque * 0.70) + (jugador.definicion * 0.30))
            if jugador.posicion == 'MED':
                peso *= 1.18
            elif jugador.posicion == 'DEL':
                peso *= 0.97
            pesos.append(peso)

        return random.choices(creadores, weights=pesos, k=1)[0]

    def _elegir_tirador(self, equipo, creador):
        tiradores = equipo.obtener_tiradores()
        if not tiradores:
            return None

        pesos = []
        for jugador in tiradores:
            peso = max(1, (jugador.definicion * 0.75) + (jugador.ataque * 0.55))
            peso *= self._obtener_factor_posicion_tiro(jugador)
            if creador is not None:
                if jugador.nombre == creador.nombre:
                    peso *= 0.84
                elif creador.posicion == 'MED' and jugador.posicion == 'MED':
                    peso *= 1.12
                elif creador.posicion == 'MED' and jugador.posicion == 'DEL':
                    peso *= 1.04
            pesos.append(peso)

        return random.choices(tiradores, weights=pesos, k=1)[0]

    def _registrar_tiro(self, es_local, al_arco):
        if es_local:
            self.tiros_local += 1
            if al_arco:
                self.tiros_arco_local += 1
        else:
            self.tiros_visitante += 1
            if al_arco:
                self.tiros_arco_visitante += 1

    def _resolver_ataque(self, equipo_ataca, equipo_defiende, es_local, minuto):
        mod_ataca = equipo_ataca.obtener_modificadores_tacticos()
        mod_defiende = equipo_defiende.obtener_modificadores_tacticos()

        fuerza_creacion = equipo_ataca.obtener_intensidad_ofensiva() * mod_ataca['ataque']
        fuerza_defensa = equipo_defiende.obtener_fuerza_defensiva() * mod_defiende['defensa']

        probabilidad_llegada = self._probabilidad_acotada(
            0.16 + ((fuerza_creacion - fuerza_defensa) / 190),
            0.08,
            0.42,
        )

        if random.random() >= probabilidad_llegada:
            return

        creador = self._elegir_creador(equipo_ataca)
        tirador = self._elegir_tirador(equipo_ataca, creador)
        if tirador is None:
            return

        portero = equipo_defiende.obtener_portero()
        fuerza_portero = portero.defensa if portero else 50

        probabilidad_arco = self._probabilidad_acotada(
            0.36 + ((tirador.ataque + tirador.definicion - fuerza_defensa) / 200),
            0.22,
            0.84,
        )

        al_arco = random.random() < probabilidad_arco
        self._registrar_tiro(es_local, al_arco)

        if not al_arco:
            self.eventos.append(f"{minuto}' Remate desviado de {tirador.nombre} para {equipo_ataca.nombre}")
            return

        probabilidad_gol = self._probabilidad_acotada(
            0.16 + (((tirador.definicion * self._obtener_factor_posicion_definicion(tirador)) + (tirador.ataque * 0.45) - fuerza_portero) / 180),
            0.08,
            0.64,
        )

        if random.random() < probabilidad_gol:
            if es_local:
                self.goles_local += 1
            else:
                self.goles_visitante += 1
            self.goleadores.append({'minuto': minuto, 'equipo': equipo_ataca.nombre, 'jugador': tirador.nombre})
            if creador is not None and creador.nombre != tirador.nombre:
                self.eventos.append(f"{minuto}' Gol de {tirador.nombre} para {equipo_ataca.nombre} tras pase de {creador.nombre}")
            else:
                self.eventos.append(f"{minuto}' Gol de {tirador.nombre} para {equipo_ataca.nombre}")
        else:
            self.eventos.append(f"{minuto}' Atajada de {portero.nombre if portero else 'el portero'} ante {tirador.nombre}")

    def simular_minuto(self, minuto):
        med_local = self.local.obtener_fuerza_linea('MED') * self.local.obtener_modificadores_tacticos()['posesion']
        med_visitante = self.visitante.obtener_fuerza_linea('MED') * self.visitante.obtener_modificadores_tacticos()['posesion']
        total_medio = med_local + med_visitante

        if total_medio <= 0:
            prob_posesion_local = 0.5
        else:
            prob_posesion_local = med_local / total_medio

        if random.random() < prob_posesion_local:
            self.posesion_local += 1
            self._resolver_ataque(self.local, self.visitante, True, minuto)
        else:
            self.posesion_visitante += 1
            self._resolver_ataque(self.visitante, self.local, False, minuto)

    def simular_partido_completo(self, mostrar_resultado=True):
        for minuto in range(1, self.minutos + 1):
            self.simular_minuto(minuto)

        resumen = {
            'local': self.local.nombre,
            'visitante': self.visitante.nombre,
            'goles_local': self.goles_local,
            'goles_visitante': self.goles_visitante,
            'tiros_local': self.tiros_local,
            'tiros_visitante': self.tiros_visitante,
            'tiros_arco_local': self.tiros_arco_local,
            'tiros_arco_visitante': self.tiros_arco_visitante,
            'posesion_local': round((self.posesion_local / self.minutos) * 100, 2) if self.minutos else 0,
            'posesion_visitante': round((self.posesion_visitante / self.minutos) * 100, 2) if self.minutos else 0,
            'goleadores': list(self.goleadores),
            'eventos': list(self.eventos),
        }

        if mostrar_resultado:
            print(f"Resultado Final: {self.local.nombre} {self.goles_local} - {self.goles_visitante} {self.visitante.nombre}")

        return resumen

import random
import sqlite3
from tabulate import tabulate

class Almacen:
    def __init__(self):
        self.conn = sqlite3.connect('jugadores.db')
        self.cursor = self.conn.cursor()
        self.crear_tabla()

    def crear_tabla(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS jugadores (
                nombre TEXT PRIMARY KEY,
                iniciales TEXT,
                fecha_nacimiento TEXT,
                victorias INTEGER,
                derrotas INTEGER,
                niveles_jugados TEXT
            )
        ''')
        self.conn.commit()

    def agregar_jugador(self, jugador):
        self.cursor.execute('''  
            INSERT OR REPLACE INTO jugadores (nombre, iniciales, fecha_nacimiento, victorias, derrotas, niveles_jugados)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (jugador.nombre, jugador.iniciales, jugador.fecha_de_nacimiento, jugador.victorias, jugador.derrotas, ','.join(jugador.niveles_jugados)))
        self.conn.commit()

    def obtener_jugador(self, nombre):
        self.cursor.execute('SELECT * FROM jugadores WHERE nombre = ?', (nombre,))
        jugador = self.cursor.fetchone()
        if jugador:
            j = Jugador()
            j.nombre = jugador[0]
            j.iniciales = jugador[1]
            j.fecha_de_nacimiento = jugador[2]
            j.victorias = jugador[3]
            j.derrotas = jugador[4]
            j.niveles_jugados = jugador[5].split(',')
            return j
        else:
            return None

    def actualizar_jugador(self, jugador):
        self.cursor.execute('''
            UPDATE jugadores SET victorias = ?, derrotas = ?, niveles_jugados = ?
            WHERE nombre = ?
        ''', (jugador.victorias, jugador.derrotas, ','.join(jugador.niveles_jugados), jugador.nombre))
        self.conn.commit()

class Dado:
    def __init__(self):
        self.valor_dado = 0

    def lanzar(self):
        self.valor_dado = random.randint(1, 6)

    def mostrar_resultado(self):
        print(f"Resultado del lanzamiento: {self.valor_dado}")

class Jugador:
    def __init__(self):
        self.nombre = ""
        self.iniciales = ""
        self.fecha_de_nacimiento = ""
        self.victorias = 0
        self.derrotas = 0
        self.niveles_jugados = []

    def obtener_datos(self):
        self.nombre = input("Ingrese su nombre: ")
        self.iniciales = input("Ingrese sus iniciales en mayúsculas (nombre, apellido paterno, apellido materno): ")
        self.fecha_de_nacimiento = input("Ingrese su fecha de nacimiento (dd/mm/aaaa): ")

    def obtener_score(self):
        return {"Nombre": self.nombre, "Victorias": self.victorias, "Derrotas": self.derrotas}

    def actualizar_historial(self, nivel):
        self.niveles_jugados.append(nivel)

    def registrar_victoria(self):
        self.victorias += 1

    def registrar_derrota(self):
        self.derrotas += 1

class SistemaDeVideojuego:
    def __init__(self, almacen):
        self.almacen = almacen
        self.nivel_dificultad = {'novato': 1, 'normal': 2, 'experto': 3}
        self.dado1 = Dado()
        self.dado2 = Dado()
        self.dado3 = Dado()
        self.usuario = Jugador()

    def iniciar(self):
        respuesta = input("¿Está registrado? (s/n): ")
        if respuesta.lower() == 's':
            nombre = input("Ingrese su nombre: ")
            self.usuario = self.almacen.obtener_jugador(nombre)
            if not self.usuario:
                print("Jugador no encontrado. Por favor, regístrese.")
                self.registro_jugador()
        elif respuesta.lower() == 'n':
            self.registro_jugador()
        else:
            print("Respuesta no válida.")
            self.iniciar()

    def registro_jugador(self):
        nuevo_jugador = Jugador()
        nuevo_jugador.obtener_datos()
        self.almacen.agregar_jugador(nuevo_jugador)
        self.usuario = self.almacen.obtener_jugador(nuevo_jugador.nombre)

    def jugar(self):
        print("¡Bienvenido al juego de dados!")
        nivel = input("Seleccione el nivel de juego (1: novato, 2: normal, 3: experto): ")
        if nivel not in ['1', '2', '3']:
            print("Nivel de juego no válido.")
            return

        nivel_nombre = list(self.nivel_dificultad.keys())[int(nivel) - 1]
        print(f"\n¡Bienvenido {self.usuario.nombre} al nivel {nivel_nombre}!")
        victoria = False

        for _ in range(3):  # Permitir hasta 3 oportunidades
            if nivel_nombre == 'novato':
                input("Presiona Enter para tirar el dado...")
                self.dado1.lanzar()
                resultado = self.dado1.valor_dado
                print(f"Resultado del lanzamiento: {resultado}")
                if resultado == 6:
                    victoria = True
                    break
            elif nivel_nombre == 'normal':
                input("Presiona Enter para tirar el primer dado...")
                self.dado1.lanzar()
                input("Presiona Enter para tirar el segundo dado...")
                self.dado2.lanzar()
                total = self.dado1.valor_dado + self.dado2.valor_dado
                print(f"Resultados: {self.dado1.valor_dado}, {self.dado2.valor_dado} (Total: {total})")
                if total == 7:
                    victoria = True
                    break
            elif nivel_nombre == 'experto':
                input("Presiona Enter para tirar el primer dado...")
                self.dado1.lanzar()
                input("Presiona Enter para tirar el segundo dado...")
                self.dado2.lanzar()
                input("Presiona Enter para tirar el tercer dado...")
                self.dado3.lanzar()
                total = self.dado1.valor_dado + self.dado2.valor_dado + self.dado3.valor_dado
                print(f"Resultados: {self.dado1.valor_dado}, {self.dado2.valor_dado}, {self.dado3.valor_dado} (Total: {total})")
                if total == 15:
                    victoria = True
                    break

        if victoria:
            print("¡Felicidades! Has ganado.")
            self.usuario.registrar_victoria()
            self.volver_a_jugar()
        else:
            print("Lo siento, has perdido.")
            self.usuario.registrar_derrota()
        self.usuario.actualizar_historial(nivel_nombre)
        self.almacen.actualizar_jugador(self.usuario)
        self.volver_a_jugar()

    def mostrar_score(self):
        if not self.usuario:
            print("Por favor, regístrese o ingrese su nombre para mostrar el puntaje.")
            return
        print("\n======== Score =========")
        niveles_jugados = self.usuario.niveles_jugados
        contador_novato = niveles_jugados.count('novato')
        contador_normal = niveles_jugados.count('normal')
        contador_experto = niveles_jugados.count('experto')

        table = [["Nombre", self.usuario.nombre],
                 ["Victorias", self.usuario.victorias],
                 ["Derrotas", self.usuario.derrotas],
                 ["Niveles jugados"],
                 ["Novato", contador_novato],
                 ["Normal", contador_normal],
                 ["Experto", contador_experto]
                ]
        print(tabulate(table, tablefmt="grid"))

    def volver_a_jugar(self):
        respuesta = input("¿Desea volver a jugar? (s/n): ")
        if respuesta.lower() == 's':
            return self.jugar()
        elif respuesta.lower() == 'n':
            return self.menu_principal()
        else:
            print("Respuesta no válida.")
            return self.volver_a_jugar()

    def menu_principal(self):
        while True:
            print("\n=== Juego de Dados ===")
            print("1. Jugar")
            print("2. Mostrar Score")
            print("3. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self.jugar()
            elif opcion == '2':
                self.mostrar_score()
            elif opcion == '3':
                confirmacion = input("¿Está seguro que desea salir? (s/n): ")
                if confirmacion.lower() == 's':
                    print("¡Gracias por jugar! Hasta la vista, baby.")
                    break
                elif confirmacion.lower() == 'n':
                    continue
                else:
                    print("Respuesta no válida. Por favor, ingrese 's' para sí o 'n' para no.")

            else:
                print("Opción no válida. Por favor, elija una opción válida.")

if __name__ == "__main__":
    almacen = Almacen()
    juego = SistemaDeVideojuego(almacen)
    juego.iniciar()
    juego.menu_principal()

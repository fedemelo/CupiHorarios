
ASISTENTES = ['A', 'E', 'F', 'M', 'N', 'W', 'Z']

# Copy paste directo del Excel, sin asco.
# Los días están separados por \t (es un TSV). Uno no ve los tabs por ser humano, pero ahí están
DISPONIBILIDAD = open('dispo_mas_reciente_del_excel.txt', 'r').read()
print(DISPONIBILIDAD)


def listar_todos_turnos() -> list:
    l = []
    for horario in listar_horas_turnos():
        for dia in ["Lun", "Mar", "Mie", "Jue", "Vie"]:
            turn = f"{dia}, {horario}"
            l.append(turn)
    return l


def parametro_peso_turnos() -> dict:
    d = {}
    for horario in listar_horas_turnos():
        express = False  # El primer turno del día es normal
        for dia in ["Lun", "Mar", "Mie", "Jue", "Vie"]:
        
            turn = f"{dia}, {horario}"
            d[turn] = 0.5 if express else 1

        express = (express-1)%2  # Invierte el booleano: después de un turno normal va express

    return d


def listar_horas_turnos() -> str:
    hours = []
    h = 8
    express = False  # El primer turno es normal
    while h < 18:
        if express:
            if h == int(h):
                hours.append("%i:00-%i:30" % (h, h))
            else:
                hours.append("%i:30-%i:00" % (int(h), int(h)+1))
            h += 0.5
        else:
            if h == int(h):
                hours.append("%i:00-%i:00" % (h, h+1))
            else:
                hours.append("%i:30-%i:30" % (int(h), int(h)+1))
            h += 1
        express = (express-1)%2  # Invierte el booleano
    return hours

# print(parametro_peso_turnos())

def parametro_disponibilidad(tsv: str, letra: str ) -> dict:
    """
    Recibe un TSV pero copy-pasteado (de forma que se pueda copiar y pegar del excel, que copia como TSV por defecto)
    y una letra (la de quien se quiere obtener la dispo).

    Bota el parámetro en sintaxis de Pyomo: para cada horario (de los posibles, dados por la función de arriba), 1 si está
    disponible, 0 si no
    """
    dispo_bool = []
    rows = tsv.split("\n")
    for row in rows:
        cols = row.split("\t")
        for dispo in cols:
            if letra in dispo:
                dispo_bool.append(1)
            else:
                dispo_bool.append(0)

    # Ojo: en el excel, dos filas pueden corresponder al mismo turno si ese turno no es express
    # Solución: En la lista de turnos, repito 2 veces cada turno normal
    turnos_con_repeticion = []
    express = False
    for horario in listar_horas_turnos():
        if express:
            for dia in ["Lun", "Mar", "Mie", "Jue", "Vie"]:
                turnos_con_repeticion.append(f"{dia}, {horario}")
        else:
            for _ in range(2):
                for dia in ["Lun", "Mar", "Mie", "Jue", "Vie"]:
                    turnos_con_repeticion.append(f"{dia}, {horario}")
        express = (express-1)%2  # Invierte el booleano
         
    return dict(zip(turnos_con_repeticion, dispo_bool))

def escribir_dispo_en_TXT()-> None:
    s = ""
    for asistente in ASISTENTES:
        s += f"m.dispo_{asistente} = {parametro_disponibilidad(DISPONIBILIDAD, asistente)}\n\n".replace(" 'L", "\n             'L")
    fhandle = open("diponibilidad.txt", "w")
    fhandle.write(s)
    fhandle.close()
    print("Se han escrito los parámetros para el modelo en disponibilidad.txt")


escribir_dispo_en_TXT()
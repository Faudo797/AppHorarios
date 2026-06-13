import random
import copy
from apphorarios.models import Ficha, FichaAsignada, Hora, Aula

def evaluar_horario(asignaciones, horas_objs):
    """
    Fitness Score: Calcula qué tan "bueno" o lógico es un horario.
    Comienza con 1000 puntos y resta penalizaciones.
    """
    puntaje = 1000
    
    # Agrupar por grado y día para evaluar distribución de materias
    # Estructura: distribucion_clases[grado_id][dia] = [asignatura_id, asignatura_id, ...]
    distribucion_clases = {}
    
    # Agrupar por profesor y día para evaluar "ventanas" o huecos libres
    # Estructura: horario_profes[profesor_id][dia] = [hora_id, hora_id, ...]
    horario_profes = {}
    
    # Mapeo de horas_id a índices secuenciales (1, 2, 3...) para saber si son consecutivas
    hora_indices = {h.id: idx for idx, h in enumerate(horas_objs)}

    for asig in asignaciones:
        g_id = asig['grado_id']
        p_id = asig['profesor_id']
        dia = asig['dia']
        h_id = asig['hora_id']
        asignatura_id = asig['ficha'].asignatura_id
        
        # Guardar para distribución de materias
        if g_id not in distribucion_clases: distribucion_clases[g_id] = {}
        if dia not in distribucion_clases[g_id]: distribucion_clases[g_id][dia] = []
        distribucion_clases[g_id][dia].append(asignatura_id)
        
        # Guardar para ventanas de profesor
        if p_id not in horario_profes: horario_profes[p_id] = {}
        if dia not in horario_profes[p_id]: horario_profes[p_id][dia] = []
        horario_profes[p_id][dia].append(h_id)

    # REGLA 1: Evitar que la misma clase tenga la misma materia repetida en el mismo día
    for g_id, dias in distribucion_clases.items():
        for dia, materias in dias.items():
            for materia in set(materias):
                veces = materias.count(materia)
                if veces > 1:
                    # Penalizar fuertemente las materias repetidas en un solo día
                    # (Si son 2 horas de matemáticas seguidas, aSc lo permite, pero
                    # para simplificar la heurística general, restaremos 20 puntos por cada repetición).
                    puntaje -= 20 * (veces - 1)

    # REGLA 2: Evitar ventanas (huecos libres) para los profesores
    for p_id, dias in horario_profes.items():
        for dia, h_ids in dias.items():
            if len(h_ids) < 2:
                continue
            
            # Obtener los índices secuenciales ordenados de las horas que dicta
            indices = sorted([hora_indices[h] for h in h_ids])
            
            # Contar cuántas horas de "hueco" hay entre la primera clase y la última
            # Ejemplo: dicta la 1ra y la 4ta -> hay 2 huecos (2da y 3ra).
            # indices = [0, 3] -> (3 - 0 - 1) = 2 huecos
            for i in range(len(indices) - 1):
                huecos_entre_clases = indices[i+1] - indices[i] - 1
                if huecos_entre_clases > 0:
                    puntaje -= 10 * huecos_entre_clases

    return puntaje

def generar_horario(iteraciones=10, estrategia='2-2'):
    # 1. Preparar datos base
    dias = [d[0] for d in FichaAsignada.DIAS_SEMANA]
    horas_objs = list(Hora.objects.all().order_by('hora_inicio'))
    aulas = list(Aula.objects.all())
    
    if not aulas:
        return False, "No hay aulas registradas para asignar."

    # 2. Cargar estado actual de asignaciones
    asignaciones_actuales = FichaAsignada.objects.select_related('ficha').all()
    grid_base = {} 

    def add_to_grid(grid_dict, asignacion_dict):
        key = (asignacion_dict['dia'], asignacion_dict['hora_id'])
        if key not in grid_dict:
            grid_dict[key] = []
        grid_dict[key].append(asignacion_dict)
    
    for a in asignaciones_actuales:
        add_to_grid(grid_base, {
            'ficha': a.ficha,
            'profesor_id': a.ficha.profesor_id,
            'grado_id': a.ficha.grado_id,
            'aula_id': a.aula_id,
            'dia': a.dia,
            'hora_id': a.hora_id
        })

    # 3. Determinar qué bloques faltan por asignar
    fichas = Ficha.objects.select_related('asignatura').all()
    bloques_no_asignados = []

    for ficha in fichas:
        asignadas_count = FichaAsignada.objects.filter(ficha=ficha).count()
        faltantes = ficha.horas_totales - asignadas_count
        
        bloques_ficha = []
        if estrategia == '2-2':
            while faltantes >= 2:
                bloques_ficha.append({'ficha': ficha, 'duracion': 2})
                faltantes -= 2
            if faltantes == 1:
                bloques_ficha.append({'ficha': ficha, 'duracion': 1})
        elif estrategia == '2-1-1':
            if faltantes >= 2:
                bloques_ficha.append({'ficha': ficha, 'duracion': 2})
                faltantes -= 2
            while faltantes > 0:
                bloques_ficha.append({'ficha': ficha, 'duracion': 1})
                faltantes -= 1
        else: # '1-1-1-1'
            while faltantes > 0:
                bloques_ficha.append({'ficha': ficha, 'duracion': 1})
                faltantes -= 1
                
        bloques_no_asignados.extend(bloques_ficha)

    domain_dias = dias
    domain_horas = [h.id for h in horas_objs]
    domain_aulas = [a.id for a in aulas]

    def es_valido(grid, ficha, dia, hora_id, aula_id):
        key = (dia, hora_id)
        if key in grid:
            for asig in grid[key]:
                if asig['profesor_id'] == ficha.profesor_id:
                    return False
                if asig['grado_id'] == ficha.grado_id:
                    return False
                if asig['aula_id'] == aula_id:
                    return False
                    
        # Limitar la cantidad de veces que esta materia se dicta en este mismo día
        veces_en_dia = 0
        for h_check in domain_horas:
            key_check = (dia, h_check)
            if key_check in grid:
                for asig in grid[key_check]:
                    if asig['ficha'].id == ficha.id:
                        veces_en_dia += 1
                        
        # Por defecto, intentar que solo haya 1 sesión (o 1 bloque) por día
        limite_diario = 1
        if ficha.horas_totales > len(domain_dias):
            limite_diario = 2 # Si hay más horas que días en la semana, inevitablemente debe repetir algún día
            
        if veces_en_dia >= limite_diario:
            return False
            
        # Evitar bloques (horas consecutivas) accidentales para la misma ficha
        # Si la estrategia pide bloques (duracion=2), ambas horas se validan antes de entrar al grid, por lo que esto no las bloquea.
        idx = domain_horas.index(hora_id)
        if idx > 0:
            key_ant = (dia, domain_horas[idx - 1])
            if key_ant in grid:
                for asig in grid[key_ant]:
                    if asig['ficha'].id == ficha.id:
                        return False
        if idx < len(domain_horas) - 1:
            key_sig = (dia, domain_horas[idx + 1])
            if key_sig in grid:
                for asig in grid[key_sig]:
                    if asig['ficha'].id == ficha.id:
                        return False
                        
        return True

    # Pre-calcular horas totales por profesor para la heurística
    horas_profesor = {}
    for b in bloques_no_asignados:
        p_id = b['ficha'].profesor_id
        horas_profesor[p_id] = horas_profesor.get(p_id, 0)
    mejor_horario = None

    # Motor Greedy (Voraz) Instantáneo
    grid_actual = copy.deepcopy(grid_base)
    nuevas_asignaciones = []
    
    # Heurística MRV: Más difíciles primero
    bloques_mezclados = list(bloques_no_asignados)
    bloques_mezclados.sort(key=lambda b: (
        b['duracion'], 
        horas_profesor.get(b['ficha'].profesor_id, 0)
    ), reverse=True)

    for b in bloques_mezclados:
        ficha_actual = b['ficha']
        duracion = b['duracion']
        asignado = False

        for dia in domain_dias:
            if asignado: break
            for idx_h, hora_id in enumerate(domain_horas):
                if asignado: break
                for aula_id in domain_aulas:
                    if duracion == 1:
                        if es_valido(grid_actual, ficha_actual, dia, hora_id, aula_id):
                            asig_dict = {
                                'ficha': ficha_actual, 'profesor_id': ficha_actual.profesor_id,
                                'grado_id': ficha_actual.grado_id, 'aula_id': aula_id,
                                'dia': dia, 'hora_id': hora_id
                            }
                            add_to_grid(grid_actual, asig_dict)
                            nuevas_asignaciones.append(asig_dict)
                            asignado = True
                            break
                    elif duracion == 2:
                        if idx_h + 1 < len(domain_horas):
                            hora_id_2 = domain_horas[idx_h + 1]
                            if es_valido(grid_actual, ficha_actual, dia, hora_id, aula_id) and \
                               es_valido(grid_actual, ficha_actual, dia, hora_id_2, aula_id):
                                asig_1 = {
                                    'ficha': ficha_actual, 'profesor_id': ficha_actual.profesor_id,
                                    'grado_id': ficha_actual.grado_id, 'aula_id': aula_id,
                                    'dia': dia, 'hora_id': hora_id
                                }
                                asig_2 = {
                                    'ficha': ficha_actual, 'profesor_id': ficha_actual.profesor_id,
                                    'grado_id': ficha_actual.grado_id, 'aula_id': aula_id,
                                    'dia': dia, 'hora_id': hora_id_2
                                }
                                add_to_grid(grid_actual, asig_1)
                                add_to_grid(grid_actual, asig_2)
                                nuevas_asignaciones.append(asig_1)
                                nuevas_asignaciones.append(asig_2)
                                asignado = True
                                break
                                
        # Si asignado es False, simplemente pasamos a la siguiente ficha. 
        # Las fichas no asignadas quedarán en la barra lateral del usuario.

    todas_asignaciones = list(nuevas_asignaciones)
    for k, v in grid_base.items():
        todas_asignaciones.extend(v)
        
    mejor_horario = todas_asignaciones

    # 5. Guardar la mejor solución encontrada en todas las iteraciones
    if mejor_horario is not None:
        FichaAsignada.objects.bulk_create([
            FichaAsignada(
                ficha=a['ficha'],
                aula_id=a['aula_id'],
                dia=a['dia'],
                hora_id=a['hora_id']
            ) for a in nuevas_asignaciones
        ])
        
        # Check if there are unassigned blocks
        if len(nuevas_asignaciones) < sum(b['duracion'] for b in bloques_no_asignados):
            return True, "Generación completada al instante. Algunas clases quedaron sin asignar por falta de espacio y están en el panel izquierdo."
        return True, "Generación exitosa."
    else:
        return False, "Ocurrió un error inesperado al inicializar la generación."

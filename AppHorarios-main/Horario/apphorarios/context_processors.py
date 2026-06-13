from apphorarios.models import ConfiguracionColegio

def configuracion_colegio(request):
    try:
        config = ConfiguracionColegio.get_config()
        return {
            'institution_name': config.nombre,
            'year': config.anio_lectivo,
            'period': config.periodo,
        }
    except Exception:
        return {
            'institution_name': 'Institución Educativa Demo',
            'year': '2026',
            'period': 'Semestre 1',
        }

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Horario.settings')

application = get_wsgi_application()

# 🚀 TRUCO MÁGICO: Crear superusuario automáticamente al encender
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # Cambia 'admind' y 'tu_contraseña_aqui' por lo que tú quieras
    if not User.objects.filter(username='admind').exists():
        User.objects.create_superuser('admind', 'admin@correo.com', 'admin123')
        print("====== SUPERUSUARIO CREADO CON ÉXITO ======")
except Exception as e:
    print(f"Error al crear el superusuario: {e}")

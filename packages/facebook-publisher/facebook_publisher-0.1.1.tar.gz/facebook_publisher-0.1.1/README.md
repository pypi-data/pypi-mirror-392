# Facebook SDK para SaaS

SDK Python para automatizar interacción con Facebook Groups usando Playwright. Diseñado para integrarse fácilmente en proyectos SaaS con múltiples usuarios.

# Instalación

pip install facebook_publisher

# Instala las dependencias:

pip install playwright
playwright install

# Estructura

facebook_sdk/client.py — Cliente principal para interactuar con Facebook.

facebook_sdk/session.py — Manejo de sesión y contexto persistente.

facebook_sdk/login.py — Funciones relacionadas al login.

facebook_sdk/groups.py — Funciones para listar, entrar y manejar grupos.

facebook_sdk/posts.py — Funciones para publicar texto y multimedia.

facebook_sdk/exceptions.py — Excepciones personalizadas.

facebook_sdk/utils.py — Funciones auxiliares y helpers.

# Uso básico
from facebook_sdk.client import FacebookClient

# Crear instancia con credenciales y ruta para sesión persistente
fb = FacebookClient(
    email="tu-email",
    password="tu-password",
    user_data_dir="path_a_carpeta_usuario",
    headless=False
)

# Iniciar navegador y sesión
fb.start()
fb.login()
fb.close_notification_dialog()
fb.go_to_groups_section()

# Extraer grupos
grupos = fb.extract_groups()
print("Grupos disponibles:")
for g in grupos:
    print(f"{g['nombre']} - {g['url']}")

# Publicar en un grupo
fb.publish_to_groups([grupos[0]["url"]], text="Hola desde SDK!", photos=None)

# Finalizar sesión y navegador
fb.stop()

# Recomendaciones para SaaS

Usa user_data_dir único por usuario para mantener sesión.

Instancia un objeto FacebookClient por usuario concurrente.

Considera agregar un pool de navegadores o procesos para manejar concurrencia.

Implementa control de errores robusto usando las excepciones personalizadas.

Usa logs para monitorear la actividad de cada cliente.

## Privacidad
Copyright (c) 2025 Raydiel Espinosa

All Rights Reserved.

This software is proprietary and confidential. 
No part of this software may be used, copied, modified, merged, published, 
distributed, sublicensed, or sold without explicit written permission 
from the copyright holder.

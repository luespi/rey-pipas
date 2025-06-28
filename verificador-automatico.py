#!/usr/bin/env python3
"""
🔍 VERIFICADOR AUTOMÁTICO - REY PIPAS
Estructura Tradicional de Django
Verificación completa del sistema
"""

import os
import sys
from pathlib import Path

# Colores para la terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print("🔍 VERIFICADOR DE INSTALACIÓN - REY PIPAS")
    print("   Estructura Tradicional de Django")
    print(f"{'='*60}{Colors.ENDC}\n")

def check_file(filepath, critical=True):
    """Verifica si un archivo existe"""
    exists = os.path.exists(filepath)
    status = f"{Colors.GREEN}✓{Colors.ENDC}" if exists else f"{Colors.RED}✗{Colors.ENDC}"
    importance = f"{Colors.RED}[CRÍTICO]{Colors.ENDC}" if critical else f"{Colors.YELLOW}[OPCIONAL]{Colors.ENDC}"

    print(f"  {status} {importance} {filepath}")
    return exists

def check_directory(dirpath):
    """Verifica si un directorio existe"""
    exists = os.path.exists(dirpath)
    status = f"{Colors.GREEN}✓{Colors.ENDC}" if exists else f"{Colors.RED}✗{Colors.ENDC}"
    print(f"  {status} Directorio: {dirpath}")
    return exists

def check_django_structure():
    """Verifica la estructura tradicional de Django"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📁 VERIFICANDO ESTRUCTURA PRINCIPAL...{Colors.ENDC}")

    critical_files = {
        'manage.py': True,
        'requirements.txt': True,
        'rey_pipas/__init__.py': True,
        'rey_pipas/settings.py': True,
        'rey_pipas/urls.py': True,
        'rey_pipas/wsgi.py': True,
        'rey_pipas/asgi.py': False,
    }

    missing_critical = []

    for file, is_critical in critical_files.items():
        if not check_file(file, is_critical) and is_critical:
            missing_critical.append(file)

    return len(missing_critical) == 0, missing_critical

def check_apps():
    """Verifica las aplicaciones Django"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📁 VERIFICANDO APLICACIONES...{Colors.ENDC}")

    apps = ['users', 'orders', 'vehicles', 'payments', 'core']
    apps_ok = True

    for app in apps:
        app_path = f"apps/{app}"
        print(f"\n  📱 App: {app}")

        if not check_directory(app_path):
            apps_ok = False
            continue

        # Archivos críticos de cada app
        critical_files = [
            f"{app_path}/__init__.py",
            f"{app_path}/apps.py",
            f"{app_path}/models.py",
        ]

        # Archivos opcionales
        optional_files = [
            f"{app_path}/views.py",
            f"{app_path}/urls.py",
            f"{app_path}/admin.py",
            f"{app_path}/forms.py",
        ]

        for file in critical_files:
            if not check_file(file, critical=True):
                apps_ok = False

        for file in optional_files:
            check_file(file, critical=False)

    return apps_ok

def check_templates():
    """Verifica los templates"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📁 VERIFICANDO TEMPLATES...{Colors.ENDC}")

    template_dirs = [
        'templates',
        'templates/auth',
        'templates/dashboard',
        'templates/landing',
    ]

    templates_ok = True
    for dir in template_dirs:
        if not check_directory(dir):
            templates_ok = False

    # Verificar archivos de templates importantes
    important_templates = [
        'templates/base.html',
        'templates/landing/index.html',
        'templates/auth/login.html',
        'templates/auth/register.html',
        'templates/dashboard/admin_dashboard.html',
        'templates/dashboard/client_dashboard.html',
        'templates/dashboard/operator_dashboard.html',
    ]

    print(f"\n  {Colors.CYAN}📄 Templates principales:{Colors.ENDC}")
    for template in important_templates:
        check_file(template, critical=False)

    return templates_ok

def check_static_media():
    """Verifica directorios static y media"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📁 VERIFICANDO STATIC Y MEDIA...{Colors.ENDC}")

    dirs = ['static', 'static/css', 'static/js', 'static/images', 'media']
    all_ok = True

    for dir in dirs:
        if not check_directory(dir):
            all_ok = False

    return all_ok

def check_database():
    """Verifica la base de datos"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🗄️  VERIFICANDO BASE DE DATOS...{Colors.ENDC}")

    db_exists = check_file('db.sqlite3', critical=False)

    if not db_exists:
        print(f"  {Colors.YELLOW}⚠️  No se encontró db.sqlite3 - Necesitas ejecutar las migraciones{Colors.ENDC}")

    return db_exists

def check_django_installation():
    """Verifica si Django está instalado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🐍 VERIFICANDO INSTALACIÓN DE DJANGO...{Colors.ENDC}")

    try:
        import django
        version = django.get_version()
        print(f"  {Colors.GREEN}✓ Django {version} instalado{Colors.ENDC}")

        # Verificar versión
        major, minor = map(int, version.split('.')[:2])
        if major >= 4:
            print(f"  {Colors.GREEN}✓ Versión compatible{Colors.ENDC}")
            return True
        else:
            print(f"  {Colors.YELLOW}⚠️  Versión antigua de Django{Colors.ENDC}")
            return True
    except ImportError:
        print(f"  {Colors.RED}✗ Django NO está instalado{Colors.ENDC}")
        return False

def generate_fix_commands(missing_files):
    """Genera comandos para arreglar problemas"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}🔧 COMANDOS PARA SOLUCIONAR PROBLEMAS:{Colors.ENDC}")

    if 'manage.py' in missing_files:
        print(f"\n  {Colors.CYAN}# Crear manage.py:{Colors.ENDC}")
        print("  django-admin startproject rey_pipas .")

    if 'rey_pipas/__init__.py' in missing_files:
        print(f"\n  {Colors.CYAN}# Crear estructura del proyecto:{Colors.ENDC}")
        print("  mkdir -p rey_pipas")
        print("  touch rey_pipas/__init__.py")

    if any('apps/' in f for f in missing_files):
        print(f"\n  {Colors.CYAN}# Crear estructura de apps:{Colors.ENDC}")
        print("  mkdir -p apps/users apps/orders apps/vehicles apps/payments apps/core")
        print("  touch apps/__init__.py")
        print("  touch apps/users/__init__.py apps/orders/__init__.py")
        print("  touch apps/vehicles/__init__.py apps/payments/__init__.py")
        print("  touch apps/core/__init__.py")

    print(f"\n  {Colors.CYAN}# Instalar dependencias:{Colors.ENDC}")
    print("  pip install -r requirements.txt")

    print(f"\n  {Colors.CYAN}# Crear y aplicar migraciones:{Colors.ENDC}")
    print("  python manage.py makemigrations")
    print("  python manage.py migrate")

    print(f"\n  {Colors.CYAN}# Crear superusuario:{Colors.ENDC}")
    print("  python manage.py createsuperuser")

def main():
    """Función principal del verificador"""
    print_header()

    # Cambiar al directorio del proyecto si es necesario
    if os.path.exists('manage.py'):
        os.chdir('.')
    elif os.path.exists('../manage.py'):
        os.chdir('..')

    # Verificaciones
    all_ok = True
    missing_files = []

    # 1. Verificar instalación de Django
    django_ok = check_django_installation()
    if not django_ok:
        all_ok = False

    # 2. Verificar estructura principal
    structure_ok, missing = check_django_structure()
    if not structure_ok:
        all_ok = False
        missing_files.extend(missing)

    # 3. Verificar apps
    apps_ok = check_apps()
    if not apps_ok:
        all_ok = False

    # 4. Verificar templates
    templates_ok = check_templates()
    if not templates_ok:
        all_ok = False

    # 5. Verificar static y media
    static_ok = check_static_media()
    if not static_ok:
        all_ok = False

    # 6. Verificar base de datos
    db_ok = check_database()

    # Resumen final
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print("📊 RESUMEN DE VERIFICACIÓN")
    print(f"{'='*60}{Colors.ENDC}")

    if all_ok and db_ok:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ¡TODO ESTÁ PERFECTO!{Colors.ENDC}")
        print(f"{Colors.GREEN}El sistema está listo para ejecutarse.{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Ejecuta: python manage.py runserver{Colors.ENDC}")
    elif all_ok and not db_ok:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  CASI LISTO{Colors.ENDC}")
        print(f"{Colors.YELLOW}Solo falta crear la base de datos.{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Ejecuta estos comandos:{Colors.ENDC}")
        print("  python manage.py makemigrations")
        print("  python manage.py migrate")
        print("  python manage.py createsuperuser")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ HAY PROBLEMAS QUE RESOLVER{Colors.ENDC}")
        print(f"{Colors.RED}Revisa los archivos faltantes arriba.{Colors.ENDC}")

        if missing_files:
            generate_fix_commands(missing_files)

    print(f"\n{Colors.CYAN}Para más ayuda, revisa la documentación del proyecto.{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
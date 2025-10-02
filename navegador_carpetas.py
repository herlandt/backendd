#!/usr/bin/env python
"""
📁 NAVEGADOR DE CARPETAS - BACKEND CONDOMINIO
============================================

Script para navegar fácilmente entre las carpetas organizadas
para los diferentes equipos de desarrollo.
"""

import os
import sys

def print_header():
    """Imprime el header del navegador"""
    print("=" * 60)
    print("📁 NAVEGADOR DE CARPETAS - BACKEND CONDOMINIO")
    print("=" * 60)
    print("📅 Fecha: Octubre 2, 2025")
    print("🎯 Propósito: Navegación entre equipos de desarrollo")
    print("=" * 60)
    print()

def show_folder_structure():
    """Muestra la estructura de carpetas organizada"""
    
    print("📂 ESTRUCTURA ACTUAL:")
    print()
    print("📁 RAÍZ DEL PROYECTO:")
    print("   ├── 📱 equipo_movil/          # Para desarrollo Flutter")
    print("   ├── 🌐 equipo_web/            # Para desarrollo React/Web")
    print("   ├── 📄 openapi_schema_*.yaml  # Schemas compartidos")
    print("   ├── 📋 SCHEMA_*.md            # Documentación schemas")
    print("   ├── ⚙️  manage.py              # Django principal")
    print("   ├── 📂 config/                # Configuración backend")
    print("   ├── 📂 usuarios/              # App usuarios")
    print("   ├── 📂 condominio/            # App condominio")
    print("   ├── 📂 finanzas/              # App finanzas")
    print("   ├── 📂 seguridad/             # App seguridad")
    print("   └── 📂 mantenimiento/         # App mantenimiento")
    print()
    
def show_mobile_team():
    """Muestra información del equipo móvil"""
    
    print("📱 EQUIPO MÓVIL (Flutter):")
    print("=" * 40)
    print("📂 Carpeta: equipo_movil/")
    print()
    print("📄 Archivos disponibles:")
    
    mobile_path = "equipo_movil"
    if os.path.exists(mobile_path):
        files = os.listdir(mobile_path)
        for file in sorted(files):
            if file.endswith('.md'):
                print(f"   📖 {file}")
            elif file.endswith('.py'):
                print(f"   🐍 {file}")
    
    print()
    print("🚀 Comando rápido:")
    print("   cd equipo_movil")
    print("   python crear_usuarios_movil_sincronizado.py")
    print()
    print("🔗 URL para móvil: http://10.0.2.2:8000/api/")
    print()

def show_web_team():
    """Muestra información del equipo web"""
    
    print("🌐 EQUIPO WEB (React/Next.js):")
    print("=" * 40)
    print("📂 Carpeta: equipo_web/")
    print()
    print("📄 Archivos disponibles:")
    
    web_path = "equipo_web"
    if os.path.exists(web_path):
        files = os.listdir(web_path)
        for file in sorted(files):
            if file.endswith('.md'):
                print(f"   📖 {file}")
            elif file.endswith('.py'):
                print(f"   🐍 {file}")
    
    print()
    print("🚀 Comando rápido:")
    print("   cd equipo_web")
    print("   python crear_usuarios_frontend.py")
    print()
    print("🔗 URL para web: http://127.0.0.1:8000/api/")
    print()

def show_shared_resources():
    """Muestra recursos compartidos"""
    
    print("📄 RECURSOS COMPARTIDOS (RAÍZ):")
    print("=" * 40)
    
    # Buscar archivos de schema
    root_files = [f for f in os.listdir('.') if f.endswith(('.yaml', '.md')) and ('schema' in f.lower() or 'openapi' in f.lower())]
    
    print("📊 Schemas y documentación:")
    for file in sorted(root_files):
        if file.endswith('.yaml'):
            print(f"   🔧 {file}")
        elif file.endswith('.md'):
            print(f"   📖 {file}")
    
    print()
    print("⚙️ Backend Django:")
    print("   🐍 manage.py")
    print("   📂 config/")
    print("   📂 usuarios/, condominio/, finanzas/, etc.")
    print()

def interactive_menu():
    """Menú interactivo para navegación"""
    
    while True:
        print("🎯 MENÚ DE NAVEGACIÓN:")
        print("=" * 40)
        print("1. 📱 Ver equipo móvil")
        print("2. 🌐 Ver equipo web") 
        print("3. 📄 Ver recursos compartidos")
        print("4. 📂 Ver estructura completa")
        print("5. 🚪 Salir")
        print()
        
        choice = input("Selecciona una opción (1-5): ").strip()
        
        print()
        
        if choice == '1':
            show_mobile_team()
        elif choice == '2':
            show_web_team()
        elif choice == '3':
            show_shared_resources()
        elif choice == '4':
            show_folder_structure()
        elif choice == '5':
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida. Intenta de nuevo.")
        
        print("-" * 60)
        print()

def main():
    """Función principal"""
    print_header()
    
    # Verificar que estamos en la raíz del proyecto
    if not os.path.exists('manage.py'):
        print("❌ Error: Este script debe ejecutarse desde la raíz del proyecto Django")
        print("   (donde está el archivo manage.py)")
        sys.exit(1)
    
    # Verificar que las carpetas organizadas existen
    if not os.path.exists('equipo_movil') or not os.path.exists('equipo_web'):
        print("❌ Error: Las carpetas organizadas no existen")
        print("   Asegúrate de haber ejecutado la organización de archivos")
        sys.exit(1)
    
    # Mostrar resumen inicial
    print("✅ NAVEGADOR LISTO")
    print("📁 Carpetas organizadas detectadas correctamente")
    print()
    
    # Ejecutar menú interactivo
    interactive_menu()

if __name__ == "__main__":
    main()
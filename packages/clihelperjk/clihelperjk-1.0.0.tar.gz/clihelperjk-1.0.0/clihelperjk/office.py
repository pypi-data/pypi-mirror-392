# clihelperjk/office.py

import os
import subprocess

# ANSI colores
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
RESET = "\033[0m"

OFFICE_PATHS = [
    r"C:\Program Files\Microsoft Office\Office16",
    r"C:\Program Files (x86)\Microsoft Office\Office16"
]

def detect_office_path():
    for path in OFFICE_PATHS:
        if os.path.exists(path):
            return path
    return None

def run_command(command):
    try:
        subprocess.run(["powershell", "-Command", command], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error al ejecutar: {e}{RESET}")

def show_steps():
    print(f"{CYAN}=== CLIHELPERJK — Microsoft Office Admin ==={RESET}")
    print(f"{GREEN}Detección automática de rutas y versión{RESET}")
    path = detect_office_path()
    if path:
        print(f"{YELLOW}Ruta encontrada: {path}{RESET}")
    else:
        print(f"{RED}No se encontró ninguna ruta de Office instalada{RESET}")

def view_status():
    path = detect_office_path()
    if path:
        print(f"{BLUE}Mostrando estado de licencias...{RESET}")
        run_command(f"cd '{path}'; cscript ospp.vbs /dstatus")
    else:
        print(f"{RED}No se puede mostrar estado, ruta no encontrada.{RESET}")

def remove_key():
    path = detect_office_path()
    if not path:
        print(f"{RED}No se encontró ruta de Office{RESET}")
        return

    key = input(f"{YELLOW}Ingrese los últimos 5 dígitos de la clave a desinstalar: {RESET}")
    confirm = input(f"{MAGENTA}¿Está seguro de desinstalar la clave {key}? (Y/N): {RESET}")
    if confirm.lower() == "y":
        run_command(f"cd '{path}'; cscript ospp.vbs /unpkey:{key}")
        print(f"{GREEN}Clave {key} eliminada (si existía){RESET}")
    else:
        print(f"{CYAN}Operación cancelada{RESET}")

def goto_office():
    path = detect_office_path()
    if path:
        print(f"{GREEN}Abriendo carpeta de Office en Explorer...{RESET}")
        run_command(f"explorer '{path}'")
    else:
        print(f"{RED}No se encontró ruta de Office{RESET}")

def main_menu():
    while True:
        print(f"\n{CYAN}=== CLIHELPERJK Menu ==={RESET}")
        print(f"{YELLOW}[1]{RESET} Ver estado de licencia (/dstatus)")
        print(f"{YELLOW}[2]{RESET} Desinstalar clave (/unpkey)")
        print(f"{YELLOW}[3]{RESET} Abrir carpeta Office")
        print(f"{YELLOW}[4]{RESET} Mostrar rutas detectadas")
        print(f"{YELLOW}[5]{RESET} Salir")

        choice = input(f"{MAGENTA}Seleccione una opción: {RESET}")
        if choice == "1":
            view_status()
        elif choice == "2":
            remove_key()
        elif choice == "3":
            goto_office()
        elif choice == "4":
            show_steps()
        elif choice == "5":
            print(f"{CYAN}Saliendo...{RESET}")
            break
        else:
            print(f"{RED}Opción inválida, intente de nuevo{RESET}")

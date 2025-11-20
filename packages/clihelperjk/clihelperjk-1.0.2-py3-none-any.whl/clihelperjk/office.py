# clihelperjk/office.py

import os
import subprocess
import sys
import locale
import signal

# SOLUCIÓN: Inicializar colores ANSI para Windows
if sys.platform == "win32":
    os.system("")

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
    r"C:\Program Files (x86)\Microsoft Office\Office16",
]


def detect_office_path():
    for path in OFFICE_PATHS:
        if os.path.exists(path):
            return path
    return None


def run_subprocess(cmd, cwd=None):
    """Ejecuta un comando con Popen y garantiza terminar el proceso si el usuario presiona Ctrl+C."""
    enc = locale.getpreferredencoding(False)
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding=enc,
        errors="replace",
        cwd=cwd,
        creationflags=creationflags,
    )

    try:
        out, err = proc.communicate()
    except KeyboardInterrupt:
        # Interrupción por Ctrl+C: intentar terminar el proceso hijo limpia y rápidamente
        print(f"\n{YELLOW}Interrumpido por usuario. Terminando proceso...{RESET}")
        try:
            if sys.platform == "win32":
                # En Windows enviar CTRL_BREAK_EVENT al grupo de procesos
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                proc.send_signal(signal.SIGINT)
        except Exception:
            pass
        try:
            out, err = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
            except Exception:
                pass
            out, err = proc.communicate()
        # Propagar la interrupción hacia arriba para que el menu pueda salir si quiere
        raise KeyboardInterrupt
    return proc.returncode, out, err


def run_command(command):
    try:
        print(f"{BLUE}Ejecutando: {command}{RESET}")
        rc, out, err = run_subprocess(["powershell", "-Command", command])
        if out:
            print(out)
        if err:
            print(f"{YELLOW}Advertencia: {err}{RESET}")
        return rc == 0
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error al ejecutar: {e}{RESET}")
        if getattr(e, "stdout", None):
            print(f"Salida: {e.stdout}")
        if getattr(e, "stderr", None):
            print(f"Error: {e.stderr}")
        return False
    except KeyboardInterrupt:
        print(f"{CYAN}Operación cancelada por usuario{RESET}")
        return False


def run_cscript_command(args):
    """Función especial para ejecutar comandos cscript"""
    path = detect_office_path()
    if not path:
        print(f"{RED}No se encontró ruta de Office{RESET}")
        return False
    
    try:
        print(f"{BLUE}Ejecutando desde: {path}{RESET}")
        rc, out, err = run_subprocess(["cscript", "ospp.vbs"] + args, cwd=path)
        if out:
            print(out)
        if err:
            print(f"{YELLOW}Advertencia: {err}{RESET}")
        return rc == 0
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error ejecutando cscript: {e}{RESET}")
        if getattr(e, "stdout", None):
            print(f"Salida: {e.stdout}")
        if getattr(e, "stderr", None):
            print(f"Error: {e.stderr}")
        return False
    except KeyboardInterrupt:
        print(f"{CYAN}Operación cancelada por usuario{RESET}")
        return False
    except Exception as e:
        print(f"{RED}Error inesperado: {e}{RESET}")
        return False


def show_steps():
    print(f"{CYAN}=== CLIHELPERJK — Microsoft Office Admin ==={RESET}")
    print(f"{GREEN}Detección automática de rutas y versión{RESET}")
    path = detect_office_path()
    if path:
        print(f"{YELLOW}Ruta encontrada: {path}{RESET}")
    else:
        print(f"{RED}No se encontró ninguna ruta de Office instalada{RESET}")


def view_status():
    print(f"{BLUE}Mostrando estado de licencias...{RESET}")
    run_cscript_command(["/dstatus"])


def remove_key():
    path = detect_office_path()
    if not path:
        print(f"{RED}No se encontró ruta de Office{RESET}")
        return

    key = input(
        f"{YELLOW}Ingrese los últimos 5 dígitos de la clave a desinstalar: {RESET}"
    )
    confirm = input(
        f"{MAGENTA}¿Está seguro de desinstalar la clave {key}? (Y/N): {RESET}"
    )
    if confirm.lower() == "y":
        run_cscript_command([f"/unpkey:{key}"])
        print(f"{GREEN}Comando de eliminación ejecutado{RESET}")
    else:
        print(f"{CYAN}Operación cancelada{RESET}")


def goto_office():
    path = detect_office_path()
    if path:
        print(f"{GREEN}Abriendo carpeta de Office en Explorer...{RESET}")
        # Compatible con PowerShell
        run_command(f"explorer '{path}'")
    else:
        print(f"{RED}No se encontró ruta de Office{RESET}")


def activate_office():
    print(f"{GREEN}Ejecutando script de activación en línea...{RESET}")
    print(f"{YELLOW}Comando: irm https://get.activated.win | iex{RESET}")

    confirm = input(f"{MAGENTA}¿Desea continuar? (Y/N): {RESET}")
    if confirm.lower() != "y":
        print(f"{CYAN}Operación cancelada{RESET}")
        return

    run_command("irm https://get.activated.win | iex")
    print(f"{GREEN}Script ejecutado.{RESET}")


def main_menu():
    try:
        while True:
            print(f"\n{CYAN}=== CLIHELPERJK Menu ==={RESET}")
            print(f"{YELLOW}[1]{RESET} Ver estado de licencia (/dstatus)")
            print(f"{YELLOW}[2]{RESET} Desinstalar clave (/unpkey)")
            print(f"{YELLOW}[3]{RESET} Abrir carpeta Office")
            print(f"{YELLOW}[4]{RESET} Mostrar rutas detectadas")
            print(f"{YELLOW}[5]{RESET} Activar Office")
            print(f"{YELLOW}[6]{RESET} Salir")

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
                activate_office()
            elif choice == "6":
                print(f"{CYAN}Saliendo...{RESET}")
                break
            else:
                print(f"{RED}Opción inválida, intente de nuevo{RESET}")
    except KeyboardInterrupt:
        print(f"\n{CYAN}Interrumpido por usuario. Saliendo...{RESET}")
        return
import os
import sys

# Intentar importación relativa (cuando se ejecuta como paquete).
# Si falla (ejecutando el archivo directamente), ajustar sys.path e importar por nombre de paquete.
try:
    from .office import main_menu
except Exception:
    pkg_root = os.path.dirname(os.path.dirname(__file__))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from clihelperjk.office import main_menu

def main():
    main_menu()

if __name__ == "__main__":
    main()

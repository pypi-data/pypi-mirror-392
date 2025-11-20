# clihelperjk

CLI interactivo para administración básica de Microsoft Office (detección de ruta, /dstatus, /unpkey, abrir carpeta y menú interactivo).

Instalación local:
```bash
pip install .
```

Uso:
- Ejecutar interactivo: python -m clihelperjk
- O script instalado: clihelperjk

Comandos:
- clihelperjk dstatus [--path PATH]
- clihelperjk unpkey [KEY] [--yes] [--path PATH]
- clihelperjk open [--path PATH]
- clihelperjk info
- clihelperjk menu

# PyDNI

Es un módulo educativo de Python que permite validar DNIs y CIFs españoles de forma sencilla y rápida.  
Ideal para proyectos que necesiten comprobar la validez de identificadores fiscales o personales en España.


## Características

- Verificación de DNI (Documento Nacional de Identidad)
- Verificación de CIF (Código de Identificación Fiscal)
- Función unificada `verificar_identificador()` que detecta el tipo automáticamente
- Estructura modular, fácil de integrar en otros proyectos
- Código limpio y compatible con Python 3.10 o superior


## Instalación

```bash
pip install .
```

(Ejecuta este comando en la carpeta donde esté el `setup.py` del paquete.)

Si prefieres usarlo directamente sin instalarlo, puedes importarlo desde el directorio:

```python
from PyDNI import verificar_dni, verificar_cif, verificar_identificador
```


## Uso básico

```python
from PyDNI import verificar_dni, verificar_cif, verificar_identificador

# Verificar un DNI
print(verificar_dni("12345678Z"))   # True

# Verificar un CIF
print(verificar_cif("A58818501"))   # True

# Detección automática
print(verificar_identificador("12345678Z"))   # "DNI válido"
print(verificar_identificador("A58818501"))   # "CIF válido"
```


## Estructura del paquete

```
PyDNI/
├── PyDNI/
│   ├── __init__.py
│   ├── dni.py
│   ├── cif.py
│   └── utils.py
├── setup.py
├── test.py
└── CHANGELOG.md
```


## Requisitos

- Python 3.10 o superior
- No requiere dependencias externas


## Test rápido

Ejecuta el archivo `test.py` incluido:

```bash
python test.py
```

Deberías ver algo como:

```
DNI 12345678Z: True
CIF A58818501: True
Auto (DNI): DNI válido
Auto (CIF): CIF válido
```


## Próximas mejoras

- Soporte para NIE (Número de Identificación de Extranjeros)
- Validación de NIF genérico (personas jurídicas y extranjeras)
- Pruebas unitarias automáticas (pytest)
- Publicación oficial en PyPI

## Autor

**Alberto Gonzalez**  
agonzalezla@protonmail.com  

## Licencia

Este proyecto se distribuye bajo la licencia MIT.  
Consulta el archivo `LICENSE`
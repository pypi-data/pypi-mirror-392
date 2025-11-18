from .dni import verificar_dni
from .cif import verificar_cif
from .nie import verificar_nie
from .nif import verificar_nif
from .utils import verificar_identificador

__all__ = [
    "verificar_dni",
    "verificar_cif",
    "verificar_nie",
    "verificar_nif",
    "verificar_identificador",
]
__version__ = "0.2.0"

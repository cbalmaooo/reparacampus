"""Reloj inyectable (S04).

Producción usa RelojSistema (UTC del servidor). Las pruebas usan RelojFijo para
verificar exactamente 48 h y un instante posterior sin esperar ni tocar el reloj
del sistema.
"""
from datetime import datetime, timedelta, timezone


class RelojSistema:
    def ahora(self):
        return datetime.now(timezone.utc)


class RelojFijo:
    def __init__(self, instante):
        if instante.tzinfo is None:
            raise ValueError("RelojFijo requiere un datetime con zona horaria UTC")
        self.instante = instante

    def ahora(self):
        return self.instante

    def avanzar(self, **kwargs):
        self.instante += timedelta(**kwargs)

from BDD import BDD

class Empresa():
    def __init__(self, direccion, nit, telefono):
        self._direccion = direccion
        self._nit = nit
        self._telefono = telefono

    def get_direccion(self):
        return self._direccion
    def get_nit(self):
        return self._nit
    def get_telefono(self):
        return self._telefono

    def subir(self):
        c = BDD()
        db = c.db()
        data = {
            "Direccion": self.get_direccion(),
            "NIT": self.get_nit(),
            "Telefono": self.get_telefono(),
        }
        db.child("Empresa").set(data)
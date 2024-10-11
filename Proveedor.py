from BDD import BDD

class Proveedor():
    def __init__(self, id, nit, contacto, nombre, direccion):
        self._id = id
        self._nit = nit
        self._contacto = contacto
        self._nombre = nombre
        self._direccion = direccion

    def get_id(self):
        return self._id
    def get_nit(self):
        return self._nit
    def get_contacto(self):
        return self._contacto
    def get_nombre(self):
        return self._nombre
    def get_direccion(self):
        return self._direccion

    def subir(self):
        c = BDD()
        db = c.db()
        data = {
            "Contacto": self.get_contacto(),
            "Direccion": self.get_direccion(),
            "NIT": self.get_nit(),
            "Nombre": self.get_nombre(),
        }
        db.child("Proveedor").child(self.get_id()).set(data)

    def eliminar(self):
        c = BDD()
        db = c.db()
        db.child("Proveedor").child(self.get_id()).remove()
    
    def buscar(self):
        c = BDD()
        db = c.db()
        b = db.child("Proveedor").get()
        bus = 0
        for t in b.each():
            if (t.val()['Nombre'] == self.get_nombre()):
                bus = t.key()
        return(bus)
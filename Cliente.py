from BDD import BDD

class Cliente():
    def __init__(self, id, ci, contacto, nombre):
        self._id = id
        self._ci = ci
        self._contacto = contacto
        self._nombre = nombre

    def get_id(self):
        return self._id
    def get_ci(self):
        return self._ci
    def get_contacto(self):
        return self._contacto
    def get_nombre(self):
        return self._nombre

    def subir(self):
        c = BDD()
        db = c.db()
        data = {
            "CI": self.get_ci(),
            "Contacto": self.get_contacto(),
            "Nombre": self.get_nombre(),
        }
        i = 0 
        b = db.child("Cliente").get()

        for t in b.each():
            if (t.val()['CI'] == self.get_ci()):
                i = 1

        if i == 0:
            db.child("Cliente").child(self.get_id()).set(data)
        return i

    def editar(self):
        c = BDD()
        db = c.db()
        data = {
            "CI": self.get_ci(),
            "Contacto": self.get_contacto(),
            "Nombre": self.get_nombre(),
        }
        db.child("Cliente").child(self.get_id()).set(data)

    def eliminar(self):
        c = BDD()
        db = c.db()
        db.child("Cliente").child(self.get_id()).remove()
    
    def buscar(self):
        c = BDD()
        db = c.db()
        b = db.child("Cliente").get()
        bus = 0
        for t in b.each():
            if (t.val()['CI'] == self.get_ci()):
                bus = t.key()
        return(bus)
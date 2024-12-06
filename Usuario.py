from BDD import BDD

class Usuario:
    def __init__(self, ci, nombre, usuario, contraseña):
        self._ci = ci
        self._nombre = nombre
        self._usuario = usuario
        self._contraseña = contraseña
    
    def get_nombre(self):
        return self._nombre
    def get_ci(self):
        return self._ci
    def get_usuario(self):
        return self._usuario
    def get_contraseña(self):
        return self._contraseña

    def subir(self):
        print("listo")

    def editar(self):
        print("listo")
    
    def eliminar(self, d):
        c = BDD()
        db = c.db()
        db.child("Usuarios").child(d).child(self.get_nombre()).remove()
        print("listo")

    def buscar(self, nom):
        c = BDD()
        db = c.db()

        v = db.child("Usuarios").child("Ventas").get()
        e = db.child("Usuarios").child("Almacenes").get()
        a = db.child("Usuarios").child("Administracion").get()

        n = 0
        for t in v.each():
            if (t.key() == nom):
                n = t.key()
           
        for t in e.each():
            if (t.key() == nom):
                n = t.key()
        
        for t in a.each():
            if (t.key() == nom):
                n = t.key()

        return n
                
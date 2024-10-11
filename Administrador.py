from Usuario import Usuario
from BDD import BDD

class Administrador(Usuario):
    def __init__(self, ci, nombre, usuario, contraseña, nivel):
        super().__init__(ci, nombre, usuario, contraseña)
        self._nivel = nivel
    
    def get_nivel(self):
        return self._nivel

    def subir(self):
        c = BDD()
        db = c.db()

        data = { 
            "CI": super().get_ci(),
            "Nivel": self.get_nivel(),
            "Usuario": super().get_usuario(),
            "Contraseña": super().get_contraseña()
        }

        db.child("Usuarios").child("Administracion").child(super().get_nombre()).set(data)
        return super().subir()
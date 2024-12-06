from Usuario import Usuario
from BDD import BDD

class Vendedor(Usuario):
    def __init__(self, ci, nombre, usuario, contraseña, comision):
        super().__init__(ci, nombre, usuario, contraseña)
        self._comision = comision

    def get_comision(self):
        return self._comision

    def subir(self):
        c = BDD()
        db = c.db()

        data = { 
            "CI": super().get_ci(),
            "Comision": self.get_comision(),
            "Usuario": super().get_usuario(),
            "Contraseña": super().get_contraseña(),
            "DebeCambiarContraseña": True  # Nuevo campo
        }

        db.child("Usuarios").child("Ventas").child(super().get_nombre()).set(data)
        return super().subir()
    
    def editar(self):
        c = BDD()
        db = c.db()

        data = { 
            "CI": super().get_ci(),
            "Comision": self.get_comision(),
            "Usuario": super().get_usuario(),
            "Contraseña": super().get_contraseña(),
            "DebeCambiarContraseña": False  # Nuevo campo
        }

        db.child("Usuarios").child("Ventas").child(super().get_nombre()).set(data)
        return super().editar()
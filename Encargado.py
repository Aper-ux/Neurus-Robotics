from Usuario import Usuario
from BDD import BDD

class EncargadoDeAlmacenes(Usuario):
    def __init__(self, ci, nombre, usuario, contraseña, turno):
        super().__init__(ci, nombre, usuario, contraseña)
        self._turno = turno

    def get_turno(self):
        return self._turno

    def subir(self):
        c = BDD()
        db = c.db()

        data = { 
            "CI": super().get_ci(),
            "Turno": self.get_turno(),
            "Usuario": super().get_usuario(),
            "Contraseña": super().get_contraseña(),
            "DebeCambiarContraseña": True  # Nuevo campo
        }

        db.child("Usuarios").child("Almacenes").child(super().get_nombre()).set(data)
        return super().subir()
    
    def editar(self):
        c = BDD()
        db = c.db()

        data = { 
            "CI": super().get_ci(),
            "Turno": self.get_turno(),
            "Usuario": super().get_usuario(),
            "Contraseña": super().get_contraseña(),
            "DebeCambiarContraseña": False  # Nuevo campo
        }

        db.child("Usuarios").child("Almacenes").child(super().get_nombre()).set(data)
        return super().editar()
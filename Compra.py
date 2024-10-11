from BDD import BDD
from datetime import date

class Compra():
    def __init__(self, id, cantidad, encargado, precio, producto, proveedor,total):
        self._id = id
        self._cantidad = cantidad
        self._encargado = encargado
        self._precio = precio
        self._producto = producto
        self._proveedor = proveedor
        self._total = total

    def get_id(self):
        return self._id
    def get_cantidad(self):
        return self._cantidad
    def get_encargado(self):
        return self._encargado
    def get_precio(self):
        return self._precio
    def get_producto(self):
        return self._producto
    def get_proveedor(self):
        return self._proveedor
    def get_total(self):
        return self._total
    
    def subir(self):
        c = BDD()
        db = c.db()
        today = date.today()
        t = str(today)
        data = {
            "Cantidad": self.get_cantidad(),
            "Encargado": self.get_encargado(),
            "Fecha": t,
            "Precio": self.get_precio(),
            "Productos": self.get_producto(),
            "Proveedor": self.get_proveedor(),
            "Total": self.get_total(),
        }
        db.child("Compra").child(self.get_id()).set(data)
    
    def eliminar(self):
        c = BDD()
        db = c.db()
        db.child("Compra").child(self.get_id()).remove()
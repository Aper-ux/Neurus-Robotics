from BDD import BDD
from datetime import date

class Venta():
    def __init__(self, id, cantidad, cliente, producto, total, vendedor):
        self._id = id
        self._cantidad = cantidad
        self._cliente = cliente
        self._producto = producto
        self._total = total
        self._vendedor = vendedor

    def get_id(self):
        return self._id
    def get_cantidad(self):
        return self._cantidad
    def get_cliente(self):
        return self._cliente
    def get_producto(self):
        return self._producto
    def get_total(self):
        return self._total
    def get_vendedor(self):
        return self._vendedor

    def subir(self):
        c = BDD()
        db = c.db()
        today = date.today()
        t = str(today)
        data = {
            "Cantidad": self.get_cantidad(),
            "Cliente": self.get_cliente(),
            "Fecha": t,
            "Productos": self.get_producto(),
            "Total": self.get_total(),
            "Vendedor": self.get_vendedor(),
        }
        db.child("Venta").child(self.get_id()).set(data)

    def eliminar(self):
        c = BDD()
        db = c.db()
        db.child("Venta").child(self.get_id()).remove()
from BDD import BDD

class Producto():
    def __init__(self, id, descripcion, precio, stock, tipo):
        self._id = id
        self._descripcion = descripcion
        self._precio = precio
        self._stock = stock
        self._tipo = tipo

    def get_id(self):
        return self._id
    def get_descripcion(self):
        return self._descripcion
    def get_precio(self):
        return self._precio
    def get_stock(self):
        return self._stock
    def get_tipo(self):
        return self._tipo

    def subir(self):
        c = BDD()
        db = c.db()
        data = {
            "Descripcion": self.get_descripcion(),
            "Precio": self.get_precio(),
            "Stock": self.get_stock(),
            "Tipo": self.get_tipo(),
        }
        db.child("Producto").child(self.get_id()).set(data)

    def eliminar(self):
        c = BDD()
        db = c.db()
        db.child("Producto").child(self.get_id()).remove()
    
    def buscar(self):
        c = BDD()
        db = c.db()
        b = db.child("Producto").get()
        bus = 0
        for t in b.each():
            if (t.key() == self.get_id()):
                bus = t.key()
        return(bus)
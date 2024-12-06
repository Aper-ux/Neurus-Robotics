from logging import warning
from flask import Flask, render_template, redirect, url_for, request, session, jsonify

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta

from BDD import BDD
import numpy as np
import os
from reportlab.platypus import (SimpleDocTemplate, PageBreak, Image, Spacer, Paragraph, Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A2, A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect, String, Group, Line
import hashlib

import logging
from datetime import datetime


from arrow import utcnow
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import *
from reportlab.pdfgen import canvas

from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.barcharts import VerticalBarChart

from Usuario import Usuario
from Vendedor import Vendedor
from Administrador import Administrador
from Encargado import EncargadoDeAlmacenes
from Cliente import Cliente
from Proveedor import Proveedor
from Producto import Producto
from Empresa import Empresa
from Venta import Venta
from Compra import Compra

class main:
    def __init__(self, i, p, c, pc, cc, prc):
        self.i = i
        self.p = p
        self.c = c
        self.pc = pc
        self.cc = cc
        self.prc = prc

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ignacio.agramont.11@gmail.com'
app.config['MAIL_PASSWORD'] = 'ekgp nnmu bwlr zkpy'
app.config['MAIL_DEFAULT_SENDER'] = 'ignacio.agramont.11@gmail.com'

mail = Mail(app)

categorias = ["Administracion", "Ventas", "Almacenes"]
roles = ["Administracion", "Almacenes", "Ventas","root"]
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(email, salt="password-reset-salt")

def send_reset_email(to_email, reset_url):
    msg = Message("Recuperación de contraseña", recipients=[to_email])
    msg.body = f"Hola, usa este enlace para restablecer tu contraseña: {reset_url}. Este enlace expira en 1 hora."
    mail.send(msg)

def sanitize_token(token):
    # Reemplazar caracteres problemáticos por caracteres seguros
    return token.replace('.', '_').replace('-', '_')

def hash_token(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    db = BDD().db()

    roles = ["Administracion", "Almacenes", "Ventas"]
    usuario_encontrado = None
    categoria_encontrada = None

    for role in roles:
        usuarios = db.child("Usuarios").child(role).get().val()
        if usuarios:
            for nombre, datos in usuarios.items():
                if datos.get("Usuario") == email:
                    usuario_encontrado = nombre
                    categoria_encontrada = role
                    break
        if usuario_encontrado:
            break

    if not usuario_encontrado:
        return render_template('acceso.html', message="Usuario no encontrado.", success=False)

    token = generate_reset_token(email)
    sanitized_token = sanitize_token(token)
    hashed_token = hash_token(sanitized_token)
    expiration = (datetime.utcnow() + timedelta(hours=1)).isoformat()

    db.child("password_reset_tokens").child(hashed_token).set({
        "user_email": email,
        "categoria": categoria_encontrada,
        "nombre_usuario": usuario_encontrado,
        "expiration": expiration
    })

    reset_url = f"http://127.0.0.1:5000/reset-password/{sanitized_token}"
    send_reset_email(email, reset_url)

    return render_template('acceso.html', message="Correo de recuperación enviado.", success=True)


@app.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    db = BDD().db()

    # Obtener los datos del token desde Firebase
    hashed_token = hash_token(token)
    token_data = db.child("password_reset_tokens").child(hashed_token).get().val()

    if not token_data:
        return render_template('Reset.html', token=token, success=False, message="Token inválido o expirado.")

    # Verificar si el token ha expirado
    expiration = datetime.fromisoformat(token_data["expiration"])
    if datetime.utcnow() > expiration:
        db.child("password_reset_tokens").child(hashed_token).set(None)
        return render_template('Reset.html', token=token, success=False, message="El token ha expirado.")

    # Obtener datos del token
    email = token_data["user_email"]
    categoria = token_data["categoria"]
    nombre_usuario = token_data["nombre_usuario"]

    # Obtener la nueva contraseña desde el formulario
    new_password = request.form.get('password')
    if not new_password:
        return render_template('Reset.html', token=token, success=False, message="La nueva contraseña es requerida.")

    # Generar el hash de la nueva contraseña utilizando el correo como salt
    salt = email.strip()
    hashed_password = encriptar_contrasena(new_password.strip(), salt)

    # Actualizar la contraseña en Firebase
    db.child("Usuarios").child(categoria).child(nombre_usuario).update({"Contraseña": hashed_password})

    # Eliminar el token usado
    db.child("password_reset_tokens").child(hashed_token).set(None)

    return render_template('Reset.html', token=token, success=True, message="Contraseña actualizada con éxito.")


@app.route('/reset-password/<token>', methods=['GET'])
def reset_password_form(token):
    sanitized_token = sanitize_token(token)
    hashed_token = hash_token(sanitized_token)

    db = BDD().db()
    token_data = db.child("password_reset_tokens").child(hashed_token).get().val()

    if not token_data:
        return render_template('Reset.html', success=False, message="Token inválido o expirado.")

    return render_template('Reset.html', token=token)

# LogIn
prod = []
cant = []

prodc = []
cantc = []
prec = []
i = main(0,prod, cant, prodc, cantc, prec)
pro = main(i.i,prod, cant, prodc, cantc, prec)
@app.route('/')
def Login():
    pro.p = []
    pro.c = []
    pro.pc = []
    pro.cc = []
    pro.prc = []
    return render_template("Acceso.html")

def verificar_contrasena(contrasena, salt, hash_almacenado):
    hash_object = hashlib.sha256()
    hash_object.update((salt + contrasena).encode('utf-8'))
    hash_calculado = hash_object.hexdigest()
    return hash_calculado == hash_almacenado

# Configuración básica del logging
logging.basicConfig(
    filename="registro_logs.txt",  # Nombre del archivo
    level=logging.INFO,            # Nivel mínimo de los mensajes que se registrarán
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del mensaje
    datefmt="%Y-%m-%d %H:%M:%S",   # Formato de la fecha y hora
)

# Ejemplo de funciones que generan logs
def ejecutar_proceso():
    try:
        logging.info("Inicio del proceso.")
        # Código que puede generar excepciones
        resultado = 10 / 0  # Esto generará un error
        logging.info(f"Resultado del proceso: {resultado}")
    except ZeroDivisionError as e:
        logging.error(f"Error en el proceso: {e}")
    finally:
        logging.info("Fin del proceso.")    

@app.route('/Login/<error>', methods = ['POST'])
def LoginE(error):
    return render_template("Acceso.html", error=error)

def obtener_ruta_por_division(division, cambiar_contrasena=False):
    """
    Devuelve la ruta correspondiente según la división o contexto.
    
    Args:
        division (str): La división del usuario (Ventas, Almacenes, Administracion).
        cambiar_contrasena (bool): Indica si el usuario debe cambiar su contraseña.
        
    Returns:
        str: La ruta correspondiente.
    """
    match division:
        case "Ventas":
            return url_for('CambiarContraseña') if cambiar_contrasena else url_for('Ventas')
        case "Almacenes":
            return url_for('CambiarContraseña') if cambiar_contrasena else url_for('Productos')
        case "Administracion":
            return url_for('CambiarContraseña') if cambiar_contrasena else url_for('Usuarios')
        case "root":
            return url_for('Usuarios')
        case _:
            raise ValueError(f"División no reconocida: {division}")
        
def log_user_activity(usuario, area, exito=True):
    """
    Registra la actividad del usuario en un archivo de logs y en consola.
    """
    estado = "Inicio de sesión exitoso" if exito else "Intento de inicio de sesión fallido"
    mensaje = f"{estado}: Usuario={usuario}, Área={area}"
    print(mensaje)  # Mostrar en consola
    logging.info(mensaje)  # Guardar en archivo de logs


# Ruta del archivo donde se guardarán los registros
user_logs_file = 'user_logs.txt'

def guardar_registro(usuario, division, estado, ip, url):
    """
    Guarda un registro del inicio de sesión en el archivo de logs.
    
    Args:
        usuario (str): Nombre del usuario.
        division (str): División a la que pertenece (Ventas, Administración, etc.).
        estado (str): Estado del inicio de sesión (Exitoso o Fallido).
        ip (str): IP desde la que se realiza el intento de inicio de sesión.
        url (str): URL completa de la solicitud.
    """
    with open(user_logs_file, 'a') as log_file:
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"{fecha_hora} - IP: {ip} - URL: {url} - Usuario: {usuario}, División: {division}, Estado: {estado}\n")

import re

@app.route('/CambiarContraseña', methods=['POST', 'GET'])
def CambiarContraseña():
    print("Ingresando a CambiarContraseña")
    try:
        # Validar si el usuario está en sesión
        user = session.get('name')
        div = session.get('div')

        if not user or div not in ["Ventas", "Almacenes", "Administracion"]:
            error = "Sesión no válida. Inicie sesión nuevamente."
            return redirect(f'/Login?error={error}')

        # Conexión a la base de datos
        c = BDD()
        db = c.db()

        # Obtener datos del usuario desde la base de datos
        usuario = db.child("Usuarios").child(div).child(user).get().val()
        error = None

        if request.method == 'POST':
            nueva_contrasena = request.form.get('NuevaContraseña')
            confirmar_contrasena = request.form.get('ConfirmarContraseña')

            # Validar contraseñas
            if nueva_contrasena and confirmar_contrasena:
                # Validar formato de la contraseña
                mensaje_error = validar_contrasena(nueva_contrasena)
                if mensaje_error:
                    error = mensaje_error
                elif nueva_contrasena != confirmar_contrasena:
                    error = "Las contraseñas no coinciden. Inténtelo nuevamente."
                else:
                    # Actualizar contraseña en la base de datos
                    db.child("Usuarios").child(div).child(user).update({
                        "Contraseña": encriptar_contrasena(nueva_contrasena, usuario["Usuario"]),
                        "DebeCambiarContraseña": False
                    })
                    mensaje = "Contraseña cambiada exitosamente. Inicie sesión nuevamente."
                    ruta = obtener_ruta_por_division(div)
                    return redirect(ruta, code=307)
            else:
                error = "Por favor complete ambos campos."

        # Renderizar la página inicial para cambiar contraseña
        return render_template("CambiarContraseña.html", usuario=usuario, error=error)

    except Exception as e:
        print(f"Error en CambiarContraseña: {e}")
        return redirect('/Login?error=Error inesperado en el servidor.')

def validar_contrasena(contrasena):
    """
    Valida que la contraseña cumpla con los siguientes requisitos:
    - Mínimo 12 caracteres
    - Al menos 1 letra mayúscula
    - Al menos 1 letra minúscula
    - Al menos 1 número
    - Al menos 1 carácter especial
    """
    if len(contrasena) < 12:
        return "La contraseña debe tener al menos 12 caracteres."
    if not re.search(r"[A-Z]", contrasena):
        return "La contraseña debe contener al menos una letra mayúscula."
    if not re.search(r"[a-z]", contrasena):
        return "La contraseña debe contener al menos una letra minúscula."
    if not re.search(r"[0-9]", contrasena):
        return "La contraseña debe contener al menos un número."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", contrasena):
        return "La contraseña debe contener al menos un carácter especial."
    return None  # Contraseña válida


@app.route('/Ingresar', methods=['POST'])
def Ingresar():
    try:
        # Conexión a la base de datos
        print("Estableciendo conexión con la base de datos...")
        c = BDD()
        db = c.db()
        print("Conexión con la base de datos establecida.")

        # Obtención de datos del formulario
        us = request.form.get('Usuario', None)
        pas = request.form.get('Contraseña', None)
        print(f"Usuario ingresado: {us}, Contraseña ingresada: {pas}")

        # Obtener la IP y la URL completa del cliente
        ip_cliente = request.remote_addr
        url_solicitud = request.url
        print(f"IP del cliente: {ip_cliente}")
        print(f"URL de la solicitud: {url_solicitud}")

        if not us or not pas:
            print("Usuario o contraseña no proporcionados.")
            guardar_registro(us, "Desconocido", "Fallido: Usuario o contraseña no proporcionados", ip_cliente, url_solicitud)
            return redirect('/Login/error', code=307)

        # Validar intentos fallidos
        if i.i >= 3:
            print("Máximo de intentos alcanzado.")
            guardar_registro(us, "Desconocido", "Fallido: Máximo de intentos alcanzado", ip_cliente, url_solicitud)
            return redirect('/Login/error3', code=307)

        # Divisiones de usuarios
        print("Obteniendo datos de 'Ventas', 'Almacenes' y 'Administracion'...")
        divisiones = {
            "Ventas": db.child("Usuarios").child("Ventas").get(),
            "Almacenes": db.child("Usuarios").child("Almacenes").get(),
            "Administracion": db.child("Usuarios").child("Administracion").get(),
            "root": db.child("Usuarios").child("root").get()
        }

        for division, datos in divisiones.items():
            if datos:
                for t in datos.each():
                    usuario = t.val()
                    #print(f"Procesando nodo de '{division}': {usuario}")

                    if usuario and usuario.get('Usuario') == us:
                        # Usar el correo como salt
                        salt = usuario['Usuario'].strip()
                        #print(f"Salt utilizado (correo): {salt}")

                        # Generar el hash
                        generated_hash = encriptar_contrasena(pas.strip(), salt)
                        #print(f"Hash generado para validación: {generated_hash}")
                        #print(f"Hash almacenado: {usuario['Contraseña']}")

                        if generated_hash == usuario['Contraseña']:
                            session['name'] = t.key()
                            session['div'] = division
                            print(f"Inicio de sesión exitoso en '{division}'.")
                            
                            # Revisamos si el usuario debe cambiar su contraseña
                            cambiar_contrasena = usuario.get('DebeCambiarContraseña', False)
                            guardar_registro(us, division, "Exitoso", ip_cliente, url_solicitud)
                            return redirect(obtener_ruta_por_division(division, cambiar_contrasena), code=307)
                        else:
                            print("Contraseña incorrecta.")

        # Si no se encontró al usuario
        i.i += 1
        print(f"Intento fallido {i.i}. Usuario no encontrado.")
        guardar_registro(us, "Desconocido", f"Fallido: Intento {i.i}", ip_cliente, url_solicitud)
        return redirect('/Login/error', code=307)

    except Exception as e:
        print(f"Error en el proceso de inicio de sesión: {e}")
        guardar_registro("Error", "Sistema", f"Excepción: {str(e)}", request.remote_addr, request.url)
        return redirect('/Login/error', code=307)


@app.route('/Desbloquear', methods=['POST'])
def Desbloquear():
    llave = request.form['llave']
    if llave == "hq(f>X3X9LQg4B9Qn2Z#":
        i.i = 2
        return redirect('/')
    else:
        error = "error3"
        return redirect(('/Login/' + error), code=307)


# Venta
@app.route("/Ventas", methods = ['POST','GET'])
def Ventas():
    c = BDD()
    db = c.db()
    d = db.child("Cliente").get()
    bdp = db.child("Producto").get()
    i = db.child("Empresa").get()
    n = 0
    for t in d.each():
        n = int(t.key()) + 1 
    ns = "00" + str(n) 

    if request.method == "POST":
        s = 1
    elif request.method == "GET":
        s = 0
    a = dict(zip(pro.p, pro.c))
    return render_template("Ventas.html", s = s, n = ns, bdp=bdp, a=a, i=i, c=d)

@app.route("/Ventas/Prod", methods = ['POST'])
def Prod():
    c = BDD()
    db = c.db()

    codigo = request.form['Pr']
    cantidad = request.form['c']
    
    d = db.child("Cliente").get()
    bdp = db.child("Producto").get()
    i = db.child("Empresa").get()

    n = 0
    for t in d.each():
        n = int(t.key()) + 1 
    ns = "00" + str(n) 

    d0 = db.child("Producto").child(codigo).get()
    if int(cantidad) > int(d0.val()['Stock']):
        a = dict(zip(pro.p, pro.c))
        d = db.child("Producto").get()
        i = db.child("Empresa").get()
        n = 0
        for t in d.each():
            n = int(t.key()) + 1 
        ns = "000" + str(n) 
        return render_template("Productos.html", data = d, n = ns, b = codigo, i=i, c=d)

    pro.p.append(codigo)
    pro.c.append(cantidad)
    a = dict(zip(pro.p, pro.c))
    print(a)
    
    
    return render_template("Ventas.html", s = 0, n = ns, bdp=bdp, a = a, i=i, c=d)

@app.route("/Ventas/venta", methods = ['POST','GET'])
def venta():
    c = BDD()
    db = c.db()
    d = db.child("Venta").get()
    n = 0
    for t in d.each():
        n = int(t.key()) + 1

    id = "000" + str(n)
    cantidad = str(pro.c)
    ci = request.form['Cliente']
    clie = Cliente('',ci,'','')
    cliente = clie.buscar()
    vendedor = session['name']
    producto = str(pro.p)
    print(len(producto))
    if len(producto) == 2:
        return redirect("/Ventas")

    total = 0
    cont = 0
    cont2 = 0
    d2 = db.child("Producto").get()
    for j in d2.each():
        cont = 0
        for x in range(0,len(pro.p)):
            cont += 1
            cont2 = 0
            for k in range(0,len(pro.c)):
                cont2 += 1
                if j.key() == pro.p[x]:
                    if cont == cont2:
                        total += j.val()['Precio'] * int(pro.c[k])

    ven = Venta(id,cantidad, cliente, producto, total, vendedor)
    ven.subir()

    d0 = db.child("Venta").child(id).get() 
    d1 = db.child("Cliente").child(d0.val()['Cliente']).get()
    d2 = db.child("Producto").get()
    d3 = db.child("Empresa").get() 

    clienteF = d1.val()['Nombre']
    ciF = d1.val()['CI']

    a = dict(zip(pro.p, pro.c))
    
    for z in a:
        for q in d2.each():
            if (z == q.key()):
                st = q.val()['Stock']
                sto = int(st) - int(a.get(z))
                p3 = Producto(q.key(),q.val()['Descripcion'],q.val()['Precio'],str(sto),q.val()['Tipo'])
                p3.subir()

    impr =[["CODIGO       ","DESCRIPCION                               ","PRECIO       ","CANTIDAD       ","TOTAL   "]]
    totalF = 0
    neto = 0
    for t in a:
        codF = t
        cantF = a.get(t)
        totalF = 0
        for k in d2.each():
            if codF == k.key():
                descrF = k.val()['Descripcion']
                precF = k.val()['Precio']
                totalF += precF * int(cantF)
                neto += totalF
                lis = [codF, descrF, precF, cantF, totalF]
                impr.append(lis)
                print(codF, descrF, precF, cantF, totalF)
    # print(impr)
    # print(neto)

    ############# inicia conversion numero a literal ##############3
    def numero_to_letras(numero):
        global literal
        indicador = [("",""),("MIL","MIL"),("MILLON","MILLONES"),("MIL","MIL"),("BILLON","BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero)*100))
        contador = 0
        numero_letras = ""
        while entero >0:
            a = entero % 1000
            if contador == 0:
                en_letras = convierte_cifra(a,1).strip()
            else :
                en_letras = convierte_cifra(a,0).strip()
            if a==0:
                numero_letras = en_letras+" "+numero_letras
            elif a==1:
                if contador in (1,3):
                    numero_letras = indicador[contador][0]+" "+numero_letras
                else:
                    numero_letras = en_letras+" "+indicador[contador][0]+" "+numero_letras
            else:
                numero_letras = en_letras+" "+indicador[contador][1]+" "+numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        numero_letras = numero_letras+" con " + str(decimal) +"/100"
        print ('numero: ',numero)
        print (numero_letras)
        literal=numero_letras
    def convierte_cifra(numero,sw):
        lista_centana = ["",("CIEN","CIENTO"),"DOSCIENTOS","TRESCIENTOS","CUATROCIENTOS","QUINIENTOS","SEISCIENTOS","SETECIENTOS","OCHOCIENTOS","NOVECIENTOS"]
        lista_decena = ["",("DIEZ","ONCE","DOCE","TRECE","CATORCE","QUINCE","DIECISEIS","DIECISIETE","DIECIOCHO","DIECINUEVE"),
					("VEINTE","VEINTI"),("TREINTA","TREINTA Y "),("CUARENTA" , "CUARENTA Y "),
					("CINCUENTA" , "CINCUENTA Y "),("SESENTA" , "SESENTA Y "),
					("SETENTA" , "SETENTA Y "),("OCHENTA" , "OCHENTA Y "),
					("NOVENTA" , "NOVENTA Y ")
				]
        lista_unidad = ["",("UN" , "UNO"),"DOS","TRES","CUATRO","CINCO","SEIS","SIETE","OCHO","NUEVE"]
        centena = int (numero / 100)
        decena = int((numero -(centena * 100))/10)
        unidad = int(numero - (centena * 100 + decena * 10))
        texto_centena = ""
        texto_decena = ""
        texto_unidad = ""
        texto_centena = lista_centana[centena]
        if centena == 1:
            if (decena + unidad)!=0:
                texto_centena = texto_centena[1]
            else :
                texto_centena = texto_centena[0]
        texto_decena = lista_decena[decena]
        if decena == 1 :
            texto_decena = texto_decena[unidad]
        elif decena > 1 :
            if unidad != 0 :
                texto_decena = texto_decena[1]
            else:
                texto_decena = texto_decena[0]
        if decena != 1:
            texto_unidad = lista_unidad[unidad]
            if unidad == 1:
                texto_unidad = texto_unidad[sw]
        return "%s %s %s" %(texto_centena,texto_decena,texto_unidad)
    numero_to_letras(neto)
    ########### hasta aqui conversion numero a literal ##############3###############
    
    doc = SimpleDocTemplate("C:/Neurus Robotics/static/Factura.pdf", pagesize = A4)
    story=[]

    d = Drawing(0,80)
    d.add(String(0,80,'NEURUS ROBOTICS', fontSize=15, fillColor=colors.navy,fontName="Helvetica-Bold"))
    d.add(String(290,80,'FACTURA Nro. ', fontSize=13, fillColor=colors.black,fontName="Helvetica-Bold"))
    d.add(String(383,80,id ,fontSize=11, fillColor=colors.black,fontName="Helvetica-Bold"))
    d.add(String(0,65,'El Alto, La Paz - Bolivia ' ,fontSize=10, fillColor=colors.black,fontName="Helvetica-Bold"))
    d.add(String(0,50, d3.val()['Direccion'],fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d.add(String(0,35,'Telefono: ',fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d.add(String(47,35, d3.val()['Telefono'] ,fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d.add(String(0,20,'N.I.T. : ',fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d.add(String(40,20, d3.val()['NIT'] ,fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d.add(String(0,0, 'Cliente: ',fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d.add(String(40,0,clienteF ,fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d.add(String(300,0, 'NIT/CI:',fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d.add(String(340,0,ciF ,fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
    fechaReporte = fecha.replace("-", "de")
    d.add(String(290,65, fechaReporte ,fontSize=10, fillColor=colors.black,fontName="Helvetica-Bold"))
    d.add(String(290,50, 'Expedido por: ' ,fontSize=10, fillColor=colors.black,fontName="Helvetica-Bold"))      
    d.add(String(360,50, session['name'] ,fontSize=10, fillColor=colors.black,fontName="Helvetica-Bold"))   

    story.append(d)
    story.append(Spacer(0,15))

    tabla2 = Table(data = impr,
              style = [
                       ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                       ('BOX',(0,0),(-1,-1),2,colors.grey),
                       ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                       ('BACKGROUND',(0,1), (-1,-1), colors.lavender),
                       ]
              )
    story.append(tabla2)
    story.append(Spacer(0,15))

    d22 = Drawing(0,50)
    d22.add(String(360,50, 'Total: ' ,fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d22.add(String(390,50, str(neto) ,fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d22.add(String(2,20,'Son ',fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    d22.add(String(30,20,literal,fontSize=11, fillColor=colors.black,fontName="Helvetica"))
    story.append(d22)
    doc.build(story)
    os.startfile("C:/Neurus Robotics/static/Factura.pdf")
    pro.p = []
    pro.c = []
    return redirect("/Ventas")

@app.route("/Ventas/AgregarClienteF", methods = ['POST'])
def AgregarClienteF():
    id = request.form['Id']
    ci = request.form['CI']
    c = request.form['Contacto']
    n = request.form['Nombre']
    cliente = Cliente(id,ci,c,n)
    cliente.subir()
    return redirect("/Ventas")

@app.route("/Ventas/limpiar", methods = ['POST'])
def limpiar():
    pro.p = []
    pro.c = []    
    return redirect("/Ventas")

# Registro de ventas

@app.route("/Ventas/RV", methods = ['POST','GET'])
def RV():
    c = BDD()
    db = c.db()
    d = db.child("Venta").get()
    c = db.child("Cliente").get()
    i = db.child("Empresa").get()
    return render_template("RV.html", data = d, i=i, c=c, b=0, m=0, a = 0, p1 = 0)

@app.route("/Ventas/RV/BusquedaFV", methods = ['POST','GET'])
def BFV():
    c = BDD()
    db = c.db()
    d = db.child("Venta").get()
    c = db.child("Cliente").get()
    i = db.child("Empresa").get()

    b = request.form['fecha']
    return render_template("RV.html", data = d, i=i, c=c, b=b, m = 0, a = 0, p1 = 0)

@app.route("/Ventas/RV/BusquedaMV", methods = ['POST','GET'])
def BMV():
    c = BDD()
    db = c.db()
    d = db.child("Venta").get()
    c = db.child("Cliente").get()
    i = db.child("Empresa").get()

    m = request.form['mes']
    print(m)
    return render_template("RV.html", data = d, i=i, c=c, b=0, m=m, a = 0, p1 = 0)

@app.route("/Ventas/RV/DetallesVenta", methods = ['POST','GET'])
def RVdetalles():
    c = BDD()
    db = c.db()
    d = db.child("Venta").get()
    c = db.child("Cliente").get()
    i = db.child("Empresa").get()

    venta = request.form['bbb']

    prods = ""
    cants = ""
    for t in d.each():
        if t.key() == venta:
            prods = t.val()['Productos']
            cants = t.val()['Cantidad']

    productos = prods.split(',')
    cantidades = cants.split(',')

    a = dict(zip(productos, cantidades))
    p1 = db.child("Producto").get()

    for x in a:
        for t in p1.each():
            if t.key() in x:
                print(t.key(),t.val()['Descripcion'],a.get(x),t.val()['Precio'])

    return render_template("RV.html", data = d, i=i, c=c, b=0, m=0, a = a, p1 = p1, bbb=venta)

@app.route("/Ventas/RV/EliminarVenta", methods = ['POST','GET'])
def EliminarVenta():
    venta = request.form['bbbb']
    
    ven = Venta(venta,"","","","","")
    ven.eliminar()

    return redirect("/Ventas/RV")

# Clientes
@app.route("/Clientes", methods = ['POST','GET'])
def Clientes():
    c = BDD()
    db = c.db()
    d = db.child("Cliente").get()
    i = db.child("Empresa").get()
    n = 0
    for t in d.each():
        n = int(t.key()) + 1 
    ns = "00" + str(n) 

    return render_template("Clientes.html", data = d, n = ns, b = 0, i=i)

@app.route("/Clientes/AgregarCliente", methods = ['POST'])
def AgregarCliente():
    id = request.form['Id']
    ci = request.form['CI']
    c = request.form['Contacto']
    n = request.form['Nombre']
    cliente = Cliente(id,ci,c,n)
    j = cliente.subir()
    if j == 0:
        return redirect("/Clientes")
    elif j == 1:
        c = BDD()
        db = c.db()
        d = db.child("Cliente").get()
        i = db.child("Empresa").get()
        n = 0
        for t in d.each():
            n = int(t.key()) + 1 
        ns = "00" + str(n)
        return render_template("Clientes.html", data = d, n = ns, b = 0, i=i, j=j)


@app.route("/Clientes/EditarCliente", methods = ['POST'])
def EditarCliente():
    id = request.form['Id']
    ci = request.form['CI']
    c = request.form['Contacto']
    n = request.form['Nombre']
    cliente = Cliente(id,ci,c,n)
    cliente.editar()
    return redirect("/Clientes")

@app.route("/Clientes/EliminarCliente", methods = ['POST'])
def EliminarCliente():
    id = request.form['Id']
    cliente = Cliente(id,'','','')
    cliente.eliminar()
    return redirect("/Clientes")

@app.route("/Clientes/BuscarCliente", methods = ['POST'])
def BuscarCliente():
    ci = request.form['c']
    cliente = Cliente('',ci,'','')
    b = cliente.buscar()

    c = BDD()
    db = c.db()
    d = db.child("Cliente").get()
    i = db.child("Empresa").get()
    n = 0
    for t in d.each():
        n = int(t.key()) + 1 
    ns = "00" + str(n) 

    return render_template("Clientes.html", data = d, n = ns, b = b, i=i)

# Productos
@app.route("/Productos", methods = ['POST','GET'])
def Productos():
    c = BDD()
    db = c.db()
    d = db.child("Producto").get()
    i = db.child("Empresa").get()
    n = 0
    for t in d.each():
        n = int(t.key()) + 1 
    ns = "000" + str(n) 

    if request.method == "POST":
        s = 1
    elif request.method == "GET":
        s = 0
    return render_template("Productos.html", data = d, n = ns, b = 0, s = s, i=i)

@app.route("/Productos/AgregarEditarProducto", methods = ['POST'])
def AgregarEditarProducto():
    id = request.form['Id']
    d = request.form['Descripcion']
    p = request.form['Precio']
    s = request.form['Stock']
    t = request.form['Tipo']
    p2 = float(p)
    producto = Producto(id,d,p2,s,t)
    producto.subir()
    return redirect("/Productos")

@app.route("/Productos/EliminarProducto", methods = ['POST'])
def EliminarProducto():
    id = request.form['Id']
    producto = Producto(id,'','','','')
    producto.eliminar()
    return redirect("/Productos")

@app.route("/Productos/BuscarProducto", methods = ['POST'])
def BuscarProducto():
    cod = request.form['cod']
    producto = Producto(cod,'','','','')
    b = producto.buscar()

    c = BDD()
    db = c.db()
    d = db.child("Producto").get()
    i = db.child("Empresa").get()

    n = 0
    for t in d.each():
        n = int(t.key()) + 1 
    ns = "000" + str(n) 

    return render_template("Productos.html", data = d, n = ns, b = b, i=i)

# Proveedores
@app.route("/Proveedores", methods = ['POST','GET'])
def Proveedores():
    c = BDD()
    db = c.db()
    d = db.child("Proveedor").get()
    i = db.child("Empresa").get()

    n = 0
    for t in d.each():
        n = int(t.key()) + 1 
    ns = "000" + str(n) 

    return render_template("Proveedores.html", data = d, n = ns, b = 0, i = i)

@app.route("/Proveedores/AgregarEditarProveedor", methods = ['POST'])
def AgregarEditarProveedor():
    id = request.form['Id']
    nit = request.form['NIT']
    c = request.form['Contacto']
    n = request.form['Nombre']
    d = request.form['Direccion']
    proveedor = Proveedor(id,nit,c,n,d)
    proveedor.subir()
    return redirect("/Proveedores")

@app.route("/Proveedores/EliminarProveedor", methods = ['POST'])
def EliminarProveedor():
    id = request.form['Id']
    proveedor = Proveedor(id,'','','','')
    proveedor.eliminar()
    return redirect("/Proveedores")

@app.route("/Proveedores/BuscarProveedor", methods = ['POST'])
def BuscarProveedor():
    nom = request.form['nom']
    proveedor = Proveedor('','','',nom,'')
    b = proveedor.buscar()

    c = BDD()
    db = c.db()
    d = db.child("Proveedor").get()
    i = db.child("Empresa").get()
    n = 0
    for t in d.each():
        n = int(t.key()) + 1 
    ns = "000" + str(n) 

    return render_template("Proveedores.html", data = d, n = ns, b = b, i=i)

# Compras
@app.route("/Compras", methods = ['POST','GET'])
def Compras():
    c = BDD()
    db = c.db()
    bdp = db.child("Producto").get()
    i = db.child("Empresa").get()
    prov = db.child("Proveedor").get()

    a = dict(zip(pro.p, pro.c))
    
    return render_template("Compras.html", bdp=bdp, a=a, i=i, prov=prov)

@app.route("/Compras/Prodc", methods = ['POST'])
def Prodc():
    codigo = request.form['Pr']
    precio = request.form['Pc']
    cantidad = request.form['c']

    pro.pc.append(codigo)
    pro.cc.append(int(cantidad))
    pro.prc.append(float(precio))

    dupl = 0
    for k in range(len(pro.pc)):
        if (pro.pc[k] == codigo):
            dupl += 1
            if (dupl > 1):
                return redirect("/Compras/limpiarc")

    a = dict(zip(pro.pc, pro.cc))

    c = BDD()
    db = c.db()
    bdp = db.child("Producto").get()
    i = db.child("Empresa").get()
    prov = db.child("Proveedor").get()

    for z in a:
        for q in bdp.each():
            if (z == q.key()):
                st = q.val()['Stock']
                sto = int(st) + int(a.get(z))
                p3 = Producto(q.key(),q.val()['Descripcion'],q.val()['Precio'],str(sto),q.val()['Tipo'])
                p3.subir()
    return render_template("Compras.html", bdp=bdp, a=a, prc = pro.prc, i=i, prov=prov)

@app.route("/Compras/compra", methods=['POST'])
def compra():
    c = BDD()
    db = c.db()
    d = db.child("Compra").get()
    n = 0

    for t in d.each():
        n = int(t.key()) + 1

    id = "000" + str(n)
    cantidad = str(pro.cc)
    encargado = session['name']
    precio = str(pro.prc)
    producto = str(pro.pc)
    prov = request.form['Proveedor']
    prove = Proveedor('', '', '', prov, '')

    # Buscar proveedor
    proveedor = prove.buscar()
    if proveedor is None:
        print("Error: Proveedor no encontrado.")
        return redirect("/Compras/error_proveedor", code=307)

    # quiza sea bueno quitarlo
    if len(producto) <= 2:  # Ajustado para mayor claridad
        return redirect("/Compras")

    tot = np.multiply(pro.cc, pro.prc)
    total = sum(tot)

    com = Compra(id, cantidad, encargado, precio, producto, proveedor, total)
    com.subir()

    # Reiniciar variables de producto
    pro.pc = []
    pro.cc = []
    pro.prc = []
    return redirect("/Compras")

@app.route("/Compras/limpiarc", methods = ['POST','GET'])
def limpiarc():
    pro.pc = []
    pro.cc = []
    pro.prc = []    
    return redirect("/Compras")

@app.route("/Compras/RC", methods = ['POST','GET'])
def RC():
    c = BDD()
    db = c.db()
    d = db.child("Compra").get()
    p = db.child("Proveedor").get()
    i = db.child("Empresa").get()
    return render_template("RC.html", data = d, i=i, p=p, b=0, m = 0, a = 0, p1 = 0)

@app.route("/Compras/RC/BusquedaFC", methods = ['POST','GET'])
def BFC():
    c = BDD()
    db = c.db()
    d = db.child("Compra").get()
    p = db.child("Proveedor").get()
    i = db.child("Empresa").get()

    b = request.form['fecha']
    return render_template("RC.html", data = d, i=i, p=p, b=b, m = 0, a = 0, p1 = 0)

@app.route("/Compras/RC/BusquedaMC", methods = ['POST','GET'])
def BMC():
    c = BDD()
    db = c.db()
    d = db.child("Compra").get()
    p = db.child("Proveedor").get()
    i = db.child("Empresa").get()

    m = request.form['mes']
    print(m)
    return render_template("RC.html", data = d, i=i, p=p, b=0, m = m, a = 0, p1 = 0)

@app.route("/Compras/RC/Detallec", methods = ['POST','GET'])
def Detallec():
    c = BDD()
    db = c.db()
    d = db.child("Compra").get()
    p = db.child("Proveedor").get()
    i = db.child("Empresa").get()

    compra = request.form['bbb']

    prods = ""
    cants = ""
    precs = ""
    for t in d.each():
        if t.key() == compra:
            prods = t.val()['Productos']
            cants = t.val()['Cantidad']
            precs = t.val()['Precio']

    productos = prods.split(',')
    cantidades = cants.split(',')
    precios = precs.split(',')

    a = dict(zip(productos, cantidades))
    p1 = db.child("Producto").get()

    cont = 0
    for x in a:
        cont += 1
        for t in p1.each():
            if t.key() in x:
                for v in precios:
                    if precios.index(v) == cont:
                        print(t.key(),t.val()['Descripcion'],a.get(x),v)

    return render_template("RC.html", data = d, i=i, p=p, b=0, m = 0, a = a, p1 = p1, precios = precios, bbb=compra)

@app.route("/Compras/RC/EliminarCompra", methods = ['POST','GET'])
def EliminarCompra():
    compra = request.form['bbbb']
    print(compra) 
    com = Compra(compra,"","","","","","")
    com.eliminar()

    return redirect("/Compras/RC")

# Usuarios
@app.route("/Usuarios", methods = ['POST','GET'])
def Usuarios():
    c = BDD()
    db = c.db()
    d = db.child("Usuarios").get()
    adm = db.child("Usuarios").child("Administracion").get()
    vnt = db.child("Usuarios").child("Ventas").get()
    eal = db.child("Usuarios").child("Almacenes").get()
    i = db.child("Empresa").get()

    if request.method == "POST":
        s = 1
    elif request.method == "GET":
        s = 0
    return render_template("Usuarios.html", data = d, adm = adm, vnt = vnt, eal = eal, b = 0, s = s, i=i)

def encriptar_contrasena(contrasena, salt):
    hash_object = hashlib.sha256()
    hash_object.update((salt + contrasena).encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    return hash_hex

@app.route("/Usuarios/AgregarUsuario", methods=['POST'])
def AgregarUsuario():
    id = request.form['Id']
    n = request.form['Nombre']
    ci = request.form['CI']
    pu = request.form['pu']
    u = request.form['Usuario']
    c = request.form['Contraseña']

    c = encriptar_contrasena(c, u)

    if id == 'Ventas':
        usuario = Vendedor(ci, n, u, c, pu)
    elif id == 'Almacenes':
        usuario = EncargadoDeAlmacenes(ci, n, u, c, pu)
    elif id == 'Administracion':
        usuario = Administrador(ci, n, u, c, pu)
    
    usuario.subir()
    return redirect("/Usuarios")

import re

@app.route("/Usuarios/EditarUsuario", methods=['POST'])
def EditarUsuario():
    id = request.form['Id']
    n = request.form['Nombre']
    ci = request.form['CI']
    pu = request.form['pu']
    u = request.form['Usuario']
    c = request.form['Contraseña']

    # Detectar si la contraseña está en formato SHA-256
    def es_sha256(valor):
        patron = r'^[a-f0-9]{64}$'  # Patrón para un hash SHA-256 (64 caracteres hexadecimales)
        return re.match(patron, valor) is not None

    if not es_sha256(c):  # Solo encriptar si no es SHA-256
        c = encriptar_contrasena(c, u)

    if id == 'Ventas':
        usuario = Vendedor(ci, n, u, c, pu)
    elif id == 'Almacenes':
        usuario = EncargadoDeAlmacenes(ci, n, u, c, pu)
    elif id == 'Administracion':
        usuario = Administrador(ci, n, u, c, pu)
    
    usuario.editar()
    return redirect("/Usuarios")

@app.route("/Usuarios/EliminarUsuario", methods = ['POST'])
def EliminarUsuario():
    id = request.form['Id']
    n = request.form['Nombre']
    usuario = Usuario('',n,'','')
    usuario.eliminar(id)
    return redirect("/Usuarios")

@app.route("/Usuarios/BuscarUsuario", methods = ['POST'])
def BuscarUsuario():
    nom = request.form['nom']
    usuario = Usuario('',nom,'','')
    b = usuario.buscar(nom)

    c = BDD()
    db = c.db()
    d = db.child("Usuarios").get()
    i = db.child("Empresa").get()

    adm = db.child("Usuarios").child("Administracion").get()
    vnt = db.child("Usuarios").child("Ventas").get()
    eal = db.child("Usuarios").child("Almacenes").get()

    return render_template("Usuarios.html", data = d, adm = adm, vnt = vnt, eal = eal, b = b, i=i)

# Empresa
@app.route("/EditarInfo", methods = ['POST'])
def EditarInfo():
    dir = request.form['Direccioni']
    nit = request.form['NITi']
    tel = request.form['Telefonoi']

    empresa = Empresa(dir,nit,tel)
    empresa.subir()
    return redirect("/Usuarios")

# Impresión Clientes
@app.route("/Clientes/Imprimir", methods = ['POST','GET'])
def ImprimirC():
    c = BDD() 
    db = c.db()
    d = db.child("Cliente").get()

    impr =[["Codigo  ","CI/NIT               ","Nombre                        ","Contacto"]]
    for t in d.each():
        i = [t.key(),t.val()['CI'],t.val()['Nombre'],t.val()['Contacto']]
        impr.append(i)
    
    doc = SimpleDocTemplate("C:/Neurus Robotics/static/Clientes.pdf", pagesize = A4)
    story=[]

    d = Drawing(0,5)
    d.add(String(-26,30,'Neurus Robotics', fontSize=18, fillColor=colors.navy,fontName="Helvetica-Bold"))
    d.add(String(-26,3,'Reporte de clientes', fontSize=17, fillColor=colors.navy,fontName="Helvetica"))
    fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
    fechaReporte = fecha.replace("-", "de")
    d.add(String(307,3, fechaReporte ,fontSize=12, fillColor=colors.black,fontName="Helvetica"))
     
    story.append(d)
    story.append(Spacer(0,15))

    tabla2 = Table(data = impr,
              style = [
                       ('GRID',(0,0),(-1,-1),0.5,colors.black),
                       ('BOX',(0,0),(-1,-1),2,colors.black),
                       ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                       ('BACKGROUND',(0,1), (-1,-1), colors.lavender),
                       ]
              )

    story.append(tabla2)
    story.append(Spacer(0,15))

    doc.build(story)
    os.startfile("C:/Neurus Robotics/static/Clientes.pdf")

    return redirect("/Clientes")

# Impresion productos
@app.route("/Productos/Imprimir", methods = ['POST','GET'])
def ImprimirP():
    c = BDD() 
    db = c.db()
    d = db.child("Producto").get()

    impr =[["Codigo      ","Descripción                        ","Stock     ","Precio                        ","Tipo      "]]
    for t in d.each():
        i = [t.key(),t.val()['Descripcion'],t.val()['Precio'],t.val()['Stock'],t.val()['Tipo']]
        impr.append(i)
    
    doc = SimpleDocTemplate("C:/Neurus Robotics/static/Productos.pdf", pagesize = A4)
    story=[]

    d = Drawing(0,5)
    d.add(String(-26,30,'Neurus Robotics', fontSize=18, fillColor=colors.navy,fontName="Helvetica-Bold"))
    d.add(String(-26,3,'Reporte de productos', fontSize=17, fillColor=colors.navy,fontName="Helvetica"))
    fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
    fechaReporte = fecha.replace("-", "de")
    d.add(String(307,3, fechaReporte ,fontSize=12, fillColor=colors.black,fontName="Helvetica"))
     
    story.append(d)
    story.append(Spacer(0,15))

    tabla2 = Table(data = impr,
              style = [
                       ('GRID',(0,0),(-1,-1),0.5,colors.black),
                       ('BOX',(0,0),(-1,-1),2,colors.black),
                       ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                       ('BACKGROUND',(0,1), (-1,-1), colors.lavender),
                       ]
              )

    story.append(tabla2)
    story.append(Spacer(0,15))

    doc.build(story)
    os.startfile("C:/Neurus Robotics/static/Productos.pdf")

    return redirect("/Productos")

# Impresion proveedores
@app.route("/Proveedores/Imprimir", methods = ['POST','GET'])
def ImprimirProv():
    c = BDD() 
    db = c.db()
    d = db.child("Proveedor").get()

    impr =[["Codigo      ","NIT          ","Nombre     ","Direccion                ","Contacto      "]]
    for t in d.each():
        i = [t.key(),t.val()['NIT'],t.val()['Nombre'],t.val()['Direccion'],t.val()['Contacto']]
        impr.append(i)
    
    doc = SimpleDocTemplate("C:/Neurus Robotics/static/Proveedores.pdf", pagesize = A4)
    story=[]

    d = Drawing(0,5)
    d.add(String(-49,30,'Neurus Robotics', fontSize=18, fillColor=colors.navy,fontName="Helvetica-Bold"))
    d.add(String(-49,3,'Reporte de proveedores', fontSize=17, fillColor=colors.navy,fontName="Helvetica"))
    fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
    fechaReporte = fecha.replace("-", "de")
    d.add(String(330,3, fechaReporte ,fontSize=12, fillColor=colors.black,fontName="Helvetica"))
     
    story.append(d)
    story.append(Spacer(0,15))

    tabla2 = Table(data = impr,
              style = [
                       ('GRID',(0,0),(-1,-1),0.5,colors.black),
                       ('BOX',(0,0),(-1,-1),2,colors.black),
                       ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                       ('BACKGROUND',(0,1), (-1,-1), colors.lavender),
                       ]
              )

    story.append(tabla2)
    story.append(Spacer(0,15))

    doc.build(story)
    os.startfile("C:/Neurus Robotics/static/Proveedores.pdf")

    return redirect("/Proveedores")

# Impresion ventas
@app.route("/Ventas/RV/Imprimir", methods = ['POST','GET'])
def ImprimirV():
    c = BDD() 
    db = c.db()
    d = db.child("Venta").get()
    d0 = db.child("Cliente").get()

    impr =[["Codigo  ","Cliente     ","Total  ","Vendedor  ","Fecha  "]]
    for t in d.each():
        for k in d0.each():
            if t.val()['Cliente'] == k.key():
                i = [t.key(),k.val()['Nombre'],t.val()['Total'],t.val()['Vendedor'],t.val()['Fecha']]
                impr.append(i)
    
    doc = SimpleDocTemplate("C:/Neurus Robotics/static/Ventas.pdf", pagesize = A4)
    story=[]

    d = Drawing(0,5)
    d.add(String(-53,30,'Neurus Robotics', fontSize=18, fillColor=colors.navy,fontName="Helvetica-Bold"))
    d.add(String(-53,3,'Reporte de ventas', fontSize=17, fillColor=colors.navy,fontName="Helvetica"))
    fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
    fechaReporte = fecha.replace("-", "de")
    d.add(String(335,3, fechaReporte ,fontSize=12, fillColor=colors.black,fontName="Helvetica"))
     
    story.append(d)
    story.append(Spacer(0,15))

    tabla2 = Table(data = impr,
              style = [
                       ('GRID',(0,0),(-1,-1),0.5,colors.black),
                       ('BOX',(0,0),(-1,-1),2,colors.black),
                       ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                       ('BACKGROUND',(0,1), (-1,-1), colors.lavender),
                       ]
              )

    story.append(tabla2)
    story.append(Spacer(0,15))

    doc.build(story)
    os.startfile("C:/Neurus Robotics/static/Ventas.pdf")

    return redirect("/Ventas/RV")

# Impresion compras
@app.route("/Compras/RC/Imprimir", methods = ['POST','GET'])
def ImprimirComp():
    c = BDD() 
    db = c.db()
    d = db.child("Compra").get()
    d0 = db.child("Proveedor").get()

    impr =[["Codigo  ","Proveedor ","Total     ","Encargado       ","Fecha    "]]
    for t in d.each():
        for k in d0.each():
            if t.val()['Proveedor'] == k.key():
                i = [t.key(),k.val()['Nombre'],t.val()['Total'],t.val()['Encargado'],t.val()['Fecha']]
                impr.append(i)
    
    doc = SimpleDocTemplate("C:/Neurus Robotics/static/Compras.pdf", pagesize = A4)
    story=[]

    d = Drawing(0,5)
    d.add(String(-53,30,'Neurus Robotics', fontSize=18, fillColor=colors.navy,fontName="Helvetica-Bold"))
    d.add(String(-53,3,'Reporte de compras', fontSize=17, fillColor=colors.navy,fontName="Helvetica"))
    fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
    fechaReporte = fecha.replace("-", "de")
    d.add(String(335,3, fechaReporte ,fontSize=12, fillColor=colors.black,fontName="Helvetica"))
     
    story.append(d)
    story.append(Spacer(0,15))

    tabla2 = Table(data = impr,
              style = [
                       ('GRID',(0,0),(-1,-1),0.5,colors.black),
                       ('BOX',(0,0),(-1,-1),2,colors.black),
                       ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                       ('BACKGROUND',(0,1), (-1,-1), colors.lavender),
                       ]
              )

    story.append(tabla2)
    story.append(Spacer(0,15))

    doc.build(story)
    os.startfile("C:/Neurus Robotics/static/Compras.pdf")

    return redirect("/Compras/RC")

# Impresion proveedores
@app.route("/Usuarios/Imprimir", methods = ['POST','GET'])
def ImprimirU():
    c = BDD() 
    db = c.db()
    d = db.child("Usuarios").child("Ventas").get()
    d0 = db.child("Usuarios").child("Almacenes").get()
    d1 = db.child("Usuarios").child("Administracion").get()

    impr =[["Area             ","Nombre              ","CI       ","Nivel/Turno/Comisión   ","Usuario                  ","Contraseña         "]]
    for t in d1.each():
        i = ["Administración",t.key(),t.val()['CI'],t.val()['Nivel'],t.val()['Usuario'],t.val()['Contraseña']]
        impr.append(i)
    for t in d.each():
        i = ["Ventas",t.key(),t.val()['CI'],t.val()['Comision'],t.val()['Usuario'],t.val()['Contraseña']]
        impr.append(i)
    for t in d0.each():
        i = ["Almacenes",t.key(),t.val()['CI'],t.val()['Turno'],t.val()['Usuario'],t.val()['Contraseña']]
        impr.append(i)

    doc = SimpleDocTemplate("C:/Neurus Robotics/static/Usuarios.pdf", pagesize = A4)
    story=[]

    d = Drawing(0,5)
    d.add(String(-49,30,'Neurus Robotics', fontSize=18, fillColor=colors.navy,fontName="Helvetica-Bold"))
    d.add(String(-49,3,'Reporte de usuarios', fontSize=17, fillColor=colors.navy,fontName="Helvetica"))
    fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
    fechaReporte = fecha.replace("-", "de")
    d.add(String(330,3, fechaReporte ,fontSize=12, fillColor=colors.black,fontName="Helvetica"))
     
    story.append(d)
    story.append(Spacer(0,15))

    tabla2 = Table(data = impr,
              style = [
                       ('GRID',(0,0),(-1,-1),0.5,colors.black),
                       ('BOX',(0,0),(-1,-1),2,colors.black),
                       ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                       ('BACKGROUND',(0,1), (-1,-1), colors.lavender),
                       ]
              )

    story.append(tabla2)
    story.append(Spacer(0,15))

    doc.build(story)
    os.startfile("C:/Neurus Robotics/static/Usuarios.pdf")

    return redirect("/Usuarios")

# Estadisticas

@app.route("/Productos/Reportep")
def Reportep(): 
    c = BDD() 
    db = c.db()
    d = db.child("Producto").get()

    lb = []

    for t in d.each():
        lb.append(t.val()['Tipo'])

    dat = {i:lb.count(i) for i in lb}

    labels = []
    datos = []
    for j in dat:
        labels.append(j)
        datos.append(dat.get(j))

    print(dat, labels, datos)

    doc2 = SimpleDocTemplate('C:/Neurus Robotics/static/Estadistica1.pdf', pagesize=A4)
    story = []

    d = Drawing(400, 80)

    d.add(String(150,100, 'Neurus Robotics', fontSize=40, fillColor=colors.orange, fontName="Helvetica-Bold"))
    d.add(String(182,66, 'Productos por tipo', fontSize=35, fillColor=colors.cadetblue, fontName="Helvetica"))
    story.append(d)

    d = Drawing(300, 200)
    pc = Pie()
    pc.x = 65
    pc.y = 15
    pc.width = 200
    pc.height = 200
    pc.data = datos
    pc.labels = labels
    pc.sideLabels = 1  # Con 0 no se muestran líneas hacia las etiquetas

    legend = Legend() 
    legend.x               = 320 
    legend.y               = -20 
    legend.dx              = 14  
    legend.dy              = 8  
    legend.fontName        = 'Helvetica-Bold'
    legend.fontSize        = 12  
    legend.boxAnchor       = 'n'  
    legend.columnMaximum   = 15  
    legend.strokeWidth     = 1  
    legend.strokeColor     = colors.black  
    legend.deltax          = 75  
    legend.deltay          = 10  
    legend.autoXPadding    = 5  
    legend.yGap            = 0  
    legend.dxTextSpace     = 5  
    legend.alignment       = 'right'  
    legend.dividerLines    = 1|2|4  
    legend.dividerOffsY    = 6  
    legend.subCols.rpad    = 30  

    colores  = [colors.salmon, colors.skyblue, colors.lavender, colors.yellowgreen, colors.orange]
    for i, color in enumerate(colores): 
        pc.slices[i].fillColor = color
    
    legend.colorNamePairs  = [(
                            pc.slices[i].fillColor, 
                            (pc.labels[i][0:30], '%0.2i' % pc.data[i])
                           ) for i in range(len(pc.data))]

    d.add(pc) 
    d.add(legend)
    story.append(d)

    # barras
    d = Drawing(400, 400)
    data = [datos]
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 250
    bc.width = 350
    bc.data = data
    bc.strokeColor = colors.black
    bc.fillColor = colors.lavenderblush
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 5
    bc.valueAxis.valueStep = 10  #paso de distancia entre punto y punto
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = labels
    bc.groupSpacing = 10
    bc.barSpacing = 2
    d.add(bc)
    story.append(d)

    doc2.build(story)
    os.startfile("C:/Neurus Robotics/static/Estadistica1.pdf")
    return redirect("/Productos")

@app.route("/Compras/RC/Reportec")
def Reportec(): 
    c = BDD() 
    db = c.db()
    d = db.child("Compra").get()

    lb = []

    for t in d.each():
        mes = t.val()['Fecha'].split('-')
        lb.append(mes[1])

    dat = {i:lb.count(i) for i in lb}

    labels = []
    datos = []
    for j in dat:
        labels.append(j)
        datos.append(dat.get(j))

    print(dat, labels, datos)

    doc2 = SimpleDocTemplate('C:/Neurus Robotics/static/Estadistica2.pdf', pagesize=A4)
    story = []

    d = Drawing(400, 80)

    d.add(String(150,100, 'Neurus Robotics', fontSize=40, fillColor=colors.orange, fontName="Helvetica-Bold"))
    d.add(String(188,66, 'Compras por mes', fontSize=35, fillColor=colors.cadetblue, fontName="Helvetica"))
    d.add(String(0,36, 'El siguiente grafico representa la densidad de compras realizadas en los diferentes meses', fontSize=11, fillColor=colors.cadetblue, fontName="Helvetica"))
    story.append(d)

    d = Drawing(300, 200)
    pc = Pie()
    pc.x = 65
    pc.y = 15
    pc.width = 200
    pc.height = 200
    pc.data = datos
    pc.labels = labels
    pc.sideLabels = 1  # Con 0 no se muestran líneas hacia las etiquetas

    legend = Legend() 
    legend.x               = 320 
    legend.y               = -20 
    legend.dx              = 14  
    legend.dy              = 8  
    legend.fontName        = 'Helvetica-Bold'
    legend.fontSize        = 12  
    legend.boxAnchor       = 'n'  
    legend.columnMaximum   = 15  
    legend.strokeWidth     = 1  
    legend.strokeColor     = colors.black  
    legend.deltax          = 75  
    legend.deltay          = 10  
    legend.autoXPadding    = 5  
    legend.yGap            = 0  
    legend.dxTextSpace     = 5  
    legend.alignment       = 'right'  
    legend.dividerLines    = 1|2|4  
    legend.dividerOffsY    = 6  
    legend.subCols.rpad    = 30  

    colores  = [colors.salmon, colors.skyblue, colors.lavender, colors.yellowgreen, colors.orange, colors.red, colors.blue, colors.green, colors.greenyellow, colors.aquamarine, colors.rosybrown, colors.royalblue]
    for i, color in enumerate(colores): 
        pc.slices[i].fillColor = color
    
    legend.colorNamePairs  = [(
                            pc.slices[i].fillColor, 
                            (pc.labels[i][0:30], '%0.2i' % pc.data[i])
                           ) for i in range(len(pc.data))]

    d.add(pc) 
    d.add(legend)
    story.append(d)

    # barras
    d = Drawing(400, 400)
    data = [datos]
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 250
    bc.width = 350
    bc.data = data
    bc.strokeColor = colors.black
    bc.fillColor = colors.lavenderblush
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 50
    bc.valueAxis.valueStep = 10  #paso de distancia entre punto y punto
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = labels
    bc.groupSpacing = 10
    bc.barSpacing = 2
    d.add(bc)
    story.append(d)

    doc2.build(story)
    os.startfile("C:/Neurus Robotics/static/Estadistica2.pdf")
    return redirect("/Compras/RC")

@app.route("/Ventas/RV/Reportev")
def Reportev(): 
    c = BDD() 
    db = c.db()
    d = db.child("Venta").get()

    lb = []

    for t in d.each():
        mes = t.val()['Fecha'].split('-')
        lb.append(mes[1])

    dat = {i:lb.count(i) for i in lb}

    labels = []
    datos = []
    for j in dat:
        labels.append(j)
        datos.append(dat.get(j))

    print(dat, labels, datos)

    doc2 = SimpleDocTemplate('C:/Neurus Robotics/static/Estadistica3.pdf', pagesize=A4)
    story = []

    d = Drawing(400, 80)

    d.add(String(150,100, 'Neurus Robotics', fontSize=40, fillColor=colors.orange, fontName="Helvetica-Bold"))
    d.add(String(188,66, 'Ventas por mes', fontSize=35, fillColor=colors.cadetblue, fontName="Helvetica"))
    d.add(String(0,36, 'El siguiente grafico representa la densidad de ventas realizadas en los diferentes meses', fontSize=11, fillColor=colors.cadetblue, fontName="Helvetica"))
    story.append(d)

    d = Drawing(300, 200)
    pc = Pie()
    pc.x = 65
    pc.y = 15
    pc.width = 200
    pc.height = 200
    pc.data = datos
    pc.labels = labels
    pc.sideLabels = 1  # Con 0 no se muestran líneas hacia las etiquetas

    legend = Legend() 
    legend.x               = 320 
    legend.y               = -20 
    legend.dx              = 14  
    legend.dy              = 8  
    legend.fontName        = 'Helvetica-Bold'
    legend.fontSize        = 12  
    legend.boxAnchor       = 'n'  
    legend.columnMaximum   = 15  
    legend.strokeWidth     = 1  
    legend.strokeColor     = colors.black  
    legend.deltax          = 75  
    legend.deltay          = 10  
    legend.autoXPadding    = 5  
    legend.yGap            = 0  
    legend.dxTextSpace     = 5  
    legend.alignment       = 'right'  
    legend.dividerLines    = 1|2|4  
    legend.dividerOffsY    = 6  
    legend.subCols.rpad    = 30  

    colores  = [colors.salmon, colors.skyblue, colors.lavender, colors.yellowgreen, colors.orange, colors.red, colors.blue, colors.green, colors.greenyellow, colors.aquamarine, colors.rosybrown, colors.royalblue]
    for i, color in enumerate(colores): 
        pc.slices[i].fillColor = color
    
    legend.colorNamePairs  = [(
                            pc.slices[i].fillColor, 
                            (pc.labels[i][0:30], '%0.2i' % pc.data[i])
                           ) for i in range(len(pc.data))]

    d.add(pc) 
    d.add(legend)
    story.append(d)

    # barras
    d = Drawing(400, 400)
    data = [datos]
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 250
    bc.width = 350
    bc.data = data
    bc.strokeColor = colors.black
    bc.fillColor = colors.lavenderblush
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 80 #escala
    bc.valueAxis.valueStep = 10  #paso de distancia entre punto y punto
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = labels
    bc.groupSpacing = 10
    bc.barSpacing = 2
    d.add(bc)
    story.append(d)

    doc2.build(story)
    os.startfile("C:/Neurus Robotics/static/Estadistica3.pdf")
    return redirect("/Ventas/RV")

if __name__ == "__main__":
    app.secret_key = "llave"
    app.run(debug = True)
    logging.info("Inicio del programa.")
    ejecutar_proceso()
    logging.info("Fin del programa.")
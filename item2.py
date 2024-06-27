import hashlib
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Función para hashear contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Configuración de la base de datos SQLite
conn = sqlite3.connect('usuarios.db')
c = conn.cursor()

# Crear tabla si no existe
c.execute('''CREATE TABLE IF NOT EXISTS usuarios
             (nombre text, apellido text, registro text, hash_pass text)''')
conn.commit()

# Clase para manejar las peticiones HTTP
class RequestHandler(BaseHTTPRequestHandler):
    
    # Método para manejar las peticiones GET
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Welcome to the Python Web Server!</h1></body></html>')
        elif parsed_path.path == '/validate':
            params = parse_qs(parsed_path.query)
            nombre = params['nombre'][0]
            apellido = params['apellido'][0]
            registro = params['registro'][0]
            
            # Consultar la base de datos para validar usuario
            c.execute("SELECT * FROM usuarios WHERE nombre=? AND apellido=? AND registro=?", (nombre, apellido, registro))
            row = c.fetchone()
            
            if row:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f'<html><body><h1>Validación exitosa para {nombre} {apellido}</h1></body></html>'.encode())
            else:
                self.send_response(401)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('<html><body><h1>Error de validación</h1></body></html>'.encode('utf-8'))

# Función para ejecutar el servidor web en el puerto 8500
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8500):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

# Ejecutar el servidor web en segundo plano
if __name__ == '__main__':
    from threading import Thread
    server_thread = Thread(target=run)
    server_thread.start()

    # Ejemplo de almacenamiento de usuario y contraseña hasheada
    nombre = 'Ignacio'
    apellido = 'Garrido'
    registro = 'devnet'
    password = 'password123'
    hash_pass = hash_password(password)

    # Insertar usuario en la base de datos
    c.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?)", (nombre, apellido, registro, hash_pass))
    conn.commit()

    # Mostrar mensaje para verificar inserción
    print(f'Usuario {nombre} {apellido} almacenado en la base de datos con contraseña hasheada: {hash_pass}')

    # Ejemplo de validación de usuario (comando respectivo)
    # Se simula una solicitud GET a /validate con los parámetros nombre, apellido y registro

    # Terminar el servidor
    server_thread.join()

# Cerrar la conexión a la base de datos al finalizar
conn.close()

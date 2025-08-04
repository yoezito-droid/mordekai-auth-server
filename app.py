from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Credenciales de usuarios (en producción deberían estar en una base de datos)
USERS = {
    "admin": "48511549",
    "usuario1": "12345678",
    "usuario2": "87654321",
    "usuario3": "11223344",
    "usuario4": "44332211",
    "usuario5": "55667788",
    "usuario6": "88776655",
    "usuario7": "99887766"
}

# Sesiones activas (en producción deberían estar en Redis o base de datos)
active_sessions = {}

@app.route('/')
def home():
    return jsonify({
        "message": "Mordekai Auth Server",
        "status": "running",
        "endpoints": ["/login", "/logout", "/check_session", "/status"]
    })

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        device_id = data.get('device_id')
        
        # Validar datos requeridos
        if not username or not password or not device_id:
            return jsonify({
                "success": False,
                "message": "Datos incompletos"
            }), 400
        
        # Verificar credenciales
        if username not in USERS or USERS[username] != password:
            return jsonify({
                "success": False,
                "message": "Usuario o contraseña incorrectos"
            }), 401
        
        # Verificar si el usuario ya está activo
        if username in active_sessions:
            return jsonify({
                "success": False,
                "message": f"El usuario '{username}' ya está activo en otro dispositivo"
            }), 403
        
        # Crear sesión
        active_sessions[username] = {
            "device_id": device_id,
            "login_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        print(f"Login exitoso: {username} desde {device_id}")
        
        return jsonify({
            "success": True,
            "message": "Login exitoso",
            "username": username
        })
        
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

@app.route('/logout', methods=['POST'])
def logout():
    try:
        data = request.get_json()
        username = data.get('username')
        device_id = data.get('device_id')
        
        if not username or not device_id:
            return jsonify({
                "success": False,
                "message": "Datos incompletos"
            }), 400
        
        # Verificar si la sesión existe
        if username in active_sessions:
            session = active_sessions[username]
            if session["device_id"] == device_id:
                del active_sessions[username]
                print(f"Logout exitoso: {username} desde {device_id}")
                return jsonify({
                    "success": True,
                    "message": "Logout exitoso"
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Sesión no válida"
                }), 403
        else:
            return jsonify({
                "success": False,
                "message": "Usuario no tiene sesión activa"
            }), 404
            
    except Exception as e:
        print(f"Error en logout: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

@app.route('/check_session', methods=['POST'])
def check_session():
    try:
        data = request.get_json()
        username = data.get('username')
        device_id = data.get('device_id')
        
        if not username or not device_id:
            return jsonify({
                "success": False,
                "active": False,
                "message": "Datos incompletos"
            }), 400
        
        if username in active_sessions:
            session = active_sessions[username]
            if session["device_id"] == device_id:
                # Actualizar última actividad
                session["last_activity"] = datetime.now().isoformat()
                return jsonify({
                    "success": True,
                    "active": True,
                    "message": "Sesión activa"
                })
            else:
                return jsonify({
                    "success": True,
                    "active": False,
                    "message": "Sesión en otro dispositivo"
                })
        else:
            return jsonify({
                "success": True,
                "active": False,
                "message": "No hay sesión activa"
            })
            
    except Exception as e:
        print(f"Error en check_session: {str(e)}")
        return jsonify({
            "success": False,
            "active": False,
            "message": "Error interno del servidor"
        }), 500

@app.route('/status', methods=['GET'])
def status():
    try:
        active_sessions_list = []
        for username, session in active_sessions.items():
            active_sessions_list.append({
                "username": username,
                "device_id": session["device_id"],
                "last_activity": session["last_activity"]
            })
        
        return jsonify({
            "success": True,
            "active_sessions": active_sessions_list,
            "total_sessions": len(active_sessions),
            "max_users": len(USERS)
        })
        
    except Exception as e:
        print(f"Error en status: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 
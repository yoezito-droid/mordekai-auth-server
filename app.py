from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import os
import threading
import time

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
    "usuario7": "99887766",
    "usuario8": "33445566",
    "usuario9": "66778899",
    "usuario10": "11223355",
    "usuario11": "55443322",
    "usuario12": "77889900",
    "usuario13": "22334455",
    "usuario14": "66554433",
    "usuario15": "88990011",
    "usuario16": "44556677",
    "usuario17": "77665544",
    "usuario18": "99001122",
    "usuario19": "55667788",
    "usuario20": "88776655",
    "usuario21": "11223344",
    "usuario22": "44332211",
    "usuario23": "66778899",
    "usuario24": "99887766",
    "usuario25": "22334455",
    "usuario26": "55443322",
    "usuario27": "77889900",
    "usuario28": "33445566",
    "usuario29": "66554433",
    "usuario30": "88990011"
}

# Sesiones activas (en producción deberían estar en Redis o base de datos)
active_sessions = {}

# Función para limpiar sesiones automáticamente
def auto_cleanup_sessions():
    """Limpia las sesiones automáticamente cada semana (lunes 8am)"""
    while True:
        try:
            now = datetime.now()
            
            # Verificar si es lunes a las 8am
            if now.weekday() == 0 and now.hour == 8 and now.minute == 0:
                sessions_cleared = len(active_sessions)
                active_sessions.clear()
                print(f"[AUTO-CLEANUP] Limpieza semanal automática completada. Sesiones eliminadas: {sessions_cleared}")
                
                # Esperar 1 hora para evitar múltiples ejecuciones
                time.sleep(3600)
            else:
                # Verificar cada minuto
                time.sleep(60)
                
        except Exception as e:
            print(f"[AUTO-CLEANUP] Error en limpieza automática: {str(e)}")
            time.sleep(300)  # Esperar 5 minutos si hay error

# Iniciar thread de limpieza automática
cleanup_thread = threading.Thread(target=auto_cleanup_sessions, daemon=True)
cleanup_thread.start()

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

@app.route('/clear_all_sessions', methods=['POST'])
def clear_all_sessions():
    try:
        # Limpiar todas las sesiones activas
        sessions_cleared = len(active_sessions)
        active_sessions.clear()
        
        print(f"Todas las sesiones han sido limpiadas. Sesiones eliminadas: {sessions_cleared}")
        
        return jsonify({
            "success": True,
            "message": f"Todas las sesiones han sido limpiadas. Sesiones eliminadas: {sessions_cleared}",
            "sessions_cleared": sessions_cleared
        })
        
    except Exception as e:
        print(f"Error al limpiar sesiones: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

@app.route('/cleanup_info', methods=['GET'])
def cleanup_info():
    """Información sobre la limpieza automática"""
    try:
        now = datetime.now()
        next_cleanup = now + timedelta(days=(7 - now.weekday()) % 7)
        next_cleanup = next_cleanup.replace(hour=8, minute=0, second=0, microsecond=0)
        
        return jsonify({
            "success": True,
            "auto_cleanup_enabled": True,
            "cleanup_schedule": "Lunes 8:00 AM",
            "next_cleanup": next_cleanup.isoformat(),
            "days_until_cleanup": (next_cleanup - now).days,
            "current_sessions": len(active_sessions)
        })
        
    except Exception as e:
        print(f"Error al obtener información de limpieza: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 
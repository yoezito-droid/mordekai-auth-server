from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import os
import threading
import time

# ===========================================
# SISTEMA DE AUTENTICACION - MORDEKAI AYACUCHO
# Actualizado: 10 de agosto 2025
# Total usuarios: 101 (1 admin + 100 usuarios)
# ===========================================

app = Flask(__name__)
CORS(app)

# Credenciales de usuarios (en producción deberían estar en una base de datos)
USERS = {
    "admin": "48511549",
    "usuario1": "73921549",
    "usuario2": "71344070",
    "usuario3": "61938159",
    "usuario4": "52355767",
    "usuario5": "98043374",
    "usuario6": "92964076",
    "usuario7": "53017175",
    "usuario8": "37701866",
    "usuario9": "20885567",
    "usuario10": "27165503",
    "usuario11": "68288045",
    "usuario12": "45710718",
    "usuario13": "88971779",
    "usuario14": "57368870",
    "usuario15": "77409071",
    "usuario16": "13139961",
    "usuario17": "75990128",
    "usuario18": "76189482",
    "usuario19": "16706754",
    "usuario20": "99641546",
    "usuario21": "98827733",
    "usuario22": "98612957",
    "usuario23": "98612957",
    "usuario24": "95583391",
    "usuario25": "26477104",
    "usuario26": "89776397",
    "usuario27": "88971779",
    "usuario28": "33445566",
    "usuario29": "66554433",
    "usuario30": "13503413",
    "usuario31": "58085673",
    "usuario32": "47702104",
    "usuario33": "65484666",
    "usuario34": "29043991",
    "usuario35": "46104115",
    "usuario36": "26015615",
    "usuario37": "65484666",
    "usuario38": "60131945",
    "usuario39": "29043991",
    "usuario40": "97827675",
    "usuario41": "77963053",
    "usuario42": "67730345",
    "usuario43": "79273266",
    "usuario44": "19375927",
    "usuario45": "58470125",
    "usuario46": "23540718",
    "usuario47": "26371077",
    "usuario48": "42025887",
    "usuario49": "42025887",
    "usuario50": "82274366",
    "usuario51": "41153856",
    "usuario52": "26477104",
    "usuario53": "88702320",
    "usuario54": "86031279",
    "usuario55": "54058294",
    "usuario56": "48691185",
    "usuario57": "31891346",
    "usuario58": "86449378",
    "usuario59": "80346689",
    "usuario60": "10072842",
    "usuario61": "58898264",
    "usuario62": "18534727",
    "usuario63": "87728038",
    "usuario64": "53305997",
    "usuario65": "22953788",
    "usuario66": "25188603",
    "usuario67": "10072842",
    "usuario68": "89685901",
    "usuario69": "57037560",
    "usuario70": "43915001",
    "usuario71": "53394749",
    "usuario72": "53305997",
    "usuario73": "53305997",
    "usuario74": "61906138",
    "usuario75": "75031010",
    "usuario76": "26802546",
    "usuario77": "61585111",
    "usuario78": "89212713",
    "usuario79": "16706754",
    "usuario80": "99919332",
    "usuario81": "46131247",
    "usuario82": "51273168",
    "usuario83": "58571002",
    "usuario84": "75858753",
    "usuario85": "78036172",
    "usuario86": "58571002",
    "usuario87": "75031010",
    "usuario88": "36191344",
    "usuario89": "26802546",
    "usuario90": "64511690",
    "usuario91": "35386581",
    "usuario92": "35386581",
    "usuario93": "10196501",
    "usuario94": "10196501",
    "usuario95": "78036172",
    "usuario96": "32750432",
    "usuario97": "53394749",
    "usuario98": "32750432",
    "usuario99": "32750432",
    "usuario100": "36191344"
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
        "endpoints": ["/login", "/logout", "/check_session", "/status", "/dashboard"]
    })

@app.route('/dashboard')
def dashboard():
    """Endpoint para servir el dashboard HTML de sesiones activas"""
    dashboard_html = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mordekai Auth Server - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }

        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .stat-label {
            font-size: 1.1em;
            color: #666;
        }

        .sessions-section {
            padding: 30px;
        }

        .sessions-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .sessions-title {
            font-size: 1.8em;
            color: #2c3e50;
        }

        .refresh-btn {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
        }

        .refresh-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }

        .sessions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }

        .session-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #3498db;
            transition: all 0.3s ease;
        }

        .session-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        }

        .session-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }

        .user-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5em;
            font-weight: bold;
            margin-right: 15px;
        }

        .user-info h3 {
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .user-info p {
            color: #7f8c8d;
            font-size: 0.9em;
        }

        .session-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .detail-item {
            display: flex;
            align-items: center;
            padding: 8px 0;
        }

        .detail-icon {
            margin-right: 8px;
            color: #3498db;
        }

        .detail-label {
            font-weight: 500;
            color: #2c3e50;
            margin-right: 5px;
        }

        .detail-value {
            color: #7f8c8d;
            font-size: 0.9em;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #7f8c8d;
        }

        .empty-icon {
            font-size: 4em;
            margin-bottom: 20px;
            opacity: 0.5;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-online {
            background: #27ae60;
        }

        .status-offline {
            background: #e74c3c;
        }

        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .sessions-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Mordekai Auth Server</h1>
            <p>Dashboard de Sesiones Activas</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-number" id="totalSessions">-</div>
                <div class="stat-label">Sesiones Activas</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🔢</div>
                <div class="stat-number" id="maxUsers">-</div>
                <div class="stat-label">Límite de Usuarios</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-number" id="usagePercent">-</div>
                <div class="stat-label">Uso del Servidor</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🟢</div>
                <div class="stat-number" id="serverStatus">-</div>
                <div class="stat-label">Estado del Servidor</div>
            </div>
        </div>

        <div class="sessions-section">
            <div class="sessions-header">
                <h2 class="sessions-title">📋 Sesiones Activas</h2>
                <button class="refresh-btn" onclick="loadSessions()">
                    🔄 Actualizar
                </button>
            </div>

            <div id="sessionsContainer">
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Cargando sesiones...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_URL = '/status';

        async function loadSessions() {
            const container = document.getElementById('sessionsContainer');
            
            try {
                // Mostrar loading
                container.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Cargando sesiones...</p>
                    </div>
                `;

                const response = await fetch(API_URL);
                const data = await response.json();

                // Actualizar estadísticas
                updateStats(data);

                // Mostrar sesiones
                displaySessions(data.active_sessions || []);

            } catch (error) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">❌</div>
                        <h3>Error al cargar datos</h3>
                        <p>No se pudo conectar con el servidor</p>
                        <p style="font-size: 0.9em; margin-top: 10px;">${error.message}</p>
                    </div>
                `;
            }
        }

        function updateStats(data) {
            document.getElementById('totalSessions').textContent = data.total_sessions || 0;
            document.getElementById('maxUsers').textContent = data.max_users || 0;
            
            const usage = data.max_users > 0 ? Math.round((data.total_sessions / data.max_users) * 100) : 0;
            document.getElementById('usagePercent').textContent = usage + '%';
            
            document.getElementById('serverStatus').textContent = data.status || 'running';
        }

        function displaySessions(sessions) {
            const container = document.getElementById('sessionsContainer');
            
            if (sessions.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">👤</div>
                        <h3>No hay sesiones activas</h3>
                        <p>Actualmente no hay usuarios conectados al servidor</p>
                    </div>
                `;
                return;
            }

            const sessionsHTML = sessions.map(session => `
                <div class="session-card">
                    <div class="session-header">
                        <div class="user-avatar">
                            ${session.username.charAt(0).toUpperCase()}
                        </div>
                        <div class="user-info">
                            <h3>${session.username}</h3>
                            <p>
                                <span class="status-indicator status-online"></span>
                                Conectado
                            </p>
                        </div>
                    </div>
                    <div class="session-details">
                        <div class="detail-item">
                            <span class="detail-icon">📱</span>
                            <span class="detail-label">Dispositivo:</span>
                            <span class="detail-value">${session.device_id}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-icon">🕒</span>
                            <span class="detail-label">Última actividad:</span>
                            <span class="detail-value">${formatDate(session.last_activity)}</span>
                        </div>
                    </div>
                </div>
            `).join('');

            container.innerHTML = `
                <div class="sessions-grid">
                    ${sessionsHTML}
                </div>
            `;
        }

        function formatDate(dateString) {
            if (!dateString) return 'N/A';
            
            try {
                const date = new Date(dateString);
                return date.toLocaleString('es-ES', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (error) {
                return dateString;
            }
        }

        // Cargar datos al iniciar la página
        document.addEventListener('DOMContentLoaded', loadSessions);

        // Actualizar automáticamente cada 30 segundos
        setInterval(loadSessions, 30000);
    </script>
</body>
</html>'''
    
    return dashboard_html, 200, {'Content-Type': 'text/html'}

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

# Actualizado: 10 de agosto 2025 - 100 usuarios agregados 
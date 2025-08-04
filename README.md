# Servidor de Autenticación - Mordekai Ayacucho

## 🚀 Despliegue en Render.com

### **Pasos para desplegar:**

1. **Crear cuenta en Render.com:**
   - Ve a [render.com](https://render.com)
   - Regístrate con tu cuenta de GitHub

2. **Crear nuevo Web Service:**
   - Click en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub
   - Selecciona el repositorio que contiene este servidor

3. **Configuración del servicio:**
   - **Name:** `mordekai-auth-server`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free (o el que prefieras)

4. **Variables de entorno (opcional):**
   - `PORT`: 10000 (Render lo configura automáticamente)

5. **Desplegar:**
   - Click en "Create Web Service"
   - Espera a que termine el despliegue

### **URL del servidor:**
```
https://tu-nombre-de-servicio.onrender.com
```

### **Endpoints disponibles:**
- `GET /` - Información del servidor
- `POST /login` - Autenticación
- `POST /logout` - Cerrar sesión
- `POST /check_session` - Verificar sesión
- `GET /status` - Estado de sesiones

### **Credenciales de prueba:**
- Usuario: `admin`, Contraseña: `48511549`
- Usuario: `usuario1`, Contraseña: `12345678`
- Y otros usuarios definidos en el código

### **Pruebas locales:**
```bash
cd server
pip install -r requirements.txt
python app.py
```

El servidor estará disponible en: `http://localhost:5000` 
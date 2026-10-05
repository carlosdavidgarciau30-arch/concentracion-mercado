# Guía de primer uso: ejecutar y publicar

Esta guía está pensada para personas que nunca han ejecutado una aplicación de Python/Streamlit.

## 1. Probar la aplicación en su computador

### Recomendación de Python
Use Python 3.12 o 3.13.

### Windows

1. Instale Python desde https://www.python.org/downloads/
2. Durante la instalación marque **Add Python to PATH**.
3. Descomprima la carpeta del proyecto.
4. Abra la carpeta `concentracion_mercado`.
5. Haga clic en la barra de direcciones del Explorador, escriba `cmd` y presione Enter.
6. En la ventana negra escriba, una línea a la vez:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La aplicación debería abrirse en el navegador. Si no se abre sola, copie la dirección que aparezca en la terminal, normalmente:

`http://localhost:8501`

Para detener la aplicación vuelva a la terminal y presione `Ctrl + C`.

### macOS / Linux

1. Compruebe que tiene Python 3.
2. Descomprima la carpeta del proyecto.
3. Abra Terminal dentro de `concentracion_mercado`.
4. Ejecute:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abra la dirección que muestre la terminal, normalmente `http://localhost:8501`.

## 2. Pruebas manuales recomendadas

Antes de publicar, revise estas situaciones:

1. **Mercado conocido**
   - N = 4
   - cuotas = 40, 30, 20, 10
   - CR2 debe ser aproximadamente 0,7000
   - IHH debe ser 0,3000
   - dominancia aproximadamente 0,3933
   - entropía aproximadamente 1,2799

2. **Caso de umbral**
   - N = 4
   - cuotas = 25, 25, 25, 25
   - IHH = 0,2500
   - en la pregunta, la respuesta correcta debe ser
     **Está exactamente en un umbral**.

3. **Cuotas con cero**
   - N = 3
   - cuotas = 60, 40, 0
   - la página debe aceptarlas.

4. **Reinicio de tabla**
   - escriba cuotas con N = 4;
   - cambie N a 5;
   - la tabla debe reiniciarse.

5. **Mercado aleatorio**
   - pulse el botón para generar cuotas;
   - el total debe ser 100 %.

6. **Monte Carlo**
   - pruebe primero 100 repeticiones;
   - luego 1.000;
   - seleccione distintos indicadores en el gráfico;
   - revise que aparezca la línea "Tu mercado" y el percentil.

## 3. Publicar con GitHub + Streamlit Community Cloud

Esta es la ruta recomendada para obtener una URL pública.

### Paso A: crear un repositorio en GitHub

1. Cree una cuenta en GitHub si todavía no tiene una.
2. Cree un repositorio nuevo, por ejemplo:
   `concentracion-mercado`
3. Puede dejarlo **público** si quiere que la aplicación sea pública por defecto.
4. Suba el contenido de esta carpeta al repositorio.

Deben quedar visibles en la raíz del repositorio, como mínimo:

- `app.py`
- `indicadores.py`
- `simulacion.py`
- `graficos.py`
- `pregunta.py`
- `requirements.txt`

No suba la carpeta `.venv`.

### Paso B: desplegar en Streamlit Community Cloud

1. Entre a https://share.streamlit.io/
2. Inicie sesión y conecte su cuenta de GitHub.
3. Pulse **Create app**.
4. Seleccione la opción que indica que ya tiene una app.
5. Elija:
   - repositorio: `concentracion-mercado`
   - rama: normalmente `main`
   - archivo principal: `app.py`
6. Si aparece la opción, elija un subdominio para la URL.
7. Pulse **Deploy**.

Streamlit instalará automáticamente las dependencias indicadas en
`requirements.txt`.

Cuando termine, obtendrá una dirección parecida a:

`https://nombre-elegido.streamlit.app`

## 4. Si aparece un error al publicar

Abra los logs de Streamlit Community Cloud. Los errores más frecuentes son:

- un archivo no fue subido a GitHub;
- `requirements.txt` no está en la raíz;
- se eligió un archivo principal distinto de `app.py`;
- hay una dependencia que no pudo instalarse.

Copie el error completo y tráigalo a ChatGPT para revisarlo.

## 5. Archivos que no deben modificar al principio

Para la primera prueba no cambie:

- las fórmulas en `indicadores.py`;
- la distribución Dirichlet en `simulacion.py`;
- los umbrales de la pregunta en `pregunta.py`.

Primero compruebe que la versión actual funciona de extremo a extremo.

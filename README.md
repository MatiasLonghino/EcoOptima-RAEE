Instalación y ejecución local

Para ejecutar el proyecto de forma local, se deben seguir los siguientes pasos:

1. Clonar el repositorio
git clone [URL_DEL_REPOSITORIO](https://github.com/MatiasLonghino/EcoOptima-RAEE.git)
2. Ingresar a la carpeta del proyecto
3. Crear un entorno virtual
python -m venv env
4. Activar el entorno virtual

En Windows:
env\Scripts\activate

En Linux o Mac:
source env/bin/activate

5. Instalar dependencias
pip install -r requirements.txt
6. Ejecutar la aplicación
streamlit run app.py

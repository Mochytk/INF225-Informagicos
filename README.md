# INF236-GRUPO-13

Este es el repositorio del *Grupo 13*, cuyos integrantes son:
* Rodrigo Ariel Cáceres Gaete - 202273616-k
* Martin Ignacio Ferrera Borquez - 202273552-K
* Sergio Roberto Rojas Gutiérrez - 202273619-4
* José Andrés Yáñez Chávez - 202273508-2
* **Tutor**: Javiera Osorio

## Wiki
Puede acceder a la Wiki mediante el siguiente [enlace](https://github.com/Mochytk/INF236-GRUPO-13/wiki)

## Videos
* [Video Hito 3](https://youtu.be/u5LrkK-0U38)
* [Video Hito 5](https://youtu.be/ra4RlnNAZF0)

## Aspectos técnicos relevantes
### Configuración inicial
El primer paso para hacer funcionar la página es clonar el repositorio. Para ello, se puede hacer uso de GitHub Desktop o del siguiente comando:

`git clone https://github.com/Mochytk/INF236-GRUPO-13.git`

Además, se deben instalar las siguientes aplicaciones:
- Python 3.12 o posterior
- Node.js 22 o posterior
- npm 10.9.2 o posterior

Una vez cumplidos estos requisitos, se deberán ejecutar los siguientes comandos para instalar las librerías de Python necesarias:

- `python -m pip install Django==5.2`
- `pip install djangorestframework`
- `pip install django-cors-headers`
- `pip install djangorestframework-simplejwt`
- `python -m pip install Pillow` ¡¡¡NUEVO!!!  

### Desplegar el proyecto (Sin Docker)
Una vez finalizada la configuración inicial, debemos hacer funcionar la página. Para ello, lo primero será inicializar el backend (Django + Django REST), para lo cual abrimos la terminal desde la carpeta "paes" y ejecutamos el siguiente comando:

`python manage.py runserver`

Luego, debemos iniciar el frontend (Vue), para lo cual abrimos una terminal en la carpeta "vue" y ejecutamos los siguientes comandos:

`npm install`

`npm run dev`

Nota: el comando `npm install` solo es necesario para la primera ejecución.

Finalmente para acceder a la página se debe copiar la url que se indice en 'Local:', y pegarla en su buscador de preferencia donde se podrá navegar como desee.

### Desplegar el proyecto (Con Docker) ¡¡¡NUEVO!!!
Este nuevo método necesita tener el software 'Docker-Desktop' instalado (link para su instalación: https://www.docker.com/products/docker-desktop/). Se sigue un procedimiento similar: primero abrimos la terminal y nos dirigimos a la carpeta 'app', una vez ahí se ejecuta el siguiente comando que desplegará automáticamente tanto el backend como el frontend del proyecto:

`docker-compose up --build`

Une vez hecho eso use los siguientes links en su navegador de preferencia para acceder a lo que deseé:

`http://localhost:5173/` -> Frontend

`http://localhost:8000/` -> Backend (en proceso)

`http://localhost:8000/api/login/` -> API Login

`http://127.0.0.1:8000/admin/login/?next=/admin/` -> Login para el administrador


### Credenciales de inicio de sesión en la página web
Por el momento existen 2 perfiles para iniciar sesión. Ambos usuarios fueron hechos con el fin de testear el funcionamiento de la página:

  1)Usuario 'Docente':
  
    Correo: hola@hotmail.com
    
    Contraseña: rodrigoat
    
  2)Usuario 'Alumno':
  
    Correo: a@a.com 
    
    Contraseña: estudiante

### Posibles errores y sus soluciones
  1)
  ~~~
'npm : No se puede cargar el archivo C:\Program Files\nodejs\npm.ps1 porque la ejecución de 
scripts está deshabilitada en este sistema. Para obtener más información, consulta el tema 
about_Execution_Policies en https:/go.microsoft.com/fwlink/?LinkID=135170.
En línea: 1 Carácter: 1
+ npm run dev
+ ~~~
+ CategoryInfo          : SecurityError: (:) [], PSSecurityException
+ FullyQualifiedErrorId : UnauthorizedAccess'
~~~

  -> Este error puede ocurrir en Windows si, en la terminal, al dirigirse al directorio "INF236-GRUPO-13\app\vue>", se introduce el comando `npm run dev`. La razón es que, en algunos casos, PowerShell bloquea la ejecución de scripts por razones de seguridad, y npm.ps1 es un script que forma parte de Node.js
  
  -> Solución: en la misma terminal y en el mismo directorio se debe introducir exactamente este comando: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. Esto permitirá ejecutar scripts, pero solo en esta sesión de PowerShell, por lo que si se cierra el editor de código se deberá volver a hacer el mismo proceso una vez abierto nuevamente el proyecto.
  
  2)
  En algunas distribuciones de Linux existe la posibilidad de que al tratar de instalar librerías de Python aparezca el siguiente error:
  ~~~
  error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.

    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.

    See /usr/share/doc/python3.11/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
  ~~~
  -> Este error puede ocurrir debido a que, por defecto en algunas distribuciones Linux, Python evita que se puedan hacer cambios en el sistema por motivos de seguridad.
  
  -> Solución: Es posible cambiar la configuración de cómo se gestionan los paquetes del sistema usando el siguiente comando: `python3 -m pip config set global.break-system-packages true`.

### El proyecto está basado en la documentación disponible en:
- Sección [Servicios](https://github.com/Mochytk/INF236-GRUPO-13/wiki/Servicios) de la [Wiki](https://github.com/Mochytk/INF236-GRUPO-13/wiki).
- [Métodos de la API de al red de colegios SIP](https://docs.google.com/spreadsheets/d/1EpDN1tzUwHGL3f3PVp9PCgyoJPDbeeiUk6s3VOLamCY/edit?gid=744756109#gid=744756109)

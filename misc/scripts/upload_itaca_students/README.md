# Upload Itaca Students

Este script genera y despliega dentro del contenedor de odoodock de Maya, un fichero CSV con los datos mínimos necesarios del alumnado para diferentes procesos internos de gestión, como las bajas.

El documentos se genera partir de los datos de los alumnos extraidos de Itaca en formato (XML) y de la documentación de la Identidad Digital (PDF)

## Funcionamiento

La conversión del pdf se realiza a través de _tabula-py_ un wrapper sobre [_tabula_](https://tabula.technology/) que necesita para su ejecución Java. Para simplificar la ejecución, se genera un contenedor que contiene todo lo necesario para que el funcionamiento sea lo más óptimo posible: JDK, Python3, g++, dotenv...

La estrutura del fichero xml debe ser:

```
<alumnos>
  <alumno/>
  ...
  <alumno/>
</alumnos>
```

## Instalación

> Es necesario Docker para ejecutar el script

1. Crear una carpeta

2. Inicializar un repo de git

   ```
   > git init
   ```

3. Añadir el remoto de _maya_core_

   ```
   > git remote add origin https://github.com/CEED-Informatica/maya_core.git
   ```

4. Activar el sparseCheckout

   ```
   > git config core.sparseCheckout true
   ```

5. Seleccionar la carpeta a obtener

   ```
   > git sparse-checkout set onfig misc/scripts/upload_itaca_students
   ```

6. Traer el código, haciendo un pull

   ```
   > git pull origin main
   ```

7. Una vez tenemos ya el fichero hay que dar permisos de ejecución al script

   ```
   >  chmod +x upload_itaca_students.sh
   ```

## Ejecución

1. Configurar en fichero .env.origen con los datos necesarios para la conexión

2. Ejecutar el script. Por ejemplo:

   ```
   >  ./upload_itaca_students.sh -x ../alumnos.xml -m ../IDigtal.pdf 
   ```

   **Parámetros**

    ```
    Uso: ./upload_itaca_students.sh -x <ruta/al/xml.xml> -m <ruta/al/pdf.pdf> [OPCIONES]

    Parámetros obligatorios:
     -x <archivo>  Ruta al fichero XML con los datos de los estudiantes.
     -m <archivo>  Ruta al fichero PDF con los datos de los correos corporativos de los estudiantes.

    Parámetros opcionales:
     -p <password>   Password ssh para el usuario del servidor Maya.
     -f <valor>      Estudios sobre los que se filtra a los alumnos: 5 (Ciclos), 6 (Bachillerato), 7 (Formación para Adultos), -1 (Todos/sin filtro). Por defecto: 5
     -s              Si se incluye, sSi se indica, únicamente se hace la conversión a csv y se copia el fichero en la ruta indicada del ordenador local.
     -h              Muestra esta ayuda.
```

## Conexión Maya &harr; Moodle

> A lo largo del documento, el prompt **$** indica un comando a introducir en el host, mientras que el prompt **>** indica un comando a introducir en el contenedor. Además, **[PWD_MODULO]** indica el directorio raíz del módulo.
### Creación del token de comunicación

1. [ ] Configurar el fichero _[PWD_MODULO]/misc/scripts/save_token_moodle/moodle_host.txt_ con la url del servidor de Moodle.

    > En el caso de trabajar con el servicio Moodle que proporcina _odoodock_, la url es el nombre del servicio: _http://moodle:8080_ . 

    En el caso de estar trabajando con _odoodock_ hay que modificar el fichero desde dentro del contenedor:

    ```
    $ docker exec -it odoodock-web-1 bash
    > cd /mnt/extra-addons/misc/scripts/save_token_moodle
    > nano moodle_host.txt
    ```

2. [ ] Dar permisos de ejecución al script.

    ```
    cd [PWD_MODULO]/misc/scripts/create_users/
    chmod +x save_token_moodle.py
    ```

    o, si se trabaja con [odoodock](https://aoltra.github.io/odoodock/):

    ```
    > chmod +x save_token_moodle.py
    ```

3. [ ] Ejecutar el script

    ```
    ./save_token_moodle.py
    ```

    o, si se trabaja con [odoodock](https://aoltra.github.io/odoodock/):

    ```
    > ./save_token_moodle.py
    ```

    con los parámetros:

      * (1) Usuario: usuario de referencia para que **Maya** lea sus credenciales. Ha de ser el mismo que el que se configura en los ajustes de _Odoo_ como usuario. **Maya** permite que existan varias opciones (varias usuarios) que se conectan a Moodle. Este usuario funciona a modo de clave para saber que usuario de moodle y contraseña se va a utilizar. Es muy habitual que sea _maya_
      * (2) Usuario _Moodle_: usuario de _Moodle_ que relizará las gestiones. Ver apartado 3 del documento de [configuración de Moodle](/maya-core/docs/requirements/moodle-config). Tiene que tener asignado el rol profesor.
      * (3) Contraseña del usuario _Moodle_.


4. [ ] Configurar la URL y el usuario de acceso a _Moodle_
  
      Como _administrador_ acceder en _Odoo_:

         Ajustes / Maya | Core / Moodle 
         
      Y asignar como URL la url del servidor de moodle (por ejemplo _https://aules.edu.gva.es/ed_) y como usuario el (1) _Usuario_ indicado en el paso anterior (¡no el usuario Moodle!).

### Creación de las aulas virtuales

4. [ ]  Utilizando de plantilla el fichero _[PWD_MODULO]/misc/scripts/classrooms_demo.csv_ añadir todas las aulas virtuales del sistema para posteriormente incorporarlas a **Maya** mediante el script _[PWD_MODULO]/misc/scripts/create_classrooms/create_classrooms.py_

    ```
    cd [PWD_MODULO]/misc/scripts/create_classrooms/
    chmod +x create_classrooms.py
    ./create_classrooms.py -sr USERADMIN -ps PASSADMIN -db NOMDB FICHERO.csv 
    ```
    donde: 

      * USERADMIN: usuario administrador.
      * PASSADMIN: pasword del usuario administrador.
      * NOMDB: es el nombre de la base de datos. 
      * FICHERO.csv: fichero con los datos de las aulas.

    En el caso de estar trabajando con [odoodock](https://aoltra.github.io/odoodock/) hay que ejecutar el script desde dentro del contenedor:

    ```
    $ docker exec -it odoodock-web-1 bash
    > cd /mnt/extra-addons/maya_core/misc/scripts/create_classrooms
    > chmod +x create_classrooms.py
    > ./create_classrooms.py -sr USERADMIN -ps PASSADMIN -db NOMDB FICHERO.csv 
    ```

    > Es muy importante que el código del aula siga las indicaciones comentadas en el apartado 2 del documento de [configuración de Moodle](/maya-core/docs/requirements/moodle-config).

    > El campo comentario no es procesado por el script
 
    > El script no permite la vinculación de varios módulos en una misma aula. Esos enlaces hay que realizarlos insertando una sola aula en el script para, posteriormente desde Odoo, editar ese aula y añadir todos los módulos (subjects) asociados.

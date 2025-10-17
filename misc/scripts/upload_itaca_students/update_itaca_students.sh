 
#!/bin/bash

# Variables
PASSWORD=""
FST_VALUE=""
NO_SSH=0 # 0 para false (no está puesto), 1 para true (está puesto)
XML_FILE=""
PDF_FILE=""

# Ayuda
usage() {
    echo "Uso: $0 -x <ruta/al/xml.xml> -m <ruta/al/pdf.pdf> [OPCIONES]"
    echo ""
    echo "Parámetros obligatorios:"
    echo "  -x <archivo>  Ruta al fichero XML con los datos de los estudiantes."
    echo "  -m <archivo>  Ruta al fichero PDF con los datos de los correos corporativos de los estudiantes."
    echo ""
    echo "Parámetros opcionales:"
    echo "  -p <password>   Password ssh para el usuario del servidor Maya."
    echo "  -f <valor>      Estudios sobre los que se filtra a los alumnos: 5 (Ciclos), 6 (Bachillerato), 7 (Formación para Adultos), -1 (Todos/sin filtro). Por defecto: 5"
    echo "  -s              Si se incluye, sSi se indica, únicamente se hace la conversión a csv y se copia el fichero en la ruta indicada del ordenador local."
    echo "  -h              Muestra esta ayuda."
    exit 1
}

echo "\033[1mMaya | upload-itaca-students. v0.1\033[0m"

# Las opciones tienen:
#   x:, m:, p:, f: (con argumentos obligatorios)
#   s, h (sin argumentos)
while getopts "x:m:p:f:sh" opt; do
    case "$opt" in
        x)
            XML_FILE="$OPTARG"
            ;;
        m)
            PDF_FILE="$OPTARG"
            ;;
        p)
            PASSWORD="$OPTARG"
            ;;
        f)
            FST_VALUE="$OPTARG"
            ;;
        s)
            NO_SSH=1
            ;;
        h)
            usage
            ;;
        \?)
            echo "Error: Opción inválida -$OPTARG" >&2
            usage
            ;;
        :)
            echo "Error: La opción -$OPTARG requiere un argumento." >&2
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "$XML_FILE" ] || [ -z "$PDF_FILE" ]; then
    echo "\033[0;31m[ERROR]\033[0m Faltan los parámetros obligatorios -x y/o -m." >&2
    usage
fi

if [ -n "$FST_VALUE" ]; then
    case "$FST_VALUE" in
        4|5|7|-1)
            # Valor válido
            ;;
        *)
            echo "\033[0;31m[ERROR]\033[0m El valor para -f debe ser 4, 5, 7 o -1. Se proporcionó: $FST_VALUE" >&2
            exit 1
            ;;
    esac
fi

# Argumentos obligatorios
PYTHON_ARGS="/app/data/input.xml /app/data/input.pdf"

# Argumentos Opcionales
# Contraseña
if [ -n "$PASSWORD" ]; then
    PYTHON_ARGS="$PYTHON_ARGS -p $PASSWORD"
fi

# filtro
if [ -n "$FST_VALUE" ]; then
    PYTHON_ARGS="$PYTHON_ARGS -fst $FST_VALUE"
fi

# NSSH (si está presente)
if [ "$NO_SSH" -eq 1 ]; then
    PYTHON_ARGS="$PYTHON_ARGS -nssh"
fi

# Fichero de Salida
# CSV_FILE="salida_$(date +%Y%m%d_%H%M%S).csv"
# CSV_FILE="itaca_students.csv"
# PYTHON_ARGS+=" /app/data/$CSV_FILE"

mkdir -p data
cp "$PDF_FILE" data/input.pdf
cp "$XML_FILE" data/input.xml

echo "\033[0;34m[INFO]\033[0m Iniciando el procesamiento en el contenedor Docker..."
echo "\033[0;34m[INFO]\033[0m Argumentos de Python: main.py $PYTHON_ARGS"

# Ejecuta el servicio, pasando los argumentos al script Python
docker compose run --rm upload_itaca_students \
    python3 main.py $PYTHON_ARGS

# Elimino los archivos de entrada del WORKDIR una vez procesados
rm data/input.pdf data/input.xml

echo "\033[0;34m[INFO]\033[0m Proceso finalizado."
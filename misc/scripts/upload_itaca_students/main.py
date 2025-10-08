import csv
import os
from dotenv import load_dotenv
import paramiko
import argparse
import shutil
import xml.etree.ElementTree as ET
import pandas as pd
import tabula 

def validate_filter_studies(value):
  """
  Comprueba que el filtro sea el adecuado

  Args:
      value(str): valor definido por el usuario como filtro
  """
  allowed = ['4', '5', '7', '-1']
  if value not in allowed:
    parser.error(f"\033[0;31m[ERROR]\033[0m El parámetro -fst debe ser uno de {allowed}. Valor recibido: {value}")
  return value

def students_xml2csv(xml_filename, filter = None, headers_included = []) -> tuple[list, list]:
  """
  Convierte un archivo XML con una estructura de <alumnos><alumno .../></alumnos>
  donde los datos del alumno son atributos, a un archivo CSV.

  Args:
      xml_filename (str): La ruta al archivo XML de entrada.
      filter (str): 5 (FP), FPA (7), BA (4), ALL (-1): filtrado por enseñanza
  """

  print(f'\n================== XML ==================')
  print(f"\033[0;34m[INFO]\033[0m Procesando XML: '{xml_filename}'...")

  headers = []

  try:
    tree = ET.parse(xml_filename)
    root = tree.getroot()

    students = root.findall('./alumnos/alumno')

    if not students:
      print(f"\033[0;31m[ERROR]\033[0m No se encontraron elementos <alumno> dentro de <alumnos> en el XML.")
      exit()
    
    headers = [key for key in students[0].attrib.keys() if key in headers_included]

  except FileNotFoundError:
    print(f"\033[0;31m[ERROR]\033[0m El archivo XML '{xml_filename}' no se encontró.")
    exit(1)
  except ET.ParseError:
    print(f"\033[0;31m[ERROR]\033[0m No se pudo parsear el archivo XML '{xml_filename}'. Revisa su formato.")
    exit(1)
  except Exception as e:
    print(f"\033[0;31m[ERROR]\033[0m Ocurrió un error inesperado al leer el XML: {e}")
    exit(1)

  students_data = []

  for student in students:
    row = {}
    
    # Recorre todas las cabeceras definidas
    for key in headers:
      # Obtiene el valor del atributo (o None si no existe)
      # Uso get() para obtener el valor del atributo. Si no existe, incluyo una cadena vacía
      # para evitar errores y asegurar que todas las filas tengan el mismo número de columnas.
      row[key] = student.get(key, '')

    # Filtrado por enseñanza
    if filter != '-1' and row.get('ensenanza', '') != filter:
        continue
      
    # como el NIA va a ser la clave de union con el pdf, lo dejo lo más limpio posible
    row['NIA'] = str(row.get('NIA', '')).strip()
    
    students_data.append(row)

  print(f'\033[0;32m[OK]\033[0m XML procesado. Datos:')
  print(f'\n   - Alumnos totales: {len(students)}\n   - Alumnos filtro ({filter}): {len(students_data)}')

  return students_data, headers
 
def read_table_from_pdf(pdf_filename: str) -> pd.DataFrame:
  """
  Extrae todas las tablas de todas las páginas de un PDF usando tabula-py.
  Solo se incluyen las tablas con al menos 5 columnas.
  De cada tabla se toman la primera (NIA) y la quinta columna (email corporativo).
  Devuelve un único DataFrame con todos los resultados combinados.

  Args:
      pdf_filename (str): Ruta al archivo PDF.

  Returns:
      pd.DataFrame: DataFrame combinado con columnas ['NIA_pdf', 'email_corporativo'].
  """
  print(f'\n================== PDF ==================')
  print(f"\033[0;34m[INFO]\033[0m Procesando PDF: '{pdf_filename}' con tabula-py...")

  try:
    # Lee TODAS las tablas de TODAS las páginas
    dfs = tabula.read_pdf(
        pdf_filename,
        pages='all',
        multiple_tables=True,
        lattice=True,
        stream=False,
        silent=True
    )

    if not dfs:
      print(f"\033[0;31m[ERROR]\033[0m No se encontraron tablas en el PDF '{pdf_filename}'.")
      return pd.DataFrame(columns=['NIA_pdf', 'email_corporativo'])

    # Lista para acumular los DataFrames válidos
    valid_tables = []

    for idx, df_pdf in enumerate(dfs):
      if df_pdf is None or df_pdf.empty:
        # print(f"\033[0;33m[WARNING]\033[0m Tabla {idx+1} vacía o inválida, se omite.")
        continue

      if df_pdf.shape[1] < 5:
        # print(f"\033[0;33m[WARNING]\033[0m Tabla {idx+1} con solo {df_pdf.shape[1]} columnas, se omite.")
        continue

      try:
        # Selecciona la 1ª y 5ª columna
        df_emails = df_pdf.iloc[:, [0, 4]].copy()
        df_emails.columns = ['NIA_pdf', 'email_corporativo']

        # Limpieza
        df_emails.dropna(subset=['NIA_pdf', 'email_corporativo'], inplace=True)
        df_emails['NIA_pdf'] = df_emails['NIA_pdf'].astype(str).str.strip()
        df_emails['email_corporativo'] = df_emails['email_corporativo'].astype(str).str.strip()

        if not df_emails.empty:
          valid_tables.append(df_emails)
          # print(f"\033[0;32m[OK]\033[0m Tabla {idx+1} añadida ({len(df_emails)} registros).")

      except Exception as e:
        print(f"\033[0;31m[ERROR]\033[0m Procesando tabla {idx+1}: {e}")

    # Combina todas las tablas válidas
    if valid_tables:
      df_combined = pd.concat(valid_tables, ignore_index=True)
      print(f"\033[0;32m[OK]\033[0m Extracción PDF completada. Datos:")
      print(f"\n   - Tablas válidas: {len(valid_tables)}\n   - Registros: {len(df_combined)}")
      return df_combined
    else:
      print(f"\033[0;31m[ERROR]\033[0m No se encontró ninguna tabla válida con al menos 5 columnas.")
      return pd.DataFrame(columns=['NIA_pdf', 'email_corporativo'])

  except FileNotFoundError:
    print(f"\033[0;31m[ERROR]\033[0m El archivo PDF '{pdf_filename}' no se encontró.")
    return pd.DataFrame(columns=['NIA_pdf', 'email_corporativo'])
  except Exception as e:
    print(f"\033[0;31m[ERROR]\033[0m Error al procesar el PDF con tabula-py: {e}")
    return pd.DataFrame(columns=['NIA_pdf', 'email_corporativo'])


## Cuerpo del script ##

print('\033[1mMaya | [container] upload-itaca-students. v0.1\033[0m')

parser = argparse.ArgumentParser(
  description = 'Incluye en Maya un fichero XML de estudiantes obtenido de Itaca')

# argumentos
parser.add_argument('xml_filename', help = 'Fichero xml con los datos de los estudiantes.') 
parser.add_argument('pdf_filename', help = 'Fichero pdf con los datos de los correos corporativos de los estudiantes.') 

parser.add_argument(
  '-fst', '--filter-studies', default='5', type=validate_filter_studies,
  help='Estudios sobre los que se filtra a los alumnos: 5 (Ciclos), 6 (Bachillerato), 7 (Formación para Adultos), -1 (Todos/sin filtro). Por defecto: 5'
)
parser.add_argument('-p', '--password', help='Password ssh para el usuario del servidor Maya.')
parser.add_argument('-nssh', '--no-ssh', action='store_true', help='Si se indica, únicamente se hace la conversión a csv y se copia el fichero en la ruta indicada del ordenador local.')

args = parser.parse_args()
xml_filename = args.xml_filename
pdf_filename = args.pdf_filename
filter_studies = args.filter_studies
server_password = args.password
no_ssh = args.no_ssh

# obtención de los valores desde .env
load_dotenv('/app/.env')
server_ip = os.getenv("SERVER_IP")
server_user = os.getenv("SERVER_USER")
remote_folder = os.getenv("REMOTE_FOLDER")


# comprobación de que los parámetros estén ok
if not remote_folder:
  print("\033[0;31m[ERROR]\033[0m La variable REMOTE_FOLDER no está definida en el fichero .env o está vacía.")
  exit(1)

if not server_ip and not no_ssh:
  print("\033[0;31m[ERROR]\033[0m La variable SERVER_IP no está definida en el fichero .env o está vacía.")
  exit(1)

if not server_user and not no_ssh:
  print("\033[0;31m[ERROR]\033[0m La variable SERVER_USER no está definida en el fichero .env o está vacía.")
  exit(1)

if not server_password and not no_ssh:
  print("\033[0;31m[ERROR]\033[0m No se ha indicado el password ssh para el usuario del servidor Maya.")
  exit(1)

# Cabeceras del fichero xml que vamos a incluir
HEADERS_TO_INCLUDE = ['NIA','nombre','apellido1','apellido2','email1','email2',
                       'telefono1','ensenanza']

# Paso 1 -> Obtenemos los datos del xml
students_data, base_headers = students_xml2csv(xml_filename, filter_studies, 
                 headers_included = HEADERS_TO_INCLUDE )
                 
# Paso 2 -> Obtenemos los datos del pdf
df_emails = read_table_from_pdf(pdf_filename)
if df_emails.empty:
  print('\033[0;34m[INFO]\033[0m No se pudo obtener la tabla de correos corporativos del PDF.')
  
# Paso 3 -> Unión (merge por NIA)
print(f'\n================== JOIN ==================')
df_students = pd.DataFrame(students_data)
df_students['NIA'] = df_students['NIA'].astype(str).str.strip()
df_emails['NIA_pdf'] = df_emails['NIA_pdf'].astype(str).str.strip()

df_merged = pd.merge(
    df_students,
    df_emails,
    how='left',
    left_on='NIA',
    right_on='NIA_pdf'
)

df_merged.drop(columns=['NIA_pdf'], inplace=True)
if 'email_corporativo' not in base_headers:
    base_headers.append('email_corporativo')

emails_merged_count = df_merged['email_corporativo'].notna().sum()
print(f'\033[0;32m[OK]\033[0m JOIN realizado. Datos sobre correos corporativos:')
print(f'\n   - Encontrados para vincular:  {len(df_merged)}\n   - Vinculados: {emails_merged_count}')

# Paso 4 -> creación del CSV
print(f'\n=============== Creación CSV ===============\n')
local_file_path = './data/temp.csv'
try:
    df_merged.to_csv(local_file_path, index=False, encoding='utf-8')
    print(f"\033[0;32m[OK]\033[0m CSV generado correctamente: {local_file_path}")
except Exception as e:
    print(f"\033[0;31m[ERROR]\033[0m Error al escribir CSV: {e}")


print(f'\n================== Copia ==================\n')
try:
  if args.no_ssh:
    # Copia el archivo localmente en la carpeta indicada por remote_folder
    os.makedirs(remote_folder, exist_ok=True)
    dest_path = os.path.join(remote_folder, os.path.basename(local_file_path))

    shutil.copy(local_file_path, dest_path)
    print(f"\033[0;32m[OK]\033[0m Archivo copiado localmente a: {dest_path}")
  else:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_ip, username=server_user, password=server_password)
    sftp = ssh.open_sftp()
    remote_path = os.path.join(remote_folder, os.path.basename(local_file_path))
    sftp.put(local_file_path, remote_path)
    sftp.close()
    ssh.close()
    print(f'\033[0;34m[OK]\033[0m Archivo copiado vía SSH a: {remote_path}')
except Exception as e:
    print(f"\033[0;31m[ERROR]\033[0m {e}")
    if "[Errno 13]" in e:
      print('\033[0;34m[INFO]\033[0m Comprueba los permisos de REMOTE_FOLDER. Desde el servidor de Maya')
      print('\033[0;34m[INFO]\033[0m >   docker exec -it <nombre_contenedor_odoo> id odoo')
      print('\033[0;34m[INFO]\033[0m >   sudo chown -R <uid>:<gid> /home/administrador/maya/.server-info/odoo/repo')

"""
if os.path.exists('temp.csv'):
  try:
    os.remove('temp.csv')
    print('\033[0;34m[INFO]\033[0m temp.csv eliminado.')
  except Exception as e:
    print(f"\033[0;31m[ERROR]\033[0m No se pudo eliminar temp.csv: {e}")
"""
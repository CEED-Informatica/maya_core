#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import csv
import sys, argparse

def print_dictionary(dictionary):
  """
  Muestra por pantalla un diccionario de una manera más ordenada
  """
  for key, value in dictionary.items():  
    print(' * {} ({})'.format(key, value))

def print_list(list):
  """
  Muestra por pantalla una lista de una manera más ordenada
  """
  for value in list:  
    print(' * {}'.format(value))

print('\033[1mMaya | link-subject-techer. v2.0\033[0m')

parser = argparse.ArgumentParser(
  description = 'Enlaza profesores (employee) y con módulos (subject) desde un csv')

# argumentos
parser.add_argument('csv_filename', help = 'Fichero csv con los datos: login,course,subject,course,subject,...') 
parser.add_argument('-u', '--url', default = 'http://localhost', help = 'URL del servidor Odoo. Por defecto: http://localhost')
parser.add_argument('-p', '--port', default = '8069', help = 'Puerto del servidor Odoo. Por defecto: 8069')
parser.add_argument('-db', '--database', required = True, help = 'Base de datos. Requerido')
parser.add_argument('-sr', '--user', default = 'admin', help = 'Usuario administrador Odoo. Por defecto: admin')
parser.add_argument('-ps', '--password', default = 'admin', help = 'Contraseña usuario administrador Odoo. Por defecto: admin')

args = parser.parse_args()

url = args.url + ':' + args.port
db = args.database
username = args.user
password = args.password

teachers_subjects_rel = []
teachers = set()

# end point xmlrpc/2/common permite llamadas sin autenticar
print('\033[0;32m[INFO]\033[0m Conectando con',url, ' -> ', db)
try:
  common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
  print('\033[0;32m[INFO]\033[0m Odoo server', common.version()['server_version'])
except Exception as e:
  print('\033[0;31m[ERROR]\033[0m ' + str(e))
  print('\033[0;31m[ERROR]\033[0m Compruebe que el servidor de Odoo esté arrancado')
  print(f'\033[0;32m[INFO]\033[0m Saliendo...')
  exit()

# autenticación
uid = common.authenticate(db, username, password, {})

try:
  with open(args.csv_filename) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter = ',')
    line_count = 0
    for row in csv_reader:
      if line_count > 0:
        teachers_subjects_rel.append({
          'teacher': row[0],
          'course': row[1],
          'subject': row[2],
        })
        teachers.add(row[0])
      line_count += 1


except Exception as e:
  print('\033[0;31m[ERROR]\033[0m ' + str(e))
  print(f'\033[0;32m[INFO]\033[0m Saliendo...')
  exit()     

print('\033[0;32m[INFO]\033[0m Módulos asignados a profesores en csv:', len(teachers_subjects_rel))    

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

try:
  # ciclos
  course_output = models.execute_kw(db, uid, password, 'maya_core.course', 'search_read', [[]], { 'fields':  ['abbr', 'id', 'code'] } )
  courses_ec = {}
  for course in course_output:
    courses_ec[course['code']] = [course['id'], course['abbr']]

  print(f'\033[0;32m[INFO]\033[0m Ciclos:')
  print_dictionary(courses_ec)

  # módulos
  subject_output = models.execute_kw(db, uid, password, 'maya_core.subject', 'search_read', [[]], { 'fields':  ['abbr', 'code', 'id', 'courses_ids']})
  subjects_ec = {}
  for subj in subject_output:
    subjects_ec[subj['code']] = [subj['id'], subj['courses_ids'], subj['abbr'] ]

  print(f'\033[0;32m[INFO]\033[0m Módulos:')
  print_dictionary(subjects_ec)

except Exception as e:
  print('\033[0;31m[ERROR]\033[0m ' + str(e))
  print(f'\033[0;32m[INFO]\033[0m Saliendo...')
  exit()

line_count_OK = 0
line_count_ERROR = 0

for teacher in teachers:
  # hay que buscar si el empleado existe.
  # obtengo el id del usuario
  id = models.execute_kw(db, uid, password, 'res.users', 'search_read', 
                                          [[['login','=', teacher]]], { 'fields': ['id', 'maya_employee_id', 'name']})
  
  if len(id) == 0:
    raise Exception(f'No existe el usuario {teacher} en Odoo.')
  
  if id[0]['maya_employee_id'] == False:
    raise Exception(f'No existe un empleado asociado al usuario {tsr["teacher"]}.')
  
  # se eliminan, si las hay, las relaciones previas con otros módulos
  # es decir, cada vez que ejecuto el script se actualizan todas las relaciones
  teacher_of_subjects = models.execute_kw(db, uid, password, 
                                              'maya_core.subject_employee_rel', 
                                              'search_read', 
                                              [[['employee_id','=', id[0]['maya_employee_id'][0]]]], { 'fields': ['id']})

  print(f'\033[0;32m[INFO]\033[0m\tEliminando relaciones ({len(teacher_of_subjects)}) entre {id[0]["name"]} y los módulos que impartía')
  if len(teacher_of_subjects):
    for ids in teacher_of_subjects:
        models.execute_kw(db, uid, password, 'maya_core.subject_employee_rel', 'unlink', [[ids['id']]])

for tsr in teachers_subjects_rel:  
  print("\033[0;32m[INFO]\033[0m Procesando", tsr['teacher'])
  try:
   
    # hay que buscar si el empleado existe.
    # obtengo el id del usuario
    id = models.execute_kw(db, uid, password, 'res.users', 'search_read', 
                                            [[['login','=', tsr['teacher']]]], { 'fields': ['id', 'maya_employee_id', 'name']})
    
    if len(id) == 0:
      raise Exception(f'No existe el usuario {tsr["teacher"]} en Odoo.')
    
    if id[0]['maya_employee_id'] == False:
      raise Exception(f'No existe un empleado asociado al usuario {tsr["teacher"]}.')
    
    # se comprueba que la relación módulo/ciclo exista
    if not any(course_id == courses_ec[tsr['course']][0] for course_id in subjects_ec[tsr['subject']][1]):
      raise Exception(f'El módulo {tsr["subject"]} no se cursa en {tsr["course"]}. Profesor/a {id[0]["name"]} ({tsr["teacher"]})')
  

    # enlazo los módulos que imparte
    models.execute_kw(db, uid, password, 'maya_core.subject_employee_rel','create', [{
            'course_id': courses_ec[tsr['course']][0],
            'subject_id': subjects_ec[tsr['subject']][0],
            'employee_id': id[0]['maya_employee_id'][0]
          }])

    line_count_OK += 1  
    print(f'\033[0;32m[INFO]\033[0m\t   Asociando {id[0]["name"]} ({tsr["teacher"]} -> {subjects_ec[tsr["subject"]][2]} (id: {subjects_ec[tsr["subject"]][0]}) / {courses_ec[tsr["course"]][1]} (id: {courses_ec[tsr["course"]][0]})')
    
  except (xmlrpc.client.Fault) as e:
    print('   \033[0;31m[ERROR]\033[0m ' + e.faultString)
    line_count_ERROR += 1
  except KeyError:
    print('   \033[0;31m[ERROR]\033[0m Clave no encontrada. Posiblemente el departamento no existe')
    line_count_ERROR += 1
  except Exception as e:
    print('   \033[0;31m[ERROR]\033[0m ' + str(e))
    line_count_ERROR += 1

print(f'\033[0;32m[INFO]\033[0m Procesadas {line_count_OK} relaciones / Errores: {line_count_ERROR}.')



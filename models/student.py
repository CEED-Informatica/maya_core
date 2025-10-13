# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime

import pandas as pd

class Student(models.Model):
  """
  Define un estudiante
  """

  _name = 'maya_core.student'
  _description = 'Estudiante'
  _order = 'surname'

  moodle_id = fields.Char(string = 'moodle_id', size = 9, required = True)
  nia = fields.Char(string = 'NIA', size = 9)
  name = fields.Char(string = 'Nombre', required = True)
  surname = fields.Char(string = 'Apellidos', required = True)

  # emails
  email = fields.Char(string = 'Email')
  email_support = fields.Char(string = 'Email de apoyo')
  email_coorp = fields.Char(string = 'Email corporativo')

  student_info = fields.Char(string = 'Nombre completo', compute = '_compute_full_student_info')

  # puede estar matriculado en varios ciclos
  courses_ids = fields.Many2many('maya_core.course')
  
  """ subjects_ids = fields.Many2many('maya_core.subject',
    string = 'Módulos',
    relation = 'maya_core_subject_student_rel', 
    column1 = 'student_id', column2 = 'subject_id') """
  subjects_ids = fields.One2many('maya_core.subject_student_rel', 'student_id')
  
  def _compute_full_student_info(self):
    for record in self:
      record.student_info = record.surname + ', ' + record.name

  @staticmethod
  def update_student_data_from_itaca(record, df, data_stack):
    """
    Procesa un único estudiante buscando sus emails en el DataFrame df.
    Devuelve una tupla (actualizado: bool, lista_de_errores)
    """
    errors = []
    update = False

    for email in [record.email_coorp, record.email, record.email_support]:
      if update:  # ya se ha actualizado, no sigo buscando
        break

      if not email or not email.strip():
        continue

      email = email.strip()
      count = (data_stack == email).sum()

      if count == 0:
        errors.append(f"No se encuentra información en Itaca para el alumno {record.student_info}")
        continue

      if count > 1:
        errors.append(f"Dos o más entradas de la base de datos de Itaca contienen el mismo mail {email}")
        continue

      # buscamos en columnas específicas
      for column in ['email_corporativo', 'email1', 'email2']:
        found = df[df[column] == email]
        if len(found) == 1:
            data = found.iloc[0].to_dict()
            record.email_coorp = data['email_corporativo']
            record.nia = data['NIA']
            record.email = data['email1']
            record.email_support = data['email2']
            update = True
            break

    return update, errors

  def update_itaca_fields(self):
    """
    Actualiza los datos desde Itaca de todos los estudiantes seleccionados
    """
    #TODO parametrizar estos datos en configuraciones
    # TODO mejorar creando un diccionario por mail, pero deberia controlar que pasa con dos claves iguales
    archivo_csv = '/mnt/odoo-repo/itaca/temp.csv'
  
    try:
      df = pd.read_csv(archivo_csv)
    except FileNotFoundError:
      raise UserError(f"¡Operación cancelada!\n\nNo se pudo encontrar el fichero de datos Itaca en {archivo_csv}.")
    
    # aplano la lista para ver si el valor del mail está o está  repetido
    data_stack = df.stack()
    errors = []
    
    for record in self:
      _, record_errors = Student.update_student_data_from_itaca(record, df, data_stack)
      errors.extend(record_errors)

    # creo un fichero de texto con los errores
    errors_filename = ''
    if len (errors)>0:
      date_str = datetime.now().strftime("%y%m%d%H%M")

      errors_filename = f"/mnt/odoo-repo/itaca/errores_itaca_{date_str}.txt" 
      try:
        with open(errors_filename, 'w', encoding='utf-8') as f:
            for line in errors:
                f.write(f"{line}\n")
        
        errors_filename = f'\r{len(errors)} error(es). Más información en: ' + errors_filename

      except IOError as e:
        raise UserError(f"Error al escribir en el fichero: {str(e)}")


    message = f'{len(self)} contactos procesados. ' + errors_filename  

    return {
      'type': 'ir.actions.client',
      'tag': 'display_notification',
      'params': {
          'title': 'Actualización completa',
          'message': message,
          'type': 'info',  # 'success', 'warning', 'danger', 'info'
          'sticky': False,
      }
    }
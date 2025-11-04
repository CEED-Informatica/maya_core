# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime
import pandas as pd

from ...maya_core.support.helper import read_itaca_csv, adjust_course_code

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

  telephone1 = fields.Char(string = 'Teléfono 1')
  telephone2 = fields.Char(string = 'Teléfono 2')

  student_info = fields.Char(string = 'Nombre completo', compute = '_compute_full_student_info')

  # puede estar matriculado en varios ciclos
  courses_ids = fields.One2many(
    'maya_core.student_course_rel', 
    'student_id', 
    string='Matrículas en cursos'
  )
  
  subjects_ids = fields.One2many('maya_core.subject_student_rel', 'student_id', order='subject_course asc, subject_name asc')

  
  def _compute_full_student_info(self):
    for record in self:
      record.student_info = record.surname + ', ' + record.name

  @staticmethod
  def update_student_data_from_itaca(record, df, data_stack, course_dict):
    """
    Procesa un único estudiante buscando sus emails en el DataFrame df.
    Actualiza también los cursos y grupos en los que está matriculado
    En caso de no aparecer marca la matrícula como baja
    Devuelve una tupla (actualizado: bool, lista_de_errores)
    """
    errors = []
    updated = False

    # Busco por cualquier email válido
    possible_emails = [
        (record.email_coorp or '').strip(),
        (record.email or '').strip(),
        (record.email_support or '').strip(),
    ]
    possible_emails = [e for e in possible_emails if e]

    if not possible_emails:
      errors.append(f"El estudiante {record.student_info} no tiene ningún email para buscar en Itaca.")
      return updated, errors

    # Buscar en Itaca
    found_rows = pd.DataFrame()
    for email in possible_emails:
      # otengo todas las filas  en las que el email esté en el registro del alumnno
      rows = df[(df['email_corporativo'] == email) | (df['email1'] == email) | (df['email2'] == email)]
      if not rows.empty:
        found_rows = rows
        break

    if found_rows.empty:
      errors.append(f"No se encuentra información en Itaca para {record.student_info} (emails: {', '.join(possible_emails)})")
      return updated, errors

    # Si hay varias filas compruebo que sea el mismo NIA (se puede dar el caso de 
    # hermanos y que el correo se el de alguno de los padres)
    nias = found_rows['NIA'].dropna().unique().tolist()
    if len(nias) > 1:
      errors.append(
        f"Varias entradas en Itaca para {record.student_info} con distintos NIA: {nias}. "
        f"Revisa el fichero, el email no es único."
      )
      return updated, errors

    nia = nias[0] if nias else None
    if nia:
      record.nia = nia

    # Actualizo los datos personales desde la primera fila
    row = found_rows.iloc[0]
    record.email_coorp = row.get('email_corporativo') or record.email_coorp
    record.email = row.get('email1') or record.email
    record.email_support = row.get('email2') or record.email_support
    record.telephone1 = row.get('telefono1') or record.telephone1
    record.telephone2 = row.get('telefono2') or record.telephone2
    updated = True

    # Proceso todos los cursos asociados
    itaca_courses = []
    for _, row in found_rows.iterrows():
      code = adjust_course_code(str(row.get('curso')).strip())
      group = str(row.get('grupo')).strip() or None
      course_id = course_dict.get(code)

      if not course_id:
        errors.append(f"Curso con código {code} no encontrado en Odoo para {record.student_info}")
        continue

      itaca_courses.append(course_id)

      rel = record.courses_ids.filtered(lambda r: r.course_id.id == course_id)
      if rel:
        if rel.group != group or not rel.active:
            rel.write({'group': group, 'active': True})
      else:
        record.env['maya_core.student_course_rel'].create({
            'student_id': record.id,
            'course_id': course_id,
            'group': group,
        })

    # si no aparecen las marco como baja
    for rel in record.courses_ids:
        if rel.course_id.id not in itaca_courses:
            rel.active = False

    return updated, errors

  def update_itaca_fields(self):
    """
    Actualiza los datos desde Itaca de todos los estudiantes seleccionados
    """
    #TODO parametrizar estos datos en configuraciones
    # TODO mejorar creando un diccionario por mail, pero deberia controlar que pasa con dos claves iguales
    itaca_filename = self.env['ir.config_parameter'].get_param('maya_core.itaca_students_data')
    if not itaca_filename:
      print(f'\033[0;31m[ERROR]\033[0m No se ha definido el nombre del fichero de datos de itaca')
      return

    csv_file = '/mnt/odoo-repo/itaca/' + itaca_filename
    """ 
    try:
      df = pd.read_csv(csv_file)
    except FileNotFoundError:
      raise UserError(f"¡Operación cancelada!\n\nNo se pudo encontrar el fichero de datos Itaca en {csv_file}.")
    
    # aplano la lista para ver si el valor del mail está o está  repetido
    data_stack = df.stack() """
    try:
      df, data_stack = read_itaca_csv(csv_file)
    except Exception as e:
      print(f"\033[0;31m[ERROR]\033[0m Error procesando el fichero csv: {str(e)}")
      return
    
    # creo un diccionario con los cursos
    course_dict = {
        c.code.strip(): c.id
        for c in self.env['maya_core.course'].search([])
        if c.code
    }
  
    errors = []
    
    for record in self:
      _, record_errors = Student.update_student_data_from_itaca(record, df, data_stack, course_dict)
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
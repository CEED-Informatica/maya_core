# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import ValidationError

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
  email_coorp = fields.Char(string = 'Email coorporativo')

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


  def update_student_from_itaca(self):
    """
    Actualiza los datos desde Itaca de un estudiante
    """
    print("pasooO   1")

  def update_itaca_fields(self):
    """
    Actualiza los datos desde Itaca de todos los estudiantes seleccionados
    """

    for record in self:
      print(record.name)
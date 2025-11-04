# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StudentCourseRel(models.Model):
  """
  Se crea como tabla de relación (pivote) entre Student y Course para dar soporte a un campo 
  intermedio (group)
  """
  _name = 'maya_core.student_course_rel'
  _description = 'Relación entre student y course'

  student_id = fields.Many2one(
    'maya_core.student', 
    string='Estudiante', 
    required=True, 
    ondelete='cascade'
  )
  course_id = fields.Many2one(
    'maya_core.course', 
    string='Curso', 
    required=True, 
    ondelete='cascade'
  )

  group = fields.Char(string='Grupo')
  active = fields.Boolean(default=True)
  
  course_name = fields.Char(related='course_id.name', string='Curso', store=False)
  course_teaching = fields.Selection(related='course_id.teaching', string='Enseñanza', store=False)


  # Constraints para evitar duplicados (un estudiante solo puede estar
  # una vez en el mismo curso)
  _sql_constraints = [
      ('student_course_uniq', 'unique(student_id, course_id)', 
       'Este estudiante ya está matriculado en este curso.')
  ]

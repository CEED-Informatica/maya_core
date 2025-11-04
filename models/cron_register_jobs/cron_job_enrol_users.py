# -*- coding: utf-8 -*-

from odoo import models, api
import logging

# Moodle
from ...support.maya_moodleteacher.maya_moodle_connection import MayaMoodleConnection
from ...support.maya_moodleteacher.maya_moodle_user import MayaMoodleUsers

_logger = logging.getLogger(__name__)

class CronJobEnrolUsers(models.TransientModel):
  _name = 'maya_core.cron_job_enrol_users'
  
  @staticmethod
  def enrol_student(self, user, subject_id, course_id, only_create: bool = False):
    """
    Matricula a un usuario maya en un módulo
    Si no existe el usuario, lo crea

    user: usuario moodle
    subject_id: identificador Maya del módulo
    course_id: identificador Maya del ciclo 
    only_create: solo crea el usuario si no existe. No lo vincula con el aula
    """

    # comprobación: ya está en Maya
    # devuelve un recorset
    student = self.env['maya_core.student'].search([('moodle_id', '=', user.id_)])
    if len(student) == 0:
      # No existe, se crea el estudiante Maya
      new_student = self.env['maya_core.student'].create({
        'moodle_id': user.id_,
        'name': user.firstname,
        'surname': user.lastname,
        'email': user.email
      })
      _logger.info('Creando en Maya al estudiante moodle_id:{}'.format(user.id_))
    else: 
      _logger.info('El estudiante moodle_id:{} ya existe en Maya'.format(user.id_))
      new_student = student[0]

    if only_create:
      return new_student

    enrolled = new_student.subjects_ids.filtered(lambda r: r.subject_id.id == subject_id)

    if len(enrolled) == 0:
      # No está matriculado en ese módulo, se matricula
      # el 4 añade una relación entre el record y el record relacionado (subject_id)
      # Al menos en la versión 13, en relaciones M2M con tabla intermedia personalizada no crea el registro
      # así que se crea de manera manual 
      self.env['maya_core.subject_student_rel'].create({
        'student_id': new_student.id,
        'subject_id': subject_id,
        'course_id': course_id
      })

      # y luego se vincula
      #new_student.subjects_ids = [ (4, subject_id, 0 )] 
      _logger.info("Estudiante moodle_id:{} no matriculado en el módulo_maya_id: {} -> Matriculando".format(user.id_,course_id))
    else:
      _logger.info("Alumno moodle_id:{} ya estaba matriculado en el módulo_maya_id: {}".format(user.id_, course_id))

    return new_student

  @api.model
  def cron_enrol_students(self, classroom_id, course_id, subject_id):
    """
    Asocia (matricula) estudiantes en un aula

    cron_job_data: estructura del tipo CronJobData que debe incluir:
       classroom_id: aula de Moodle de la que tiene que coger los usuarios
       subject_id: identificador de Maya de la materia en la que se matricula
       course_id: identificador de Maya del ciclo formativo

    En caso de que el estudiante no se encuentre en Maya lo crea
    """
    # comprobaciones iniciales
    if classroom_id == None:
      _logger.error("CRON: classroom_id no definido")
      return
    
    if course_id == None:
      _logger.error("CRON: course_id no definido")
      return
    
    if subject_id == None:
      _logger.error("CRON: subject_id no definido")
      return
    
    try:
      conn = MayaMoodleConnection( 
        user = self.env['ir.config_parameter'].get_param('maya_core.moodle_user'), 
        moodle_host = self.env['ir.config_parameter'].get_param('maya_core.moodle_url')) 
    except Exception:
      raise Exception('No es posible realizar la conexión con Moodle')

    # obtención de los usuarios
    users = MayaMoodleUsers.from_course(conn, classroom_id, only_students = True)

    for user in users:
      CronJobEnrolUsers.enrol_student(self, user, subject_id, course_id)
      #self.enrol_student(user, subject_id, course_id)

    
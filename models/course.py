from odoo import models, fields, _

class Course(models.Model):
  """  
  Define un curso: ciclo formativo, tipo bachillerato, etc
  """

  _name = 'maya_core.course'
  _description = 'Ciclo Formativo'

  abbr = fields.Char('Abreviatura', size = 5,required = True, translate=True)
  name = fields.Char('Ciclo', required = True, translate=True)
  code = fields.Char('Código', required = True, size = 6)

  teaching = fields.Selection([
    ('4', _('Bachillerato')),
    ('5', _('Ciclos')),
    ('7', _('ESPA'))
     ], string = _('Tipo de enseñanza'), default = '7')

  subjects_ids = fields.Many2many('maya_core.subject', string = 'Módulos')
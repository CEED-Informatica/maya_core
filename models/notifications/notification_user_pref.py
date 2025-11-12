from odoo import models, fields, api

class NotificationUserPref(models.Model):
  """
  Define las posibles configuraciones de notificaciones Maya
  que puedw realizar un usuario
  """

  _name = 'maya_core.notification_user_pref'
  _description = 'Preferencias de las notificaciones de Maya por usuario'
  _order = 'provider_id'

  user_id = fields.Many2one(
    'res.users',
    string="Usuario",
    required=True,
    ondelete="cascade"
  )

  provider_id = fields.Many2one(
    'maya_core.notification_provider',
    string="Módulo",
    required=True,
    ondelete="cascade"
  )

  enabled = fields.Boolean("Recibir notificaciones", default=True)

  _sql_constraints = [
      ('unique_user_provider', 'unique(user_id, provider_id)', "La preferencia ya existe para este usuario y módulo.")
  ]

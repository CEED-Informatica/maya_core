# -*- coding: utf-8 -*-

from odoo import models, fields

class NotificationGroup(models.Model):
  """
  Modela los diferentes grupos de notificaciones que puede proporcionasr un provider
  """
  _name = "maya_core.notification_group"
  _description = "Tipo de notificación que puede proporcionar un módulo"
  _order = "name"

  name = fields.Char("Nombre", required=True)
  is_enabled = fields.Boolean("Notificaciones activadas", default=True)
  provider_id = fields.Many2one('maya_core.notification_provider',
    required=True,
    ondelete='cascade',  # Si se borra el notification_provider, se borra este grupo
  )

  def render_block(self, user, group) -> str:
    """
    Genera el bloque HTML a insertar en la notificación
    Será sobreescrito por cada módulo
    
    :return HTML listo para insertar.
    """
    return ""
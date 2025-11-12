# -*- coding: utf-8 -*-

from odoo import models, fields

class NotificationProvider(models.Model):
  """
  Registra cada módulo que puede generar notificaciones
  """

  _name = "maya_core.notification_provider"
  _description = "Módulos que pueden proporcionar notificaciones"
  _order = "name"

  name = fields.Char("Nombre", required=True)
  technical_name = fields.Char("Nombre técnico del módulo", required=True, index=True)
  is_enabled = fields.Boolean("Notificaciones activadas", default=True)
  groups = fields.One2many('maya_core.notification_group', 'provider_id', string = 'Grupos de notificaciones')


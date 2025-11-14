# -*- coding: utf-8 -*-

from odoo import models, fields, _

class NotificationItem(models.Model):
    """
    Notificación generada por cada módulo
    """

    _name = "maya_core.notification_item"
    _description = "Notificación pendiente"

    provider_id = fields.Many2one('maya_core.notification_provider', required=True)
    user_id = fields.Many2one('res.users', required=True, ondelete='cascade')
    ngroup_id = fields.Many2one('maya_core.notification_group', required=True)
    summary = fields.Char()        # texto corto
    body = fields.Text()           # html o texto extra
    date = fields.Datetime(default=fields.Datetime.now)
    priority = fields.Selection([
        ('0', _('Baja')),
        ('1', _('Media')),
        ('2', _('Alta')),
        ('3', _('Crítica')) 
    ], default='1')
   
    link_objects = fields.Json(string="URL de los objetos implicados en la notificación")
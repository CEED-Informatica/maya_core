# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    moodle_user = fields.Char(string = 'Usuario acceso a Moodle', config_parameter='maya_core.moodle_user',
                              help = 'Usuario (clave) definido en .maya_moodleteacher')
    moodle_url = fields.Char(string = 'URL del servidor de Moodle', config_parameter='maya_core.moodle_url')

    moodle_user_admin = fields.Char(string = 'Administrador acceso a Moodle', config_parameter='maya_core.moodle_user_admin',
                              help = 'Usuario (clave) definido en .maya_moodleteacher con permisos de administración en Moodle')

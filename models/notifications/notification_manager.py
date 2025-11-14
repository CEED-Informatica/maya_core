from odoo import models, api
from datetime import date

class NotificationManager(models.Model):
  """
  Gestiona la ejecución de las notificaciones
  """
  _name = "maya_core.notification_manager"
  _description = "Gestor de notificaciones Maya"

  # -----------------------------------------------------------
  # Construye el cuerpo del email combinando los módulos
  # -----------------------------------------------------------
  def build_email_body_for_user(self, user, providers):
      html_parts = []

      for provider in providers:

        html_parts.append(
          self.env['ir.ui.view']._render_template(
          'maya_core.notification_provider_header',{
            'name': provider.name,
          }))

        for group in provider.groups:
          block = group.render_block(user, group)
          if block:
            html_parts.append(
              self.env['ir.ui.view']._render_template(
                'maya_core.notification_group_header',{
                'name': group.name.upper(),
              }))
              
            html_parts.append(block)

        if len(html_parts)<=1: # sólo cabecera del provider
          return ''

      return '\n'.join(html_parts)

  @api.model
  def run_notifications(self):
    """
    Envía las notificaciones a todos los usuarios del sistema que estén activos
    """
    users = self.env['res.users'].search([('active', '=', True), ('maya_employee_id','!=', False)])

    template = self.env.ref('maya_core.email_template_notificacion_maya_users')
    today = date.today().strftime('%d/%m/%Y')

    providers = self.env['maya_core.notification_provider'].search([('is_enabled', '=', True)])

    for user in users:
      body_html = self.build_email_body_for_user(user, providers)

      if len(body_html) == 0: # no hay notificaciones para ese usuario
        continue

      # Se usa el template global pero reemplazamos el cuerpo
      template.with_context(
          today = today,
          body_html_dynamic=body_html
      ).send_mail(
          user.maya_employee_id.id,
          force_send=False,
          email_values={
            'email_to': user.email,
            #'email_from': 'Notificaciones Maya <notificaciones@tu_dominio.com>',
         }
      )

    return 

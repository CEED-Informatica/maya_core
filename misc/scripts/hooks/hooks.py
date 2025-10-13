# -*- coding: utf-8 -*-

import os
import logging
from odoo.tools import config

_logger = logging.getLogger(__name__)

"""
IMPORTANTE:
  - Los scripts llamados desde el manifest SOLO se ejecutan en la instalación,
  NO EN LAS ACTUALIZACIONES
"""

def create_itaca_data_folder():
  """
  Hook para crear un directorio de datos para almacenar los datos de Itaca
  """
  data_dir = '/mnt/odoo-repo/'

  itaca_path = os.path.join(data_dir, 'itaca')
  
  # Comprobamos si la carpeta no existe y la creamos.
  if not os.path.exists(itaca_path):
    try:
      _logger.info(f"Creando directorio de datos de Itaca : {itaca_path}")
      os.makedirs(itaca_path)
      _logger.info("Directorio creado exitosamente.")
    except OSError as e:
        _logger.error(f"Error al crear el directorio {itaca_path}: {e}")
  else:
    _logger.info(f"El directorio {itaca_path} ya existe.")
# -*- coding: utf-8 -*-
# import subprocess
# import re

import fitz
from math  import isclose
import pandas as pd
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

def is_set_flag(value, option):
    """
    Devuelve True o False si la opción aparece en el valor
    Por ejemplo: is_set_flag(25, 1) -> True
    Por ejemplo: is_set_flag(25, 2) -> False
    """
    return value & 1 << option != 0

def set_flag(value, option):
    """
    Asigna un uno (pone a True) en la propiedad (posición) indicada 
    Por ejemplo: set_flag(24, 1) -> 25
    """
    return value | (1 << option) 

def unset_flag(value, option):
    """
    Asigna un cero (pone a False) en la propiedad (posición) indicada 
    Por ejemplo: unset_flag(25, 1) -> 24
    """
    return value | ~(1 << option) 

def get_data_from_pdf(pdf_file: str, template: list):
    """
    Obtiene información de los formularios de un pdf
    """
    
    """ # Ejecutar pdftk y capturar la salida
    pdftk_command = ['pdftk', pdf_file, 'dump_data_fields_utf8']
    output = subprocess.run(pdftk_command, capture_output = True, text = True, check = True)

    # Procesamos la salida utilizando expresiones regulares
    field_regex = re.compile('FieldType: (.*)\\nFieldName: (.*)\\n(.*\\n|.*\\n.*\\n)FieldValue: (.*)\\n')
    #"FieldName: (.*)\n|FieldValue: (.*)\n"gm

    fields = {}

    for match in field_regex.finditer(output.stdout):
      fields[match.group(2)] = (match.group(4).strip(), match.group(1))  """
    
    def inttype2string(int_type: int) -> str:
        """
        Devuelve el tipo del field de un pdf en formato string a partir del entero
        """
        return {
            7: 'Text',
            6: 'Signature',
            3: 'Choice',
            2: 'Button',
        }.get(int_type)
    
    fields = {}
    fields_w = {}

    # inicializo con los valores por defecto
    for field in template:
      fields[field[0]] = (field[4], inttype2string(field[3]))

    try:
      doc = fitz.open(pdf_file, filetype="pdf")
    except:
      raise Exception("No es posible leer el pdf")
      
    for page in doc:
        
      fields_found = False  
        
      # se intenta leer los fields del formulario
      for field in page.widgets():
         
        # if field.field_name == template[0][0]: # hack para ir elegir un método u otro
        #   fields_found = True
        
        # en caso de button (casilla de selección) que no tenga valor, le asigno off
        if field.field_type == 2 and field.field_value.strip() == '':
          field.field_value = 'Off'

        fields_w[field.field_name] = (field.field_value.strip(), inttype2string(field.field_type))
        
      # hay fields en el pdf. no hace falta que intente obtenerlos por texto
      # if fields_found:
      #   continue
        

      file_dict = page.get_text('dict')  # Obtengo un diccionario con los datos de la página
      blocks_info = file_dict['blocks'] # me quedo sólo la lista de los bloques
    
      for block in blocks_info:   # cada block es un diccionario   
        if block['type'] != 0: # solo bloques de texto
          continue
      
        for line in block['lines']:
          # print(line)  # descomentar para investigar las areas
          for span in line['spans']:
            x0, y0 = span['origin'] 
            for field in template:                         
              if isclose(x0, field[1], abs_tol = 4) and isclose(y0, field[2], abs_tol = 3.5) :            
                if field[3] == 2:
                  if len(span['text']) == 1: # al estar tan cerca los bloques, la holgura pudiera coger otros elementos
                                             # nos aseguramos de que solo tenga un caracter
                    fields[field[0]] = ('Yes', inttype2string(field[3]))
                else:
                  fields[field[0]] = (span['text'].strip(), inttype2string(field[3]))
        
    return fields, fields_w
 
def create_HTML_list_from_list(data_list, intro = '', ident = True) -> str:
    """
    Genera una lista HMTL a partir de un list 
    """ 
    html_list = ''
    padding_left = '3rem'
    if not ident:
       padding_left = '0rem'

    html_list = f'<p style="padding-left: {padding_left}">{intro}</p><ul style="margin-left: 3rem">'
    for mf in data_list:
      html_list += f'<li>{mf}'  
    html_list += '</ul>'

    return html_list

def split_list(a: list, n: int) -> list:
    """
    Divide una lista de n listas a partir de la lista a
    Basado en: https://stackoverflow.com/a/2135920
    """
    if n<=0:
        return a
    
    n = min(n, len(a))
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def read_itaca_csv(filename: str) -> tuple[pd.DataFrame, pd.Series]:
  """
  Lee el fichero CSV con los datos de Itaca y devuelve el DataFrame original y su versión aplanada.

  :param filename: Ruta completa al fichero CSV.
  :return: Una tupla (df, df_aplanado) donde:
            - df: DataFrame original leído del CSV
            - df_aplanado: Serie con todos los valores del DataFrame aplanados
  :raises UserError: Si el fichero no existe o no se puede leer.
  """
  try:
    df = pd.read_csv(filename)
  except FileNotFoundError:
    raise UserError(f"¡Operación cancelada!\n\nNo se pudo encontrar el fichero de datos Itaca en {filename}.")
  except pd.errors.ParserError as e:
    raise UserError(f"Error al leer el fichero CSV {filename}: {str(e)}")

  df_aplanado = df.stack()

  return df, df_aplanado

def adjust_course_code(in_code: str) -> str:
  """
  Toma un codigo de ciclo de la nueva ley lfp y lo pasa al loe
  Esta funcion deberia ser obsoleta en al curso 2627, cuando actualicemos
  los códigos de los ciclos en maya
  """
  dict_lfp = {
              '3306174046': '441104',   # AFI
              '3306174048': '441104',   # AFI
              '3306174062': '906104',   # ADI 
              '3306174064': '906104',   # ADI
              '3306169651': '845104',   # DAW
              '3306169658': '845104',   # DAW
              '3306169635': '836104',   # DAM
              '3306169637': '836104',   # DAM
              '3306169744': '829104',   # ASIR
              '3306169751': '829104',   # ASIR
              '3306172482': '714104',   # GAT
              '3306172484': '714104',   # GAT
              '3306172403': '828104',   # GIAT
              '3306172410': '828104',   # GIAT
              '3306172330': '827104',   # AVGE
              '3306172332': '827104',   # AVGE
              '3306172133': '449104',   # CI
              '3306172135': '449104',   # CI
              '3306172181': '898104',   # TIL
              '3306172183': '898104',   # TIL
              '3306172149': '899104',   # GVEC
              '3306172151': '899104',   # GVEC
              '3306172167': '222104',   # MIP
              }
  
  if in_code not in dict_lfp:
    return None

  return dict_lfp[in_code]

def add_error_code(code: str, error_codes: str) -> str:
    """
    Añade un código de error a un modelo, evitando duplicados

    :code código de error a añadir
    :error_codes código de errores previos
    """
    
    codes = set((error_codes or '').split(','))
    codes.add(code)
    
    return ','.join(sorted([c for c in codes if c]))
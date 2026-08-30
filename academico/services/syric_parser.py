import re
import pandas as pd
from datetime import datetime
from django.db import transaction
from django.contrib.auth.models import User
from academico.models import Curso, Cursante, Inscripcion, TituloCursante

def clean_dni(val):
    if pd.isna(val):
        return ""
    # Remove all non-numeric characters (points, spaces, hyphens)
    cleaned = re.sub(r'\D', '', str(val))
    return cleaned

def extract_contacts(contacts_str):
    if pd.isna(contacts_str) or not isinstance(contacts_str, str):
        return "", ""
    
    # Search for an email pattern
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email_match = re.search(email_pattern, contacts_str)
    email = email_match.group(0) if email_match else ""
    
    # Remove email pattern to search for phone number
    remaining = contacts_str.replace(email, "") if email else contacts_str
    
    # Search for telephone number pattern: numbers with potential dashes, spaces, parentheses
    phone_pattern = r'(\+?[\d\s\(\)-]{6,}\d)'
    phone_match = re.search(phone_pattern, remaining)
    
    phone = ""
    if phone_match:
        phone = phone_match.group(0).strip()
        # Clean extra spaces inside the phone
        phone = re.sub(r'\s+', ' ', phone)
    
    return email, phone

def parse_date_value(val):
    if pd.isna(val) or val == "" or str(val).strip() == "":
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.date()
    
    val_str = str(val).strip()
    # Try common formats
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            continue
            
    # Try pandas parser as fallback
    try:
        dt = pd.to_datetime(val_str, errors='coerce')
        if not pd.isna(dt):
            return dt.date()
    except Exception:
        pass
    return None

def parse_single_title(title_str):
    title_str = title_str.strip()
    if not title_str:
        return None, "", None
        
    # Extract level inside brackets at the end, e.g. [Terciario]
    level_match = re.search(r'\[([^\]]+)\]\s*$', title_str)
    level = level_match.group(1).strip() if level_match else None
    
    # Remove level bracket from main string if found
    main_part = title_str
    if level_match:
        main_part = title_str[:level_match.start()].strip()
        
    # Extract code (numeric at the start)
    # e.g. 100452 - TECNICO... or 100452 TECNICO... or just TECNICO...
    code_match = re.match(r'^(\d+)\s*(?:-\s*)?', main_part)
    code = code_match.group(1).strip() if code_match else None
    
    # Remove code from main part if found
    name = main_part
    if code_match:
        name = main_part[code_match.end():].strip()
        
    return code, name, level

def import_syric_file(file_obj, filename, curso_id):
    stats = {
        'total': 0,
        'creados_cursantes': 0,
        'actualizados_cursantes': 0,
        'creadas_inscripciones': 0,
        'actualizadas_inscripciones': 0,
        'existentes_inscripciones': 0,
        'errores': []
    }
    
    try:
        curso = Curso.objects.get(id=curso_id)
    except Curso.DoesNotExist:
        stats['errores'].append({
            'fila': 0,
            'identificador': 'N/A',
            'error': f'El curso seleccionado con ID {curso_id} no existe.'
        })
        return stats

    # Load file with pandas based on file extension
    try:
        if filename.endswith('.csv'):
            import io
            # Read bytes and decode to text
            content_bytes = file_obj.read()
            try:
                decoded_content = content_bytes.decode('utf-8')
            except UnicodeDecodeError:
                decoded_content = content_bytes.decode('latin-1')
            
            df = pd.read_csv(io.StringIO(decoded_content), sep=None, engine='python')
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_obj)
        else:
            stats['errores'].append({
                'fila': 0,
                'identificador': 'Archivo',
                'error': 'Formato de archivo no soportado. Debe ser .xlsx, .xls o .csv'
            })
            return stats
    except Exception as e:
        stats['errores'].append({
            'fila': 0,
            'identificador': 'Archivo',
            'error': f'Error al leer el archivo: {str(e)}'
        })
        return stats

    # Normalize columns names to lower case
    df.columns = [str(c).strip() for c in df.columns]
    columns_lower = [c.lower() for c in df.columns]
    
    # Dynamic header mapping
    dni_col = None
    nombre_col = None
    apellido_col = None
    nombre_completo_col = None
    contactos_col = None
    email_col = None
    telefono_col = None
    titulo_col = None
    nacimiento_col = None
    preinscripcion_col = None
    fecha_insc_col = None
    
    for col in df.columns:
        c_low = col.lower()
        if 'dni' in c_low or 'documento' in c_low or 'nro doc' in c_low or 'cedula' in c_low:
            dni_col = col
        elif 'apellido' in c_low:
            apellido_col = col
        elif 'nombre' in c_low:
            if 'completo' in c_low or 'apellido' in c_low:
                nombre_completo_col = col
            else:
                nombre_col = col
        elif 'contacto' in c_low:
            contactos_col = col
        elif 'email' in c_low or 'correo' in c_low:
            email_col = col
        elif 'telefono' in c_low or 'teléfono' in c_low or 'celular' in c_low:
            telefono_col = col
        elif 'titulo' in c_low or 'título' in c_low or 'estudios' in c_low:
            titulo_col = col
        elif 'nacimiento' in c_low or 'fecha_nac' in c_low or 'nac' in c_low:
            nacimiento_col = col
        elif 'preinscripcion' in c_low or 'preinscripción' in c_low or 'id_pre' in c_low or 'syric' in c_low:
            preinscripcion_col = col
        elif 'fecha' in c_low and ('insc' in c_low or 'alta' in c_low):
            fecha_insc_col = col

    # Check minimum columns
    if not dni_col:
        stats['errores'].append({
            'fila': 0,
            'identificador': 'Cabeceras',
            'error': 'No se pudo identificar una columna de DNI/Documento. Verifique el archivo.'
        })
        return stats

    stats['total'] = len(df)

    # Ingest rows
    for index, row in df.iterrows():
        fila_num = index + 1
        raw_dni = row.get(dni_col)
        dni = clean_dni(raw_dni)
        
        if not dni:
            stats['errores'].append({
                'fila': fila_num,
                'identificador': f'Fila {fila_num}',
                'error': 'DNI vacío o inválido.'
            })
            continue

        try:
            # Determine Name and Surname
            nombre = ""
            apellido = ""
            if nombre_completo_col and row.get(nombre_completo_col):
                full_name = str(row[nombre_completo_col]).strip()
                if ',' in full_name:
                    parts = full_name.split(',', 1)
                    apellido = parts[0].strip()
                    nombre = parts[1].strip()
                else:
                    parts = full_name.split(' ', 1)
                    nombre = parts[0].strip()
                    apellido = parts[1].strip() if len(parts) > 1 else ""
            else:
                nombre = str(row.get(nombre_col, '')).strip() if not pd.isna(row.get(nombre_col)) else ""
                apellido = str(row.get(apellido_col, '')).strip() if not pd.isna(row.get(apellido_col)) else ""
            
            # If still missing, fill with defaults
            if not nombre and not apellido:
                nombre = "Cursante"
                apellido = f"DNI {dni}"
            elif not nombre:
                nombre = "Cursante"
            elif not apellido:
                apellido = "Cursante"

            # Determine email and phone
            email = ""
            telefono = ""
            if contactos_col and row.get(contactos_col):
                email, telefono = extract_contacts(str(row[contactos_col]))
            
            # Direct email/phone column overrides if present
            if email_col and row.get(email_col) and not pd.isna(row.get(email_col)):
                email = str(row[email_col]).strip()
            if telefono_col and row.get(telefono_col) and not pd.isna(row.get(telefono_col)):
                telefono = str(row[telefono_col]).strip()

            # Parse dates
            fecha_nacimiento = None
            if nacimiento_col:
                fecha_nacimiento = parse_date_value(row.get(nacimiento_col))
                
            fecha_inscripcion = None
            if fecha_insc_col:
                fecha_inscripcion = parse_date_value(row.get(fecha_insc_col))
            if not fecha_inscripcion:
                fecha_inscripcion = datetime.now().date()

            titulo_previo = str(row.get(titulo_col, '')).strip() if (titulo_col and not pd.isna(row.get(titulo_col))) else ""
            id_preinscripcion = str(row.get(preinscripcion_col, '')).strip() if (preinscripcion_col and not pd.isna(row.get(preinscripcion_col))) else ""

            # Save in database inside a transaction block
            with transaction.atomic():
                # 1. Update or create Cursante
                cursante_obj, created_cursante = Cursante.objects.update_or_create(
                    dni=dni,
                    defaults={
                        'nombre': nombre,
                        'apellido': apellido,
                        'email': email or None,
                        'telefono': telefono or None,
                        'fecha_nacimiento': fecha_nacimiento,
                        'titulo_previo': titulo_previo or None,
                    }
                )
                
                if created_cursante:
                    stats['creados_cursantes'] += 1
                else:
                    stats['actualizados_cursantes'] += 1

                # Process multiple titles
                if titulo_previo:
                    title_chunks = [c.strip() for c in titulo_previo.split('|') if c.strip()]
                    for chunk in title_chunks:
                        code, t_name, t_level = parse_single_title(chunk)
                        if t_name:
                            TituloCursante.objects.get_or_create(
                                cursante=cursante_obj,
                                nombre=t_name,
                                defaults={
                                    'codigo': code or None,
                                    'nivel': t_level or None,
                                }
                            )

                # 2. Get or create Inscripcion (Incremental safe import)
                inscripcion_obj, created_inscripcion = Inscripcion.objects.get_or_create(
                    cursante=cursante_obj,
                    curso=curso,
                    defaults={
                        'id_preinscripcion_syric': id_preinscripcion or None,
                        'fecha_inscripcion': fecha_inscripcion,
                    }
                )

                if created_inscripcion:
                    stats['creadas_inscripciones'] += 1
                else:
                    stats['existentes_inscripciones'] += 1

        except Exception as ex:
            stats['errores'].append({
                'fila': fila_num,
                'identificador': f'DNI {dni}',
                'error': f'Error en procesamiento de BD: {str(ex)}'
            })

    return stats

import flet as ft

# Importamos la fábrica de sesiones de SQLAlchemy definida en conexion.py.
# Cada vez que necesitamos hablar con la base de datos, llamamos a SessionLocal()
# para obtener una sesión nueva, y la cerramos cuando terminamos.
from conexion import SessionLocal

# Importamos las funciones CRUD de cada "sector" (módulo de lógica de negocio).
# La UI no escribe SQL directamente: delega todo en estas funciones.
from sectores.profesores import (listar_profesores, crear_profesor,
                                  eliminar_profesor, tutores_disponibles)
from sectores.alumnos import (listar_alumnos, crear_alumno, eliminar_alumno,
                               listar_grupos, crear_grupo, listar_cursos)
from sectores.candidatos import (listar_candidatos, crear_candidato,
                                  eliminar_candidato, listar_llamadas,
                                  crear_llamada, listar_entrevistas, crear_entrevista)
from sectores.comite import listar_comites, crear_comite, eliminar_comite


# ============================================================
# PALETA DE COLORES Y CONSTANTES VISUALES
# Centralizar los colores aquí permite cambiar el tema en un solo lugar
# sin tener que buscarlos por todo el código.
# ============================================================
BG_DARK    = "#0F1117"   # Fondo principal (casi negro azulado)
BG_CARD    = "#1A1D2E"   # Fondo de tarjetas y formularios
BG_SIDEBAR = "#111320"   # Fondo de la barra de menú superior
ACCENT     = "#4F8EF7"   # Azul principal: títulos, bordes activos, íconos
ACCENT2    = "#7C5CBF"   # Violeta secundario (reservado para uso futuro)
SUCCESS    = "#2ECC71"   # Verde para mensajes de éxito
ERROR      = "#E74C3C"   # Rojo para errores y botón de eliminar
WARNING    = "#F39C12"   # Naranja para advertencias (reservado)
TEXT_MAIN  = "#EAE8FF"   # Texto principal (blanco lavanda)
TEXT_SUB   = "#8A8AAB"   # Texto secundario (gris medio, para labels)
BORDER     = "#2A2D45"   # Color de bordes de contenedores y tablas


def db():
    """Atajo para obtener una sesión de base de datos.
    Se usa así:
        session = db()
        datos = listar_algo(session)
        session.close()
    """
    return SessionLocal()


# ============================================================
# HELPERS UI
# Funciones reutilizables que devuelven widgets Flet ya configurados
# con el estilo visual de la app. Evitan repetir los mismos parámetros
# de color, borde y tipografía en cada panel.
# ============================================================

def make_header_cell(text: str) -> ft.DataColumn:
    """Columna de encabezado para DataTable.
    El texto aparece en azul acento y negrita para distinguirlo de los datos.
    """
    return ft.DataColumn(
        ft.Text(text, color=ACCENT, weight=ft.FontWeight.W_600, size=13)
    )


def make_data_cell(text) -> ft.DataCell:
    """Celda de datos para DataTable.
    Convierte cualquier valor a string; si es None o vacío, muestra '—'.
    """
    return ft.DataCell(ft.Text(str(text or "—"), color=TEXT_MAIN, size=13))


def make_field(label: str, value="", hint="", width=None, multiline=False, rows=1):
    """Campo de texto estilizado.
    Parámetros clave:
    - multiline: True para campos de varias líneas (ej: curriculum)
    - rows: cantidad de líneas visibles cuando multiline=True
    """
    return ft.TextField(
        label=label,
        value=str(value),
        hint_text=hint,
        width=width,
        multiline=multiline,
        min_lines=rows,
        max_lines=rows if multiline else None,
        border_color=BORDER,
        focused_border_color=ACCENT,        # El borde cambia a azul al hacer foco
        label_style=ft.TextStyle(color=TEXT_SUB),
        text_style=ft.TextStyle(color=TEXT_MAIN),
        bgcolor=BG_DARK,
        border_radius=8,
    )


def make_dropdown(label: str, options: list, value=None, width=None):
    """Selector desplegable estilizado.
    Recibe una lista de tuplas (key, texto_visible) y las convierte
    en opciones de Flet automáticamente.
    Ejemplo: [("TUTOR", "Tutor"), ("ESPECIALISTA", "Especialista")]
    """
    return ft.Dropdown(
        label=label,
        value=value,
        width=width,
        border_color=BORDER,
        focused_border_color=ACCENT,
        label_style=ft.TextStyle(color=TEXT_SUB),
        text_style=ft.TextStyle(color=TEXT_MAIN),
        bgcolor=BG_DARK,
        border_radius=8,
        options=[ft.dropdown.Option(key=str(k), text=str(v)) for k, v in options],
    )


def make_btn(text: str, on_click=None, color=ACCENT, icon=None):
    """Botón primario con fondo de color.
    Por defecto usa el azul acento; se puede pasar ERROR para botones de eliminar.
    """
    return ft.ElevatedButton(
        content=ft.Text(text, color="#ffffff", weight=ft.FontWeight.W_600),
        icon=icon,
        bgcolor=color,
        on_click=on_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        ),
    )


def make_icon_btn(icon, on_click=None, color=TEXT_SUB, tooltip=""):
    """Botón de solo ícono, usado en las celdas de acción de la tabla
    (ej: el ícono de papelera para eliminar un registro).
    """
    return ft.IconButton(
        icon=icon,
        on_click=on_click,
        icon_color=color,
        tooltip=tooltip,
    )


def make_page_title(text: str, icon=None):
    """Título de página con ícono opcional a la izquierda.
    Devuelve una Row con el ícono en azul y el texto en blanco grande.
    """
    items = []
    if icon:
        items.append(ft.Icon(icon, color=ACCENT, size=28))
    items.append(ft.Text(text, size=26, weight=ft.FontWeight.W_700, color=TEXT_MAIN))
    return ft.Row(items, spacing=12)


def snack(page: ft.Page, msg: str, success=True):
    """Muestra un mensaje toast (SnackBar) en la parte inferior de la pantalla.
    - success=True  → fondo verde
    - success=False → fondo rojo
    Se agrega al overlay de la página para que aparezca sobre todo el contenido.
    """
    sb = ft.SnackBar(
        content=ft.Text(msg, color="#ffffff"),
        bgcolor=SUCCESS if success else ERROR,
        duration=3000,  # Se cierra solo a los 3 segundos
    )
    page.overlay.append(sb)
    sb.open = True
    page.update()


# ============================================================
# PANEL PROFESORES
# Pantalla completa para gestionar los profesores del sistema.
# Permite crear nuevos profesores y eliminar existentes.
# ============================================================

def panel_profesores(page):
    page.clean()       # Borra el contenido actual de la pantalla
    page.bgcolor = BG_DARK

    # ── Campos del formulario de alta ───────────────────────
    # Cada campo corresponde a una columna de la tabla "profesores" en la BD
    dni           = make_field("DNI", width=150)
    nombre        = make_field("Nombre", width=150)
    apellidos     = make_field("Apellidos", width=150)
    domicilio     = make_field("Domicilio", width=200)
    nivel_estudios= make_field("Nivel Estudios", width=150)
    titulacion    = make_field("Titulación", width=150)
    # El tipo determina qué rol cumple el profesor: tutor, especialista o ambos
    tipo          = make_dropdown("Tipo", [
        ("TUTOR","Tutor"), ("ESPECIALISTA","Especialista"), ("AMBOS","Ambos")
    ], width=150)

    # ── Tabla de profesores ──────────────────────────────────
    # Se crea vacía; _refresh() la pobla con datos de la BD
    tabla = ft.DataTable(
        columns=[
            make_header_cell("ID"),
            make_header_cell("DNI"),
            make_header_cell("Nombre"),
            make_header_cell("Apellidos"),
            make_header_cell("Tipo"),
            make_header_cell("Acciones"),
        ],
        border=ft.border.all(1, BORDER),
        border_radius=10,
        heading_row_color=ft.Colors.with_opacity(0.08, ACCENT),  # Encabezado con tinte azul sutil
        column_spacing=24,
        rows=[],  # Empieza vacía
    )
    # Envolvemos la tabla en un Container para poder llamar .update() sobre ella
    tabla_container = ft.Container(content=tabla)

    # ── _build_rows ──────────────────────────────────────────
    def _build_rows(profes):
        """Convierte una lista de objetos Profesor (ORM) en filas de DataTable.
        El botón de eliminar captura el id del profesor con un closure (pid=p.id)
        para evitar el bug clásico de lambda en bucles.
        """
        rows = []
        for p in profes:
            rows.append(ft.DataRow(cells=[
                make_data_cell(p.id),
                make_data_cell(p.dni),
                make_data_cell(p.nombre),
                make_data_cell(p.apellidos),
                make_data_cell(p.tipo),
                ft.DataCell(ft.Row([
                    make_icon_btn(ft.Icons.DELETE,
                                  lambda e, pid=p.id: eliminar_y_recargar(pid),
                                  ERROR, "Eliminar"),
                ])),
            ]))
        return rows

    # ── _refresh ─────────────────────────────────────────────
    def _refresh():
        """Recarga la tabla desde la base de datos.
        Siempre abre una sesión nueva, consulta, cierra la sesión
        y actualiza el widget en pantalla.
        """
        session = db()
        profes = listar_profesores(session)
        session.close()
        tabla_container.content.rows = _build_rows(profes)
        tabla_container.update()

    def eliminar_y_recargar(pid):
        """Elimina un profesor por su ID y recarga la tabla."""
        session = db()
        eliminar_profesor(session, pid)
        session.close()
        snack(page, "Profesor eliminado")
        _refresh()

    def guardar(e):
        """Lee los campos del formulario, crea el profesor en BD
        y limpia los campos para un nuevo ingreso.
        """
        session = db()
        crear_profesor(session, dni.value, nombre.value, apellidos.value,
                       domicilio.value, nivel_estudios.value, titulacion.value, tipo.value)
        session.close()
        # Limpiar campos después de guardar
        dni.value = nombre.value = apellidos.value = ""
        domicilio.value = nivel_estudios.value = titulacion.value = ""
        snack(page, "Profesor guardado")
        _refresh()

    # ── Layout de la pantalla ────────────────────────────────
    page.add(
        ft.Container(
            content=ft.Column([
                # Botón para volver al menú principal
                ft.Row([
                    ft.TextButton("← Volver",
                                  on_click=lambda _: menu_principal(page),
                                  style=ft.ButtonStyle(color=ACCENT)),
                ]),
                make_page_title("Profesores", ft.Icons.PERSON),
                ft.Divider(color=BORDER),

                # Tarjeta del formulario de alta
                ft.Container(
                    content=ft.Column([
                        ft.Row([dni, nombre, apellidos]),
                        ft.Row([domicilio, nivel_estudios, titulacion]),
                        ft.Row([tipo, make_btn("Guardar", on_click=guardar,
                                               icon=ft.Icons.SAVE)]),
                    ], spacing=12),
                    bgcolor=BG_CARD,
                    border=ft.border.all(1, BORDER),
                    border_radius=12,
                    padding=ft.padding.all(20),
                ),
                ft.Container(height=16),  # Espaciador entre formulario y tabla

                # Contenedor de la tabla con scroll horizontal si hay muchas columnas
                ft.Container(
                    content=ft.Column([tabla_container], scroll=ft.ScrollMode.AUTO),
                ),
            ], spacing=16, expand=True),
            expand=True,
            padding=ft.padding.all(28),
            bgcolor=BG_DARK,
        )
    )
    _refresh()  # Carga los datos existentes al abrir el panel


# ============================================================
# PANEL ALUMNOS
# Similar al de profesores pero con la particularidad de que
# un alumno puede pertenecer a un grupo (relación FK).
# ============================================================

def panel_alumnos(page):
    page.clean()
    page.bgcolor = BG_DARK

    dni       = make_field("DNI", width=150)
    nombre    = make_field("Nombre", width=150)
    apellidos = make_field("Apellidos", width=150)
    # Dropdown de grupos: se carga dinámicamente desde la BD
    grupo_drop = make_dropdown("Grupo", [], width=200)

    tabla = ft.DataTable(
        columns=[
            make_header_cell("ID"),
            make_header_cell("DNI"),
            make_header_cell("Nombre"),
            make_header_cell("Apellidos"),
            make_header_cell("Grupo"),
            make_header_cell("Acciones"),
        ],
        border=ft.border.all(1, BORDER),
        border_radius=10,
        heading_row_color=ft.Colors.with_opacity(0.08, ACCENT),
        column_spacing=24,
        rows=[],
    )
    tabla_container = ft.Container(content=tabla)

    def _build_rows(alumnos, grupos_dict):
        """Construye filas de tabla.
        grupos_dict es un dict {id_grupo: objeto_grupo} para hacer lookup
        del código de grupo sin consultar la BD por cada fila.
        """
        rows = []
        for a in alumnos:
            # Resuelve el nombre del grupo o muestra "Sin grupo"
            grupo_text = (f"{grupos_dict[a.id_grupo].codigo}"
                          if a.id_grupo and a.id_grupo in grupos_dict else "Sin grupo")
            rows.append(ft.DataRow(cells=[
                make_data_cell(a.id),
                make_data_cell(a.dni),
                make_data_cell(a.nombre),
                make_data_cell(a.apellidos),
                make_data_cell(grupo_text),
                ft.DataCell(ft.Row([
                    make_icon_btn(ft.Icons.DELETE,
                                  lambda e, aid=a.id: eliminar_y_recargar(aid),
                                  ERROR, "Eliminar"),
                ])),
            ]))
        return rows

    def recargar_grupos():
        """Puebla el dropdown de grupos con los datos actuales de la BD.
        Se llama al abrir el panel para que las opciones estén disponibles
        antes de que el usuario intente crear un alumno.
        """
        session = db()
        grupos = listar_grupos(session)
        session.close()
        grupo_drop.options = [ft.dropdown.Option(key="", text="Sin grupo")]
        for g in grupos:
            label = f"{g.codigo} (Curso {g.id_curso})"
            grupo_drop.options.append(ft.dropdown.Option(key=str(g.id), text=label))
        page.update()

    def _refresh():
        session = db()
        alumnos = listar_alumnos(session)
        # Construimos el dict de grupos en la misma sesión para evitar abrirla dos veces
        grupos  = {g.id: g for g in listar_grupos(session)}
        session.close()
        tabla_container.content.rows = _build_rows(alumnos, grupos)
        tabla_container.update()

    def eliminar_y_recargar(aid):
        session = db()
        eliminar_alumno(session, aid)
        session.close()
        snack(page, "Alumno eliminado")
        _refresh()

    def guardar(e):
        session = db()
        gid = grupo_drop.value
        # Si no se seleccionó grupo, pasamos None a la BD (columna nullable)
        crear_alumno(session, dni.value, nombre.value, apellidos.value,
                     int(gid) if gid and gid.strip() else None)
        session.close()
        dni.value = nombre.value = apellidos.value = ""
        grupo_drop.value = ""
        snack(page, "Alumno guardado")
        _refresh()

    recargar_grupos()  # Carga las opciones del dropdown antes de mostrar la pantalla

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton("← Volver",
                                  on_click=lambda _: menu_principal(page),
                                  style=ft.ButtonStyle(color=ACCENT)),
                ]),
                make_page_title("Alumnos", ft.Icons.PEOPLE),
                ft.Divider(color=BORDER),
                ft.Container(
                    content=ft.Column([
                        ft.Row([dni, nombre, apellidos, grupo_drop]),
                        ft.Row([make_btn("Guardar", on_click=guardar,
                                         icon=ft.Icons.SAVE)]),
                    ], spacing=12),
                    bgcolor=BG_CARD,
                    border=ft.border.all(1, BORDER),
                    border_radius=12,
                    padding=ft.padding.all(20),
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column([tabla_container], scroll=ft.ScrollMode.AUTO),
                ),
            ], spacing=16, expand=True),
            expand=True,
            padding=ft.padding.all(28),
            bgcolor=BG_DARK,
        )
    )
    _refresh()


# ============================================================
# PANEL CANDIDATOS
# Gestiona personas que postulan para ser profesores.
# Tiene un campo de curriculum multilinea adicional.
# ============================================================

def panel_candidatos(page):
    page.clean()
    page.bgcolor = BG_DARK

    dni        = make_field("DNI", width=150)
    nombre     = make_field("Nombre", width=150)
    apellidos  = make_field("Apellidos", width=150)
    # Campo de texto largo para el CV del candidato
    curriculum = make_field("Curriculum", width=300, multiline=True, rows=3)
    # Tipo de puesto al que aplica el candidato
    tipo       = make_dropdown("Tipo Deseado", [
        ("TUTOR","Tutor"), ("ESPECIALISTA","Especialista"), ("AMBOS","Ambos")
    ], width=150)

    tabla = ft.DataTable(
        columns=[
            make_header_cell("ID"),
            make_header_cell("DNI"),
            make_header_cell("Nombre"),
            make_header_cell("Apellidos"),
            make_header_cell("Tipo"),
            make_header_cell("Acciones"),
        ],
        border=ft.border.all(1, BORDER),
        border_radius=10,
        heading_row_color=ft.Colors.with_opacity(0.08, ACCENT),
        column_spacing=24,
        rows=[],
    )
    tabla_container = ft.Container(content=tabla)

    def _build_rows(candidatos):
        rows = []
        for c in candidatos:
            rows.append(ft.DataRow(cells=[
                make_data_cell(c.id),
                make_data_cell(c.dni),
                make_data_cell(c.nombre),
                make_data_cell(c.apellidos),
                make_data_cell(c.tipo_deseado),
                ft.DataCell(ft.Row([
                    make_icon_btn(ft.Icons.DELETE,
                                  lambda e, cid=c.id: eliminar_y_recargar(cid),
                                  ERROR, "Eliminar"),
                ])),
            ]))
        return rows

    def _refresh():
        session = db()
        candidatos = listar_candidatos(session)
        session.close()
        tabla_container.content.rows = _build_rows(candidatos)
        tabla_container.update()

    def eliminar_y_recargar(cid):
        session = db()
        eliminar_candidato(session, cid)
        session.close()
        snack(page, "Candidato eliminado")
        _refresh()

    def guardar(e):
        session = db()
        crear_candidato(session, dni.value, nombre.value, apellidos.value,
                        curriculum.value, tipo.value)
        session.close()
        dni.value = nombre.value = apellidos.value = curriculum.value = ""
        snack(page, "Candidato guardado")
        _refresh()

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton("← Volver",
                                  on_click=lambda _: menu_principal(page),
                                  style=ft.ButtonStyle(color=ACCENT)),
                ]),
                make_page_title("Candidatos", ft.Icons.PEOPLE_ALT),
                ft.Divider(color=BORDER),
                ft.Container(
                    content=ft.Column([
                        ft.Row([dni, nombre, apellidos]),
                        ft.Row([curriculum, tipo]),
                        ft.Row([make_btn("Guardar", on_click=guardar,
                                         icon=ft.Icons.SAVE)]),
                    ], spacing=12),
                    bgcolor=BG_CARD,
                    border=ft.border.all(1, BORDER),
                    border_radius=12,
                    padding=ft.padding.all(20),
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column([tabla_container], scroll=ft.ScrollMode.AUTO),
                ),
            ], spacing=16, expand=True),
            expand=True,
            padding=ft.padding.all(28),
            bgcolor=BG_DARK,
        )
    )
    _refresh()


# ============================================================
# PANEL COMITÉ
# Gestiona los comités selectivos anuales.
# Un comité tiene un año y tres miembros: presidente, secretario y vocal.
# Los IDs de los miembros referencian a profesores existentes.
# ============================================================

def panel_comite(page):
    page.clean()
    page.bgcolor = BG_DARK

    anio       = make_field("Año", width=100)
    # Los tres campos de miembros esperan IDs de profesores ya cargados en el sistema
    presidente = make_field("ID Presidente", width=120)
    secretario = make_field("ID Secretario", width=120)
    vocal      = make_field("ID Vocal", width=100)

    tabla = ft.DataTable(
        columns=[
            make_header_cell("ID"),
            make_header_cell("Año"),
            make_header_cell("Presidente"),
            make_header_cell("Secretario"),
            make_header_cell("Vocal"),
            make_header_cell("Acciones"),
        ],
        border=ft.border.all(1, BORDER),
        border_radius=10,
        heading_row_color=ft.Colors.with_opacity(0.08, ACCENT),
        column_spacing=24,
        rows=[],
    )
    tabla_container = ft.Container(content=tabla)

    def _build_rows(comites):
        rows = []
        for c in comites:
            rows.append(ft.DataRow(cells=[
                make_data_cell(c.id),
                # El año se muestra en azul y negrita para destacarlo visualmente
                ft.DataCell(ft.Text(str(c.anio), color=ACCENT,
                                    weight=ft.FontWeight.W_700, size=14)),
                make_data_cell(c.id_presidente),
                make_data_cell(c.id_secretario),
                make_data_cell(c.id_vocal),
                ft.DataCell(ft.Row([
                    make_icon_btn(ft.Icons.DELETE,
                                  lambda e, cid=c.id: eliminar_y_recargar(cid),
                                  ERROR, "Eliminar"),
                ])),
            ]))
        return rows

    def _refresh():
        session = db()
        comites = listar_comites(session)
        session.close()
        tabla_container.content.rows = _build_rows(comites)
        tabla_container.update()

    def eliminar_y_recargar(cid):
        session = db()
        eliminar_comite(session, cid)
        session.close()
        snack(page, "Comité eliminado")
        _refresh()

    def guardar(e):
        # Convertimos a int porque los campos de texto devuelven strings
        session = db()
        crear_comite(session, int(anio.value), int(presidente.value),
                     int(secretario.value), int(vocal.value))
        session.close()
        anio.value = presidente.value = secretario.value = vocal.value = ""
        snack(page, "Comité creado")
        _refresh()

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton("← Volver",
                                  on_click=lambda _: menu_principal(page),
                                  style=ft.ButtonStyle(color=ACCENT)),
                ]),
                make_page_title("Comité Selectivo", ft.Icons.SUPERVISED_USER_CIRCLE),
                ft.Divider(color=BORDER),
                ft.Container(
                    content=ft.Column([
                        ft.Row([anio, presidente, secretario, vocal]),
                        ft.Row([make_btn("Crear comité", on_click=guardar,
                                         icon=ft.Icons.GROUPS)]),
                    ], spacing=12),
                    bgcolor=BG_CARD,
                    border=ft.border.all(1, BORDER),
                    border_radius=12,
                    padding=ft.padding.all(20),
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column([tabla_container], scroll=ft.ScrollMode.AUTO),
                ),
            ], spacing=16, expand=True),
            expand=True,
            padding=ft.padding.all(28),
            bgcolor=BG_DARK,
        )
    )
    _refresh()


# ============================================================
# MENÚ PRINCIPAL
# Pantalla de inicio de la aplicación.
# Ofrece dos formas de navegar: barra de menú superior y tarjetas de acceso rápido.
# ============================================================

def menu_principal(page):
    page.bgcolor = BG_DARK
    page.title = "Sistema de Gestión - Academia de Formación"

    # Funciones de navegación: limpian la pantalla y cargan el panel correspondiente
    def abrir_profesores(e): panel_profesores(page)
    def abrir_alumnos(e):    panel_alumnos(page)
    def abrir_candidatos(e): panel_candidatos(page)
    def abrir_comite(e):     panel_comite(page)

    page.clean()
    page.add(
        ft.Container(
            content=ft.Column([

                # ── Barra de menú superior ───────────────────
                # Menú tipo "archivo" clásico con submenús desplegables
                ft.Container(
                    content=ft.Row([
                        # Menú "Archivo": solo tiene la opción de salir
                        ft.PopupMenuButton(
                            items=[ft.PopupMenuItem(
                                "Salir", icon=ft.Icons.EXIT_TO_APP,
                                on_click=lambda e: page.window.close())],
                            content=ft.Text("Archivo", color=TEXT_MAIN,
                                            weight=ft.FontWeight.BOLD),
                        ),
                        # Menú "Herramientas": acceso a los cuatro paneles
                        ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem("Profesores", icon=ft.Icons.SCHOOL,
                                                 on_click=abrir_profesores),
                                ft.PopupMenuItem("Alumnos", icon=ft.Icons.PEOPLE,
                                                 on_click=abrir_alumnos),
                                ft.PopupMenuItem("Candidatos", icon=ft.Icons.PERSON_SEARCH,
                                                 on_click=abrir_candidatos),
                                ft.PopupMenuItem("Comité", icon=ft.Icons.ASSIGNMENT_IND,
                                                 on_click=abrir_comite),
                            ],
                            content=ft.Text("Herramientas", color=TEXT_MAIN,
                                            weight=ft.FontWeight.BOLD),
                        ),
                    ], spacing=20),
                    bgcolor=BG_SIDEBAR,
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                    # Línea divisoria inferior que separa el menú del contenido
                    border=ft.border.only(bottom=ft.border.BorderSide(1, BORDER)),
                ),

                # ── Contenido principal del menú ─────────────
                ft.Container(
                    content=ft.Column([
                        # Encabezado con ícono y nombre del sistema
                        ft.Row([
                            ft.Icon(ft.Icons.SCHOOL, color=ACCENT, size=36),
                            ft.Text("Sistema de Gestión",
                                    size=28, weight=ft.FontWeight.W_900, color=TEXT_MAIN),
                        ], spacing=12),
                        ft.Text("Academia de Formación Profesional",
                                size=14, color=TEXT_SUB),
                        ft.Divider(color=BORDER),
                        ft.Text("Accesos Rápidos", size=16,
                                color=TEXT_SUB, weight=ft.FontWeight.W_600),
                        # Tarjetas de acceso rápido: misma funcionalidad que el menú,
                        # pero más visual y fácil de usar con el ratón
                        ft.Row([
                            _quick_card("Profesores", ft.Icons.SCHOOL,    abrir_profesores),
                            _quick_card("Alumnos",    ft.Icons.PEOPLE,    abrir_alumnos),
                            _quick_card("Candidatos", ft.Icons.PERSON_SEARCH, abrir_candidatos),
                            _quick_card("Comité",     ft.Icons.ASSIGNMENT_IND, abrir_comite),
                        ], spacing=16, wrap=True),  # wrap=True para que se acomoden en pantallas chicas
                    ], spacing=16),
                    expand=True,
                    padding=ft.padding.all(32),
                ),
            ], spacing=0, expand=True),
            expand=True,
            bgcolor=BG_DARK,
        )
    )


def _quick_card(label, icon, on_click):
    """Tarjeta cuadrada clickeable para los accesos rápidos del menú.
    Muestra un ícono grande arriba y el nombre del módulo abajo.
    El parámetro ink=True agrega el efecto ripple al hacer clic.
    """
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, color=ACCENT, size=36),
            ft.Text(label, color=TEXT_MAIN, size=14, weight=ft.FontWeight.W_600),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        bgcolor=BG_CARD,
        border=ft.border.all(1, BORDER),
        border_radius=14,
        padding=ft.padding.all(24),
        width=140, height=110,
        on_click=on_click,
        ink=True,  # Efecto de onda al hacer clic (Material Design)
    )


# ============================================================
# PUNTO DE ENTRADA
# Flet llama a main(page) al iniciar la aplicación.
# Aquí se configuran las propiedades globales de la ventana
# antes de cargar la primera pantalla.
# ============================================================

def main(page: ft.Page):
    page.window.maximized = True       # La ventana arranca maximizada
    page.bgcolor = BG_DARK
    page.theme_mode = ft.ThemeMode.DARK  # Tema oscuro global de Flet
    page.padding = 0                   # Sin padding extra alrededor del contenido
    menu_principal(page)               # Carga la pantalla de inicio


ft.run(main)
import flet as ft
from coneccion import SessionLocal
from sectores.profesores import (listar_profesores, crear_profesor,
                                  eliminar_profesor, tutores_disponibles)
from sectores.alumnos import (listar_alumnos, crear_alumno, eliminar_alumno,
                               listar_grupos, crear_grupo, listar_cursos)
from sectores.candidatos import (listar_candidatos, crear_candidato,
                                  eliminar_candidato, listar_llamadas,
                                  crear_llamada, listar_entrevistas, crear_entrevista)
from sectores.comite import listar_comites, crear_comite, eliminar_comite


# ============================================================
# PALETA Y CONSTANTES (tomadas del primer código)
# ============================================================
BG_DARK    = "#0F1117"
BG_CARD    = "#1A1D2E"
BG_SIDEBAR = "#111320"
ACCENT     = "#4F8EF7"
ACCENT2    = "#7C5CBF"
SUCCESS    = "#2ECC71"
ERROR      = "#E74C3C"
WARNING    = "#F39C12"
TEXT_MAIN  = "#EAE8FF"
TEXT_SUB   = "#8A8AAB"
BORDER     = "#2A2D45"


def db():
    return SessionLocal()


# ============================================================
# HELPERS UI (del primer código)
# ============================================================

def make_header_cell(text: str) -> ft.DataColumn:
    return ft.DataColumn(
        ft.Text(text, color=ACCENT, weight=ft.FontWeight.W_600, size=13)
    )


def make_data_cell(text) -> ft.DataCell:
    return ft.DataCell(ft.Text(str(text or "—"), color=TEXT_MAIN, size=13))


def make_field(label: str, value="", hint="", width=None, multiline=False, rows=1):
    return ft.TextField(
        label=label,
        value=str(value),
        hint_text=hint,
        width=width,
        multiline=multiline,
        min_lines=rows,
        max_lines=rows if multiline else None,
        border_color=BORDER,
        focused_border_color=ACCENT,
        label_style=ft.TextStyle(color=TEXT_SUB),
        text_style=ft.TextStyle(color=TEXT_MAIN),
        bgcolor=BG_DARK,
        border_radius=8,
    )


def make_dropdown(label: str, options: list, value=None, width=None):
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
        options=[ft.DropdownOption(key=str(k), text=str(v)) for k, v in options],
    )


def make_btn(text: str, on_click=None, color=ACCENT, icon=None):
    return ft.ElevatedButton(
        content=ft.Text(text, color="#ffffff", weight=ft.FontWeight.W_600),
        icon=icon,
        bgcolor=color,
        on_click=on_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        ),
    )


def make_icon_btn(icon, on_click=None, color=TEXT_SUB, tooltip=""):
    return ft.IconButton(
        icon=icon,
        on_click=on_click,
        icon_color=color,
        tooltip=tooltip,
    )


def make_page_title(text: str, icon=None):
    items = []
    if icon:
        items.append(ft.Icon(icon, color=ACCENT, size=28))
    items.append(ft.Text(text, size=26, weight=ft.FontWeight.W_700, color=TEXT_MAIN))
    return ft.Row(items, spacing=12)


def snack(page: ft.Page, msg: str, success=True):
    sb = ft.SnackBar(
        content=ft.Text(msg, color="#ffffff"),
        bgcolor=SUCCESS if success else ERROR,
        duration=3000,
    )
    page.overlay.append(sb)
    sb.open = True
    page.update()


# ============================================================
# PANEL PROFESORES
# ============================================================

def panel_profesores(page):
    page.clean()
    page.bgcolor = BG_DARK

    # ── Campos del formulario ────────────────────────────────
    dni           = make_field("DNI", width=150)
    nombre        = make_field("Nombre", width=150)
    apellidos     = make_field("Apellidos", width=150)
    domicilio     = make_field("Domicilio", width=200)
    nivel_estudios= make_field("Nivel Estudios", width=150)
    titulacion    = make_field("Titulación", width=150)
    tipo          = make_dropdown("Tipo", [
        ("TUTOR","Tutor"), ("ESPECIALISTA","Especialista"), ("AMBOS","Ambos")
    ], width=150)

    # ── Tabla ────────────────────────────────────────────────
    tabla = ft.DataTable(
        columns=[
            make_header_cell("ID"),
            make_header_cell("DNI"),
            make_header_cell("Nombre"),
            make_header_cell("Apellidos"),
            make_header_cell("Tipo"),
            make_header_cell("Acciones"),
        ],
        border=ft.Border.all(1, BORDER),
        border_radius=10,
        heading_row_color=ft.Colors.with_opacity(0.08, ACCENT),
        column_spacing=24,
        rows=[],
    )
    tabla_container = ft.Container(content=tabla)

    # ── _build_rows ──────────────────────────────────────────
    def _build_rows(profes):
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
        session = db()
        profes = listar_profesores(session)
        session.close()
        tabla_container.content.rows = _build_rows(profes)
        tabla_container.update()

    def eliminar_y_recargar(pid):
        session = db()
        eliminar_profesor(session, pid)
        session.close()
        snack(page, "Profesor eliminado")
        _refresh()

    def guardar(e):
        session = db()
        crear_profesor(session, dni.value, nombre.value, apellidos.value,
                       domicilio.value, nivel_estudios.value, titulacion.value, tipo.value)
        session.close()
        dni.value = nombre.value = apellidos.value = ""
        domicilio.value = nivel_estudios.value = titulacion.value = ""
        snack(page, "Profesor guardado")
        _refresh()

    _refresh()

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton("← Volver",
                                  on_click=lambda _: menu_principal(page),
                                  style=ft.ButtonStyle(color=ACCENT)),
                ]),
                make_page_title("Profesores", ft.Icons.PERSON),
                ft.Divider(color=BORDER),
                # Formulario
                ft.Container(
                    content=ft.Column([
                        ft.Row([dni, nombre, apellidos]),
                        ft.Row([domicilio, nivel_estudios, titulacion]),
                        ft.Row([tipo, make_btn("Guardar", on_click=guardar,
                                               icon=ft.Icons.SAVE)]),
                    ], spacing=12),
                    bgcolor=BG_CARD,
                    border=ft.Border.all(1, BORDER),
                    border_radius=12,
                    padding=ft.Padding.all(20),
                ),
                ft.Container(height=16),
                # Tabla
                ft.Container(
                    content=ft.Column([tabla_container], scroll=ft.ScrollMode.AUTO),
                ),
            ], spacing=16, expand=True),
            expand=True,
            padding=ft.Padding.all(28),
            bgcolor=BG_DARK,
        )
    )


# ============================================================
# PANEL ALUMNOS
# ============================================================

def panel_alumnos(page):
    page.clean()
    page.bgcolor = BG_DARK

    dni       = make_field("DNI", width=150)
    nombre    = make_field("Nombre", width=150)
    apellidos = make_field("Apellidos", width=150)
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
        border=ft.Border.all(1, BORDER),
        border_radius=10,
        heading_row_color=ft.Colors.with_opacity(0.08, ACCENT),
        column_spacing=24,
        rows=[],
    )
    tabla_container = ft.Container(content=tabla)

    def _build_rows(alumnos, grupos_dict):
        rows = []
        for a in alumnos:
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
        session = db()
        grupos = listar_grupos(session)
        session.close()
        grupo_drop.options = [ft.DropdownOption(key="", text="Sin grupo")]
        for g in grupos:
            label = f"{g.codigo} (Curso {g.id_curso})"
            grupo_drop.options.append(ft.DropdownOption(key=str(g.id), text=label))
        page.update()

    def _refresh():
        session = db()
        alumnos = listar_alumnos(session)
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
        crear_alumno(session, dni.value, nombre.value, apellidos.value,
                     int(gid) if gid and gid.strip() else None)
        session.close()
        dni.value = nombre.value = apellidos.value = ""
        grupo_drop.value = ""
        snack(page, "Alumno guardado")
        _refresh()

    recargar_grupos()
    _refresh()

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
                    border=ft.Border.all(1, BORDER),
                    border_radius=12,
                    padding=ft.Padding.all(20),
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column([tabla_container], scroll=ft.ScrollMode.AUTO),
                ),
            ], spacing=16, expand=True),
            expand=True,
            padding=ft.Padding.all(28),
            bgcolor=BG_DARK,
        )
    )


# ============================================================
# PANEL CANDIDATOS
# ============================================================

def panel_candidatos(page):
    page.clean()
    page.bgcolor = BG_DARK

    dni        = make_field("DNI", width=150)
    nombre     = make_field("Nombre", width=150)
    apellidos  = make_field("Apellidos", width=150)
    curriculum = make_field("Curriculum", width=300, multiline=True, rows=3)
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
        border=ft.Border.all(1, BORDER),
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
                    border=ft.Border.all(1, BORDER),
                    border_radius=12,
                    padding=ft.Padding.all(20),
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column([tabla_container], scroll=ft.ScrollMode.AUTO),
                ),
            ], spacing=16, expand=True),
            expand=True,
            padding=ft.Padding.all(28),
            bgcolor=BG_DARK,
        )
    )


# ============================================================
# PANEL COMITÉ
# ============================================================

def panel_comite(page):
    page.clean()
    page.bgcolor = BG_DARK

    anio       = make_field("Año", width=100)
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
        border=ft.Border.all(1, BORDER),
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
        session = db()
        crear_comite(session, int(anio.value), int(presidente.value),
                     int(secretario.value), int(vocal.value))
        session.close()
        anio.value = presidente.value = secretario.value = vocal.value = ""
        snack(page, "Comité creado")
        _refresh()

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
                    border=ft.Border.all(1, BORDER),
                    border_radius=12,
                    padding=ft.Padding.all(20),
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column([tabla_container], scroll=ft.ScrollMode.AUTO),
                ),
            ], spacing=16, expand=True),
            expand=True,
            padding=ft.Padding.all(28),
            bgcolor=BG_DARK,
        )
    )


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def menu_principal(page):
    page.bgcolor = BG_DARK
    page.title = "Sistema de Gestión - Academia de Formación"

    def abrir_profesores(e): panel_profesores(page)
    def abrir_alumnos(e):    panel_alumnos(page)
    def abrir_candidatos(e): panel_candidatos(page)
    def abrir_comite(e):     panel_comite(page)

    page.clean()
    page.add(
        ft.Container(
            content=ft.Column([
                # Barra de menú
                ft.Container(
                    content=ft.Row([
                        ft.PopupMenuButton(
                            items=[ft.PopupMenuItem(
                                "Salir", icon=ft.Icons.EXIT_TO_APP,
                                on_click=lambda e: page.window.close())],
                            content=ft.Text("Archivo", color=TEXT_MAIN,
                                            weight=ft.FontWeight.BOLD),
                        ),
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
                    padding=ft.Padding.symmetric(horizontal=20, vertical=10),
                    border=ft.Border.only(bottom=ft.BorderSide(1, BORDER)),
                ),
                # Contenido principal
                ft.Container(
                    content=ft.Column([
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
                        ft.Row([
                            _quick_card("Profesores", ft.Icons.SCHOOL,    abrir_profesores),
                            _quick_card("Alumnos",    ft.Icons.PEOPLE,    abrir_alumnos),
                            _quick_card("Candidatos", ft.Icons.PERSON_SEARCH, abrir_candidatos),
                            _quick_card("Comité",     ft.Icons.ASSIGNMENT_IND, abrir_comite),
                        ], spacing=16, wrap=True),
                    ], spacing=16),
                    expand=True,
                    padding=ft.Padding.all(32),
                ),
            ], spacing=0, expand=True),
            expand=True,
            bgcolor=BG_DARK,
        )
    )


def _quick_card(label, icon, on_click):
    """Tarjeta de acceso rápido para el menú principal."""
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, color=ACCENT, size=36),
            ft.Text(label, color=TEXT_MAIN, size=14, weight=ft.FontWeight.W_600),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        bgcolor=BG_CARD,
        border=ft.Border.all(1, BORDER),
        border_radius=14,
        padding=ft.Padding.all(24),
        width=140, height=110,
        on_click=on_click,
        ink=True,
    )


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

def main(page: ft.Page):
    page.window.maximized = True
    page.bgcolor = BG_DARK
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    menu_principal(page)


ft.run(main)
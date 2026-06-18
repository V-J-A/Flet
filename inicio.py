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


def db():
    return SessionLocal()


def panel_profesores(page):
    page.clean()
    page.bgcolor = ft.Colors.BLACK

    def cargar_tabla():
        session = db()
        profes = listar_profesores(session)
        session.close()
        tabla.rows.clear()
        for p in profes:
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(p.id))),
                    ft.DataCell(ft.Text(p.dni or '')),
                    ft.DataCell(ft.Text(p.nombre or '')),
                    ft.DataCell(ft.Text(p.apellidos or '')),
                    ft.DataCell(ft.Text(p.tipo or '')),
                    ft.DataCell(ft.ElevatedButton("Eliminar", on_click=lambda _, pid=p.id: eliminar_y_recargar(pid))),
                ])
            )
        page.update()

    def eliminar_y_recargar(pid):
        session = db()
        eliminar_profesor(session, pid)
        session.close()
        cargar_tabla()

    def guardar(e):
        session = db()
        crear_profesor(session, dni.value, nombre.value, apellidos.value,
                       domicilio.value, nivel_estudios.value, titulacion.value, tipo.value)
        session.close()
        dni.value = nombre.value = apellidos.value = ''
        domicilio.value = nivel_estudios.value = titulacion.value = ''
        cargar_tabla()

    dni = ft.TextField(label="DNI", width=150)
    nombre = ft.TextField(label="Nombre", width=150)
    apellidos = ft.TextField(label="Apellidos", width=150)
    domicilio = ft.TextField(label="Domicilio", width=200)
    nivel_estudios = ft.TextField(label="Nivel Estudios", width=150)
    titulacion = ft.TextField(label="Titulación", width=150)
    tipo = ft.Dropdown(label="Tipo", width=150, options=[
        ft.dropdown.Option("TUTOR"), ft.dropdown.Option("ESPECIALISTA"), ft.dropdown.Option("AMBOS")
    ])

    tabla = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("DNI")),
        ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Apellidos")),
        ft.DataColumn(ft.Text("Tipo")), ft.DataColumn(ft.Text("Acción")),
    ])

    cargar_tabla()

    page.add(
        ft.Row([ft.ElevatedButton("<-- Volver", on_click=lambda _: menu_principal(page))]),
        ft.Text("Profesores", size=24, color=ft.Colors.WHITE),
        ft.Row([dni, nombre, apellidos]),
        ft.Row([domicilio, nivel_estudios, titulacion]),
        ft.Row([tipo, ft.ElevatedButton("Guardar", on_click=guardar)]),
        ft.Divider(color=ft.Colors.WHITE),
        tabla,
    )


def panel_alumnos(page):
    page.clean()
    page.bgcolor = ft.Colors.BLACK

    def recargar_grupos():
        session = db()
        grupos = listar_grupos(session)
        session.close()
        grupo_drop.options.clear()
        grupo_drop.options.append(ft.dropdown.Option("", "Sin grupo"))
        for g in grupos:
            label = f"{g.codigo} (Curso {g.id_curso})"
            grupo_drop.options.append(ft.dropdown.Option(str(g.id), label))
        page.update()

    def cargar_tabla():
        session = db()
        alumnos = listar_alumnos(session)
        grupos = {g.id: g for g in listar_grupos(session)}
        session.close()
        tabla.rows.clear()
        for a in alumnos:
            grupo_text = f"{grupos[a.id_grupo].codigo}" if a.id_grupo and a.id_grupo in grupos else "Sin grupo"
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(a.id))),
                    ft.DataCell(ft.Text(a.dni or '')),
                    ft.DataCell(ft.Text(a.nombre or '')),
                    ft.DataCell(ft.Text(a.apellidos or '')),
                    ft.DataCell(ft.Text(grupo_text)),
                    ft.DataCell(ft.ElevatedButton("Eliminar", on_click=lambda _, aid=a.id: eliminar_y_recargar(aid))),
                ])
            )
        page.update()

    def eliminar_y_recargar(aid):
        session = db()
        eliminar_alumno(session, aid)
        session.close()
        cargar_tabla()

    def guardar(e):
        session = db()
        gid = grupo_drop.value
        crear_alumno(session, dni.value, nombre.value, apellidos.value,
                     int(gid) if gid and gid.strip() else None)
        session.close()
        dni.value = nombre.value = apellidos.value = ''
        grupo_drop.value = ''
        cargar_tabla()

    dni = ft.TextField(label="DNI", width=150)
    nombre = ft.TextField(label="Nombre", width=150)
    apellidos = ft.TextField(label="Apellidos", width=150)
    grupo_drop = ft.Dropdown(label="Grupo", width=200)

    tabla = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("DNI")),
        ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Apellidos")),
        ft.DataColumn(ft.Text("Grupo")), ft.DataColumn(ft.Text("Acción")),
    ])

    recargar_grupos()
    cargar_tabla()

    page.add(
        ft.Row([ft.ElevatedButton("<-- Volver", on_click=lambda _: menu_principal(page))]),
        ft.Text("Alumnos", size=24, color=ft.Colors.WHITE),
        ft.Row([dni, nombre, apellidos, grupo_drop]),
        ft.Row([ft.ElevatedButton("Guardar", on_click=guardar)]),
        ft.Divider(color=ft.Colors.WHITE),
        tabla,
    )


def panel_candidatos(page):
    page.clean()
    page.bgcolor = ft.Colors.BLACK

    def cargar_tabla():
        session = db()
        candidatos = listar_candidatos(session)
        session.close()
        tabla.rows.clear()
        for c in candidatos:
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(c.id))),
                    ft.DataCell(ft.Text(c.dni or '')),
                    ft.DataCell(ft.Text(c.nombre or '')),
                    ft.DataCell(ft.Text(c.apellidos or '')),
                    ft.DataCell(ft.Text(c.tipo_deseado or '')),
                    ft.DataCell(ft.ElevatedButton("Eliminar", on_click=lambda _, cid=c.id: eliminar_y_recargar(cid))),
                ])
            )
        page.update()

    def eliminar_y_recargar(cid):
        session = db()
        eliminar_candidato(session, cid)
        session.close()
        cargar_tabla()

    def guardar(e):
        session = db()
        crear_candidato(session, dni.value, nombre.value, apellidos.value,
                        curriculum.value, tipo.value)
        session.close()
        dni.value = nombre.value = apellidos.value = curriculum.value = ''
        cargar_tabla()

    dni = ft.TextField(label="DNI", width=150)
    nombre = ft.TextField(label="Nombre", width=150)
    apellidos = ft.TextField(label="Apellidos", width=150)
    curriculum = ft.TextField(label="Curriculum", width=300, multiline=True)
    tipo = ft.Dropdown(label="Tipo Deseado", width=150, options=[
        ft.dropdown.Option("TUTOR"), ft.dropdown.Option("ESPECIALISTA"), ft.dropdown.Option("AMBOS")
    ])

    tabla = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("DNI")),
        ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Apellidos")),
        ft.DataColumn(ft.Text("Tipo")), ft.DataColumn(ft.Text("Acción")),
    ])

    cargar_tabla()

    page.add(
        ft.Row([ft.ElevatedButton("<-- Volver", on_click=lambda _: menu_principal(page))]),
        ft.Text("Candidatos", size=24, color=ft.Colors.WHITE),
        ft.Row([dni, nombre, apellidos]),
        ft.Row([curriculum, tipo]),
        ft.Row([ft.ElevatedButton("Guardar", on_click=guardar)]),
        ft.Divider(color=ft.Colors.WHITE),
        tabla,
    )


def panel_comite(page):
    page.clean()
    page.bgcolor = ft.Colors.BLACK

    def cargar_tabla():
        session = db()
        comites = listar_comites(session)
        session.close()
        tabla.rows.clear()
        for c in comites:
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(c.id))),
                    ft.DataCell(ft.Text(str(c.anio))),
                    ft.DataCell(ft.Text(str(c.id_presidente))),
                    ft.DataCell(ft.Text(str(c.id_secretario))),
                    ft.DataCell(ft.Text(str(c.id_vocal))),
                    ft.DataCell(ft.ElevatedButton("Eliminar", on_click=lambda _, cid=c.id: eliminar_y_recargar(cid))),
                ])
            )
        page.update()

    def eliminar_y_recargar(cid):
        session = db()
        eliminar_comite(session, cid)
        session.close()
        cargar_tabla()

    def guardar(e):
        session = db()
        crear_comite(session, int(anio.value), int(presidente.value),
                     int(secretario.value), int(vocal.value))
        session.close()
        anio.value = presidente.value = secretario.value = vocal.value = ''
        cargar_tabla()

    anio = ft.TextField(label="Año", width=100)
    presidente = ft.TextField(label="ID Presidente", width=100)
    secretario = ft.TextField(label="ID Secretario", width=100)
    vocal = ft.TextField(label="ID Vocal", width=100)

    tabla = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Año")),
        ft.DataColumn(ft.Text("Presidente")), ft.DataColumn(ft.Text("Secretario")),
        ft.DataColumn(ft.Text("Vocal")), ft.DataColumn(ft.Text("Acción")),
    ])

    cargar_tabla()

    page.add(
        ft.Row([ft.ElevatedButton("<-- Volver", on_click=lambda _: menu_principal(page))]),
        ft.Text("Comité Selectivo", size=24, color=ft.Colors.WHITE),
        ft.Row([anio, presidente, secretario, vocal]),
        ft.Row([ft.ElevatedButton("Guardar", on_click=guardar)]),
        ft.Divider(color=ft.Colors.WHITE),
        tabla,
    )


def menu_principal(page):
    page.bgcolor = ft.Colors.BLACK
    page.title = "Sistema de Gestión - Academia de Formación"

    def abrir_profesores(e):
        panel_profesores(page)

    def abrir_alumnos(e):
        panel_alumnos(page)

    def abrir_candidatos(e):
        panel_candidatos(page)

    def abrir_comite(e):
        panel_comite(page)

    page.clean()
    page.add(
        ft.Row([
            ft.PopupMenuButton(
                items=[ft.PopupMenuItem("Salir", icon=ft.Icons.EXIT_TO_APP,
                                        on_click=lambda e: page.window.close())],
                content=ft.Text("Archivo", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem("Profesores", icon=ft.Icons.SCHOOL, on_click=abrir_profesores),
                    ft.PopupMenuItem("Alumnos", icon=ft.Icons.PEOPLE, on_click=abrir_alumnos),
                    ft.PopupMenuItem("Candidatos", icon=ft.Icons.PERSON_SEARCH, on_click=abrir_candidatos),
                    ft.PopupMenuItem("Comité", icon=ft.Icons.ASSIGNMENT_IND, on_click=abrir_comite),
                ],
                content=ft.Text("Herramientas", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ),
        ], spacing=20),
        ft.Divider(),
        ft.Text("Sistema de Gestión - Academia de Formación", size=28, color=ft.Colors.WHITE),
        ft.Divider(),
        ft.Text("Accesos Rápidos:", size=16, color=ft.Colors.WHITE),
        ft.Row([
            ft.IconButton(icon=ft.Icons.SCHOOL, tooltip="Profesores", on_click=abrir_profesores),
            ft.IconButton(icon=ft.Icons.PEOPLE, tooltip="Alumnos", on_click=abrir_alumnos),
            ft.IconButton(icon=ft.Icons.PERSON_SEARCH, tooltip="Candidatos", on_click=abrir_candidatos),
            ft.IconButton(icon=ft.Icons.ASSIGNMENT_IND, tooltip="Comité", on_click=abrir_comite),
        ]),
    )


def main(page: ft.Page):
    page.window.maximized = True
    menu_principal(page)


ft.run(main)

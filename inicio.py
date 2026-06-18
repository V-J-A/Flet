import flet as ft

# Cuando crees tus otros módulos, importarlos acá:
# from profesores import VentanaProfesores
# from alumnos import VentanaAlumnos
# from candidatos import VentanaCandidatos


def menu_principal(page: ft.Page):
    page.bgcolor = ft.Colors.BLACK
    page.title = "Sistema de Gestión - Academia de Formación"

    # --- FUNCIONES DE NAVEGACIÓN ---
    def abrir_profesores(e):
        page.clean()
        page.add(ft.Text("Panel de Gestión de Profesores (Fijos y Especialistas)", size=24))
        page.add(ft.Button("<-- Volver", on_click=lambda _: volver_al_menu()))
        page.update()

    def abrir_alumnos(e):
        page.clean()
        page.add(ft.Text("Panel de Alumnos, Grupos y Control de Asistencia", size=24))
        page.add(ft.Button("<-- Volver", on_click=lambda _: volver_al_menu()))
        page.update()

    def abrir_candidatos(e):
        page.clean()
        page.add(ft.Text("Panel de Selección: Candidatos, Llamadas y Entrevistas", size=24))
        page.add(ft.Button("<-- Volver", on_click=lambda _: volver_al_menu()))
        page.update()

    def abrir_comite(e):
        page.clean()
        page.add(ft.Text("Panel del Comité Evaluador", size=24))
        page.add(ft.Button("<-- Volver", on_click=lambda _: volver_al_menu()))
        page.update()

    def volver_al_menu():
        """Se usa solo al navegar de vuelta: limpia y reconstruye."""
        page.clean()
        construir_menu()
        page.update()

    # --- MENÚ ARCHIVO ---
    archivo_menu = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(
                content=ft.Text("Salir"),
                icon=ft.Icons.EXIT_TO_APP,
                on_click=lambda e: page.window.close()
            ),
        ],
        content=ft.Text("Archivo", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    )

    # --- MENÚ HERRAMIENTAS ---
    herramientas_menu = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(content=ft.Text("Profesores"),            icon=ft.Icons.SCHOOL,         on_click=abrir_profesores),
            ft.PopupMenuItem(content=ft.Text("Alumnos y Grupos"),      icon=ft.Icons.PEOPLE,          on_click=abrir_alumnos),
            ft.PopupMenuItem(content=ft.Text("Candidatos (Vacantes)"), icon=ft.Icons.PERSON_SEARCH,   on_click=abrir_candidatos),
            ft.PopupMenuItem(content=ft.Text("Comité Evaluador"),      icon=ft.Icons.ASSIGNMENT_IND,  on_click=abrir_comite),
        ],
        content=ft.Text("Herramientas", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    )

    # --- BOTONES DE ACCESO RÁPIDO ---
    boton_profesores = ft.IconButton(icon=ft.Icons.SCHOOL,         tooltip="Gestionar Profesores", on_click=abrir_profesores)
    boton_alumnos    = ft.IconButton(icon=ft.Icons.PEOPLE,         tooltip="Gestionar Alumnos",    on_click=abrir_alumnos)
    boton_candidatos = ft.IconButton(icon=ft.Icons.PERSON_SEARCH,  tooltip="Candidatos y Vacantes",on_click=abrir_candidatos)
    boton_comite     = ft.IconButton(icon=ft.Icons.ASSIGNMENT_IND, tooltip="Comité Evaluador",     on_click=abrir_comite)

    def construir_menu():
        """Agrega los controles del menú a la página."""
        page.add(
            ft.Row(controls=[archivo_menu, herramientas_menu], spacing=20),
            ft.Divider(),
            ft.Text("Accesos Rápidos:", size=16, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
            ft.Row(controls=[boton_profesores, boton_alumnos, boton_candidatos, boton_comite], spacing=15)
        )

    # Primera carga: sin page.clean(), solo page.add()
    construir_menu()


def main(page: ft.Page):
    page.window.maximized = True
    menu_principal(page)


ft.run(main)
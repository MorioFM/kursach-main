"""
Главный файл приложения
"""
import flet as ft
import os
from database import KindergartenDB
from view.children_view import ChildrenView
from view.groups_view import GroupsView
from view.teachers_view import TeachersView
from view.parents_view import ParentsView
from view.attendance_view import AttendanceView
from view.electronic_journal_view import ElectronicJournalView
from view.events_view import EventsView
from view.settings_view import SettingsView
from view.home_view import HomeView
from view.login_view import LoginView
from view.users_view import UsersView
from navigation_drawer import AppNavigationDrawer
from settings.config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, DATABASE_NAME


def main(page: ft.Page):
    """Главная функция приложения"""
    icon_path = os.path.abspath("C:/Users/zsa-6/Desktop/kursach-main/src/assets/828770ec-5c95-4431-a4a7-0f3c102c1caf.ico")
    page.window.icon = icon_path
    page.title = APP_TITLE
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.padding = 0
    
    # Обработчик изменения размера окна
    def on_resize(e):
        try:
            page.update()
        except:
            pass
    
    page.on_resized = on_resize
    
    # Загружаем сохраненную тему
    saved_theme = page.client_storage.get("app_theme")
    if saved_theme == "dark":
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT

    def logout():
        """Выход из системы"""
        page.client_storage.remove("is_logged_in")
        page.client_storage.remove("username")
        show_login()
    
    # Текст с именем пользователя
    username_text = ft.Text("", size=14, key="username_text")
    
    # Создаем контейнер для заголовка с динамическим цветом
    header_container = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    on_click=lambda e: page.open(page.drawer),
                    key="menu_button"
                ),
                ft.Text(APP_TITLE, size=20, weight="bold", key="app_title"),
                ft.Container(expand=True),
                username_text,
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    tooltip="Выйти",
                    on_click=lambda e: logout(),
                    key="logout_button"
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=10,
        key="header_container"
    )

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        
        # Сохраняем выбранную тему
        theme_value = "dark" if page.theme_mode == ft.ThemeMode.DARK else "light"
        page.client_storage.set("app_theme", theme_value)
        
        page.update()

    theme_switch = ft.Switch(
        label="Тема приложения",
        value=page.theme_mode == ft.ThemeMode.DARK,
        on_change=toggle_theme,
        key="theme_switch"
    )
    
    def show_login():
        """Показать экран авторизации"""
        # Инициализируем базу данных для авторизации
        db = KindergartenDB(DATABASE_NAME)
        db.connect()
        db.create_tables()
        
        page.controls.clear()
        login_view = LoginView(show_main_app, db, page)
        page.add(login_view)
        page.update()
    
    def show_main_app():
        """Показать основное приложение"""
        # Получаем имя пользователя и обновляем текст
        username = page.client_storage.get("username")
        username_text.value = f"Пользователь: {username}" if username else ""
        
        page.controls.clear()
        init_main_app(page, header_container, theme_switch)
        page.update()
    
    # Всегда показываем экран авторизации при запуске
    show_login()

def init_main_app(page, header_container, theme_switch):
    """Инициализация основного приложения"""
    # Инициализация базы данных
    db = KindergartenDB(DATABASE_NAME)
    db.connect()
    db.create_tables()
    
    # Проверяем роль пользователя
    user_role = page.client_storage.get("user_role")
    is_admin = user_role == "admin"
    
    # Контейнер для текущего представления
    content_container = ft.Container(expand=True, key="content_container")
    
    # Создаем представления
    home_view = HomeView(db, lambda: refresh_current_view(), page)
    children_view = ChildrenView(db, lambda: refresh_current_view(), page)
    groups_view = GroupsView(db, lambda: refresh_current_view(), page)
    teachers_view = TeachersView(db, lambda: refresh_current_view())
    parents_view = ParentsView(db, lambda: refresh_current_view(), page)
    attendance_view = AttendanceView(db, lambda: refresh_current_view(), page)
    events_view = EventsView(db, lambda: refresh_current_view(), page)
    settings_view = SettingsView(page, theme_switch)
    users_view = UsersView(db, lambda: refresh_current_view(), page) if is_admin else None
    
    # Создаем electronic_journal_view после добавления страницы
    electronic_journal_view = None
    
    # Текущее представление
    current_view = [home_view]
    
    def refresh_current_view():
        """Обновить текущее представление"""
        if current_view[0] == home_view:
            home_view.load_home()
        elif current_view[0] == children_view:
            children_view.load_children()
        elif current_view[0] == groups_view:
            groups_view.load_groups()
        elif current_view[0] == teachers_view:
            teachers_view.load_teachers()
        elif current_view[0] == parents_view:
            parents_view.load_parents()
        elif current_view[0] == attendance_view:
            attendance_view.load_attendance()
        elif current_view[0] == electronic_journal_view:
            if hasattr(electronic_journal_view, 'build_journal'):
                electronic_journal_view.build_journal()
        elif current_view[0] == settings_view:
            settings_view.load_settings()
        elif current_view[0] == users_view:
            if users_view:
                users_view.load_users()
    
    def switch_view(view_name, e=None):
        """Переключить представление"""
        view_map = {
            "home": home_view,
            "children": children_view,
            "groups": groups_view,
            "teachers": teachers_view,
            "parents": parents_view,
            "attendance": attendance_view,
            "electronic_journal": electronic_journal_view,
            "events": events_view,
            "settings": settings_view,
            "users": users_view
        }
        
        view = view_map.get(view_name)
        if not view:
            return
            
        current_view[0] = view
        content_container.content = view
        
        # Загрузить данные для представления
        if view == home_view:
            home_view.load_home()
        elif view == children_view:
            children_view.load_children()
        elif view == groups_view:
            groups_view.load_groups()
        elif view == teachers_view:
            teachers_view.load_teachers()
        elif view == parents_view:
            parents_view.load_parents()
        elif view == attendance_view:
            attendance_view.load_attendance()
        elif view == electronic_journal_view:
            electronic_journal_view.page = page
            if hasattr(electronic_journal_view, 'build_journal'):
                electronic_journal_view.build_journal()
        elif view == events_view:
            events_view.load_events()
        elif view == settings_view:
            settings_view.load_settings()
        elif view == users_view:
            if users_view:
                users_view.load_users()
        
        page.drawer.open = False
        page.update()



    page.drawer = AppNavigationDrawer(switch_view, is_admin)
    
    # Добавляем элементы на страницу
    page.add(header_container, ft.Divider(), content_container)
    
    # Создаем electronic_journal_view после инициализации страницы
    electronic_journal_view = ElectronicJournalView(db, lambda: refresh_current_view(), page)
    
    # Загружаем начальное представление
    switch_view("home")


if __name__ == "__main__":
    ft.app(target=main)

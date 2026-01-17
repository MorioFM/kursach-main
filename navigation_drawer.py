"""
Навигационное меню приложения
"""
import flet as ft
from typing import Callable


class AppNavigationDrawer(ft.NavigationDrawer):
    """Навигационное меню приложения"""
    
    def __init__(self, on_view_change: Callable, is_admin: bool = False, user_permissions: dict = None):
        self.on_view_change = on_view_change
        self.is_admin = is_admin
        self.user_permissions = user_permissions or {}
        
        # Базовые пункты меню
        menu_items = [
            ft.Container(height=20, key="drawer_spacer"),
        ]
        
        # Добавляем пункты с проверкой прав доступа
        pages = [
            ("home", ft.Icons.HOME_OUTLINED, "Главная"),
            ("children", ft.Icons.CHILD_CARE_OUTLINED, "Дети"),
            ("groups", ft.Icons.GROUPS_OUTLINED, "Группы"),
            ("teachers", ft.Icons.PERSON_OUTLINED, "Воспитатели"),
            ("parents", ft.Icons.FAMILY_RESTROOM_OUTLINED, "Родители"),
            ("attendance", ft.Icons.ASSIGNMENT_OUTLINED, "Журнал посещаемости"),
            ("electronic_journal", ft.Icons.CALENDAR_MONTH_OUTLINED, "Электронный журнал"),
            ("events", ft.Icons.EVENT_OUTLINED, "Мероприятия"),
        ]
        
        for page_key, icon, title in pages:
            # Админ видит все, обычные пользователи - только разрешенные
            if is_admin or self.user_permissions.get(page_key, True):
                menu_items.append(
                    ft.ListTile(
                        leading=ft.Icon(icon),
                        title=ft.Text(title),
                        on_click=lambda e, pk=page_key: self.on_view_change(pk, e),
                        key=f"nav_{page_key}"
                    )
                )
        
        menu_items.append(ft.Divider())
        
        # Добавляем пункт "Пользователи" и "Логи" только для администратора
        if is_admin:
            menu_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PEOPLE_OUTLINED),
                    title=ft.Text("Пользователи"),
                    on_click=lambda e: self.on_view_change("users", e),
                    key="nav_users"
                )
            )
            menu_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HISTORY_OUTLINED),
                    title=ft.Text("Логи системы"),
                    on_click=lambda e: self.on_view_change("logs", e),
                    key="nav_logs"
                )
            )
            menu_items.append(ft.Divider())
        
        menu_items.append(
            ft.ListTile(
                leading=ft.Icon(ft.Icons.SETTINGS_OUTLINED),
                title=ft.Text("Настройки"),
                on_click=lambda e: self.on_view_change("settings", e),
                key="nav_settings"
            )
        )
        
        super().__init__(
            on_change=self.handle_change,
            controls=menu_items
        )
    
    def handle_change(self, e):
        """Обработчик изменения состояния drawer"""
        self.open = False
        if self.page:
            self.page.update()
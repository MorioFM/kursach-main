"""
Экран авторизации
"""
import flet as ft
from typing import Callable
import hashlib
from settings.logger import app_logger


class LoginView(ft.Container):
    """Экран авторизации пользователя"""
    
    def __init__(self, on_login_success: Callable, db, page=None):
        super().__init__()
        self.on_login_success = on_login_success
        self.db = db
        self.page = page
        
        # Поля ввода
        self.username_field = ft.TextField(
            label="Логин",
            width=300,
            prefix_icon=ft.Icons.PERSON
        )
        
        self.password_field = ft.TextField(
            label="Пароль",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK
        )
        
        self.error_text = ft.Text("", color=ft.Colors.RED, size=14)
        
        # Кнопка входа
        self.login_button = ft.ElevatedButton(
            "Войти",
            width=300,
            height=40,
            on_click=self.handle_login
        )
        
        # Основной контент
        self.content = ft.Column([
            ft.Container(height=100),
            ft.Icon(ft.Icons.SCHOOL, size=80, color=ft.Colors.BLUE),
            ft.Text("Система управления детским садом", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, width=400),
            ft.Container(height=50),
            self.username_field,
            self.password_field,
            self.error_text,
            ft.Container(height=20),
            self.login_button,
            ft.Container(height=20),
            #ft.Text("Логин: admin, Пароль: admin", size=12, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
        
        self.alignment = ft.alignment.center
        self.expand = True
    
    def handle_login(self, e):
        """Обработка входа в систему"""
        username = self.username_field.value
        password = self.password_field.value
        
        if not username or not password:
            self.error_text.value = "Заполните все поля"
            if self.page:
                self.page.update()
            return
        
        # Проверка через базу данных
        user = self.db.authenticate_user(username, password)
        if user:
            # Логируем вход
            app_logger.log('LOGIN', username, details=f"Role: {user['role']}")
            
            # Сохраняем состояние авторизации
            if self.page:
                self.page.client_storage.set("is_logged_in", "true")
                self.page.client_storage.set("username", user['username'])
                self.page.client_storage.set("user_role", user['role'])
                self.page.client_storage.set("user_id", user['user_id'])
            
            self.on_login_success()
        else:
            app_logger.log('LOGIN_FAILED', username, level='WARNING')
            self.error_text.value = "Неверный логин или пароль"
            if self.page:
                self.page.update()
"""
Представление для управления пользователями (только для администратора)
"""
import flet as ft
from typing import Callable
import hashlib
from pages_styles.styles import AppStyles
from settings.logger import app_logger


class UsersView(ft.Container):
    """Представление для управления пользователями"""
    
    def __init__(self, db, on_refresh: Callable = None, page=None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.page = page
        self.selected_user = None
        
        # Поля формы
        self.username_field = AppStyles.text_field("Логин", required=True, autofocus=True)
        self.username_error = AppStyles.error_text()
        
        self.password_field = ft.TextField(
            label="Пароль",
            width=300,
            password=True,
            can_reveal_password=True
        )
        self.password_error = AppStyles.error_text()
        
        self.role_dropdown = ft.Dropdown(
            label="Роль",
            width=300,
            options=[
                ft.DropdownOption("admin", "Администратор"),
                ft.DropdownOption("user", "Пользователь")
            ],
            value="user"
        )
        
        # Чекбоксы прав доступа
        self.permissions_checkboxes = {}
        pages = {
            'home': 'Главная',
            'children': 'Дети',
            'groups': 'Группы',
            'teachers': 'Воспитатели',
            'parents': 'Родители',
            'attendance': 'Посещаемость',
            'electronic_journal': 'Электронный журнал',
            'events': 'Мероприятия'
        }
        
        permissions_controls = []
        for page_key, page_name in pages.items():
            cb = ft.Checkbox(label=page_name, value=True)
            self.permissions_checkboxes[page_key] = cb
            permissions_controls.append(cb)
        
        self.permissions_container = ft.Container(
            content=ft.Column([
                ft.Text("Права доступа:", weight=ft.FontWeight.BOLD),
                ft.Column(permissions_controls, spacing=5)
            ], spacing=10),
            padding=10,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=5
        )
        
        # Форма
        self.save_button = ft.ElevatedButton("Сохранить", on_click=self.save_user)
        self.cancel_button = ft.TextButton("Отмена", on_click=self.cancel_edit)
        
        self.form_container = ft.Container(
            content=ft.Column([
                ft.Text("Добавить пользователя", size=20, weight=ft.FontWeight.BOLD),
                self.username_field,
                self.username_error,
                self.password_field,
                self.password_error,
                self.role_dropdown,
                self.permissions_container,
                ft.Row([
                    self.save_button,
                    self.cancel_button
                ], spacing=10)
            ], spacing=5),
            padding=20,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
            visible=False
        )
        
        # Список пользователей
        self.users_list = ft.ListView(expand=True, spacing=10, padding=20)
        
        # Загружаем данные
        self.load_users()
        
        self.content = AppStyles.form_column([
            AppStyles.page_header("Пользователи", "Добавить пользователя", self.show_add_form),
            self.form_container,
            ft.Container(content=self.users_list, expand=True)
        ], spacing=20)
        self.expand = True
    
    def load_users(self):
        """Загрузка списка пользователей"""
        from database import User
        users = User.select()
        self.users_list.controls = [self._create_user_item(user) for user in users]
        if self.page:
            self.page.update()
    
    def _create_user_item(self, user):
        """Создать элемент списка для пользователя"""
        role_text = "Администратор" if user.role == "admin" else "Пользователь"
        
        current_username = self.page.client_storage.get("username") if self.page else None
        
        items = [
            ft.PopupMenuItem(text="Редактировать", icon=ft.Icons.EDIT, 
                           on_click=lambda _, u=user: self.edit_user(u)),
            ft.PopupMenuItem(text="Изменить пароль", icon=ft.Icons.LOCK_RESET, 
                           on_click=lambda _, uid=user.user_id: self.change_password(uid))
        ]
        
        if user.username != current_username:
            items.append(
                ft.PopupMenuItem(text="Удалить", icon=ft.Icons.DELETE, 
                               on_click=lambda _, uid=user.user_id: self.delete_user(uid))
            )
        
        return ft.ListTile(
            leading=ft.Icon(ft.Icons.PERSON),
            title=ft.Text(user.username, weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(f"Роль: {role_text}"),
            trailing=ft.PopupMenuButton(
                icon=ft.Icons.MORE_VERT,
                tooltip="",
                items=items
            )
        )
    
    def show_add_form(self, e):
        """Показать форму добавления"""
        self.selected_user = None
        self.clear_form()
        self.form_container.content.controls[0].value = "Добавить пользователя"
        self.password_field.disabled = False
        self.password_field.label = "Пароль"
        for cb in self.permissions_checkboxes.values():
            cb.value = True
        self.form_container.visible = True
        if self.page:
            self.page.update()
    
    def edit_user(self, user):
        """Редактировать пользователя"""
        self.selected_user = user
        self.username_field.value = user.username
        self.password_field.value = ""
        self.password_field.disabled = True
        self.password_field.label = "Пароль (используйте 'Изменить пароль' для смены)"
        self.role_dropdown.value = user.role
        
        # Загружаем права доступа
        user_perms = self.db.get_user_permissions(user.user_id)
        for page_key, cb in self.permissions_checkboxes.items():
            cb.value = user_perms.get(page_key, True)
        
        self.form_container.content.controls[0].value = f"Редактировать пользователя: {user.username}"
        self.form_container.visible = True
        if self.page:
            self.page.update()
    
    def change_password(self, user_id: int):
        """Изменить пароль пользователя"""
        from database import User
        import threading
        user = User.get_by_id(user_id)
        
        new_password_field = ft.TextField(
            label="Новый пароль",
            width=300,
            password=True,
            can_reveal_password=True
        )
        
        def save_new_password(e):
            if not new_password_field.value or len(new_password_field.value) < 3:
                self.show_error("Пароль должен содержать минимум 3 символа")
                return
            
            password_hash = hashlib.sha256(new_password_field.value.encode()).hexdigest()
            user.password = password_hash
            user.save()
            
            self.page.close(dialog)
            self.show_success(f"Пароль для пользователя {user.username} успешно изменен")
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Изменить пароль: {user.username}"),
            content=new_password_field,
            actions=[
                ft.ElevatedButton("Сохранить", on_click=save_new_password),
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog))
            ]
        )
        
        self.page.overlay.append(dialog)
        
        def open_dialog():
            dialog.open = True
            self.page.update()
        
        threading.Timer(0.1, open_dialog).start()
    
    def delete_user(self, user_id: int):
        """Удалить пользователя"""
        from database import User
        from dialogs import show_confirm_dialog
        
        user = User.get_by_id(user_id)
        
        def on_yes(e):
            try:
                username_to_delete = user.username
                user.delete_instance()
                
                current_username = self.page.client_storage.get("username") if self.page else None
                app_logger.log('DELETE', current_username, 'User', f"Deleted user: {username_to_delete}")
                
                self.load_users()
                self.show_success(f"Пользователь {username_to_delete} успешно удален")
            except Exception as ex:
                self.show_error(f"Ошибка при удалении: {str(ex)}")
        
        show_confirm_dialog(
            self.page,
            title="Удаление пользователя",
            content=f"Вы уверены, что хотите удалить пользователя {user.username}?",
            on_yes=on_yes,
            adaptive=True
        )
    
    def validate_fields(self):
        """Проверить обязательные поля"""
        self.clear_field_errors()
        is_valid = True
        
        if not self.username_field.value or not self.username_field.value.strip():
            self.username_error.value = "Заполните поле"
            self.username_error.visible = True
            is_valid = False
        
        if not self.selected_user and (not self.password_field.value or len(self.password_field.value) < 3):
            self.password_error.value = "Пароль должен содержать минимум 3 символа"
            self.password_error.visible = True
            is_valid = False
        
        if not is_valid and self.page:
            self.page.update()
        
        return is_valid
    
    def clear_field_errors(self):
        """Очистить все сообщения об ошибках"""
        self.username_error.visible = False
        self.password_error.visible = False
    
    def save_user(self, e):
        """Сохранить пользователя"""
        if not self.validate_fields():
            return
        
        try:
            from database import User
            
            username = self.username_field.value.strip()
            role = self.role_dropdown.value
            current_username = self.page.client_storage.get("username") if self.page else None
            
            # Проверяем, существует ли пользователь с таким логином
            try:
                existing_user = User.get(User.username == username)
                if not self.selected_user or existing_user.user_id != self.selected_user.user_id:
                    self.show_error(f"Пользователь с логином '{username}' уже существует")
                    return
            except:
                pass
            
            if self.selected_user:
                # Обновление
                self.selected_user.username = username
                self.selected_user.role = role
                self.selected_user.save()
                user_id = self.selected_user.user_id
                app_logger.log('UPDATE', current_username, 'User', f"Updated user: {username}")
                self.show_success("Пользователь успешно обновлен")
            else:
                # Создание
                password_hash = hashlib.sha256(self.password_field.value.encode()).hexdigest()
                user = User.create(username=username, password=password_hash, role=role)
                user_id = user.user_id
                app_logger.log('CREATE', current_username, 'User', f"Created user: {username} with role: {role}")
                self.show_success("Пользователь успешно создан")
            
            # Сохраняем права доступа
            for page_key, cb in self.permissions_checkboxes.items():
                self.db.set_user_permission(user_id, page_key, cb.value)
            
            self.form_container.visible = False
            self.load_users()
            if self.on_refresh:
                self.on_refresh()
            if self.page:
                self.page.update()
            
        except Exception as ex:
            self.show_error(f"Ошибка при сохранении: {str(ex)}")
    
    def cancel_edit(self, e):
        """Отменить редактирование"""
        self.form_container.visible = False
        self.clear_form()
        if self.page:
            self.page.update()
    
    def clear_form(self):
        """Очистить форму"""
        self.username_field.value = ""
        self.password_field.value = ""
        self.password_field.disabled = False
        self.password_field.label = "Пароль"
        self.role_dropdown.value = "user"
        for cb in self.permissions_checkboxes.values():
            cb.value = True
        self.clear_field_errors()
    
    def show_error(self, message: str):
        """Показать ошибку"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def show_success(self, message: str):
        """Показать успешное сообщение"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()

"""
Представление настроек приложения
"""
import flet as ft
from typing import Callable
from settings.config import PRIMARY_COLOR
import shutil
import os
from datetime import datetime
from settings.logger import app_logger


class SettingsView(ft.Container):
    """Представление настроек приложения"""
    
    def __init__(self, page=None, theme_switch=None, db=None):
        super().__init__()
        self.page = page
        self.theme_switch = theme_switch
        self.db = db
        
        # Секция темы
        theme_section = ft.Container(
            content=ft.Column([
                ft.Text("Внешний вид", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row([
                    ft.Icon(ft.Icons.PALETTE_OUTLINED, size=24),
                    ft.Column([
                        ft.Text("Тема приложения", size=16),
                        ft.Text("Переключение между светлой и темной темой", size=12, color=ft.Colors.GREY_600)
                    ], expand=True),
                    self.theme_switch if self.theme_switch else ft.Switch(label="Тема")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Row([
                    ft.Icon(ft.Icons.LANGUAGE_OUTLINED, size=24),
                    ft.Column([
                        ft.Text("Язык интерфейса", size=16),
                        ft.Text("Выбор языка приложения", size=12, color=ft.Colors.GREY_600)
                    ], expand=True),
                    ft.Dropdown(
                        width=150,
                        value="Русский",
                        options=[
                            ft.DropdownOption("Русский"),
                            ft.DropdownOption("English")
                        ],
                        disabled=True
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10
        )
        
        # Секция данных
        data_section = ft.Container(
            content=ft.Column([
                ft.Text("Управление данными", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row([
                    ft.Icon(ft.Icons.BACKUP_OUTLINED, size=24),
                    ft.Column([
                        ft.Text("Резервное копирование", size=16),
                        ft.Text("Создать резервную копию базы данных", size=12, color=ft.Colors.GREY_600)
                    ], expand=True),
                    ft.ElevatedButton("Создать копию", icon=ft.Icons.SAVE, on_click=self.backup_database)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Row([
                    ft.Icon(ft.Icons.UPLOAD_FILE_OUTLINED, size=24),
                    ft.Column([
                        ft.Text("Экспорт данных", size=16),
                        ft.Text("Экспортировать данные в CSV", size=12, color=ft.Colors.GREY_600)
                    ], expand=True),
                    ft.ElevatedButton("Экспорт", icon=ft.Icons.DOWNLOAD, on_click=self.export_data)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Row([
                    ft.Icon(ft.Icons.DELETE_SWEEP_OUTLINED, size=24),
                    ft.Column([
                        ft.Text("Очистка данных", size=16),
                        ft.Text("Удалить старые записи посещаемости", size=12, color=ft.Colors.GREY_600)
                    ], expand=True),
                    ft.ElevatedButton("Очистить", icon=ft.Icons.DELETE, on_click=self.clear_old_data)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10
        )
        
        # Секция приложения
        app_section = ft.Container(
            content=ft.Column([
                ft.Text("О приложении", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=24),
                    ft.Column([
                        ft.Text("Система управления детским садом", size=16),
                        ft.Text("Версия 1.0.0", size=12, color=ft.Colors.GREY_600)
                    ], expand=True)
                ])
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10
        )
        
        self.content = ft.Column([
            ft.Container(
                content=ft.Text("Настройки", size=24, weight=ft.FontWeight.BOLD),
                padding=ft.padding.only(left=20, right=20, top=10, bottom=10)
            ),
            ft.Container(height=20),
            theme_section,
            ft.Container(height=20),
            data_section,
            ft.Container(height=20),
            app_section
        ], spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
    
    def backup_database(self, e):
        """Создать резервную копию базы данных"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"kindergarten_backup_{timestamp}.db"
            shutil.copy2("kindergarten.db", backup_path)
            
            username = self.page.client_storage.get("username") if self.page else None
            app_logger.log('BACKUP', username, 'Database', f'Created backup: {backup_path}')
            
            self.show_success(f"Резервная копия создана: {backup_path}")
        except Exception as ex:
            username = self.page.client_storage.get("username") if self.page else None
            app_logger.log('BACKUP_FAILED', username, 'Database', str(ex), 'ERROR')
            self.show_error(f"Ошибка при создании копии: {str(ex)}")
    
    def export_data(self, e):
        """Экспорт данных в CSV"""
        try:
            import csv
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Экспорт детей
            children = self.db.get_all_children()
            filename = f"children_export_{timestamp}.csv"
            with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                if children:
                    writer = csv.DictWriter(f, fieldnames=children[0].keys())
                    writer.writeheader()
                    writer.writerows(children)
            
            username = self.page.client_storage.get("username") if self.page else None
            app_logger.log('EXPORT', username, 'Children', f'Exported {len(children)} records to {filename}')
            
            self.show_success(f"Данные экспортированы: {filename}")
        except Exception as ex:
            username = self.page.client_storage.get("username") if self.page else None
            app_logger.log('EXPORT_FAILED', username, 'Children', str(ex), 'ERROR')
            self.show_error(f"Ошибка при экспорте: {str(ex)}")
    
    def clear_old_data(self, e):
        """Очистка старых данных"""
        from dialogs import show_confirm_dialog
        
        def on_yes(e):
            try:
                # Удаляем записи посещаемости старше 1 года
                from database import Attendance
                from datetime import timedelta
                old_date = datetime.now() - timedelta(days=365)
                deleted = Attendance.delete().where(Attendance.date < old_date.strftime("%Y-%m-%d")).execute()
                
                username = self.page.client_storage.get("username") if self.page else None
                app_logger.log('CLEAR_DATA', username, 'Attendance', f'Deleted {deleted} old records')
                
                self.show_success(f"Удалено записей: {deleted}")
            except Exception as ex:
                username = self.page.client_storage.get("username") if self.page else None
                app_logger.log('CLEAR_DATA_FAILED', username, 'Attendance', str(ex), 'ERROR')
                self.show_error(f"Ошибка при очистке: {str(ex)}")
        
        show_confirm_dialog(
            self.page,
            title="Очистка данных",
            content="Вы уверены, что хотите удалить записи посещаемости старше 1 года?",
            on_yes=on_yes,
            adaptive=True
        )
    
    def show_success(self, message: str):
        """Показать успешное сообщение"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def show_error(self, message: str):
        """Показать ошибку"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def load_settings(self):
        """Загрузка настроек (заглушка для совместимости)"""
        pass
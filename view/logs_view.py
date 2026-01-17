"""
Представление для просмотра логов системы
"""
import flet as ft
from settings.logger import app_logger
from pages_styles.styles import AppStyles


class LogsView(ft.Container):
    """Представление для просмотра логов"""
    
    def __init__(self, page=None):
        super().__init__()
        self.page = page
        
        # Загружаем сохраненное значение лимита
        saved_limit = page.client_storage.get("logs_limit") if page else None
        default_limit = saved_limit if saved_limit else "100"
        
        # Фильтры
        self.user_filter = ft.TextField(
            label="Фильтр по пользователю",
            width=200,
            on_change=self.apply_filters
        )
        
        self.action_filter = ft.Dropdown(
            label="Фильтр по действию",
            width=200,
            value="ALL",
            options=[
                ft.dropdown.Option(key="ALL", text="Все"),
                ft.dropdown.Option(key="LOGIN", text="Вход"),
                ft.dropdown.Option(key="LOGOUT", text="Выход"),
                ft.dropdown.Option(key="CREATE", text="Создание"),
                ft.dropdown.Option(key="UPDATE", text="Изменение"),
                ft.dropdown.Option(key="DELETE", text="Удаление"),
                ft.dropdown.Option(key="EXPORT", text="Экспорт"),
                ft.dropdown.Option(key="BACKUP", text="Резервная копия")
            ],
            on_change=self.apply_filters
        )
        
        self.limit_dropdown = ft.Dropdown(
            label="Количество записей",
            width=150,
            value=default_limit,
            options=[
                ft.DropdownOption("50", "50"),
                ft.DropdownOption("100", "100"),
                ft.DropdownOption("200", "200"),
                ft.DropdownOption("500", "500")
            ],
            on_change=self.on_limit_change
        )
        
        # Список логов
        self.logs_list = ft.ListView(expand=True, spacing=10, padding=20)
        
        # Кнопки
        refresh_button = ft.ElevatedButton(
            "Обновить",
            icon=ft.Icons.REFRESH,
            on_click=self.load_logs
        )
        
        export_button = ft.ElevatedButton(
            "Экспорт в CSV",
            icon=ft.Icons.DOWNLOAD,
            on_click=self.export_logs
        )
        
        clear_button = ft.ElevatedButton(
            "Очистить старые",
            icon=ft.Icons.DELETE_SWEEP,
            on_click=self.clear_old_logs
        )
        
        self.content = ft.Column([
            AppStyles.page_header("Логи системы", None, None),
            ft.Row([
                self.user_filter,
                self.action_filter,
                self.limit_dropdown,
                refresh_button,
                export_button,
                clear_button
            ], spacing=10, wrap=True),
            ft.Container(height=10),
            ft.Container(content=self.logs_list, expand=True)
        ], spacing=10, expand=True)
        self.expand = True
    
    def load_logs(self, e=None):
        """Загрузить логи"""
        try:
            user = self.user_filter.value if self.user_filter.value and self.user_filter.value.strip() else None
            action_value = self.action_filter.value
            action = None if action_value == "ALL" else action_value
            limit = int(self.limit_dropdown.value)
            
            print(f"DEBUG: user={user}, action={action}, limit={limit}")
            
            try:
                logs = app_logger.get_logs(limit=limit, user=user, action=action)
                print(f"DEBUG: Got {len(logs)} logs")
            except Exception as ex:
                print(f"DEBUG: Exception in get_logs: {ex}")
                logs = []
            
            self.logs_list.controls = []
            for log in logs:
                level_color = {
                    'ERROR': ft.Colors.RED,
                    'WARNING': ft.Colors.ORANGE,
                    'INFO': ft.Colors.GREEN
                }.get(log['level'], ft.Colors.GREY)
                
                self.logs_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.ACCESS_TIME, size=16),
                                    ft.Text(log['timestamp'], size=14, weight=ft.FontWeight.BOLD),
                                    ft.Container(expand=True),
                                    ft.Container(
                                        content=ft.Text(log['level'], size=12, color=ft.Colors.WHITE),
                                        bgcolor=level_color,
                                        padding=5,
                                        border_radius=5
                                    )
                                ]),
                                ft.Divider(height=1),
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON, size=16),
                                    ft.Text(f"Пользователь: {log['user']}", size=13)
                                ]),
                                ft.Row([
                                    ft.Icon(ft.Icons.LABEL, size=16),
                                    ft.Text(f"Действие: {log['action']}", size=13, weight=ft.FontWeight.W_500)
                                ]),
                                ft.Row([
                                    ft.Icon(ft.Icons.CATEGORY, size=16),
                                    ft.Text(f"Объект: {log['entity']}", size=13)
                                ]) if log['entity'] else ft.Container(),
                                ft.Row([
                                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16),
                                    ft.Text(f"Детали: {log['details']}", size=13, italic=True)
                                ]) if log['details'] else ft.Container()
                            ], spacing=5),
                            padding=15
                        )
                    )
                )
            
            if not logs:
                self.logs_list.controls.append(
                    ft.Container(
                        content=ft.Text("Логов не найдено", size=16, color=ft.Colors.GREY),
                        alignment=ft.alignment.center,
                        padding=50
                    )
                )
            
            if self.page:
                self.update()
                self.page.update()
        except Exception as ex:
            print(f"Error loading logs: {str(ex)}")
            if self.page:
                self.show_error(f"Ошибка при загрузке логов: {str(ex)}")
    
    def on_limit_change(self, e):
        """Сохранить выбранный лимит и применить фильтры"""
        if self.page:
            self.page.client_storage.set("logs_limit", self.limit_dropdown.value)
        self.apply_filters(e)
    
    def apply_filters(self, e):
        """Применить фильтры"""
        self.load_logs()
    
    def export_logs(self, e):
        """Экспорт логов в CSV"""
        try:
            import csv
            from datetime import datetime
            
            logs = app_logger.get_logs(limit=int(self.limit_dropdown.value))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs_export_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                if logs:
                    writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                    writer.writeheader()
                    writer.writerows(logs)
            
            self.show_success(f"Логи экспортированы: {filename}")
            
            # Логируем экспорт
            username = self.page.client_storage.get("username") if self.page else None
            app_logger.log('EXPORT', username, 'Logs', f'Exported {len(logs)} log entries')
        except Exception as ex:
            self.show_error(f"Ошибка при экспорте: {str(ex)}")
    
    def clear_old_logs(self, e):
        """Очистить старые логи"""
        from dialogs import show_confirm_dialog
        
        def on_yes(e):
            try:
                deleted = app_logger.clear_old_logs(days=90)
                self.show_success(f"Удалено записей: {deleted}")
                self.load_logs()
            except Exception as ex:
                self.show_error(f"Ошибка при очистке: {str(ex)}")
        
        show_confirm_dialog(
            self.page,
            title="Очистка логов",
            content="Удалить логи старше 90 дней?",
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

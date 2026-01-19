"""
Детальное представление информации о мероприятии с вкладками
"""
import flet as ft
from datetime import datetime, date


class EventDetailView(ft.Container):
    """Детальное представление информации о мероприятии"""
    
    def __init__(self, db, event, on_close, page=None, on_refresh=None):
        super().__init__()
        self.db = db
        self.event = event
        self.on_close = on_close
        self.page = page
        self.on_refresh = on_refresh
        self.is_admin = page.client_storage.get("user_role") == "admin" if page else True
        
        if not self.event:
            return
        
        event_name = self.event.get('name', '')
        
        # Вкладки
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Общая информация", icon=ft.Icons.INFO, content=self._create_info_tab()),
                ft.Tab(text="Участники", icon=ft.Icons.GROUPS, content=self._create_participants_tab())
            ],
            expand=True
        )
        
        # Кнопка редактирования только для администратора
        header_buttons = []
        if self.is_admin:
            header_buttons.append(ft.IconButton(icon=ft.Icons.EDIT, tooltip="Редактировать", on_click=self.edit_event))
        header_buttons.append(ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda e: on_close()))
        
        self.content = ft.Column([
            ft.Row([
                ft.Text(event_name, size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True)
            ] + header_buttons),
            ft.Divider(),
            self.tabs
        ], expand=True)
        self.expand = True
    
    def _create_info_tab(self):
        """Создать вкладку с общей информацией"""
        return ft.Container(
            content=ft.Column([
                self._info_row("Название", self.event.get('name', '')),
                self._info_row("Дата проведения", self.event.get('date', '')),
                self._info_row("Ответственный", self.event.get('teacher_name', 'Не назначен')),
                self._info_row("Описание", self.event.get('description', 'Нет описания')),
                self._info_row("Количество групп", str(len(self.event.get('groups', []))))
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=20
        )
    
    def _create_participants_tab(self):
        """Создать вкладку с участниками"""
        self.participants_column = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        self._load_participants()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Участники", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True)
                ]),
                ft.Divider(),
                self.participants_column
            ], spacing=10),
            padding=20
        )
    
    def _load_participants(self):
        """Загрузить список участников"""
        event_groups = self.event.get('groups', [])
        
        if not event_groups:
            self.participants_column.controls = [
                ft.Container(
                    content=ft.Text("Нет участвующих групп", size=16, color=ft.Colors.GREY),
                    alignment=ft.alignment.center,
                    padding=20
                )
            ]
        else:
            for group_id in event_groups:
                group = next((g for g in self.db.get_all_groups() if g['group_id'] == group_id), None)
                if not group:
                    continue
                
                children = self.db.get_children_by_group(group_id)
                
                children_list = []
                for child in children:
                    age = self._calculate_age(child['birth_date'])
                    children_list.append(
                        ft.ListTile(
                            title=ft.Text(f"{child['last_name']} {child['first_name']}"),
                            subtitle=ft.Text(f"Возраст: {age} лет")
                        )
                    )
                
                group_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.GROUP, size=40),
                                ft.Column([
                                    ft.Text(group['group_name'], size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Детей: {len(children)}", size=14)
                                ], expand=True)
                            ]),
                            ft.Divider(),
                            ft.Column(children_list, spacing=5) if children_list else ft.Text("Нет детей в группе", color=ft.Colors.GREY)
                        ], spacing=10),
                        padding=15
                    )
                )
                self.participants_column.controls.append(group_card)
    
    def _calculate_age(self, birth_date_str):
        """Вычисление возраста"""
        try:
            if '-' in birth_date_str and len(birth_date_str.split('-')[0]) == 4:
                birth_date_obj = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            else:
                birth_date_obj = datetime.strptime(birth_date_str, "%d-%m-%Y").date()
            
            today = date.today()
            return today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
        except:
            return 0
    
    def edit_event(self, e):
        """Редактировать мероприятие"""
        event_name_field = ft.TextField(label="Название мероприятия", value=self.event.get('name', ''), width=300)
        event_date_field = ft.TextField(label="Дата проведения", value=self.event.get('date', ''), width=300, hint_text="дд-мм-гггг")
        description_field = ft.TextField(label="Описание", value=self.event.get('description', ''), width=300, multiline=True, max_lines=3)
        
        # Воспитатели
        teachers = self.db.get_all_teachers()
        teacher_dropdown = ft.Dropdown(
            label="Ответственный воспитатель",
            width=300,
            value=str(self.event.get('teacher_id', 0)) if self.event.get('teacher_id') else "0",
            options=[ft.dropdown.Option("0", "Не назначен")] + [
                ft.dropdown.Option(str(t['teacher_id']), f"{t['last_name']} {t['first_name']}")
                for t in teachers
            ]
        )
        
        # Группы
        all_groups = self.db.get_all_groups()
        event_groups = self.event.get('groups', [])
        group_checkboxes = []
        
        for group in all_groups:
            checkbox = ft.Checkbox(
                label=group['group_name'],
                value=group['group_id'] in event_groups,
                data=group['group_id']
            )
            group_checkboxes.append(checkbox)
        
        def save_changes(e):
            if not event_name_field.value:
                return
            
            teacher_id = int(teacher_dropdown.value) if teacher_dropdown.value and teacher_dropdown.value != "0" else None
            teacher_name = "Не назначен"
            if teacher_id:
                teacher = self.db.get_teacher_by_id(teacher_id)
                if teacher:
                    teacher_name = f"{teacher['last_name']} {teacher['first_name']}"
            
            selected_groups = [cb.data for cb in group_checkboxes if cb.value]
            
            self.event['name'] = event_name_field.value
            self.event['date'] = event_date_field.value
            self.event['description'] = description_field.value
            self.event['teacher_id'] = teacher_id
            self.event['teacher_name'] = teacher_name
            self.event['groups'] = selected_groups
            
            # Обновляем в хранилище
            if self.page and hasattr(self.page, 'client_storage'):
                events_storage = self.page.client_storage.get("events_storage") or []
                for i, ev in enumerate(events_storage):
                    if ev['event_id'] == self.event['event_id']:
                        events_storage[i] = self.event
                        break
                self.page.client_storage.set("events_storage", events_storage)
            
            from settings.logger import app_logger
            username = self.page.client_storage.get("username") if self.page else None
            app_logger.log('UPDATE', username, 'Event', f"Updated event: {self.event['name']}")
            
            self.tabs.tabs[0].content = self._create_info_tab()
            self.tabs.tabs[1].content = self._create_participants_tab()
            self.content.controls[0].controls[0].value = self.event['name']
            
            if self.on_refresh:
                self.on_refresh()
            
            self.page.update()
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Редактировать мероприятие"),
            content=ft.Container(
                content=ft.Column([
                    event_name_field,
                    event_date_field,
                    description_field,
                    teacher_dropdown,
                    ft.Text("Участвующие группы:", weight=ft.FontWeight.BOLD),
                    ft.Column(group_checkboxes, scroll=ft.ScrollMode.AUTO, height=150)
                ], spacing=10, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=500
            ),
            actions=[
                ft.ElevatedButton("Сохранить", on_click=save_changes),
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog))
            ]
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _info_row(self, label: str, value: str):
        """Создать строку с информацией"""
        return ft.Row([
            ft.Text(f"{label}:", size=16, weight=ft.FontWeight.BOLD, width=200),
            ft.Text(str(value), size=16, expand=True)
        ])

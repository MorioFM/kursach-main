"""
Детальное представление информации о воспитателе с вкладками
"""
import flet as ft
from datetime import datetime, date


class TeacherDetailView(ft.Container):
    """Детальное представление информации о воспитателе"""
    
    def __init__(self, db, teacher_id: int, on_close, page=None, on_refresh=None):
        super().__init__()
        self.db = db
        self.teacher_id = teacher_id
        self.on_close = on_close
        self.page = page
        self.on_refresh = on_refresh
        self.is_admin = page.client_storage.get("user_role") == "admin" if page else True
        
        # Получаем данные воспитателя
        self.teacher = self.db.get_teacher_by_id(teacher_id)
        if not self.teacher:
            return
        
        teacher_name = f"{self.teacher['last_name']} {self.teacher['first_name']} {self.teacher.get('middle_name', '')}"
        
        # Вкладки
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Общая информация", icon=ft.Icons.INFO, content=self._create_info_tab()),
                ft.Tab(text="Группы", icon=ft.Icons.GROUP, content=self._create_groups_tab())
            ],
            expand=True
        )
        
        # Кнопка редактирования только для администратора
        header_buttons = []
        if self.is_admin:
            header_buttons.append(ft.IconButton(icon=ft.Icons.EDIT, tooltip="Редактировать", on_click=self.edit_teacher))
        header_buttons.append(ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda e: on_close()))
        
        self.content = ft.Column([
            ft.Row([
                ft.Text(teacher_name, size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True)
            ] + header_buttons),
            ft.Divider(),
            self.tabs
        ], expand=True)
        self.expand = True
    
    def _create_info_tab(self):
        """Создать вкладку с общей информацией"""
        # Вычисляем возраст
        age_text = "Не указан"
        if self.teacher.get('birth_date'):
            try:
                birth_date_str = self.teacher['birth_date']
                if '-' in birth_date_str and len(birth_date_str.split('-')[0]) == 4:
                    birth_date_obj = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
                else:
                    birth_date_obj = datetime.strptime(birth_date_str, "%d-%m-%Y").date()
                
                today = date.today()
                age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
                age_text = f"{age} лет"
            except:
                pass
        
        return ft.Container(
            content=ft.Column([
                self._info_row("ФИО", f"{self.teacher['last_name']} {self.teacher['first_name']} {self.teacher.get('middle_name', '')}"),
                self._info_row("Дата рождения", self.teacher.get('birth_date', 'Не указана')),
                self._info_row("Возраст", age_text),
                self._info_row("Телефон", self.teacher.get('phone', 'Не указан')),
                self._info_row("Email", self.teacher.get('email', 'Не указан')),
                self._info_row("Адрес", self.teacher.get('address', 'Не указан')),
                self._info_row("Образование", self.teacher.get('education', 'Не указано')),
                self._info_row("Стаж работы", f"{self.teacher.get('experience', 'Не указан')} лет" if self.teacher.get('experience') else 'Не указан')
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=20
        )
    
    def _create_groups_tab(self):
        """Создать вкладку с группами"""
        self.groups_column = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        self._load_groups()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Группы", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True)
                ]),
                ft.Divider(),
                self.groups_column
            ], spacing=10),
            padding=20
        )
    
    def _load_groups(self):
        """Загрузить список групп"""
        teacher_groups = self.db.get_groups_by_teacher(self.teacher_id)
        
        if not teacher_groups:
            self.groups_column.controls = [
                ft.Container(
                    content=ft.Text("Воспитатель не закреплен за группами", size=16, color=ft.Colors.GREY),
                    alignment=ft.alignment.center,
                    padding=20
                )
            ]
        else:
            self.groups_column.controls = [
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.GROUP, size=40),
                                ft.Column([
                                    ft.Text(group.get('group_name', ''), size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Возрастная категория: {group.get('age_category', 'Не указана')}", size=14)
                                ], expand=True)
                            ])
                        ], spacing=10),
                        padding=15
                    )
                ) for group in teacher_groups
            ]
    
    def edit_teacher(self, e):
        """Редактировать воспитателя"""
        last_name_field = ft.TextField(label="Фамилия", value=self.teacher['last_name'], width=300)
        first_name_field = ft.TextField(label="Имя", value=self.teacher['first_name'], width=300)
        middle_name_field = ft.TextField(label="Отчество", value=self.teacher.get('middle_name', ''), width=300)
        
        # Разбираем телефон на код страны и номер
        phone = self.teacher.get('phone', '')
        country_code = '+7'
        phone_number = ''
        if phone:
            if phone.startswith('+375'):
                country_code = '+375'
                phone_number = phone[4:]
            elif phone.startswith('+1'):
                country_code = '+1'
                phone_number = phone[2:]
            elif phone.startswith('+7'):
                country_code = '+7'
                phone_number = phone[2:]
            else:
                phone_number = phone
        
        country_code_dropdown = ft.Dropdown(
            label="Код страны",
            width=140,
            value=country_code,
            options=[
                ft.dropdown.Option("+7", "+7 (Россия)"),
                ft.dropdown.Option("+375", "+375 (Беларусь)"),
                ft.dropdown.Option("+1", "+1 (США)")
            ]
        )
        
        phone_field = ft.TextField(label="Телефон", value=phone_number, width=150)
        email_field = ft.TextField(label="Email", value=self.teacher.get('email', ''), width=300)
        birth_date_field = ft.TextField(label="Дата рождения", value=self.teacher.get('birth_date', ''), width=300, hint_text="дд-мм-гггг")
        address_field = ft.TextField(label="Адрес", value=self.teacher.get('address', ''), width=300, multiline=True, max_lines=2)
        education_field = ft.TextField(label="Образование", value=self.teacher.get('education', ''), width=300, multiline=True, max_lines=3)
        experience_field = ft.TextField(label="Стаж работы (лет)", value=str(self.teacher.get('experience', '')), width=300)
        
        def save_changes(e):
            if not last_name_field.value or not first_name_field.value:
                return
            
            full_phone = None
            if phone_field.value and phone_field.value.strip():
                full_phone = country_code_dropdown.value + phone_field.value.replace('-', '')
            
            teacher_data = {
                'last_name': last_name_field.value,
                'first_name': first_name_field.value,
                'middle_name': middle_name_field.value or None,
                'phone': full_phone,
                'email': email_field.value or None,
                'birth_date': birth_date_field.value or None,
                'address': address_field.value or None,
                'education': education_field.value or None,
                'experience': int(experience_field.value) if experience_field.value and experience_field.value.isdigit() else None
            }
            
            self.db.update_teacher(self.teacher_id, **teacher_data)
            
            from settings.logger import app_logger
            username = self.page.client_storage.get("username") if self.page else None
            app_logger.log('UPDATE', username, 'Teacher', f"Updated teacher: {teacher_data['last_name']} {teacher_data['first_name']}")
            
            self.teacher = self.db.get_teacher_by_id(self.teacher_id)
            self.tabs.tabs[0].content = self._create_info_tab()
            self.content.controls[0].controls[0].value = f"{self.teacher['last_name']} {self.teacher['first_name']} {self.teacher.get('middle_name', '')}"
            
            if self.on_refresh:
                self.on_refresh()
            
            self.page.update()
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Редактировать воспитателя"),
            content=ft.Container(
                content=ft.Column([
                    last_name_field,
                    first_name_field,
                    middle_name_field,
                    ft.Row([country_code_dropdown, phone_field]),
                    email_field,
                    birth_date_field,
                    address_field,
                    education_field,
                    experience_field
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
            ft.Text(str(value), size=16)
        ])

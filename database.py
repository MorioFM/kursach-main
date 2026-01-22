from peewee import *
from datetime import datetime
from typing import List, Optional

# Инициализация базы данных
db = SqliteDatabase(None)


class BaseModel(Model):
    """Базовая модель для всех таблиц"""
    class Meta:
        database = db


class Teacher(BaseModel):
    """Модель воспитателя"""
    teacher_id = AutoField(primary_key=True)
    last_name = CharField(null=False)
    first_name = CharField(null=False)
    middle_name = CharField(null=True)
    phone = CharField(null=True)
    email = CharField(null=True)
    birth_date = CharField(null=True)
    address = TextField(null=True)
    education = TextField(null=True)
    experience = IntegerField(null=True)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'teachers'


class Group(BaseModel):
    """Модель группы детского сада"""
    group_id = AutoField(primary_key=True)
    group_name = CharField(null=False)
    age_category = CharField(null=False)
    teacher = ForeignKeyField(Teacher, backref='groups', null=True, column_name='teacher_id')
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'groups'


class Parent(BaseModel):
    """Модель родителя"""
    parent_id = AutoField(primary_key=True)
    last_name = CharField(null=False)
    first_name = CharField(null=False)
    middle_name = CharField(null=True)
    phone = CharField(null=True)
    email = CharField(null=True)
    address = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'parents'


class Child(BaseModel):
    """Модель ребенка"""
    child_id = AutoField(primary_key=True)
    last_name = CharField(null=False)
    first_name = CharField(null=False)
    middle_name = CharField(null=True)
    birth_date = DateField(null=False)
    gender = CharField(null=False, constraints=[Check("gender IN ('М', 'Ж')")])
    group = ForeignKeyField(Group, backref='children', null=True, column_name='group_id')
    enrollment_date = DateField(null=False)
    locker_symbol = CharField(null=True)  # Символ шкафчика
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'children'
        indexes = (
            (('last_name', 'first_name'), False),
        )


class ParentChild(BaseModel):
    """Модель связи родителя и ребенка"""
    parent = ForeignKeyField(Parent, backref='parent_children', column_name='parent_id')
    child = ForeignKeyField(Child, backref='child_parents', column_name='child_id')
    relationship = CharField(null=False)  # Мама, Папа, Опекун и т.д.
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'parent_child'
        primary_key = CompositeKey('parent', 'child')


class GroupTeacher(BaseModel):
    """Модель связи группы и воспитателя"""
    group = ForeignKeyField(Group, backref='group_teachers', column_name='group_id')
    teacher = ForeignKeyField(Teacher, backref='teacher_groups', column_name='teacher_id')
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'group_teacher'
        primary_key = CompositeKey('group', 'teacher')


class AttendanceRecord(BaseModel):
    """Модель записи в журнале посещаемости"""
    record_id = AutoField(primary_key=True)
    child = ForeignKeyField(Child, backref='attendance_records', column_name='child_id')
    date = DateField(null=False)
    status = CharField(null=False)  # Присутствует, Отсутствует, Болеет
    notes = TextField(null=True)  # Примечания
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'attendance_records'
        indexes = (
            (('child', 'date'), True),  # Уникальная запись на дату для ребенка
        )


class MedicalRecord(BaseModel):
    """Модель медицинской карты ребёнка"""
    record_id = AutoField(primary_key=True)
    child = ForeignKeyField(Child, backref='medical_records', column_name='child_id')
    blood_type = CharField(null=True)  # Группа крови
    allergies = TextField(null=True)  # Аллергии
    chronic_diseases = TextField(null=True)  # Хронические заболевания
    vaccinations = TextField(null=True)  # Прививки
    height = FloatField(null=True)  # Рост (см)
    weight = FloatField(null=True)  # Вес (кг)
    doctor_notes = TextField(null=True)  # Замечания врача
    emergency_contact = CharField(null=True)  # Контакт для экстренных случаев
    last_checkup = DateField(null=True)  # Последний осмотр
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'medical_records'


class User(BaseModel):
    """Модель пользователя"""
    user_id = AutoField(primary_key=True)
    username = CharField(unique=True, null=False)
    password = CharField(null=False)  # Хеш пароля
    role = CharField(default='admin')  # Роль пользователя
    group = ForeignKeyField(Group, backref='users', null=True, column_name='group_id')  # Группа для воспитателя
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'users'


class UserPermission(BaseModel):
    """Модель прав доступа пользователя"""
    user = ForeignKeyField(User, backref='permissions', column_name='user_id')
    page_name = CharField(null=False)  # Название страницы
    can_access = BooleanField(default=True)
    
    class Meta:
        table_name = 'user_permissions'
        primary_key = CompositeKey('user', 'page_name')


class KindergartenDB:
    """Класс для работы с базой данных детского сада через Peewee ORM"""
    
    def __init__(self, db_path: str = "kindergarten.db"):
        """
        Инициализация подключения к базе данных
        
        Args:
            db_path: путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self.connection = None
        from settings.children_settings import ChildrenSettings
        from settings.teachers_settings import TeachersSettings
        from settings.parents_settings import ParentsSettings
        from settings.groups_settings import GroupsSettings
        from settings.attendance_settings import AttendanceSettings
        from settings.medical_card_settings import MedicalCardSettings
        self._children_settings = ChildrenSettings()
        self._teachers_settings = TeachersSettings()
        self._parents_settings = ParentsSettings()
        self._groups_settings = GroupsSettings()
        self._attendance_settings = AttendanceSettings()
        self._medical_card_settings = MedicalCardSettings()
    
    def connect(self):
        """Установить соединение с базой данных"""
        db.init(self.db_path)
        db.connect()
        self.connection = db
        return self.connection
    
    def close(self):
        """Закрыть соединение с базой данных"""
        if db and not db.is_closed():
            db.close()
    
    def create_tables(self):
        """Создать таблицы в базе данных"""
        db.create_tables([Teacher, Group, Parent, Child, ParentChild, GroupTeacher, AttendanceRecord, MedicalRecord, User, UserPermission])
        
        # Миграция: добавляем колонку group_id если её нет
        try:
            db.execute_sql('ALTER TABLE users ADD COLUMN group_id INTEGER REFERENCES groups(group_id)')
        except:
            pass  # Колонка уже существует
        
        # Миграция: добавляем колонку locker_symbol если её нет
        try:
            db.execute_sql('ALTER TABLE children ADD COLUMN locker_symbol TEXT')
        except:
            pass  # Колонка уже существует
        
        # Создаем администратора по умолчанию
        try:
            User.get(User.username == 'admin')
        except:
            import hashlib
            password_hash = hashlib.sha256('admin'.encode()).hexdigest()
            User.create(username='admin', password=password_hash, role='admin', group=None)
        print("Tables created successfully")
    
    def __getattr__(self, name):
        """Динамическое делегирование методов к соответствующим настройкам"""
        # Методы для работы с воспитателями
        teacher_methods = ['add_teacher', 'get_all_teachers', 'get_teacher_by_id', 'update_teacher', 'delete_teacher', 'search_teachers']
        if name in teacher_methods:
            return getattr(self._teachers_settings, name)
        
        # Методы для работы с родителями
        parent_methods = ['add_parent', 'get_all_parents', 'get_parent_by_id', 'update_parent', 'delete_parent', 'search_parents']
        if name in parent_methods:
            return getattr(self._parents_settings, name)
        
        # Методы для работы с группами
        group_methods = ['add_group', 'get_all_groups', 'get_group_by_id', 'update_group', 'delete_group']
        if name in group_methods:
            return getattr(self._groups_settings, name)
        
        # Методы для работы с детьми
        child_methods = ['add_child', 'get_all_children', 'get_child_by_id', 'get_children_by_group', 'search_children', 
                        'update_child', 'delete_child', 'transfer_child_to_group', 'bulk_transfer_children', 'get_children_without_group',
                        'get_used_locker_symbols_in_group']
        if name in child_methods:
            return getattr(self._children_settings, name)
        
        # Методы для работы с посещаемостью
        attendance_methods = ['add_attendance_record', 'update_attendance_record']
        if name in attendance_methods:
            return getattr(self._attendance_settings, name)
        
        # Методы для работы с медицинскими картами
        medical_methods = ['get_medical_record', 'create_or_update_medical_record']
        if name in medical_methods:
            return getattr(self._medical_card_settings, name)
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def add_parent_child_relation(self, parent_id: int, child_id: int, relationship: str):
        """Добавить связь родитель-ребенок"""
        ParentChild.create(parent=parent_id, child=child_id, relationship=relationship)
    
    def remove_parent_child_relation(self, parent_id: int, child_id: int):
        """Удалить связь родитель-ребенок"""
        ParentChild.delete().where((ParentChild.parent == parent_id) & (ParentChild.child == child_id)).execute()
    
    def get_children_by_parent(self, parent_id: int):
        """Получить детей родителя"""
        relations = (ParentChild.select(ParentChild, Child, Group).join(Child).join(Group, JOIN.LEFT_OUTER).where(ParentChild.parent == parent_id))
        result = []
        for relation in relations:
            child_data = self._children_settings._child_to_dict(relation.child)
            child_data['relationship'] = relation.relationship
            result.append(child_data)
        return result
    
    def get_parents_by_child(self, child_id: int):
        """Получить родителей ребенка"""
        relations = (ParentChild.select(ParentChild, Parent).join(Parent).where(ParentChild.child == child_id))
        result = []
        for relation in relations:
            parent_data = self._parents_settings._parent_to_dict(relation.parent)
            parent_data['relationship'] = relation.relationship
            result.append(parent_data)
        return result
    
    def get_attendance_by_group_and_date(self, group_id: int, date: str):
        return self._attendance_settings.get_attendance_by_group_and_date(group_id, date, self._children_settings)
    
    def authenticate_user(self, username: str, password: str):
        """Проверка авторизации пользователя"""
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            user = User.get((User.username == username) & (User.password == password_hash))
            return {'user_id': user.user_id, 'username': user.username, 'role': user.role}
        except:
            return None
    
    def get_user_permissions(self, user_id: int):
        """Получить права доступа пользователя"""
        permissions = UserPermission.select().where(UserPermission.user == user_id)
        return {p.page_name: p.can_access for p in permissions}
    
    def set_user_permission(self, user_id: int, page_name: str, can_access: bool):
        """Установить право доступа"""
        UserPermission.replace(user=user_id, page_name=page_name, can_access=can_access).execute()
    
    def get_all_users(self):
        """Получить всех пользователей"""
        users = User.select(User, Group).join(Group, JOIN.LEFT_OUTER)
        return [{
            'user_id': u.user_id, 
            'username': u.username, 
            'role': u.role,
            'group_id': u.group.group_id if u.group else None,
            'group_name': u.group.group_name if u.group else None
        } for u in users]
    
    def set_user_group(self, user_id: int, group_id: int = None):
        """Установить группу для пользователя"""
        user = User.get_by_id(user_id)
        user.group = group_id
        user.save()
    
    def get_user_group(self, user_id: int):
        """Получить группу пользователя"""
        try:
            user = User.select(User, Group).join(Group, JOIN.LEFT_OUTER).where(User.user_id == user_id).get()
            if user.group:
                return {'group_id': user.group.group_id, 'group_name': user.group.group_name}
            return None
        except:
            return None
    
    def add_group_teacher_relation(self, group_id: int, teacher_id: int):
        """Добавить связь группа-воспитатель"""
        try:
            GroupTeacher.create(group=group_id, teacher=teacher_id)
        except:
            pass  # Связь уже существует
    
    def remove_group_teacher_relation(self, group_id: int, teacher_id: int):
        """Удалить связь группа-воспитатель"""
        GroupTeacher.delete().where((GroupTeacher.group == group_id) & (GroupTeacher.teacher == teacher_id)).execute()
    
    def get_teachers_by_group(self, group_id: int):
        """Получить воспитателей группы"""
        relations = GroupTeacher.select(GroupTeacher, Teacher).join(Teacher).where(GroupTeacher.group == group_id)
        result = []
        for relation in relations:
            teacher_data = self._teachers_settings._teacher_to_dict(relation.teacher)
            result.append(teacher_data)
        return result
    
    def get_groups_by_teacher(self, teacher_id: int):
        """Получить группы воспитателя"""
        relations = GroupTeacher.select(GroupTeacher, Group).join(Group).where(GroupTeacher.teacher == teacher_id)
        result = []
        for relation in relations:
            group_data = self._groups_settings._group_to_dict(relation.group)
            result.append(group_data)
        return result
    

    

    

    

    

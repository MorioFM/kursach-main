"""
Система логирования приложения
"""
import logging
from datetime import datetime
from database import db, BaseModel
from peewee import CharField, TextField, DateTimeField


class AuditLog(BaseModel):
    """Модель для хранения логов в базе данных"""
    timestamp = DateTimeField(default=datetime.now)
    user = CharField(max_length=100, null=True)
    action = CharField(max_length=50)
    entity = CharField(max_length=50, null=True)
    details = TextField(null=True)
    level = CharField(max_length=20, default='INFO')


class AppLogger:
    """Класс для логирования действий в приложении"""
    
    def __init__(self):
        # Настройка файлового логирования
        logging.basicConfig(
            filename='kindergarten.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        self.logger = logging.getLogger('kindergarten')
        self._table_created = False
    
    def _ensure_table(self):
        """Создать таблицу логов если её нет"""
        if not self._table_created:
            try:
                db.create_tables([AuditLog], safe=True)
                self._table_created = True
            except Exception as e:
                self.logger.error(f"Failed to create logs table: {str(e)}")
    
    def log(self, action: str, user: str = None, entity: str = None, details: str = None, level: str = 'INFO'):
        """Записать лог в файл и базу данных"""
        # Запись в файл
        log_message = f"User: {user or 'System'} | Action: {action}"
        if entity:
            log_message += f" | Entity: {entity}"
        if details:
            log_message += f" | Details: {details}"
        
        if level == 'ERROR':
            self.logger.error(log_message)
        elif level == 'WARNING':
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Запись в базу данных
        try:
            self._ensure_table()
            AuditLog.create(
                user=user,
                action=action,
                entity=entity,
                details=details,
                level=level
            )
        except Exception as e:
            self.logger.error(f"Failed to write to database: {str(e)}")
    
    def get_logs(self, limit: int = 100, user: str = None, action: str = None):
        """Получить логи из базы данных"""
        self._ensure_table()
        query = AuditLog.select().order_by(AuditLog.timestamp.desc()).limit(limit)
        
        if user and user.strip():
            query = query.where(AuditLog.user.contains(user))
        if action and action.strip():
            query = query.where(AuditLog.action == action)
        
        return [
            {
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'user': log.user or 'System',
                'action': log.action,
                'entity': log.entity or '',
                'details': log.details or '',
                'level': log.level
            }
            for log in query
        ]
    
    def clear_old_logs(self, days: int = 90):
        """Удалить логи старше указанного количества дней"""
        self._ensure_table()
        from datetime import timedelta
        old_date = datetime.now() - timedelta(days=days)
        deleted = AuditLog.delete().where(AuditLog.timestamp < old_date).execute()
        self.log('CLEAR_LOGS', 'System', details=f'Deleted {deleted} old log entries')
        return deleted


# Глобальный экземпляр логгера
app_logger = AppLogger()

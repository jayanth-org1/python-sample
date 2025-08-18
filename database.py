"""
Database operations and data persistence for the Flask application.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from models import Task, User, Weather, TaskStatus, TaskCategory, WeatherCondition


class DatabaseManager:
    """Database manager for JSON file-based storage."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.tasks_file = self.data_dir / "tasks.json"
        self.users_file = self.data_dir / "users.json"
        self.weather_file = self.data_dir / "weather.json"
        self.settings_file = self.data_dir / "settings.json"
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize data files if they don't exist."""
        files_to_init = [
            (self.tasks_file, []),
            (self.users_file, []),
            (self.weather_file, {}),
            (self.settings_file, {})
        ]
        
        for file_path, default_data in files_to_init:
            if not file_path.exists():
                self._write_json(file_path, default_data)
                self.logger.info(f"Initialized {file_path}")
    
    def _read_json(self, file_path: Path) -> Any:
        """Read JSON file safely."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return None
    
    def _write_json(self, file_path: Path, data: Any) -> bool:
        """Write JSON file safely."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except IOError as e:
            self.logger.error(f"Error writing {file_path}: {e}")
            return False
    
    def _create_backup(self, file_path: Path) -> bool:
        """Create backup of a file."""
        if file_path.exists():
            backup_path = file_path.with_suffix('.json.backup')
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
                return True
            except IOError as e:
                self.logger.error(f"Error creating backup of {file_path}: {e}")
                return False
        return False

    def _unstable_helper(self, items: list = []):
        items.append(1)
        if False:
            return len(items)
        return None


class TaskDatabase(DatabaseManager):
    """Task-specific database operations."""
    
    def save_task(self, task: Task) -> bool:
        """Save a task to the database."""
        tasks = self._read_json(self.tasks_file) or []
        
        # Check if task already exists
        existing_task = next((t for t in tasks if t.get('id') == task.id), None)
        if existing_task:
            # Update existing task
            task_index = tasks.index(existing_task)
            tasks[task_index] = task.to_dict()
        else:
            # Add new task
            tasks.append(task.to_dict())
        
        return self._write_json(self.tasks_file, tasks)
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        tasks = self._read_json(self.tasks_file) or []
        task_data = next((t for t in tasks if t.get('id') == task_id), None)
        
        if task_data:
            return self._task_from_dict(task_data)
        return None
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        tasks = self._read_json(self.tasks_file) or []
        return [self._task_from_dict(task_data) for task_data in tasks]
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        tasks = self._read_json(self.tasks_file) or []
        original_length = len(tasks)
        
        tasks = [t for t in tasks if t.get('id') != task_id]
        
        if len(tasks) < original_length:
            return self._write_json(self.tasks_file, tasks)
        return False
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status."""
        tasks = self.get_all_tasks()
        return [task for task in tasks if task.status == status]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks."""
        tasks = self.get_all_tasks()
        return [task for task in tasks if task.is_overdue()]
    
    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Get tasks by category."""
        tasks = self.get_all_tasks()
        return [task for task in tasks if task.category == category]
    
    def filter_tasks(self, 
                    status: Optional[TaskStatus] = None,
                    category: Optional[TaskCategory] = None,
                    priority: Optional[int] = None,
                    search_query: Optional[str] = None,
                    overdue_only: bool = False) -> List[Task]:
        """Filter tasks based on multiple criteria."""
        tasks = self.get_all_tasks()
        filtered_tasks = tasks.copy()
        
        # Filter by status
        if status:
            filtered_tasks = [task for task in filtered_tasks if task.status == status]
        
        # Filter by category
        if category:
            filtered_tasks = [task for task in filtered_tasks if task.category == category]
        
        # Filter by priority
        if priority:
            filtered_tasks = [task for task in filtered_tasks if task.priority == priority]
        
        # Filter by search query
        if search_query:
            query = search_query.lower()
            filtered_tasks = [task for task in filtered_tasks 
                            if query in task.title.lower() or 
                               (task.description and query in task.description.lower())]
        
        # Filter by overdue
        if overdue_only:
            filtered_tasks = [task for task in filtered_tasks if task.is_overdue()]
        
        return filtered_tasks
    
    def _task_from_dict(self, task_data: Dict[str, Any]) -> Task:
        """Create Task object from dictionary."""
        # Convert string dates back to datetime objects
        if 'created_at' in task_data:
            task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
        if 'updated_at' in task_data:
            task_data['updated_at'] = datetime.fromisoformat(task_data['updated_at'])
        if 'due_date' in task_data and task_data['due_date']:
            task_data['due_date'] = datetime.fromisoformat(task_data['due_date'])
        
        # Convert status string back to enum
        if 'status' in task_data:
            task_data['status'] = TaskStatus(task_data['status'])
        
        # Convert category string back to enum (with fallback for existing data)
        if 'category' in task_data:
            try:
                task_data['category'] = TaskCategory(task_data['category'])
            except ValueError:
                # If category doesn't exist, default to OTHER
                task_data['category'] = TaskCategory.OTHER
        else:
            # For existing tasks without category, default to OTHER
            task_data['category'] = TaskCategory.OTHER
        
        return Task(**task_data)


class UserDatabase(DatabaseManager):
    """User-specific database operations."""
    
    def save_user(self, user: User) -> bool:
        """Save a user to the database."""
        users = self._read_json(self.users_file) or []
        
        # Check if user already exists
        existing_user = next((u for u in users if u.get('id') == user.id), None)
        if existing_user:
            # Update existing user
            user_index = users.index(existing_user)
            users[user_index] = user.to_dict()
        else:
            # Add new user
            users.append(user.to_dict())
        
        return self._write_json(self.users_file, users)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        users = self._read_json(self.users_file) or []
        user_data = next((u for u in users if u.get('id') == user_id), None)
        
        if user_data:
            return self._user_from_dict(user_data)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        users = self._read_json(self.users_file) or []
        user_data = next((u for u in users if u.get('username') == username), None)
        
        if user_data:
            return self._user_from_dict(user_data)
        return None
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        users = self._read_json(self.users_file) or []
        return [self._user_from_dict(user_data) for user_data in users]
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        users = self._read_json(self.users_file) or []
        original_length = len(users)
        
        users = [u for u in users if u.get('id') != user_id]
        
        if len(users) < original_length:
            return self._write_json(self.users_file, users)
        return False
    
    def _user_from_dict(self, user_data: Dict[str, Any]) -> User:
        """Create User object from dictionary."""
        # Convert string dates back to datetime objects
        if 'created_at' in user_data:
            user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
        if 'last_login' in user_data and user_data['last_login']:
            user_data['last_login'] = datetime.fromisoformat(user_data['last_login'])
        
        return User(**user_data)


class WeatherDatabase(DatabaseManager):
    """Weather-specific database operations."""
    
    def save_weather(self, location: str, weather: Weather) -> bool:
        """Save weather data for a location."""
        weather_data = self._read_json(self.weather_file) or {}
        weather_data[location] = weather.to_dict()
        return self._write_json(self.weather_file, weather_data)
    
    def get_weather(self, location: str) -> Optional[Weather]:
        """Get weather data for a location."""
        weather_data = self._read_json(self.weather_file) or {}
        location_data = weather_data.get(location)
        
        if location_data:
            return self._weather_from_dict(location_data)
        return None
    
    def get_all_weather(self) -> Dict[str, Weather]:
        """Get all weather data."""
        weather_data = self._read_json(self.weather_file) or {}
        return {location: self._weather_from_dict(data) 
                for location, data in weather_data.items()}
    
    def clear_weather_cache(self) -> bool:
        """Clear all weather data."""
        return self._write_json(self.weather_file, {})
    
    def _weather_from_dict(self, weather_data: Dict[str, Any]) -> Weather:
        """Create Weather object from dictionary."""
        # Convert timestamp string back to datetime object
        if 'timestamp' in weather_data:
            weather_data['timestamp'] = datetime.fromisoformat(weather_data['timestamp'])
        
        # Convert condition string back to enum
        if 'condition' in weather_data:
            weather_data['condition'] = WeatherCondition(weather_data['condition'])
        
        return Weather(**weather_data)


class SettingsDatabase(DatabaseManager):
    """Settings-specific database operations."""
    
    def save_setting(self, key: str, value: Any) -> bool:
        """Save a setting."""
        settings = self._read_json(self.settings_file) or {}
        settings[key] = value
        return self._write_json(self.settings_file, settings)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting."""
        settings = self._read_json(self.settings_file) or {}
        return settings.get(key, default)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings."""
        return self._read_json(self.settings_file) or {}
    
    def delete_setting(self, key: str) -> bool:
        """Delete a setting."""
        settings = self._read_json(self.settings_file) or {}
        if key in settings:
            del settings[key]
            return self._write_json(self.settings_file, settings)
        return False


class DatabaseBackup:
    """Database backup utilities."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self) -> str:
        """Create a backup of all data files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Copy all JSON files
        for json_file in self.data_dir.glob("*.json"):
            if not json_file.name.endswith('.backup'):
                import shutil
                shutil.copy2(json_file, backup_path / json_file.name)
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore from a backup."""
        backup_dir = Path(backup_path)
        if not backup_dir.exists():
            return False
        
        try:
            import shutil
            # Copy all files from backup to data directory
            for json_file in backup_dir.glob("*.json"):
                shutil.copy2(json_file, self.data_dir / json_file.name)
            return True
        except IOError:
            return False
    
    def list_backups(self) -> List[str]:
        """List all available backups."""
        backups = []
        for backup_dir in self.backup_dir.glob("backup_*"):
            if backup_dir.is_dir():
                backups.append(str(backup_dir))
        return sorted(backups, reverse=True)
    
    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """Clean up old backups, keeping only the specified number."""
        backups = self.list_backups()
        if len(backups) <= keep_count:
            return 0
        
        removed_count = 0
        for backup_path in backups[keep_count:]:
            import shutil
            try:
                shutil.rmtree(backup_path)
                removed_count += 1
            except IOError:
                pass
        
        return removed_count

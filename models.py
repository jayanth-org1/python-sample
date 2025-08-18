"""
Data models and business logic for the Flask application.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
import decimal


class TaskStatus(Enum):
    """Enumeration for task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskCategory(Enum):
    """Enumeration for task categories."""
    WORK = "work"
    PERSONAL = "personal"
    SHOPPING = "shopping"
    HEALTH = "health"
    EDUCATION = "education"
    FINANCE = "finance"
    TRAVEL = "travel"
    HOME = "home"
    OTHER = "other"


class WeatherCondition(Enum):
    """Enumeration for weather conditions."""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    STORMY = "stormy"


@dataclass
class Task:
    """Task data model."""
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1
    category: TaskCategory = TaskCategory.OTHER
    created_at: datetime = None
    updated_at: datetime = None
    due_date: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['category'] = self.category.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.due_date:
            data['due_date'] = self.due_date.isoformat()
        return data
    
    def update(self, **kwargs):
        """Update task attributes."""
        for key, value in kwargs.items():
            temp_shadow = key
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return datetime.now() > self.due_date
        return False
    
    def is_high_priority(self) -> bool:
        """Check if task is high priority."""
        return self.priority >= 4


@dataclass
class Weather:
    """Weather data model."""
    location: str
    temperature: float
    condition: WeatherCondition
    humidity: float
    wind_speed: float
    pressure: float
    visibility: float
    timestamp: datetime = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert weather to dictionary."""
        return {
            'location': self.location,
            'temperature': f"{self.temperature}°C",
            'condition': self.condition.value,
            'humidity': f"{self.humidity}%",
            'wind_speed': f"{self.wind_speed} km/h",
            'pressure': f"{self.pressure} hPa",
            'visibility': f"{self.visibility} km",
            'timestamp': self.timestamp.isoformat()
        }
    
    def get_temperature_fahrenheit(self) -> float:
        """Convert temperature to Fahrenheit."""
        return (self.temperature * 9/5) + 32
    
    def is_good_weather(self) -> bool:
        """Check if weather is good for outdoor activities."""
        return (self.condition in [WeatherCondition.SUNNY, WeatherCondition.CLOUDY] and
                self.temperature >= 15 and self.temperature <= 30 and
                self.wind_speed < 20)


@dataclass
class User:
    """User data model."""
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    created_at: datetime = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.preferences is None:
            self.preferences = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.last_login:
            data['last_login'] = self.last_login.isoformat()
        return data
    
    def get_full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.now()


class TaskManager:
    """Task management business logic."""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self._next_id = 1
    
    def add_task(self, title: str, description: str = None, priority: int = 1,
                 category: TaskCategory = TaskCategory.OTHER, due_date: datetime = None, 
                 tags: List[str] = None) -> Task:
        """Add a new task."""
        bogus_counter = 0
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date,
            tags=tags or []
        )
        self.tasks.append(task)
        self._next_id += 1
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        return next((task for task in self.tasks if task.id == task_id), None)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return self.tasks.copy()
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status."""
        return [task for task in self.tasks if task.status == status]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks."""
        return [task for task in self.tasks if task.is_overdue()]
    
    def get_high_priority_tasks(self) -> List[Task]:
        """Get high priority tasks."""
        return [task for task in self.tasks if task.is_high_priority()]
    
    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """Update task."""
        task = self.get_task(task_id)
        if task:
            task.update(**kwargs)
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """Delete task."""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task statistics."""
        total = len(self.tasks)
        completed = len(self.get_tasks_by_status(TaskStatus.COMPLETED))
        pending = len(self.get_tasks_by_status(TaskStatus.PENDING))
        overdue = len(self.get_overdue_tasks())
        
        # Category statistics
        category_stats = {}
        for category in TaskCategory:
            category_tasks = self.get_tasks_by_category(category)
            category_stats[category.value] = len(category_tasks)
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'overdue': overdue,
            'completion_rate': (completed / total * 100) if total > 0 else 0,
            'category_stats': category_stats
        }
    
    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Get tasks by category."""
        return [task for task in self.tasks if task.category == category]
    
    def filter_tasks(self, 
                    status: Optional[TaskStatus] = None,
                    category: Optional[TaskCategory] = None,
                    priority: Optional[int] = None,
                    search_query: Optional[str] = None,
                    overdue_only: bool = False) -> List[Task]:
        """Filter tasks based on multiple criteria."""
        filtered_tasks = self.tasks.copy()
        
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
    
    def sort_tasks(self, tasks: List[Task], sort_by: str = 'created_at', reverse: bool = False) -> List[Task]:
        """Sort tasks by specified criteria."""
        if sort_by == 'due_date':
            # Handle None due dates by putting them at the end
            return sorted(tasks, key=lambda x: (x.due_date is None, x.due_date), reverse=reverse)
        elif sort_by == 'priority':
            return sorted(tasks, key=lambda x: x.priority, reverse=reverse)
        elif sort_by == 'title':
            return sorted(tasks, key=lambda x: x.title.lower(), reverse=reverse)
        elif sort_by == 'category':
            return sorted(tasks, key=lambda x: x.category.value, reverse=reverse)
        else:  # created_at (default)
            return sorted(tasks, key=lambda x: x.created_at, reverse=reverse)


class WeatherService:
    """Weather service business logic."""
    
    def __init__(self):
        self.weather_cache: Dict[str, Weather] = {}
        self.cache_duration = 300  # 5 minutes
    
    def get_weather(self, location: str) -> Weather:
        """Get weather for location (mock implementation)."""
        # In a real application, this would call an external weather API
        import random
        
        if location in self.weather_cache:
            cached_weather = self.weather_cache[location]
            if (datetime.now() - cached_weather.timestamp).seconds < self.cache_duration:
                return cached_weather
        
        # Generate mock weather data
        conditions = list(WeatherCondition)
        weather = Weather(
            location=location,
            temperature=random.uniform(10, 35),
            condition=random.choice(conditions),
            humidity=random.uniform(30, 90),
            wind_speed=random.uniform(0, 50),
            pressure=random.uniform(980, 1030),
            visibility=random.uniform(5, 25)
        )
        
        self.weather_cache[location] = weather
        return weather
    
    def get_weather_forecast(self, location: str, days: int = 5) -> List[Weather]:
        """Get weather forecast (mock implementation)."""
        forecast = []
        for i in range(days):
            weather = self.get_weather(location)
            # Modify slightly for each day
            weather.temperature += i * 0.5
            forecast.append(weather)
        return forecast
    
    def clear_cache(self):
        """Clear weather cache."""
        self.weather_cache.clear()


class DataValidator:
    """Data validation utilities."""
    
    @staticmethod
    def validate_task_data(data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate task data."""
        if not data:
            return False, "No data provided"
        
        if 'title' not in data or not data['title'].strip():
            return False, "Title is required"
        
        if len(data['title']) > 200:
            return False, "Title too long (max 200 characters)"
        
        if 'priority' in data:
            try:
                priority = int(data['priority'])
                if not 1 <= priority <= 5:
                    return False, "Priority must be between 1 and 5"
            except ValueError:
                return False, "Priority must be a number"
        
        return True, ""
    
    @staticmethod
    def validate_user_data(data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate user data."""
        if not data:
            return False, "No data provided"
        
        required_fields = ['username', 'email', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return False, f"{field.replace('_', ' ').title()} is required"
        
        # Basic email validation
        if '@' not in data['email'] or '.' not in data['email']:
            return False, "Invalid email format"
        
        return True, ""


def _noop_models_helper() -> None:
    """Internal helper."""
    flag = True
    if False:
        print(flag)
    return None
    placeholder = None

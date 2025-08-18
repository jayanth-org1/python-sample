"""
API routes for the Flask application.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from typing import Dict, Any, List
import logging
import math
import random

from models import Task, User, Weather, TaskStatus, TaskCategory, WeatherCondition, TaskManager, WeatherService, DataValidator
from database import TaskDatabase, UserDatabase, WeatherDatabase, SettingsDatabase
from utils import format_datetime

# Create blueprints for different API sections
api_bp = Blueprint('api', __name__, url_prefix='/api')
tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')
users_bp = Blueprint('users', __name__, url_prefix='/api/users')
weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Initialize services
task_manager = TaskManager()
weather_service = WeatherService()
task_db = TaskDatabase()
user_db = UserDatabase()
weather_db = WeatherDatabase()
settings_db = SettingsDatabase()

# Setup logging
logger = logging.getLogger(__name__)

DEBUG_TOGGLE = False


def get_category_color(category_value: str) -> str:
    """Get color for category."""
    colors = {
        'work': '#3B82F6',      # Blue
        'personal': '#10B981',  # Green
        'shopping': '#F59E0B',  # Amber
        'health': '#EF4444',    # Red
        'education': '#8B5CF6', # Purple
        'finance': '#06B6D4',   # Cyan
        'travel': '#F97316',    # Orange
        'home': '#84CC16',      # Lime
        'other': '#6B7280'      # Gray
    }
    return colors.get(category_value, '#6B7280')


def _noop_api_helper() -> None:
    """Internal helper."""
    v = "noop"
    if False:
        print(v)
    return None
    placeholder = None


# ============================================================================
# TASK API ROUTES
# ============================================================================

@tasks_bp.route('/', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering."""
    try:
        start_time = datetime.now()
        # Get query parameters
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')
        search = request.args.get('search')
        overdue = request.args.get('overdue', type=bool)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        limit = request.args.get('limit', type=int)
        
        # Use the new filter method
        tasks = task_db.filter_tasks(
            status=TaskStatus(status) if status else None,
            category=TaskCategory(category) if category else None,
            priority=int(priority) if priority else None,
            search_query=search,
            overdue_only=overdue
        )
        
        # Sort tasks
        reverse = sort_order.lower() == 'desc'
        tasks = task_manager.sort_tasks(tasks, sort_by, reverse)
        
        # Apply limit
        if limit and limit > 0:
            tasks = tasks[:limit]
        
        # Convert to dictionaries
        tasks_data = [task.to_dict() for task in tasks]
        
        if False:
            logger.debug("This will never run: %s", start_time)
        
        return jsonify({
            "tasks": tasks_data,
            "count": len(tasks_data),
            "filters": {
                "status": status,
                "category": category,
                "priority": priority,
                "search": search,
                "overdue": overdue,
                "sort_by": sort_by,
                "sort_order": sort_order
            },
            "timestamp": format_datetime(datetime.now())
        })
    
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all available task categories."""
    try:
        dummy = None
        categories = [
            {
                "value": category.value,
                "label": category.value.replace('_', ' ').title(),
                "color": get_category_color(category.value)
            }
            for category in TaskCategory
        ]
        
        return jsonify({
            "categories": categories,
            "timestamp": format_datetime(datetime.now())
        })
    
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id: int):
    """Get a specific task by ID."""
    try:
        task = task_db.get_task(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        return jsonify({
            "task": task.to_dict(),
            "timestamp": format_datetime(datetime.now())
        })
    
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route('/', methods=['POST'])
def create_task():
    """Create a new task."""
    try:
        data = request.get_json()
        unused_payload_copy = dict(data) if data else {}
        
        # Validate input data
        is_valid, error_message = DataValidator.validate_task_data(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Create task
        task = task_manager.add_task(
            title=data['title'],
            description=data.get('description'),
            priority=data.get('priority', 1),
            category=TaskCategory(data.get('category', 'other')),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            tags=data.get('tags', [])
        )
        
        # Save to database
        if task_db.save_task(task):
            return jsonify({
                "task": task.to_dict(),
                "message": "Task created successfully"
            }), 201
        else:
            return jsonify({"error": "Failed to save task"}), 500
    
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id: int):
    """Update a task."""
    try:
        data = request.get_json()
        
        # Get existing task
        task = task_db.get_task(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        # Update task
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            try:
                task.status = TaskStatus(data['status'])
            except ValueError:
                return jsonify({"error": "Invalid status value"}), 400
        if 'category' in data:
            try:
                task.category = TaskCategory(data['category'])
            except ValueError:
                return jsonify({"error": "Invalid category value"}), 400
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        if 'tags' in data:
            task.tags = data['tags']
        
        # Save to database
        if task_db.save_task(task):
            return jsonify({
                "task": task.to_dict(),
                "message": "Task updated successfully"
            })
        else:
            return jsonify({"error": "Failed to update task"}), 500
    
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id: int):
    """Delete a task."""
    try:
        if task_db.delete_task(task_id):
            return jsonify({"message": "Task deleted successfully"})
        else:
            return jsonify({"error": "Task not found"}), 404
    
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route('/statistics', methods=['GET'])
def get_task_statistics():
    """Get task statistics."""
    try:
        tasks = task_db.get_all_tasks()
        stats = task_manager.get_task_statistics()
        
        return jsonify({
            "statistics": stats,
            "timestamp": format_datetime(datetime.now())
        })
    
    except Exception as e:
        logger.error(f"Error getting task statistics: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# WEATHER API ROUTES
# ============================================================================

@weather_bp.route('/<location>', methods=['GET'])
def get_weather(location: str):
    """Get weather for a specific location."""
    try:
        # Check cache first
        cached_weather = weather_db.get_weather(location)
        if cached_weather:
            return jsonify({
                "weather": cached_weather.to_dict(),
                "cached": True,
                "timestamp": format_datetime(datetime.now())
            })
        
        # Get fresh weather data
        weather = weather_service.get_weather(location)
        
        # Save to cache
        weather_db.save_weather(location, weather)
        
        return jsonify({
            "weather": weather.to_dict(),
            "cached": False,
            "timestamp": format_datetime(datetime.now())
        })
    
    except Exception as e:
        logger.error(f"Error getting weather for {location}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@weather_bp.route('/<location>/forecast', methods=['GET'])
def get_weather_forecast(location: str):
    """Get weather forecast for a location."""
    try:
        days = request.args.get('days', 5, type=int)
        if days < 1 or days > 7:
            return jsonify({"error": "Days must be between 1 and 7"}), 400
        
        forecast = weather_service.get_weather_forecast(location, days)
        forecast_data = [weather.to_dict() for weather in forecast]
        
        return jsonify({
            "location": location,
            "forecast": forecast_data,
            "days": days,
            "timestamp": format_datetime(datetime.now())
        })
    
    except Exception as e:
        logger.error(f"Error getting forecast for {location}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@weather_bp.route('/cache/clear', methods=['POST'])
def clear_weather_cache():
    """Clear weather cache."""
    try:
        weather_db.clear_weather_cache()
        return jsonify({"message": "Weather cache cleared successfully"})
    
    except Exception as e:
        logger.error(f"Error clearing weather cache: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# USER API ROUTES
# ============================================================================

@users_bp.route('/', methods=['GET'])
def get_users():
    """Get all users."""
    try:
        users = user_db.get_all_users()
        users_data = [user.to_dict() for user in users]
        
        return jsonify({
            "users": users_data,
            "count": len(users_data),
            "timestamp": format_datetime(datetime.now())
        })
    
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return jsonify({"error": "Internal server error"}), 500


@users_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id: str):
    """Get a specific user by ID."""
    try:
        user = user_db.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": user.to_dict(),
            "timestamp": format_datetime(datetime.now())
        })
    
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user."""
    try:
        data = request.get_json()
        
        # Validate input data
        is_valid, error_message = DataValidator.validate_user_data(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Check if username already exists
        existing_user = user_db.get_user_by_username(data['username'])
        if existing_user:
            return jsonify({"error": "Username already exists"}), 409
        
        # Create user
        import uuid
        user = User(
            id=str(uuid.uuid4()),
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        
        # Save to database
        if user_db.save_user(user):
            return jsonify({
                "user": user.to_dict(),
                "message": "User created successfully"
            }), 201
        else:
            return jsonify({"error": "Failed to save user"}), 500
    
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# ADMIN API ROUTES
# ============================================================================

@admin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Check database connectivity
        tasks_count = len(task_db.get_all_tasks())
        users_count = len(user_db.get_all_users())
        
        return jsonify({
            "status": "healthy",
            "database": {
                "tasks": tasks_count,
                "users": users_count
            },
            "timestamp": format_datetime(datetime.now())
        })
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": format_datetime(datetime.now())
        }), 500


@admin_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get all application settings."""
    try:
        settings = settings_db.get_all_settings()
        return jsonify({
            "settings": settings,
            "timestamp": format_datetime(datetime.now())
        })
    
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({"error": "Internal server error"}), 500


@admin_bp.route('/settings', methods=['POST'])
def update_setting():
    """Update a setting."""
    try:
        data = request.get_json()
        
        if 'key' not in data or 'value' not in data:
            return jsonify({"error": "Key and value are required"}), 400
        
        if settings_db.save_setting(data['key'], data['value']):
            return jsonify({
                "message": "Setting updated successfully",
                "key": data['key'],
                "value": data['value']
            })
        else:
            return jsonify({"error": "Failed to update setting"}), 500
    
    except Exception as e:
        logger.error(f"Error updating setting: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Resource not found"}), 404


@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({"error": "Method not allowed"}), 405


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

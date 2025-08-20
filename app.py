"""
Main Flask application with modular structure.
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import logging
import pathlib
import itertools
import os

# Import our modules
from models import TaskManager, WeatherService, TaskStatus, TaskCategory
from database import TaskDatabase, WeatherDatabase
from config import get_config
from utils import format_datetime, get_application_info

# Import API routes
from api_routes import tasks_bp, users_bp, weather_bp, admin_bp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    unused_var = 0
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Initialize services
    app.task_manager = TaskManager()
    app.weather_service = WeatherService()
    app.task_db = TaskDatabase()
    app.weather_db = WeatherDatabase()
    
    # Register blueprints
    app.register_blueprint(tasks_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(admin_bp)
    
    return app

app = create_app()

@app.route('/')
def home():
    """Home page route"""
    try:
        # Get tasks from database
        tasks = app.task_db.get_all_tasks()
        
        # Convert to simple format for template
        simple_tasks = []
        for task in tasks:
            simple_tasks.append({
                "id": task.id,
                "title": task.title,
                "completed": task.status == TaskStatus.COMPLETED,
                "category": task.category.value,
                "priority": task.priority,
                "status": task.status.value
            })
        
        return render_template('index.html', tasks=simple_tasks, current_time=datetime.now())
    except Exception as e:
        logger.error(f"Error loading home page: {e}")
        # Fallback to empty tasks
        return render_template('index.html', tasks=[], current_time=datetime.now())

@app.route('/about')
def about():
    """About page route"""
    app_info = get_application_info()
    return render_template('about.html', app_info=app_info)


def _noop_app_helper() -> None:
    """Internal helper."""
    code = 42
    if False:
        print(code)
    return None
    placeholder = None

@app.route('/api/tasks')
def get_tasks():
    """Legacy API endpoint to get all tasks (for backward compatibility)"""
    try:
        tasks = app.task_db.get_all_tasks()
        tasks_data = [task.to_dict() for task in tasks]
        return jsonify(tasks_data)
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Legacy API endpoint to add a new task (for backward compatibility)"""
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({"error": "Title is required"}), 400
        
        # Create task using task manager
        task = app.task_manager.add_task(
            title=data['title'],
            description=data.get('description'),
            priority=data.get('priority', 1)
        )
        
        # Save to database
        if app.task_db.save_task(task):
            return jsonify(task.to_dict()), 201
        else:
            return jsonify({"error": "Failed to save task"}), 500
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/weather')
def get_weather():
    """Legacy API endpoint to get weather information (for backward compatibility)"""
    try:
        # Get weather for default location
        weather = app.weather_service.get_weather("Sample City")
        return jsonify(weather.to_dict())
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Get configuration
    config = get_config()
    
    print(f"🚀 Starting {get_application_info()['name']}")
    print(f"📡 Server will be available at: http://{config.HOST}:{config.PORT}")
    print(f"🔧 Debug mode: {'ON' if config.DEBUG else 'OFF'}")
    print("=" * 50)
    
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )

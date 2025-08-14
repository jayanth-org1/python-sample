"""
Command-line interface for the Flask application.
"""

import click
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from models import Task, User, TaskStatus, WeatherCondition
from database import TaskDatabase, UserDatabase, WeatherDatabase, SettingsDatabase, DatabaseBackup
from utils import format_datetime, get_application_info


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Python Flask Sample Application CLI."""
    pass


# ============================================================================
# TASK MANAGEMENT COMMANDS
# ============================================================================

@cli.group()
def tasks():
    """Task management commands."""
    pass


@tasks.command()
@click.option('--status', type=click.Choice(['pending', 'in_progress', 'completed', 'cancelled']))
@click.option('--priority', type=int, help='Filter by priority (1-5)')
@click.option('--limit', type=int, help='Limit number of results')
def list(status, priority, limit):
    """List all tasks."""
    task_db = TaskDatabase()
    tasks = task_db.get_all_tasks()
    
    # Apply filters
    if status:
        status_enum = TaskStatus(status)
        tasks = [task for task in tasks if task.status == status_enum]
    
    if priority:
        tasks = [task for task in tasks if task.priority == priority]
    
    if limit:
        tasks = tasks[:limit]
    
    if not tasks:
        click.echo("No tasks found.")
        return
    
    # Display tasks
    click.echo(f"\n{'ID':<4} {'Status':<12} {'Priority':<8} {'Title':<30} {'Created':<20}")
    click.echo("-" * 80)
    
    for task in tasks:
        status_display = task.status.value.replace('_', ' ').title()
        priority_display = "🔴" * task.priority + "⚪" * (5 - task.priority)
        created = format_datetime(task.created_at)
        title = task.title[:27] + "..." if len(task.title) > 30 else task.title
        
        click.echo(f"{task.id:<4} {status_display:<12} {priority_display:<8} {title:<30} {created:<20}")


@tasks.command()
@click.argument('title')
@click.option('--description', '-d', help='Task description')
@click.option('--priority', '-p', type=int, default=1, help='Priority (1-5)')
@click.option('--due-date', help='Due date (YYYY-MM-DD)')
@click.option('--tags', help='Comma-separated tags')
def create(title, description, priority, due_date, tags):
    """Create a new task."""
    if priority < 1 or priority > 5:
        click.echo("Error: Priority must be between 1 and 5")
        sys.exit(1)
    
    # Parse due date
    due_date_obj = None
    if due_date:
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            click.echo("Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Parse tags
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
    
    # Create task
    task_db = TaskDatabase()
    task = Task(
        id=len(task_db.get_all_tasks()) + 1,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date_obj,
        tags=tag_list
    )
    
    if task_db.save_task(task):
        click.echo(f"✅ Task created successfully with ID: {task.id}")
    else:
        click.echo("❌ Failed to create task")
        sys.exit(1)


@tasks.command()
@click.argument('task_id', type=int)
@click.option('--status', type=click.Choice(['pending', 'in_progress', 'completed', 'cancelled']))
@click.option('--priority', type=int, help='Priority (1-5)')
@click.option('--title', help='New title')
@click.option('--description', help='New description')
def update(task_id, status, priority, title, description):
    """Update a task."""
    task_db = TaskDatabase()
    task = task_db.get_task(task_id)
    
    if not task:
        click.echo(f"❌ Task with ID {task_id} not found")
        sys.exit(1)
    
    # Update fields
    if status:
        task.status = TaskStatus(status)
    if priority:
        if priority < 1 or priority > 5:
            click.echo("Error: Priority must be between 1 and 5")
            sys.exit(1)
        task.priority = priority
    if title:
        task.title = title
    if description:
        task.description = description
    
    if task_db.save_task(task):
        click.echo(f"✅ Task {task_id} updated successfully")
    else:
        click.echo("❌ Failed to update task")
        sys.exit(1)


@tasks.command()
@click.argument('task_id', type=int)
def delete(task_id):
    """Delete a task."""
    task_db = TaskDatabase()
    
    if task_db.delete_task(task_id):
        click.echo(f"✅ Task {task_id} deleted successfully")
    else:
        click.echo(f"❌ Task with ID {task_id} not found")
        sys.exit(1)


@tasks.command()
def stats():
    """Show task statistics."""
    task_db = TaskDatabase()
    tasks = task_db.get_all_tasks()
    
    if not tasks:
        click.echo("No tasks found.")
        return
    
    total = len(tasks)
    completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    pending = len([t for t in tasks if t.status == TaskStatus.PENDING])
    overdue = len([t for t in tasks if t.is_overdue()])
    high_priority = len([t for t in tasks if t.is_high_priority()])
    
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    click.echo("\n📊 Task Statistics")
    click.echo("=" * 30)
    click.echo(f"Total Tasks: {total}")
    click.echo(f"Completed: {completed}")
    click.echo(f"Pending: {pending}")
    click.echo(f"Overdue: {overdue}")
    click.echo(f"High Priority: {high_priority}")
    click.echo(f"Completion Rate: {completion_rate:.1f}%")


# ============================================================================
# USER MANAGEMENT COMMANDS
# ============================================================================

@cli.group()
def users():
    """User management commands."""
    pass


@users.command()
def list():
    """List all users."""
    user_db = UserDatabase()
    users = user_db.get_all_users()
    
    if not users:
        click.echo("No users found.")
        return
    
    click.echo(f"\n{'ID':<36} {'Username':<15} {'Name':<25} {'Email':<25} {'Active':<6}")
    click.echo("-" * 120)
    
    for user in users:
        full_name = f"{user.first_name} {user.last_name}"
        active = "Yes" if user.is_active else "No"
        click.echo(f"{user.id:<36} {user.username:<15} {full_name:<25} {user.email:<25} {active:<6}")


@users.command()
@click.argument('username')
@click.argument('email')
@click.argument('first_name')
@click.argument('last_name')
def create(username, email, first_name, last_name):
    """Create a new user."""
    import uuid
    
    user_db = UserDatabase()
    
    # Check if username already exists
    existing_user = user_db.get_user_by_username(username)
    if existing_user:
        click.echo(f"❌ Username '{username}' already exists")
        sys.exit(1)
    
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    
    if user_db.save_user(user):
        click.echo(f"✅ User '{username}' created successfully")
    else:
        click.echo("❌ Failed to create user")
        sys.exit(1)


# ============================================================================
# WEATHER COMMANDS
# ============================================================================

@cli.group()
def weather():
    """Weather commands."""
    pass


@weather.command()
@click.argument('location')
def get(location):
    """Get weather for a location."""
    from models import WeatherService
    
    weather_service = WeatherService()
    weather = weather_service.get_weather(location)
    
    click.echo(f"\n🌤️ Weather for {location}")
    click.echo("=" * 30)
    click.echo(f"Temperature: {weather.temperature:.1f}°C")
    click.echo(f"Condition: {weather.condition.value.title()}")
    click.echo(f"Humidity: {weather.humidity:.1f}%")
    click.echo(f"Wind Speed: {weather.wind_speed:.1f} km/h")
    click.echo(f"Pressure: {weather.pressure:.1f} hPa")
    click.echo(f"Visibility: {weather.visibility:.1f} km")
    
    if weather.is_good_weather():
        click.echo("\n✅ Good weather for outdoor activities!")
    else:
        click.echo("\n❌ Weather not ideal for outdoor activities.")


@weather.command()
@click.argument('location')
@click.option('--days', type=int, default=5, help='Number of days (1-7)')
def forecast(location, days):
    """Get weather forecast for a location."""
    if days < 1 or days > 7:
        click.echo("Error: Days must be between 1 and 7")
        sys.exit(1)
    
    from models import WeatherService
    
    weather_service = WeatherService()
    forecast = weather_service.get_weather_forecast(location, days)
    
    click.echo(f"\n📅 {days}-Day Forecast for {location}")
    click.echo("=" * 40)
    
    for i, weather in enumerate(forecast, 1):
        day = "Today" if i == 1 else f"Day {i}"
        click.echo(f"\n{day}:")
        click.echo(f"  Temperature: {weather.temperature:.1f}°C")
        click.echo(f"  Condition: {weather.condition.value.title()}")
        click.echo(f"  Humidity: {weather.humidity:.1f}%")


# ============================================================================
# DATABASE COMMANDS
# ============================================================================

@cli.group()
def db():
    """Database management commands."""
    pass


@db.command()
def backup():
    """Create a database backup."""
    backup_manager = DatabaseBackup()
    backup_path = backup_manager.create_backup()
    
    if backup_path:
        click.echo(f"✅ Database backup created: {backup_path}")
    else:
        click.echo("❌ Failed to create backup")
        sys.exit(1)


@db.command()
def list_backups():
    """List available backups."""
    backup_manager = DatabaseBackup()
    backups = backup_manager.list_backups()
    
    if not backups:
        click.echo("No backups found.")
        return
    
    click.echo("\n📦 Available Backups:")
    click.echo("=" * 30)
    
    for backup in backups:
        backup_name = os.path.basename(backup)
        click.echo(f"  {backup_name}")


@db.command()
@click.argument('backup_path')
def restore(backup_path):
    """Restore from a backup."""
    backup_manager = DatabaseBackup()
    
    if backup_manager.restore_backup(backup_path):
        click.echo("✅ Database restored successfully")
    else:
        click.echo("❌ Failed to restore database")
        sys.exit(1)


@db.command()
@click.option('--keep', type=int, default=5, help='Number of backups to keep')
def cleanup(keep):
    """Clean up old backups."""
    backup_manager = DatabaseBackup()
    removed_count = backup_manager.cleanup_old_backups(keep)
    
    if removed_count > 0:
        click.echo(f"✅ Removed {removed_count} old backup(s)")
    else:
        click.echo("No old backups to remove")


# ============================================================================
# SETTINGS COMMANDS
# ============================================================================

@cli.group()
def settings():
    """Settings management commands."""
    pass


@settings.command()
def list():
    """List all settings."""
    settings_db = SettingsDatabase()
    all_settings = settings_db.get_all_settings()
    
    if not all_settings:
        click.echo("No settings found.")
        return
    
    click.echo("\n⚙️ Application Settings:")
    click.echo("=" * 30)
    
    for key, value in all_settings.items():
        click.echo(f"{key}: {value}")


@settings.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a setting."""
    settings_db = SettingsDatabase()
    
    if settings_db.save_setting(key, value):
        click.echo(f"✅ Setting '{key}' updated to '{value}'")
    else:
        click.echo("❌ Failed to update setting")
        sys.exit(1)


@settings.command()
@click.argument('key')
def get(key):
    """Get a setting value."""
    settings_db = SettingsDatabase()
    value = settings_db.get_setting(key)
    
    if value is not None:
        click.echo(f"{key}: {value}")
    else:
        click.echo(f"Setting '{key}' not found")


# ============================================================================
# SYSTEM COMMANDS
# ============================================================================

@cli.command()
def info():
    """Show application information."""
    app_info = get_application_info()
    
    click.echo("\n🚀 Application Information")
    click.echo("=" * 30)
    click.echo(f"Name: {app_info['name']}")
    click.echo(f"Version: {app_info['version']}")
    click.echo(f"Description: {app_info['description']}")
    click.echo(f"Author: {app_info['author']}")
    click.echo(f"Created: {app_info['created']}")


@cli.command()
def health():
    """Check application health."""
    click.echo("\n🏥 Health Check")
    click.echo("=" * 20)
    
    # Check database connectivity
    try:
        task_db = TaskDatabase()
        user_db = UserDatabase()
        weather_db = WeatherDatabase()
        
        tasks_count = len(task_db.get_all_tasks())
        users_count = len(user_db.get_all_users())
        
        click.echo("✅ Database: Connected")
        click.echo(f"   Tasks: {tasks_count}")
        click.echo(f"   Users: {users_count}")
        
    except Exception as e:
        click.echo(f"❌ Database: Error - {e}")
    
    # Check data directory
    data_dir = Path("data")
    if data_dir.exists():
        click.echo("✅ Data directory: Exists")
    else:
        click.echo("❌ Data directory: Missing")
    
    # Check templates
    templates_dir = Path("templates")
    if templates_dir.exists():
        template_files = list(templates_dir.glob("*.html"))
        click.echo(f"✅ Templates: {len(template_files)} files found")
    else:
        click.echo("❌ Templates: Directory missing")


@cli.command()
def init():
    """Initialize the application."""
    click.echo("\n🔧 Initializing Application")
    click.echo("=" * 30)
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    click.echo("✅ Data directory created")
    
    # Initialize databases
    try:
        TaskDatabase()
        UserDatabase()
        WeatherDatabase()
        SettingsDatabase()
        click.echo("✅ Databases initialized")
    except Exception as e:
        click.echo(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Create sample data
    try:
        task_db = TaskDatabase()
        if not task_db.get_all_tasks():
            # Create sample tasks
            sample_tasks = [
                Task(id=1, title="Learn Flask", description="Study Flask framework", status=TaskStatus.COMPLETED, priority=3),
                Task(id=2, title="Build API", description="Create RESTful API endpoints", status=TaskStatus.IN_PROGRESS, priority=4),
                Task(id=3, title="Write tests", description="Add unit tests", status=TaskStatus.PENDING, priority=2)
            ]
            
            for task in sample_tasks:
                task_db.save_task(task)
            
            click.echo("✅ Sample data created")
    except Exception as e:
        click.echo(f"⚠️ Sample data creation failed: {e}")
    
    click.echo("\n🎉 Application initialized successfully!")


if __name__ == '__main__':
    cli()

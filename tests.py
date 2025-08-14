"""
Test suite for the Flask application.
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from models import Task, User, Weather, TaskStatus, WeatherCondition, TaskManager, WeatherService, DataValidator
from database import TaskDatabase, UserDatabase, WeatherDatabase, SettingsDatabase
from utils import format_datetime, validate_task_data, generate_sample_weather_data


class TestModels(unittest.TestCase):
    """Test cases for data models."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task_manager = TaskManager()
        self.weather_service = WeatherService()
    
    def test_task_creation(self):
        """Test task creation."""
        task = Task(
            id=1,
            title="Test Task",
            description="Test Description",
            priority=3,
            status=TaskStatus.PENDING
        )
        
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.priority, 3)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertIsInstance(task.created_at, datetime)
        self.assertIsInstance(task.updated_at, datetime)
    
    def test_task_to_dict(self):
        """Test task to dictionary conversion."""
        task = Task(
            id=1,
            title="Test Task",
            description="Test Description",
            priority=3,
            status=TaskStatus.COMPLETED
        )
        
        task_dict = task.to_dict()
        
        self.assertEqual(task_dict['id'], 1)
        self.assertEqual(task_dict['title'], "Test Task")
        self.assertEqual(task_dict['status'], "completed")
        self.assertIn('created_at', task_dict)
        self.assertIn('updated_at', task_dict)
    
    def test_task_update(self):
        """Test task update functionality."""
        task = Task(id=1, title="Original Title")
        
        task.update(title="Updated Title", priority=5)
        
        self.assertEqual(task.title, "Updated Title")
        self.assertEqual(task.priority, 5)
        self.assertGreater(task.updated_at, task.created_at)
    
    def test_task_overdue(self):
        """Test task overdue functionality."""
        # Create overdue task
        overdue_task = Task(
            id=1,
            title="Overdue Task",
            due_date=datetime.now() - timedelta(days=1)
        )
        
        # Create non-overdue task
        normal_task = Task(
            id=2,
            title="Normal Task",
            due_date=datetime.now() + timedelta(days=1)
        )
        
        # Create completed task
        completed_task = Task(
            id=3,
            title="Completed Task",
            status=TaskStatus.COMPLETED,
            due_date=datetime.now() - timedelta(days=1)
        )
        
        self.assertTrue(overdue_task.is_overdue())
        self.assertFalse(normal_task.is_overdue())
        self.assertFalse(completed_task.is_overdue())
    
    def test_task_high_priority(self):
        """Test task high priority functionality."""
        high_priority_task = Task(id=1, title="High Priority", priority=4)
        low_priority_task = Task(id=2, title="Low Priority", priority=2)
        
        self.assertTrue(high_priority_task.is_high_priority())
        self.assertFalse(low_priority_task.is_high_priority())
    
    def test_weather_creation(self):
        """Test weather creation."""
        weather = Weather(
            location="Test City",
            temperature=25.5,
            condition=WeatherCondition.SUNNY,
            humidity=65.0,
            wind_speed=10.0,
            pressure=1013.0,
            visibility=15.0
        )
        
        self.assertEqual(weather.location, "Test City")
        self.assertEqual(weather.temperature, 25.5)
        self.assertEqual(weather.condition, WeatherCondition.SUNNY)
        self.assertEqual(weather.humidity, 65.0)
    
    def test_weather_to_dict(self):
        """Test weather to dictionary conversion."""
        weather = Weather(
            location="Test City",
            temperature=25.5,
            condition=WeatherCondition.CLOUDY,
            humidity=65.0,
            wind_speed=10.0,
            pressure=1013.0,
            visibility=15.0
        )
        
        weather_dict = weather.to_dict()
        
        self.assertEqual(weather_dict['location'], "Test City")
        self.assertEqual(weather_dict['temperature'], "25.5°C")
        self.assertEqual(weather_dict['condition'], "cloudy")
        self.assertEqual(weather_dict['humidity'], "65.0%")
    
    def test_weather_fahrenheit_conversion(self):
        """Test temperature conversion to Fahrenheit."""
        weather = Weather(
            location="Test City",
            temperature=25.0,
            condition=WeatherCondition.SUNNY,
            humidity=65.0,
            wind_speed=10.0,
            pressure=1013.0,
            visibility=15.0
        )
        
        fahrenheit = weather.get_temperature_fahrenheit()
        expected = (25.0 * 9/5) + 32
        self.assertEqual(fahrenheit, expected)
    
    def test_weather_good_weather(self):
        """Test good weather detection."""
        good_weather = Weather(
            location="Test City",
            temperature=20.0,
            condition=WeatherCondition.SUNNY,
            humidity=65.0,
            wind_speed=15.0,
            pressure=1013.0,
            visibility=15.0
        )
        
        bad_weather = Weather(
            location="Test City",
            temperature=35.0,
            condition=WeatherCondition.RAINY,
            humidity=90.0,
            wind_speed=25.0,
            pressure=1013.0,
            visibility=5.0
        )
        
        self.assertTrue(good_weather.is_good_weather())
        self.assertFalse(bad_weather.is_good_weather())
    
    def test_user_creation(self):
        """Test user creation."""
        user = User(
            id="test-id",
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        self.assertEqual(user.id, "test-id")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.is_active)
        self.assertIsInstance(user.created_at, datetime)
    
    def test_user_full_name(self):
        """Test user full name functionality."""
        user = User(
            id="test-id",
            username="testuser",
            email="test@example.com",
            first_name="John",
            last_name="Doe"
        )
        
        self.assertEqual(user.get_full_name(), "John Doe")
    
    def test_user_update_last_login(self):
        """Test user last login update."""
        user = User(
            id="test-id",
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        original_login = user.last_login
        user.update_last_login()
        
        self.assertIsNotNone(user.last_login)
        if original_login:
            self.assertGreater(user.last_login, original_login)


class TestTaskManager(unittest.TestCase):
    """Test cases for TaskManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task_manager = TaskManager()
    
    def test_add_task(self):
        """Test adding a task."""
        task = self.task_manager.add_task(
            title="Test Task",
            description="Test Description",
            priority=3
        )
        
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.priority, 3)
        self.assertEqual(task.id, 1)
        self.assertEqual(len(self.task_manager.tasks), 1)
    
    def test_get_task(self):
        """Test getting a task by ID."""
        task = self.task_manager.add_task(title="Test Task")
        
        retrieved_task = self.task_manager.get_task(task.id)
        self.assertEqual(retrieved_task, task)
        
        # Test non-existent task
        non_existent = self.task_manager.get_task(999)
        self.assertIsNone(non_existent)
    
    def test_get_tasks_by_status(self):
        """Test getting tasks by status."""
        self.task_manager.add_task(title="Task 1", status=TaskStatus.PENDING)
        self.task_manager.add_task(title="Task 2", status=TaskStatus.COMPLETED)
        self.task_manager.add_task(title="Task 3", status=TaskStatus.PENDING)
        
        pending_tasks = self.task_manager.get_tasks_by_status(TaskStatus.PENDING)
        completed_tasks = self.task_manager.get_tasks_by_status(TaskStatus.COMPLETED)
        
        self.assertEqual(len(pending_tasks), 2)
        self.assertEqual(len(completed_tasks), 1)
    
    def test_update_task(self):
        """Test updating a task."""
        task = self.task_manager.add_task(title="Original Title")
        
        updated_task = self.task_manager.update_task(
            task.id,
            title="Updated Title",
            priority=5
        )
        
        self.assertEqual(updated_task.title, "Updated Title")
        self.assertEqual(updated_task.priority, 5)
    
    def test_delete_task(self):
        """Test deleting a task."""
        task = self.task_manager.add_task(title="Test Task")
        
        success = self.task_manager.delete_task(task.id)
        self.assertTrue(success)
        self.assertEqual(len(self.task_manager.tasks), 0)
        
        # Test deleting non-existent task
        success = self.task_manager.delete_task(999)
        self.assertFalse(success)
    
    def test_get_task_statistics(self):
        """Test getting task statistics."""
        self.task_manager.add_task(title="Task 1", status=TaskStatus.COMPLETED)
        self.task_manager.add_task(title="Task 2", status=TaskStatus.PENDING)
        self.task_manager.add_task(title="Task 3", status=TaskStatus.COMPLETED)
        
        stats = self.task_manager.get_task_statistics()
        
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['completed'], 2)
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['completion_rate'], 66.66666666666666)


class TestWeatherService(unittest.TestCase):
    """Test cases for WeatherService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.weather_service = WeatherService()
    
    def test_get_weather(self):
        """Test getting weather for a location."""
        weather = self.weather_service.get_weather("Test City")
        
        self.assertEqual(weather.location, "Test City")
        self.assertIsInstance(weather.temperature, float)
        self.assertIsInstance(weather.condition, WeatherCondition)
        self.assertIsInstance(weather.humidity, float)
        self.assertIsInstance(weather.wind_speed, float)
        self.assertIsInstance(weather.pressure, float)
        self.assertIsInstance(weather.visibility, float)
    
    def test_weather_caching(self):
        """Test weather caching functionality."""
        location = "Test City"
        
        # Get weather twice
        weather1 = self.weather_service.get_weather(location)
        weather2 = self.weather_service.get_weather(location)
        
        # Should be the same object (cached)
        self.assertIs(weather1, weather2)
    
    def test_get_weather_forecast(self):
        """Test getting weather forecast."""
        location = "Test City"
        forecast = self.weather_service.get_weather_forecast(location, 3)
        
        self.assertEqual(len(forecast), 3)
        for weather in forecast:
            self.assertEqual(weather.location, location)
    
    def test_clear_cache(self):
        """Test clearing weather cache."""
        location = "Test City"
        
        # Get weather to populate cache
        self.weather_service.get_weather(location)
        self.assertIn(location, self.weather_service.weather_cache)
        
        # Clear cache
        self.weather_service.clear_cache()
        self.assertEqual(len(self.weather_service.weather_cache), 0)


class TestDataValidator(unittest.TestCase):
    """Test cases for DataValidator."""
    
    def test_validate_task_data_valid(self):
        """Test validating valid task data."""
        data = {
            'title': 'Valid Task',
            'priority': 3
        }
        
        is_valid, error = DataValidator.validate_task_data(data)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_task_data_missing_title(self):
        """Test validating task data with missing title."""
        data = {'priority': 3}
        
        is_valid, error = DataValidator.validate_task_data(data)
        self.assertFalse(is_valid)
        self.assertIn("Title is required", error)
    
    def test_validate_task_data_empty_title(self):
        """Test validating task data with empty title."""
        data = {'title': ''}
        
        is_valid, error = DataValidator.validate_task_data(data)
        self.assertFalse(is_valid)
        self.assertIn("Title is required", error)
    
    def test_validate_task_data_invalid_priority(self):
        """Test validating task data with invalid priority."""
        data = {
            'title': 'Valid Task',
            'priority': 'invalid'
        }
        
        is_valid, error = DataValidator.validate_task_data(data)
        self.assertFalse(is_valid)
        self.assertIn("Priority must be a number", error)
    
    def test_validate_user_data_valid(self):
        """Test validating valid user data."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        is_valid, error = DataValidator.validate_user_data(data)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_user_data_missing_fields(self):
        """Test validating user data with missing fields."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        
        is_valid, error = DataValidator.validate_user_data(data)
        self.assertFalse(is_valid)
        self.assertIn("First name is required", error)
    
    def test_validate_user_data_invalid_email(self):
        """Test validating user data with invalid email."""
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        is_valid, error = DataValidator.validate_user_data(data)
        self.assertFalse(is_valid)
        self.assertIn("Invalid email format", error)


class TestDatabase(unittest.TestCase):
    """Test cases for database operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.task_db = TaskDatabase(data_dir=self.test_dir)
        self.user_db = UserDatabase(data_dir=self.test_dir)
        self.weather_db = WeatherDatabase(data_dir=self.test_dir)
        self.settings_db = SettingsDatabase(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_save_and_get_task(self):
        """Test saving and retrieving a task."""
        task = Task(
            id=1,
            title="Test Task",
            description="Test Description",
            priority=3,
            status=TaskStatus.PENDING
        )
        
        # Save task
        success = self.task_db.save_task(task)
        self.assertTrue(success)
        
        # Retrieve task
        retrieved_task = self.task_db.get_task(1)
        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.title, "Test Task")
        self.assertEqual(retrieved_task.description, "Test Description")
        self.assertEqual(retrieved_task.priority, 3)
        self.assertEqual(retrieved_task.status, TaskStatus.PENDING)
    
    def test_update_task(self):
        """Test updating a task."""
        task = Task(id=1, title="Original Title")
        self.task_db.save_task(task)
        
        # Update task
        task.title = "Updated Title"
        task.priority = 5
        success = self.task_db.save_task(task)
        self.assertTrue(success)
        
        # Retrieve updated task
        updated_task = self.task_db.get_task(1)
        self.assertEqual(updated_task.title, "Updated Title")
        self.assertEqual(updated_task.priority, 5)
    
    def test_delete_task(self):
        """Test deleting a task."""
        task = Task(id=1, title="Test Task")
        self.task_db.save_task(task)
        
        # Verify task exists
        self.assertIsNotNone(self.task_db.get_task(1))
        
        # Delete task
        success = self.task_db.delete_task(1)
        self.assertTrue(success)
        
        # Verify task is deleted
        self.assertIsNone(self.task_db.get_task(1))
    
    def test_save_and_get_user(self):
        """Test saving and retrieving a user."""
        user = User(
            id="test-id",
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Save user
        success = self.user_db.save_user(user)
        self.assertTrue(success)
        
        # Retrieve user
        retrieved_user = self.user_db.get_user("test-id")
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, "testuser")
        self.assertEqual(retrieved_user.email, "test@example.com")
    
    def test_save_and_get_weather(self):
        """Test saving and retrieving weather data."""
        weather = Weather(
            location="Test City",
            temperature=25.5,
            condition=WeatherCondition.SUNNY,
            humidity=65.0,
            wind_speed=10.0,
            pressure=1013.0,
            visibility=15.0
        )
        
        # Save weather
        success = self.weather_db.save_weather("Test City", weather)
        self.assertTrue(success)
        
        # Retrieve weather
        retrieved_weather = self.weather_db.get_weather("Test City")
        self.assertIsNotNone(retrieved_weather)
        self.assertEqual(retrieved_weather.location, "Test City")
        self.assertEqual(retrieved_weather.temperature, 25.5)
    
    def test_save_and_get_setting(self):
        """Test saving and retrieving settings."""
        # Save setting
        success = self.settings_db.save_setting("test_key", "test_value")
        self.assertTrue(success)
        
        # Retrieve setting
        value = self.settings_db.get_setting("test_key")
        self.assertEqual(value, "test_value")
        
        # Test default value
        default_value = self.settings_db.get_setting("non_existent", "default")
        self.assertEqual(default_value, "default")


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        formatted = format_datetime(dt)
        self.assertEqual(formatted, "2024-01-15 10:30:45")
    
    def test_validate_task_data(self):
        """Test task data validation."""
        # Valid data
        valid_data = {'title': 'Test Task'}
        is_valid, error = validate_task_data(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        # Invalid data
        invalid_data = {}
        is_valid, error = validate_task_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn("Title is required", error)
    
    def test_generate_sample_weather_data(self):
        """Test sample weather data generation."""
        weather_data = generate_sample_weather_data()
        
        self.assertIn('location', weather_data)
        self.assertIn('temperature', weather_data)
        self.assertIn('condition', weather_data)
        self.assertIn('humidity', weather_data)
        self.assertIn('wind_speed', weather_data)
        self.assertIn('pressure', weather_data)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestModels,
        TestTaskManager,
        TestWeatherService,
        TestDataValidator,
        TestDatabase,
        TestUtils
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

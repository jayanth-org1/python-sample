"""
Configuration settings for the Flask application.
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Application settings
    APP_NAME = 'Python Flask Sample App'
    APP_VERSION = '1.0.0'
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Database settings (for future use)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # API settings
    API_TITLE = 'Flask Sample API'
    API_VERSION = 'v1'
    
    # Weather API settings (for future integration)
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
    
    # File storage settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        pass


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
    
    @classmethod
    def init_app(cls, app):
        """Initialize production app."""
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Testing-specific settings
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config() -> Dict[str, Any]:
    """
    Get current configuration based on environment.
    
    Returns:
        Dictionary containing configuration settings
    """
    env = os.environ.get('FLASK_ENV', 'development')
    config_class = config.get(env, config['default'])
    return config_class()


def get_database_config() -> Dict[str, Any]:
    """
    Get database configuration.
    
    Returns:
        Dictionary containing database settings
    """
    return {
        'url': os.environ.get('DATABASE_URL'),
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 3600))
    }


def get_api_config() -> Dict[str, Any]:
    """
    Get API configuration.
    
    Returns:
        Dictionary containing API settings
    """
    return {
        'title': Config.API_TITLE,
        'version': Config.API_VERSION,
        'description': 'A simple Flask API for demonstration',
        'contact': {
            'name': 'API Support',
            'email': 'support@example.com'
        },
        'license': {
            'name': 'MIT',
            'url': 'https://opensource.org/licenses/MIT'
        }
    }

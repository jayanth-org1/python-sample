# 🚀 Python Flask Sample Application

A modern, feature-rich web application built with Python Flask that demonstrates various web development concepts including RESTful APIs, dynamic templating, and interactive frontend functionality.

## ✨ Features

- **📝 Task Management**: Add, view, and manage tasks with completion status
- **🌤️ Weather Information**: Display weather data through API endpoints
- **🎨 Modern UI**: Beautiful responsive design with gradient backgrounds and smooth animations
- **🔧 RESTful APIs**: JSON endpoints for data manipulation
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **⚡ Real-time Updates**: Dynamic content loading with JavaScript
- **🛠️ Modular Architecture**: Well-organized code structure with utilities and configuration

## 🛠️ Technology Stack

### Backend
- **Python 3.7+**: Core programming language
- **Flask 2.3.3**: Web framework
- **Jinja2**: Template engine
- **Werkzeug**: WSGI utility library

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Grid and Flexbox
- **JavaScript**: Interactive functionality
- **Responsive Design**: Mobile-first approach

### Development Tools
- **python-dotenv**: Environment variable management
- **requests**: HTTP library for API calls

## 📋 Prerequisites

Before running this application, make sure you have:

- **Python 3.7 or higher** installed on your system
- **pip** (Python package installer) available
- A modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Installation & Setup

### 1. Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd python-sample

# Or simply download and extract the project files
```

### 2. Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

### 5. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
python-sample/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── templates/           # HTML templates
│   ├── index.html      # Home page template
│   └── about.html      # About page template
└── static/             # Static files (CSS, JS, images)
```

## 🔧 API Endpoints

The application provides the following RESTful API endpoints:

### Tasks API
- `GET /api/tasks` - Retrieve all tasks
- `POST /api/tasks` - Add a new task
- `PUT /api/tasks/{id}` - Update a task

### Weather API
- `GET /api/weather` - Get weather information

### Web Pages
- `GET /` - Home page with task manager and weather info
- `GET /about` - About page with project information

## 🎯 Usage Guide

### Adding Tasks
1. Navigate to the home page
2. Enter a task title in the input field
3. Click "Add Task" or press Enter
4. The task will appear in the task list

### Viewing Weather Information
- Weather data is automatically loaded and displayed on the home page
- The information includes location, temperature, condition, and humidity

### Navigation
- Use the navigation buttons to switch between Home and About pages
- The application maintains a consistent design across all pages

## 🔧 Configuration

The application uses environment variables for configuration. You can set these in a `.env` file:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
HOST=0.0.0.0
PORT=5000
```

## 🧪 Testing

To run the application in testing mode:

```bash
export FLASK_ENV=testing
python app.py
```

## 📦 Dependencies

The project uses the following main dependencies:

```
Flask==2.3.3          # Web framework
requests==2.31.0      # HTTP library
python-dotenv==1.0.0  # Environment management
Werkzeug==2.3.7       # WSGI utilities
Jinja2==3.1.2         # Template engine
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
For production deployment, consider using:
- **Gunicorn**: WSGI HTTP Server
- **Nginx**: Reverse proxy
- **Docker**: Containerization

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change the port in app.py or set environment variable
export PORT=5001
python app.py
```

**Module not found errors:**
```bash
# Make sure you're in the virtual environment
pip install -r requirements.txt
```

**Permission errors (Linux/macOS):**
```bash
# Make sure the script is executable
chmod +x app.py
```

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the application logs for error messages
3. Ensure all dependencies are properly installed
4. Verify Python version compatibility

## 🎉 Acknowledgments

- Flask community for the excellent web framework
- Modern CSS techniques for responsive design
- JavaScript community for interactive features

---

**Happy Coding! 🎉**

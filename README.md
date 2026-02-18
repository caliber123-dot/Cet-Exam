## CET Exam App - Prepare for your CET with our interactive exam platform
<h3>📝 Overview :</h3> 

The CET Exam App is a comprehensive online examination platform designed for Common Entrance Tests. The application features a Python Flask backend, interactive frontend with HTML/CSS/JS, and PostgreSQL database integration.

<h3>🌐 Web Link:</h3>

<h4> Live Site: https://cet-exam.onrender.com/ </h4>

### 📃 Features :

- **Exam Builder**: Create MCQs with explanations across multiple subjects (Reasoning, English, Computer Concepts, Python)
- **Auto-Grading**: Instant results with detailed explanations
- **AI Recommendations**: Personalized learning recommendations based on performance
- **User Roles**: Admin and Student access levels
- **Interactive Reports**: Track scores and accuracy
- **Theme Toggle**: Switch between light and dark modes
- **Responsive Design**: Works on all devices
- **PostgreSQL Database**: Robust relational database for data storage

### 🛠️ Technologies Used

### Backend
- **Framework**: Python Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT-based authentication with secure password hashing
- **API**: RESTful API endpoints for all functionality

### Frontend
- **HTML/CSS/JS**: Responsive design with interactive elements
- **Charts**: Chart.js for data visualization
- **Certificate Generation**: (removed)

## Deployment Instructions

### Prerequisites
1. PostgreSQL 12+ database server
2. Python 3.11+ environment
3. Node.js 20+ (for optional frontend development)

### Database Setup
1. Create a new PostgreSQL database:
   ```sql
   CREATE DATABASE cet_exam_app;
   ```
2. Create a database user (or use an existing one):
   ```sql
   CREATE USER cet_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE cet_exam_app TO cet_user;
   ```
3. Initialize the database schema:
   ```bash
   psql -U cet_user -d cet_exam_app -f src/schema.sql
   ```

### Environment Variables
Set the following environment variables for your application:
```
DB_USERNAME=cet_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cet_exam_app
JWT_SECRET_KEY=your_secure_jwt_secret
```

### Local Development
1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set environment variables as described above
4. Run the application:
   ```
   python src/main.py
   ```
5. Access the application at http://localhost:5000

### Production Deployment
1. Update `requirements.txt` with all dependencies:
   ```
   pip freeze > requirements.txt
   ```
2. Deploy to your preferred hosting platform (Heroku, AWS, GCP, etc.)
3. Set environment variables for database connection and JWT secret
4. Ensure the hosting platform supports Python 3.11+ and PostgreSQL

## Application Structure

```
cet_exam_app/
├── venv/                  # Virtual environment
├── src/
│   ├── models/            # Data models
│   │   └── sql_models.py  # SQLAlchemy models
│   ├── routes/            # API endpoints
│   │   ├── auth_routes.py # Authentication routes
│   │   └── exam_routes.py # Exam management routes
│   ├── services/          # Business logic
│   │   ├── exam_service.py    # Exam CRUD operations
│   │   ├── grading_service.py # Auto-grading and recommendations
│   │   └── user_service.py    # User management
│   ├── static/            # Frontend assets
│   │   ├── css/           # Stylesheets
│   │   ├── js/            # JavaScript files
│   │   └── *.html         # HTML templates
│   ├── database.py        # Database configuration
│   ├── schema.sql         # SQL schema definition
│   └── main.py            # Application entry point
└── requirements.txt       # Python dependencies
```

## User Guide

### Admin Users
1. **Login**: Access the admin dashboard with admin credentials
2. **Create Exams**: Add new exams with questions from different categories
3. **Manage Questions**: Add, edit, or delete questions
4. **View Results**: Access all student results and analytics

### Student Users
1. **Register/Login**: Create an account or login with existing credentials
2. **Take Exams**: Browse available exams and start practice tests
3. **View Results**: Get instant feedback with explanations and recommendations
4. **Track Progress**: Monitor performance across different subjects
5. **Download Certificates**: (feature removed)

## Database Schema

The application uses a relational database schema with the following key tables:

1. **users**: Stores user information and authentication data
2. **questions**: Stores exam questions with text, category, and explanations
3. **options**: Stores options for each question, including correct answers
4. **exams**: Stores exam metadata like title, description, and duration
5. **exam_questions**: Maps questions to exams
6. **exam_results**: Stores exam results with scores
7. **result_answers**: Stores individual answers for each question in a result
8. **category_scores**: Stores category-specific scores for each result
9. **recommendations**: Stores AI-generated recommendations for each result

## Customization

### Adding New Question Categories
1. Update the `SubjectCategory` enum in `src/models/sql_models.py`
2. Add category-specific recommendations in `src/services/grading_service.py`

### Modifying Theme Colors
1. Edit the CSS variables in `src/static/css/styles.css`

## Troubleshooting

### Common Issues
- **Database Connection Errors**: Verify database credentials and connection settings
- **Authentication Issues**: Check JWT secret key configuration
- **Missing Dependencies**: Ensure all packages in requirements.txt are installed

### Database Migration
If you need to migrate from another database system:
1. Export your data in a compatible format (CSV, JSON)
2. Use the provided schema to create tables
3. Import data using PostgreSQL's COPY command or similar tools

## Support and Maintenance

For support or feature requests, please contact the development team.

---

© 2025 CET Exam App. All rights reserved.

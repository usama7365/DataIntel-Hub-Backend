# DataIntel Hub Backend - Python Setup

## 🚀 Migration from Node.js to FastAPI

This project has been migrated from Node.js to FastAPI (Python). Here's what you need to do to complete the setup.

## ✅ What's Been Completed

1. **FastAPI Application Structure**

   - `main.py` - Main FastAPI application
   - `routes/userRoutes.py` - API routes
   - `controllers/userController.py` - Business logic
   - `middleware/authentication.py` - JWT authentication
   - `middleware/error.py` - Error handling
   - `models/userModel.py` - User model
   - `utils/` - Utility functions (JWT, email, S3)
2. **Updated Dependencies**

   - `requirements.txt` - Python dependencies
   - `crew.py` - Updated for FastAPI integration
3. **Setup Scripts**

   - `setup_python_env.py` - Environment setup
   - `run_server.py` - Server runner

## 🔄 Remaining Steps

### 1. Install Dependencies

```bash
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Create Environment File

Create a `.env` file in the root directory:

```env
# Example environment variables for DataIntel-Hub-Backend

# OpenAI API Key
OPENAI_API_KEY=your-openai-api-key-here

# MongoDB connection URI
MONGO_URI=your-mongodb-uri-here

# Backend server port
PORT=8090

# SMTP (Email) configuration
SMPT_SERVICE=gmail
SMPT_MAIL=your-email@gmail.com
SMPT_PASSWORD=your-app-password-here
SMPT_HOST=smtp.gmail.com
SMPT_PORT=465

# JWT (Authentication) configuration
JWT_SECRET=your-jwt-secret-here
JWT_EXPIRE=5d
COOKIE_EXPIRE=2

# Frontend URL
FRONTEND_URL=http://localhost:5173 
```

### 3. Run the Server

```bash
# Option 1: Using the run script
python run_server.py

# Option 2: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using the main file
python main.py
```

### 4. Access API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 File Structure

```
DataIntel-Hub-Backend/
├── main.py                    # FastAPI application
├── crew.py                    # CrewAI integration
├── requirements.txt           # Python dependencies
├── run_server.py             # Server runner
├── setup_python_env.py       # Setup script
├── .env                      # Environment variables
├── routes/
│   └── userRoutes.py         # API routes
├── controllers/
│   └── userController.py     # Business logic
├── middleware/
│   ├── authentication.py     # JWT auth
│   └── error.py             # Error handling
├── models/
│   └── userModel.py         # User model
├── utils/
│   ├── jwtToken.py          # JWT utilities
│   ├── sendEmail.py         # Email utilities
│   └── s3upload.py          # File upload utilities
└── config/
    ├── agents.yaml           # CrewAI agents config
    └── tasks.yaml            # CrewAI tasks config
```

## 🔧 Key Features

### Authentication

- JWT-based authentication
- Email verification
- Password reset functionality
- Role-based access control

### File Upload

- CSV file upload and processing
- Integration with CrewAI for data analysis
- Local file storage with S3 backup option

### Data Integration

- Google Sheets integration
- PostgreSQL database connection
- Multi-source data analysis
- Report generation and management

### API Endpoints

#### User Management

- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/me` - Get user details
- `PUT /api/users/me/update` - Update user profile
- `PUT /api/users/password/update` - Update password

#### Email Verification

- `GET /api/users/verify/{token}` - Verify email
- `POST /api/users/email/resend` - Resend verification

#### Password Reset

- `POST /api/users/password/forgot` - Forgot password
- `PUT /api/users/password/reset/{token}` - Reset password

#### File Upload

- `POST /api/users/upload-csv` - Upload CSV for analysis
- `POST /api/users/upload-google-sheet` - Connect Google Sheets
- `POST /api/users/postgres/analyze` - Analyze PostgreSQL data

#### Report Management

- `GET /api/users/reports` - Get user reports
- `GET /api/users/reports/analytics` - Get report analytics
- `GET /api/users/reports/{report_id}` - Get specific report
- `DELETE /api/users/reports/{report_id}` - Delete report
- `PUT /api/users/reports/{report_id}` - Update report
- `GET /api/users/reports/{report_id}/download` - Download report

#### Admin Routes

- `GET /api/users/admin/users` - Get all users (admin only)

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've activated the virtual environment and installed dependencies
2. **Environment Variables**: Ensure all required environment variables are set in `.env`
3. **Port Conflicts**: Change the port in `.env` if 8000 is already in use
4. **Database Connection**: Set up MongoDB or update the database configuration

### Debug Mode

Run with debug logging:

```bash
uvicorn main:app --reload --log-level debug
```

## 🚀 Next Steps

1. **Database Integration**: Implement proper database models using SQLAlchemy or MongoDB
2. **Testing**: Add unit tests and integration tests
3. **Production**: Configure for production deployment
4. **Monitoring**: Add logging and monitoring
5. **Security**: Implement additional security measures

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🤝 Support

If you encounter any issues during setup, check:

1. Python version (3.8+ required)
2. Virtual environment activation
3. Dependencies installation
4. Environment variables configuration

### Project Information

- **Project**: DataIntel Hub
- **Event**: RemoteBase HackFest
- **Team**: Random
- **Repository**: https://github.com/usama7365/DataIntel-Hub-Backend
- **Live Demo**: https://dataintel-hub-frontend.onrender.com
- **Documentation Version**: 1.1
- **Last Updated**: July 2025

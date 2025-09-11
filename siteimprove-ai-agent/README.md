# Siteimprove AI Agent

An intelligent automation agent for Siteimprove broken links management with natural language processing capabilities.

## 🚀 Features

- **Natural Language Interface**: Control Siteimprove automation using plain English commands
- **Automated Login**: Seamless authentication with Siteimprove platform
- **Broken Links Analysis**: Automated extraction and analysis of broken links data
- **Priority Scoring**: AI-powered prioritization of broken links based on traffic and impact
- **Data Export**: Export reports in CSV, JSON, and Excel formats
- **Real-time Dashboard**: Modern React-based interface with live status updates
- **Browser Automation**: Playwright-powered web automation for reliable data extraction

## 🏗️ Architecture

```
siteimprove-ai-agent/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── models/         # Pydantic data models
│   │   ├── services/       # Business logic services
│   │   │   ├── siteimprove_automation.py  # Playwright automation
│   │   │   └── prompt_parser.py           # NLP command parsing
│   │   ├── config.py       # Configuration management
│   │   └── main.py         # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── start_server.py     # Server startup script
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API service layer
│   │   ├── types/          # TypeScript type definitions
│   │   └── App.tsx         # Main application component
│   └── package.json        # Node.js dependencies
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**

   ```bash
   cd siteimprove-ai-agent/backend
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers:**

   ```bash
   playwright install
   ```

5. **Configure environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your Siteimprove credentials
   ```

6. **Start the backend server:**
   ```bash
   python start_server.py
   ```

### Frontend Setup

1. **Navigate to frontend directory:**

   ```bash
   cd siteimprove-ai-agent/frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

## 🔧 Configuration

### Backend Configuration (.env)

```env
# Siteimprove Credentials
SITEIMPROVE_USERNAME=your_email@company.com
SITEIMPROVE_PASSWORD=your_password
SITEIMPROVE_BASE_URL=https://my2.siteimprove.com

# Server Settings
HOST=localhost
PORT=8000
DEBUG=true

# Browser Settings
HEADLESS_MODE=false
BROWSER_TIMEOUT=30000

# Cache Settings
CACHE_DURATION=3600

# File Paths
SCREENSHOT_PATH=./screenshots

# CORS Settings
CORS_ORIGINS=["http://localhost:3000"]
```

## 🎯 Usage

### Natural Language Commands

The AI agent understands natural language commands. Here are some examples:

#### Authentication

- "Login to Siteimprove"
- "Sign in"

#### Data Retrieval

- "Show me broken links"
- "Scan for broken links"
- "Get broken links report"

#### Filtering

- "Show broken links with more than 10 clicks"
- "Filter by page level 2"
- "Pages with 5+ page views"

#### Analysis

- "Which pages have the most broken links?"
- "Prioritize fixes based on page views"
- "Show most critical issues"

#### Export

- "Export to CSV"
- "Download current data"
- "Generate report"

### API Endpoints

#### Process Natural Language Commands

```http
POST /api/prompt
Content-Type: application/json

{
  "prompt": "Show me broken links with more than 5 clicks"
}
```

#### Get Broken Links Data

```http
GET /api/broken-links?force_refresh=false
```

#### Get System Status

```http
GET /api/status
```

#### Export Data

```http
POST /api/export
Content-Type: application/json

{
  "format": "csv",
  "include_priority": true
}
```

## 🤖 AI Features

### Natural Language Processing

- Intent recognition for various commands
- Parameter extraction from natural language
- Context-aware command interpretation
- Helpful suggestions and error handling

### Priority Scoring Algorithm

The system calculates priority scores based on:

- Number of broken links (weight: 2.0)
- User clicks/engagement (weight: 1.5)
- Page views/visibility (weight: 1.0)
- Page hierarchy level (weight: 0.5)

### Automation Workflow

1. **Authentication**: Automated login to Siteimprove
2. **Navigation**: Intelligent navigation to broken links report
3. **Data Extraction**: Structured data extraction from tables
4. **Processing**: Priority calculation and data enrichment
5. **Caching**: Smart caching for performance optimization

## 🔍 Monitoring & Debugging

### Browser Automation

- Screenshots are automatically saved for debugging
- Configurable headless/headed mode
- Detailed logging of automation steps
- Error handling and retry mechanisms

### API Monitoring

- Real-time status endpoint
- Request/response logging
- Performance metrics
- Error tracking

## 🚀 Deployment

### Production Setup

1. **Backend Production:**

   ```bash
   # Set production environment variables
   export DEBUG=false
   export HEADLESS_MODE=true

   # Use production WSGI server
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Frontend Production:**

   ```bash
   # Build for production
   npm run build

   # Serve static files
   npm install -g serve
   serve -s build
   ```

### Docker Deployment

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install --with-deps
COPY . .
CMD ["python", "start_server.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the GitHub repository
- Check the documentation for common solutions
- Review the logs for debugging information

## 🔮 Future Enhancements

- **Multi-site Support**: Manage multiple Siteimprove accounts
- **Scheduled Scans**: Automated periodic scanning
- **Advanced Analytics**: Trend analysis and reporting
- **Webhook Integration**: Real-time notifications
- **Machine Learning**: Predictive broken link detection
- **Mobile App**: Native mobile interface
- **API Rate Limiting**: Enhanced performance controls
- **User Management**: Multi-user access control

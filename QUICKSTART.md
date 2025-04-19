# AISE Quick Start Guide

## Prerequisites

1. Python 3.8 or higher
2. Docker and Docker Compose (recommended)
3. Git

## Quick Start with Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd aise-agent
```

2. Start the services using Docker Compose:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- RabbitMQ message broker
- FastAPI application server

## Manual Setup (Alternative)

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
source venv/bin/activate     # On Unix/MacOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following content:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=aise
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
```

4. Start the services:
- Start PostgreSQL
- Start RabbitMQ
- Run the FastAPI application:
```bash
uvicorn main:app --reload
```

## Accessing the System

1. API Documentation:
   - OpenAPI/Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

2. Health Check:
   - http://localhost:8000/health

## Basic Usage

1. Create a new project:
```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
     -H "Content-Type: application/json" \
     -d '{"name": "My Project", "description": "Project description"}'
```

2. List all projects:
```bash
curl "http://localhost:8000/api/v1/projects"
```

## Development Workflow

1. Code Structure:
   - `core/`: Core system components
   - `agents/`: Agent implementations
   - `api/`: API endpoints
   - `tests/`: Test suite

2. Running Tests:
```bash
pytest
```

3. Code Style:
```bash
# Install pre-commit hooks
pre-commit install
```

## Troubleshooting

1. Database Connection Issues:
   - Verify PostgreSQL is running
   - Check connection credentials in `.env`

2. Message Queue Issues:
   - Verify RabbitMQ is running
   - Check queue configurations

3. Agent Communication Issues:
   - Check agent logs
   - Verify message queue connectivity

## Next Steps

1. Explore the API documentation
2. Create your first agent
3. Set up monitoring
4. Configure security settings

## Support

For issues and questions:
- Check the documentation
- Open an issue on GitHub
- Join the community chat 
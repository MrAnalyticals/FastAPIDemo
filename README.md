# FastAPI Energy Trading Platform

A FastAPI-based energy commodities trading platform that connects to Azure SQL Database and runs on Azure App Service.

## Features

- Real-time trading of energy commodities (electricity, oil, gas)
- Low-latency APIs for order ingestion and trade queries
- Azure SQL Database integration using SQLAlchemy
- Deployable to Azure App Service (Linux, Python runtime)
- Full VS Code development workflow

## Quick Start

### Local Development

1. **Setup Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

2. **Configure Database**
   - Copy `.env` file and update with your Azure SQL Database credentials
   - Ensure Azure SQL firewall allows your IP address

3. **Run Application**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access API Documentation**
   - Open http://localhost:8000/docs for interactive API documentation

## Project Structure

```
fastapi-energy-trading/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point
│   ├── database.py      # Database connection and session management
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic models for request/response
│   ├── crud.py          # Database operations
│   └── utils.py         # Utility functions
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── startup.sh          # Azure App Service startup script
└── README.md           # This file
```

## API Endpoints

- `POST /trade/` - Create a new trade
- `GET /trades/` - Retrieve recent trades

## Deployment

Deploy to Azure App Service using Azure CLI:

```bash
az webapp up --name fastapi-energy-trading --resource-group myResourceGroup --runtime "PYTHON|3.11"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

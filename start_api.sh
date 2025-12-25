#!/bin/bash
# Start FastAPI Server for Product RAG Chatbot

echo "============================================================"
echo "Starting Product RAG Chatbot API Server"
echo "============================================================"
echo ""
echo "Server will be available at:"
echo "  - API Root: http://localhost:8000/"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Start server with uvicorn
uv run uvicorn phase_2.api_server:app --reload --host 0.0.0.0 --port 8000

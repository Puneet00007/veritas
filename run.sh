#!/usr/bin/env bash
set -e

echo "Starting Veritas..."

# 1. Start the backend
echo "Setting up backend..."
cd backend
if [ ! -d ".venv" ]; then
    uv venv
fi
source .venv/bin/activate
uv pip install -e ".[dev]"
echo "Starting backend on port 8000..."
uvicorn veritas.main:app --port 8000 --reload &
BACKEND_PID=$!
cd ..

# 2. Start the frontend
echo "Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    pnpm install
fi
echo "Starting frontend on port 3000..."
pnpm dev &
FRONTEND_PID=$!
cd ..

# Trap SIGINT and SIGTERM to kill both processes
trap "echo 'Shutting down servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" SIGINT SIGTERM EXIT

echo ""
echo "========================================================="
echo "Veritas is running!"
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo "Press Ctrl+C to stop both servers."
echo "========================================================="
echo ""

wait

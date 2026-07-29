#!/bin/bash

# Function to kill all background processes on exit
cleanup() {
    echo "🛑 Shutting down Car Sniper..."
    kill $(jobs -p) 2>/dev/null
    exit
}

# Trap Ctrl+C (SIGINT)
trap cleanup SIGINT EXIT

echo "🚀 Starting Car Sniper System..."

# 1. Start Backend API
echo "🔌 Starting Backend API..."
cd backend
./venv/bin/uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# 2. Start Background Crawler (DISABLED FOR DEBUGGING)
echo "🕷️  Crawler is DISABLED (Live Search Mode)..."
# cd backend
# ./venv/bin/python crawler.py &
# CRAWLER_PID=$!
# cd ..

# 3. Start Frontend
echo "💻 Starting Frontend..."
cd frontend/car-sniper
npm run dev &
FRONTEND_PID=$!
cd ../..

echo "✅ All systems GO!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Crawler: Running in background (Check 'database/db.sqlite')"
echo "---------------------------------------------------"
echo "Press Ctrl+C to stop everything."

# Wait for any process to exit
wait

cleanup

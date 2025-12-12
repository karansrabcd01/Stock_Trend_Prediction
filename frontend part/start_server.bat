@echo off
echo ========================================
echo   Stock Trend AI - Frontend Server
echo ========================================
echo.
echo Starting server on http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m http.server 8080

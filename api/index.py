from fastapi import FastAPI
import sys
import os

# Ensure the backend directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

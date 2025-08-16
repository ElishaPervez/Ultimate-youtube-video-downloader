#!/usr/bin/env python3
"""
YouTube Video Downloader - Main Entry Point
Run this file to start the application.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    main()
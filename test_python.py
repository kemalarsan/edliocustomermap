#!/usr/bin/env python3
print("Python is working!")
import sys
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}" if 'os' in globals() else "Need to import os")
#!/bin/bash
# Install requirements if needed
# pip install -r requirements.txt

# Create .app bundle for MacOS
# Note: For Mac, we use ':' as separator for --add-data
# Icon should ideally be .icns, but .png might work depending on version. 
# If you have logo.icns, replace logo.png with logo.icns

pyinstaller --clean --noconsole --onefile --windowed --name "Assistant" --icon "ui/images/logo.png" --add-data "i18n:i18n" --add-data "ui/images:ui/images" main.py

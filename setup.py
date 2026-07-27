import PyInstaller.__main__
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the icon path (if you have an icon)
# icon_path = os.path.join(current_dir, 'icon.ico')

PyInstaller.__main__.run([
    'main.py',  # Main entry point
    '--name=Otobus_Simulasyonu',  # Name of your executable
    '--onefile',  # Create a single executable file
    '--windowed',  # Don't show console window
    '--add-data=Similasyon_gui.py;.',  # Include GUI file
    '--add-data=Simlasyon_menu.py;.',  # Include menu file
    '--add-data=similasyon_anakod.py;.',  # Include main code file
    '--add-data=loglama.py;.',  # Include logging file
    '--add-data=grafikler.py;.',  # Include graphics file
    '--hidden-import=matplotlib',
    '--hidden-import=numpy',
    '--hidden-import=PIL',
    '--hidden-import=tkinter',
    # '--icon=' + icon_path,  # Add icon if you have one
    '--clean',  # Clean PyInstaller cache
    '--noconfirm',  # Replace existing spec file
]) 
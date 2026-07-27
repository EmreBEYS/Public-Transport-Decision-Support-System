import sys
import os
import tkinter as tk
from simulation_menu import SimulasyonMenu

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    # Set the working directory to the executable's directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    
    # Create and run the menu
    menu = SimulasyonMenu()
    menu.run()

if __name__ == "__main__":
    main() 
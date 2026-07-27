@echo off
echo Creating Otobus Simulasyonu executable...

echo Installing required packages...
pip install -r requirements.txt
pip install pyinstaller

echo Creating executable...
python setup.py

echo.
echo Process completed!
echo Your executable is in the 'dist' folder: Otobus_Simulasyonu.exe
echo.
echo Press any key to exit...
pause > nul 
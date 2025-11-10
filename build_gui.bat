@echo off
echo ========================================
echo Bithumb GUI Build
echo ========================================
echo.

echo Installing dependencies...
pip install PyJWT python-dotenv requests pyinstaller

echo.
echo Building...
pyinstaller BithumbGUI.spec --clean

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Output: dist\BithumbGUI.exe
echo.

pause

@echo off
echo ========================================
echo Bithumb CLI Build
echo ========================================
echo.

echo Installing dependencies...
pip install PyJWT python-dotenv requests pyinstaller

echo.
echo Building...
pyinstaller BithumbCLI.spec --clean

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Output: dist\BithumbCLI.exe
echo.

pause

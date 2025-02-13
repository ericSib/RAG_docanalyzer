@echo off
echo Installing pgvector dependencies...

REM Clone vcpkg if not exists
if not exist "C:\vcpkg" (
    echo Cloning vcpkg...
    git clone https://github.com/Microsoft/vcpkg.git C:\vcpkg
    C:\vcpkg\bootstrap-vcpkg.bat
)

REM Add vcpkg to PATH
set PATH=C:\vcpkg;%PATH%

REM Install pgvector
echo Installing pgvector...
vcpkg install pgvector:x64-windows

echo Installation completed.
echo Please restart PostgreSQL service to apply changes.

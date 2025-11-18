@echo off
echo ==================================================
echo  Installing Napari + OMERO Downloader (CCI)
echo ==================================================
echo.

REM Create environment
echo Creating conda environment "napari"...
conda create -n napari -c conda-forge napari omero-py pyqt --yes
IF ERRORLEVEL 1 (
    echo ERROR: Failed to create conda environment.
    pause
    exit /b 1
)

echo.
echo Activating environment...
call conda activate napari

echo.
echo Installing napari-omero-downloader-cci...
pip install napari-omero-downloader-cci
IF ERRORLEVEL 1 (
    echo ERROR: Failed to install plugin.
    pause
    exit /b 1
)

echo.
echo ===========================================
echo Installation complete!
echo Your environment is ready.
echo ===========================================
echo.

echo Starting napari...
napari

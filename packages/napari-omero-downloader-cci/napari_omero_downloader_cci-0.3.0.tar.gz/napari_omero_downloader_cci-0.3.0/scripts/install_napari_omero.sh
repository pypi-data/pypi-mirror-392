#!/usr/bin/env bash

echo "==========================================="
echo " Installing Napari + OMERO Downloader (CCI)"
echo "==========================================="
echo

echo "Creating Conda environment 'napari'..."
conda create -n napari -c conda-forge napari omero-py pyqt -y
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create conda environment."
    exit 1
fi

echo
echo "Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate napari

echo
echo "Installing napari-omero-downloader-cci..."
pip install napari-omero-downloader-cci
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install plugin."
    exit 1
fi

echo
echo "==========================================="
echo "Installation complete! Starting Napari..."
echo "==========================================="
napari

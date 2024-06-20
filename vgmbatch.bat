@echo off
REM Ensure VGMStream CLI is in the PATH or specify the full path to vgmstream-cli.exe
set VGMSTREAM=vgmstream-cli

REM Process each BCWAV file in the current directory
for %%f in (*.bcwav) do (
    REM Extract filename without extension
    set "filename=%%~nf"
    
    REM Decode BCWAV to WAV and retain loop points
    "%VGMSTREAM%" -o "%%~nf.wav" -L "%%f"
    
    REM Check if the output WAV file was created
    if exist "%%~nf.wav" (
        echo Processed "%%f" to "%%~nf.wav" successfully.
    ) else (
        echo Failed to process "%%f".
    )
)

echo All files processed.
pause

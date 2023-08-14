@echo off

setlocal enableDelayedExpansion
setlocal enabledelayedexpansion 

@REM Tarih ve saat formatını ayarlama
for /F "tokens=2 delims==" %%G in ('wmic OS Get localdatetime /value') do set "DT=%%G"
set "YYYY=%DT:~0,4%"
set "AA=%DT:~4,2%"
set "GG=%DT:~6,2%"
set "HH=%DT:~8,2%"
set "MM=%DT:~10,2%"
set "SS=%DT:~12,2%"

set ARPATH=%programfiles(x86)%\ossec-agent\active-response\bin\
set ARPATH_LOG="%programfiles(x86)%\ossec-agent\active-response\active-responses.log"
set PYTHON_ABSOLUTE_PATH=python

%PYTHON_ABSOLUTE_PATH% --version > nul 2>&1
if errorlevel 1 (
    echo %YYYY%/%AA%/%GG% %HH%:%MM%:%SS% active-response/bin/%~nx0: {"error": "e0", "message": "PYTHON IS NOT INSTALLED."} >> %ARPATH_LOG%
    echo. >> %ARPATH_LOG%
    exit /b
)

set "fileName=%~1"
set "URL=%~2"

if %fileName:~-2%==py ( @REM Local file active 
    if "%URL%" equ "" (
        if exist !ARPATH!!fileName! (
            %PYTHON_ABSOLUTE_PATH% "!ARPATH!!fileName!"
            exit \b
        )
    ) else (
        %PYTHON_ABSOLUTE_PATH% "!ARPATH!!fileName!" %URL%
        exit \b
    )
) 

if "%fileName%" equ "" ( 
    call :read
    set aux=!input:*"extra_args":[=!
    for /f "tokens=1 delims=]" %%a in ("!aux!") do (
        set aux=%%~a
    )

    for /f "tokens=1,2 delims=," %%a in ("!aux!") do (
        set "py_srcipt=%%a"
        set "url=%%b"
    )
    
    set "url=!url:~1!"
    set "py_srcipt=!py_srcipt:~0,-1!"

    if exist "!ARPATH!!py_srcipt!" (
        set scheme=!url:~0,4!
        if "!scheme!" equ "http" (
            %PYTHON_ABSOLUTE_PATH% "!ARPATH!!py_srcipt!" !url!
            exit /b
        ) else (
            set alert="%programfiles(x86)%\ossec-agent\active-response\bin\alert.txt
            
            echo !input! > !alert!
            %PYTHON_ABSOLUTE_PATH% "!ARPATH!!py_srcipt!" !url!
            
            del !alert!
            exit /b
        )
    )   
    exit /b
)

@REM .\active-response\bin\py-script-manager.cmd

set "name=%~1"
goto !name!

:read
set input=
for /f "delims=" %%a in ('%PYTHON_ABSOLUTE_PATH% -c "import sys; print(sys.stdin.readline())"') do (
    set input=%%a
)
exit /b

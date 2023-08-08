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

@REM localfile active deki çalistirmak istelen PYTHON dosyasi
set "fileName=%~1"
@REM localfile active deki çalistirmak istelen PYTHON dosyasin üzerinden Local ye dosya indrme veya güncelme
set "URL=%~2"

if %fileName:~-3%==py ( @REM Local file active 
    rem Bu <localfile> ile calistirmak icin tasarlandı
    if "%URL%" equ "" (
        if exist !ARPATH!!fileName! (
            @REM Python calismasi
            %PYTHON_ABSOLUTE_PATH% "!ARPATH!!fileName!"
            exit \b
        )
    ) else (
        REM URL kontrolü için PYTHON da (python check-manager.py <URL>)
        @REM echo %URL%
        %PYTHON_ABSOLUTE_PATH% "!ARPATH!!fileName!" %URL%
        exit \b
    )
) 

if "%fileName%" equ "" ( @REM Custom active response
    rem Bu <active_response> ile calistirmak icin tasarlandı (tetikleme)
    call :read
    set aux=!input:*"extra_args":[=!
    for /f "tokens=1 delims=]" %%a in ("!aux!") do (
        set aux=%%~a
    )
        
    for /f "tokens=1,2 delims=," %%a in ("!aux!") do (
        set "py_srcipt=%%a"
        set "url=%%b"
    )
    
    set "py_srcipt=!py_srcipt:~0,-1!"
    set "url=!url:~1!"

    @REM echo "!py_srcipt!" >> %ARPATH_LOG%
    if "!url!" equ "~1" (
        set script=!py_srcipt!
        echo !script!
        call :processScript !script!
        exit /b
    ) else (    
        if exist "!ARPATH!!py_srcipt!" (
            
            %PYTHON_ABSOLUTE_PATH% "!ARPATH!!py_srcipt!" !url!
        )   
    )
    exit /b
)

set "name=%~1"
goto !name!

:processScript
set "script=%~1"
echo %script%
if exist "%ARPATH%%script%" (
    set aux=!input:*"command":=!
    for /f "tokens=1 delims=," %%a in ("!aux!") do (
        set aux=%%a
    )
    set command=!aux:~1,-1!

    echo !input! > alert.txt

    start /b cmd /c "%~f0" child !script! !command!

    if "!command!" equ "add" (
        call :wait keys.txt
        echo(!output!
        del keys.txt

        call :read
        echo !input! > result.txt
    )
)
exit /b

:child
copy nul pipe1.txt >nul
copy nul pipe2.txt >nul

"%~f0" launcher %~3 <pipe1.txt >pipe2.txt | %PYTHON_ABSOLUTE_PATH% !ARPATH!%~2 <pipe2.txt >pipe1.txt

del pipe1.txt pipe2.txt
exit /b


:launcher
call :wait alert.txt
echo(!output!)
del alert.txt

if "%~2" equ "add" (
    call :read
    echo !input! >keys.txt

    call :wait result.txt
    echo(!output!)
    del result.txt
)
exit /b


:read
set input=
for /f "delims=" %%a in ('%PYTHON_ABSOLUTE_PATH% -c "import sys; print(sys.stdin.readline())"') do (
    set input=%%a
)
exit /b


:wait
if exist "%*" (
    for /f "delims=" %%a in (%*) do (
        set output=%%a
    )
) else (
    goto :wait
)
exit /b

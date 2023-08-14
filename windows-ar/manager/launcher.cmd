@echo off

setlocal enableDelayedExpansion

set ARPATH="%programfiles(x86)%\ossec-agent\active-response\bin\\"
set ARPATH_LOG="%programfiles(x86)%\ossec-agent\active-response\active-responses.log"
set PYTHON_ABSOLUTE_PATH=python

if "%~1" equ "" (
    call :read

    set aux=!input:*"extra_args":[=!
    for /f "tokens=1 delims=]" %%a in ("!aux!") do (
        set aux=%%a
    )
    set script=!aux:~1,-1!

    if exist "!ARPATH!!script!" (
        set aux=!input:*"command":=!
        for /f "tokens=1 delims=," %%a in ("!aux!") do (
            set aux=%%a
        )
        set command=!aux:~1,-1!

        echo !input! >alert.txt

        start /b cmd /c "%~f0" child !script! !command!

        if "!command!" equ "add" (
            call :wait keys.txt
            echo(!output!
            del keys.txt

            call :read
            echo !input! >result.txt
        )
    )
    exit /b
)

set "name=%~1"
goto !name!


:child
copy nul pipe1.txt >nul
copy nul pipe2.txt >nul

"%~f0" launcher %~3 <pipe1.txt >pipe2.txt | %PYTHON_ABSOLUTE_PATH% !ARPATH!%~2 <pipe2.txt >pipe1.txt

del pipe1.txt pipe2.txt
exit /b


:launcher
call :wait alert.txt
echo(!output!
del alert.txt

if "%~2" equ "add" (
    call :read
    echo !input! >keys.txt

    call :wait result.txt
    echo(!output!
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
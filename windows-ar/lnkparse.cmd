@echo off
setlocal enableDelayedExpansion

for /F "tokens=2 delims==" %%G in ('wmic OS Get localdatetime /value') do set "DT=%%G"
set "YYYY=%DT:~0,4%"
set "AA=%DT:~4,2%"
set "GG=%DT:~6,2%"
set "HH=%DT:~8,2%"
set "MM=%DT:~10,2%"
set "SS=%DT:~12,2%"
set _date=%YYYY%/%AA%/%GG% %HH%:%MM%:%SS%

set ARPATH=%programfiles(x86)%\ossec-agent\active-response\bin\
set ARPATH_LOG="%programfiles(x86)%\ossec-agent\active-response\active-responses.log"
set ARPATH_JSON_FILE="%programfiles(x86)%\ossec-agent\active-response\stdin.txt"

set input=
for /f "delims=" %%a in ('PowerShell -command "$logInput = Read-Host; Write-Output $logInput"') do (
    set input=%%a
)
set syscheck_file_path=
echo %input% > %ARPATH_JSON_FILE%

for /F "tokens=* USEBACKQ" %%F in (`Powershell -Nop -C "(Get-Content 'C:\Program Files (x86)\ossec-agent\active-response\stdin.txt'|ConvertFrom-Json).parameters.alert.syscheck.path"`) do (
    set syscheck_file_path=%%F
)
del /f %ARPATH_JSON_FILE%
set lnkparse_exe_path="D:\Program Files (x86)\pypy\Scripts\lnkparse.exe"

if exist \"%lnkparse_exe_path%\" (
    :: Extracting an LNK file data with the LnkParse3 program and structuring output with the jq tool.
    for /f "delims=" %%a in ('powershell -command "& \"%lnkparse_exe_path%\" -j \"%syscheck_file_path%\" | jq -c ."') do (
        Set str=%%a
    )
    :: Replacing single \ with double \\ in the file path for proper parsing.
    set syscheck_file_path=!syscheck_file_path:\=\\!
    :: Renaming field name "data" for proper indexing and adding file_path to the data.
    set str=!str:{"data":{={"lnk_data":{"file_path":"%syscheck_file_path%",!
    echo %_date% wazuh-lnkparse: INFO - Scan result: %str% >> %ARPATH_LOG%
    exit /b
) else (
    echo %_date% active-response/bin/%~nx0: {"error": "e0", "message": "The PYTHON Lnkparse module is not installed."} >> %ARPATH_LOG%
    exit /b
)


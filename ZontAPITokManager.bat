@echo off
title ZONT Token Manager
cls

:MENU
echo ========================================
echo    ZONT API v3 Token Manager
echo ========================================
echo.
echo 1. Get new token
echo 2. View all tokens
echo 3. Delete specific token
echo 4. Delete ALL tokens
echo 5. Exit
echo.
set /p "choice=Select action (1-5): "

if "%choice%"=="1" goto GET
if "%choice%"=="2" goto LIST
if "%choice%"=="3" goto DELETE
if "%choice%"=="4" goto DELETEALL
if "%choice%"=="5" exit
goto MENU

:GET
cls
echo ========================================
echo        Get New Token
echo ========================================
echo.
set /p "email=Your email: "
set /p "pass=Your password: "
set /p "appname=App name (e.g., MyApp): "

echo.
echo Creating Base64...
set "authstr=%email%:%pass%"
set "pscommand=powershell -Command "[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('%authstr%'))""
for /f "delims=" %%i in ('%pscommand%') do set "b64=%%i"

echo Sending request...
set "body={\"client_name\":\"%appname%\"}"
set "respfile=%temp%\zont_resp.json"

curl -X POST "https://my.zont.online/api/widget/v3/authtokens" -H "Content-Type: application/json" -H "Authorization: Basic %b64%" -H "X-ZONT-Client: %email%" -d "%body%" -s -o "%respfile%"

findstr /C:"\"ok\":true" "%respfile%" >nul
if %errorlevel% equ 0 (
    echo.
    echo SUCCESS! Token saved to token.txt
    echo.
    powershell -Command "$j=Get-Content '%respfile%'|ConvertFrom-Json; $j.token|Out-File 'token.txt' -Encoding UTF8 -NoNewline; Write-Host 'Token:' -ForegroundColor Green; Write-Host $j.token"
    echo.
    echo Token ID: 
    powershell -Command "$j=Get-Content '%respfile%'|ConvertFrom-Json; Write-Host $j.token_id"
) else (
    echo.
    echo ERROR:
    type "%respfile%"
)

del "%respfile%" 2>nul
echo.
pause
goto MENU

:LIST
cls
echo ========================================
echo        View All Tokens
echo ========================================
echo.
set /p "email=Your email: "
set /p "pass=Your password: "

set "authstr=%email%:%pass%"
set "pscommand=powershell -Command "[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('%authstr%'))""
for /f "delims=" %%i in ('%pscommand%') do set "b64=%%i"

set "respfile=%temp%\zont_list.json"
curl -X GET "https://my.zont.online/api/widget/v3/authtokens" -H "Content-Type: application/json" -H "Authorization: Basic %b64%" -H "X-ZONT-Client: %email%" -s -o "%respfile%"

echo.
findstr /C:"\"ok\":true" "%respfile%" >nul
if %errorlevel% equ 0 (
    echo Tokens list:
    echo.
    powershell -Command "$j=Get-Content '%respfile%'|ConvertFrom-Json; if($j.auth_tokens.Count -gt 0){$j.auth_tokens|Format-Table @{N='#';E={[array]::IndexOf($j.auth_tokens,$_)+1}},token_id,client_name,@{N='Created';E={if($_.created){[DateTimeOffset]::FromUnixTimeSeconds($_.created).ToString('yyyy-MM-dd HH:mm')}else{'N/A'}}},@{N='LastUsed';E={if($_.last_used){[DateTimeOffset]::FromUnixTimeSeconds($_.last_used).ToString('yyyy-MM-dd HH:mm')}else{'Never'}}}} -AutoSize; Write-Host ('Total: '+$j.auth_tokens.Count) -ForegroundColor Green}else{Write-Host 'No tokens found' -ForegroundColor Yellow}"
) else (
    echo ERROR:
    type "%respfile%"
)

del "%respfile%" 2>nul
echo.
pause
goto MENU

:DELETE
cls
echo ========================================
echo       Delete Specific Token
echo ========================================
echo.
set /p "email=Your email: "
set /p "pass=Your password: "

echo.
echo Getting your tokens...
set "authstr=%email%:%pass%"
set "pscommand=powershell -Command "[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('%authstr%'))""
for /f "delims=" %%i in ('%pscommand%') do set "b64=%%i"

set "respfile=%temp%\zont_list2.json"
curl -X GET "https://my.zont.online/api/widget/v3/authtokens" -H "Content-Type: application/json" -H "Authorization: Basic %b64%" -H "X-ZONT-Client: %email%" -s -o "%respfile%"

echo.
powershell -Command "$j=Get-Content '%respfile%'|ConvertFrom-Json; if($j.auth_tokens.Count -gt 0){$i=1; Write-Host 'Your tokens:' -ForegroundColor Cyan; Write-Host ('-'*60); foreach($t in $j.auth_tokens){Write-Host ('['+$i+'] '+$t.token_id+' ('+$t.client_name+')'); $i++} }else{Write-Host 'No tokens found' -ForegroundColor Yellow; exit 1}"

if %errorlevel% neq 0 (
    del "%respfile%" 2>nul
    pause
    goto MENU
)

echo.
set /p "token_id=Enter Token ID to delete: "

set "delfile=%temp%\zont_del.json"
curl -X DELETE "https://my.zont.online/api/widget/v3/authtokens/%token_id%" -H "Content-Type: application/json" -H "Authorization: Basic %b64%" -H "X-ZONT-Client: %email%" -s -o "%delfile%"

echo.
findstr /C:"\"ok\":true" "%delfile%" >nul
if %errorlevel% equ 0 (
    echo SUCCESS! Token deleted.
    powershell -Command "$j=Get-Content '%delfile%'|ConvertFrom-Json; Write-Host ('Deleted count: '+$j.count) -ForegroundColor Green"
) else (
    echo ERROR:
    type "%delfile%"
)

del "%respfile%" "%delfile%" 2>nul
echo.
pause
goto MENU

:DELETEALL
cls
echo ========================================
echo        Delete ALL Tokens
echo ========================================
echo.
echo WARNING! This will delete ALL your tokens!
echo All applications using these tokens will lose access!
echo.
set /p "confirm=Type YES to confirm: "
if not "%confirm%"=="YES" (
    echo Cancelled.
    pause
    goto MENU
)

echo.
set /p "email=Your email: "
set /p "pass=Your password: "

set "authstr=%email%:%pass%"
set "pscommand=powershell -Command "[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('%authstr%'))""
for /f "delims=" %%i in ('%pscommand%') do set "b64=%%i"

set "respfile=%temp%\zont_all.json"
curl -X GET "https://my.zont.online/api/widget/v3/authtokens" -H "Content-Type: application/json" -H "Authorization: Basic %b64%" -H "X-ZONT-Client: %email%" -s -o "%respfile%"

echo.
echo Deleting all tokens...
powershell -Command "$j=Get-Content '%respfile%'|ConvertFrom-Json; $d=0; foreach($t in $j.auth_tokens){try{$headers=@{'Authorization'='Basic %b64%';'X-ZONT-Client'='%email%'};Invoke-RestMethod -Uri ('https://my.zont.online/api/widget/v3/authtokens/'+$t.token_id) -Method Delete -Headers $headers|Out-Null; $d++; Write-Host ('Deleted: '+$t.token_id) -ForegroundColor Gray}catch{Write-Host ('Failed: '+$t.token_id) -ForegroundColor Red}}; Write-Host ('Total deleted: '+$d) -ForegroundColor Green"

del "%respfile%" 2>nul
echo.
echo Done.
pause
goto MENU

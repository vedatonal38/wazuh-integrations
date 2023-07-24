# Wazuh Python Script Manager

Wazuh yöneticisi üzerinde, ajanlarda kullanılmak üzere localfile ve active response özelliklerini kullanan Python betik dosyalarını çalıştırmak için bir CMD komut dosyası oluşturulmuştur. Wazuh belgelerinde Python dosyalarını `.exe` formatına dönüştürerek çalıştırmayı anlatan talimatlar bulunmaktadır. Ancak her Windows işletim sisteminde bu işlem başarılı olmayabilir. Bu yüzden, [Custom active response](https://documentation.wazuh.com/current/user-manual/capabilities/active-response/custom-active-response-scripts.html#method-2-run-a-python-script-through-a-batch-launcher) bölümündeki CMD komutunu düzenleyerek localfile özelliğinde çalışacak şekilde ayarladım.

## Windows işletim sisteminde CMD (Komut İstemi) nasıl çalışır:

1. Python'un Yüklü Olup Olmadığının Kontrol Edilmesi:
    - CMD, Windows işletim sisteminde komutları çalıştırmak için kullanılan bir arayüzdür.
    - Python'un yüklü olup olmadığını kontrol etmek için CMD'de `python --version` veya `python -V` komutu kullanılabilir.
    - Eğer Python yüklü değilse, Wazuh Manager tarafından log kaydı göndermek için aktif tepki (active response) log'una `PYTHON IS NOT INSTALLED.` mesajı yazdırılabilir.
    ```
    %PYTHON_ABSOLUTE_PATH% --version > nul 2>&1
    if errorlevel 1 (
        echo %YYYY%/%AA%/%GG% %HH%:%MM%:%SS% active-response\bin\%~nx0: {"error": "e0", "message": "PYTHON IS NOT INSTALLED."} >> %ARPATH_LOG%
        echo. >> %ARPATH_LOG%
        exit /b
    )
    ```

2. Localfile Tag ile Python Script'in Çalıştırılması:
    - Wazuh agent, belirli aralıklarla (frequency) sistemde Python scriptlerini çalıştırmak için local veya merkezi yapılandırma dosyalarını kullanabilir.
    - Aşağıdaki gibi `localfile` etiketi kullanılarak komut çalıştırılabilir:
    ```
    <localfile>
        <log_format>full_command</log_format>
        <command>"C:\"Program Files (x86)"\ossec-agent\active-response\bin\py-script-manager.cmd script.py"</command>
        <frequency>604800</frequency>
    </localfile>
    ```
    - `check-manager.py` isimli python script i agnet te uzaktan dosya indirmek için URL parametresi alır. (ikinici if blok)
    ```
    if %fileName:~-3%==py (
        if "%URL%" equ "" (
            if exist !ARPATH!!fileName! (
                %PYTHON_ABSOLUTE_PATH% !ARPATH!\%fileName%
                exit \b
            )
        ) else (
            REM python check-manager.py <URL>
            %PYTHON_ABSOLUTE_PATH% !"ARPATH\"!!fileName! %URL%
            exit \b
        )
    )
    ```
3. [Custom active response](https://documentation.wazuh.com/current/user-manual/capabilities/active-response/custom-active-response-scripts.html#method-2-run-a-python-script-through-a-batch-launcher) ile Python Script'in Çalıştırılmasıdır.
    - [Active response](https://github.com/vedatonal38/wazuh-detaysoft-doc/blob/main/README.md#active-response-script-agent-lerde-komut-y%C3%BCr%C3%BCtme) detaylı anlatım  

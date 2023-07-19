## VIRUSTOTAL & malicious files using CDB lists

Active response Python srcipt kullanmak için aşağıdaki <command> ve <active-response> bloklarını Wazuh server /var/ossec/etc/ossec.conf dosyasına ekleyin:

```
  <command>
    <name>remove-threat</name>
    <executable>py_script_manager.cmd</executable>
    <extra_args>remove-threat.py</extra_args>
    <timeout_allowed>no</timeout_allowed>
  </command>

  <active-response>
    <disabled>no</disabled>
    <command>remove-threat</command>
    <location>local</location>
    <rules_id>100003,87105</rules_id>
  </active-response>
```

| rule id | Referans |
|---|----|
| 100003 | [CDB Lists](https://wazuh.com/blog/detecting-and-responding-to-malicious-files-using-cdb-lists-and-active-response/)
| 85105 | [Virus Total](https://documentation.wazuh.com/current/user-manual/capabilities/malware-detection/virus-total-integration.html)

Değişiklikleri uygulamak için Wazuh yöneticisini yeniden başlatın:

```
sudo systemctl restart wazuh-manager
```

## NMAP

Gereksimler:
1. [Python v3.8.7](https://www.python.org/ftp/python/3.8.7/python-3.8.7-amd64.exe) veya üstü (pip önceden yüklenmiş olarak). İstendiğinde aşağıdaki kutuları işaretleyin:

    - Başlatıcıyı tüm kullanıcılar için yükleyin (önerilir).
    - Python'u PATH'e ekleyin.

2. [Microsoft Visual C++ 2015 Yeniden Dağıtılabilir.](https://www.microsoft.com/en-us/download/confirmation.aspx?id=52685)

3. [Nmap v7.94](https://nmap.org/dist/nmap-7.94-setup.exe) veya üstü. Nmap'i PATH'e eklediğinizden emin olun.

```
pip3 install python-nmap
```

Yerel yapılandırma veya merkezi yapılandırma dosyasına;
```
<!-- Run nmap python script -->
  <localfile>
    <log_format>full_command</log_format>
    <command>"C:\Program Files (x86)\ossec-agent\active-response\bin\py-script-manager.cmd nmap-srcipt.py"</command>
    <frequency>604800</frequency>
  </localfile>
```

!!! [py-script-manager.cmd](#) dosyasını indirmeyi unutmayınız.

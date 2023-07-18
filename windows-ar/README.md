
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

 https://raw.githubusercontent.com/vedatonal38/wazuh-integrations/main/windows-ar/remove-threat.py

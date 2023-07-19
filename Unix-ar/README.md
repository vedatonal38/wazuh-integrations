## VIRUSTOTAL & malicious files using CDB lists

.

## NMAP

Gereksimler:
```
sudo apt-get update && sudo apt-get install python3
sudo apt-get install python3-pip
sudo apt-get install nmap
sudo pip3 install python-nmap
```

Yerel yapılandırma veya merkezi yapılandırma dosyasına;
```
<!-- Run nmap python script -->
  <localfile>
    <log_format>full_command</log_format>
    <command>python3 /var/ossec/active-response/bin/nmap-srcipt.py</command>
    <frequency>604800</frequency>
  </localfile>
```



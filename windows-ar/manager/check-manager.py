import os
import sys
import hashlib
import platform
import datetime
from pathlib import PureWindowsPath, PurePosixPath
import urllib.request
import urllib.error

ar_name = ""
platform_name = platform.system()

if platform_name == "Windows":
    LOG_FILE = "C:\\Program Files (x86)\\ossec-agent\\active-response\\active-responses.log"
else:
    LOG_FILE = "/var/ossec/logs/active-responses.log"

def write_debug_file(msg):
    global ar_name
    with open(LOG_FILE, mode="a") as log_file:
        if not ar_name.find("active-response") == -1:
            ar_name_posix = str(PurePosixPath(PureWindowsPath(ar_name[ar_name.find("active-response"):])))
        else:
            ar_name_posix = "active-response/bin/" + str(PurePosixPath(PureWindowsPath(ar_name)))
        log_file.write(str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + " " + ar_name_posix + ": " + msg +"\n")
        
def check_url(url):
    try:
        response = urllib.request.urlopen(url)
        return response #.read().decode('utf-8')
    except urllib.error.URLError as e:
        print("Failed to connect to " + url)
        write_debug_file("Failed to connect to " + url)
        exit()
    
def calculate_file_hash(file_path=None, response=None, algorithm='sha256', chunk_size=65536):
    """Calculate the hash of a file using the specified algorithm."""
    hash_algorithm = hashlib.new(algorithm)
    if file_path:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                hash_algorithm.update(data)
    elif response:
        while True:
            data = response.read(chunk_size)
            if not data:
                break
            hash_algorithm.update(data)
        # hash_algorithm.update(html_file)
    return hash_algorithm.hexdigest()

def download_file(url, file_name):
    response = check_url(url)
    if response:
        pwd = os.getcwd() + "\\active-response\\bin\\" + file_name
        if os.path.isfile(pwd):
            hash1 = calculate_file_hash(file_path=pwd)
            hash2 = calculate_file_hash(response=response)
            if hash1 != hash2:
                try:
                    urllib.request.urlretrieve(url, filename=pwd)
                    write_debug_file("File updated successfully : " + file_name)
                except urllib.error.URLError as e:
                    write_debug_file("File updated failed : " + file_name)
            else:
                write_debug_file("No update : " + file_name)
            return
        try:
            urllib.request.urlretrieve(url, filename=file_name)
            # print("File downloaded successfully")
        except urllib.error.URLError as e:
            write_debug_file("Failed to download file : " + url)

def check_text_in_file(file_path, text_to_find):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            if text_to_find in content:
                return True
            else:
                return False
    except FileNotFoundError:
        print("Dosya bulunamadı.")
        return False

def file_chenged(file, old, new):
    content = open (file, "r").read()
    content = content.replace(old, new)
    open(file, "w").write(content)

def control():
    """
    burasi yeni indirilen active-response dosyalarin içini düzenleme yapmaktadir.
    ornegin dosyada "<PYTHON_PATH>" ifadesi bulunan mecvut bilgisayarın python yolu ile değiştirilmesi sağılmaktadır.     
    <command>
        <name>check_manager_path</name>
        <executable>py-script-manager.cmd</executable>
        <extra_args>check-manager.py</extra_args>
        <timeout_allowed>no</timeout_allowed>
    </command>
    <active-response>
        <disabled>no</disabled>
        <command>check_manager_path</command>
        <location>local</location>
        <rules_id>503</rules_id>
    </active-response>
    """
    ar_name_local = ar_name.split("\\")[-1]
    files = os.listdir(os.getcwd())
    for file in files:
        if not file.endswith(".exe") and not file == ar_name_local:
            if check_text_in_file(file, "<PYTHON_PATH>"):
                py = sys.executable
                extension = file.split(".")[0]
                py_ = py.split("\\")[-1] # lnkparse
                py = py.replace(f"{py_}", f"Scripts\{extension}.exe")
                file_chenged(file, "<PYTHON_PATH>", f"\"{py}\"")
        
def main(args):
    global ar_name, platform_name
    platform_name = platform_name.lower()
    ar_name = args[0]
    if len(args) == 1:
        write_debug_file("Start Control function")
        control()
        exit(1)
    url = args[1]
    file_extension = url.split(".")[-1]
    if file_extension == "py" or file_extension == "cmd":
        write_debug_file("Start python file run function")
        file_name = url.split("/")[-1]
        download_file(url, file_name)
    elif file_extension == "md":
        write_debug_file("Start file check function")
        html = check_url(url).read().decode('utf-8')
        lines = html.split("\n")
        files = []
        for line in lines:
            if line.startswith("https"):
                parse = line.split("/")
                class_name = parse[-2].lower()
                file_name = parse[-1]
                # print(class_name)
                if class_name == platform_name + "-ar":
                    download_file(line.strip(), file_name)
                    files.append(file_name)
                elif "l" + class_name == platform_name + "-ar":
                    download_file(line.strip(), file_name)
                    files.append(file_name)
        if platform_name == "Windows":
            control()
            for pwd_files in os.listdir(os.getcwd()):
                if not pwd_files in files and not pwd_files.endswith(".exe") and not pwd_files.endswith(".cmd") and not args[0] in pwd_files:
                    os.remove(pwd_files)
    else:
        write_debug_file("Unsupported URL : " + url)
        
if __name__ == "__main__":
    main(sys.argv)

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
        if os.path.isfile(file_name):
            hash1 = calculate_file_hash(file_path=file_name)
            hash2 = calculate_file_hash(response=response)
            if hash1 != hash2:
                try:
                    urllib.request.urlretrieve(url, filename=file_name)
                    write_debug_file("File updated successfully : " + file_name)
                except urllib.error.URLError as e:
                    write_debug_file("File updated failed : " + file_name)
            return
        try:
            urllib.request.urlretrieve(url, filename=file_name)
            # print("File downloaded successfully")
        except urllib.error.URLError as e:
            write_debug_file("Failed to download file : " + url)

def main(args):
    global ar_name, platform_name
    platform_name = platform_name.lower()
    ar_name = args[0]
    url = args[1]
    file_extension = url.split(".")[-1]
    if file_extension == "py":
        file_name = url.split("/")[-1]
        download_file(url, file_name)
    elif file_extension == "md":
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
            for pwd_files in os.listdir(os.getcwd()):
                if not pwd_files in files and not pwd_files.endswith(".exe") and not pwd_files.endswith(".cmd") and not args[0] in pwd_files:
                    os.remove(pwd_files)
    else:
        write_debug_file("Unsupported URL : " + url)
        
if __name__ == "__main__":
    main(sys.argv)

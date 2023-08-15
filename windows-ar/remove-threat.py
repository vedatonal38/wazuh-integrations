import os
import sys
import json
import datetime 
from pathlib import PureWindowsPath, PurePosixPath

if os.name == 'nt':
    LOG_FILE = "C:\\Program Files (x86)\\ossec-agent\\active-response\\active-responses.log"
else:
    LOG_FILE = "/var/ossec/logs/active-responses.log"

ADD_COMMAND = 0
DELETE_COMMAND = 1
CONTINUE_COMMAND = 2
ABORT_COMMAND = 3

OS_SUCCESS = 0
OS_INVALID = -1
ar_name = ""

class message:
    def __init__(self):
        self.alert = ""
        self.command = 0

def write_debug_file(msg):
    global ar_name
    with open(LOG_FILE, mode="a") as log_file:
        if not ar_name.find("active-response") == -1:
            ar_name_posix = str(PurePosixPath(PureWindowsPath(ar_name[ar_name.find("active-response"):])))
        else:
            ar_name_posix = "active-response/bin/" + str(PurePosixPath(PureWindowsPath(ar_name)))
        log_file.write(str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + " " + ar_name_posix + ": " + msg +"\n")


def setup_and_check_message():
    # get alert from stdin
    input_str = ""
    for line in sys.stdin:
        input_str = line
        break

    try:
        data = json.loads(input_str)
    except ValueError:
        write_debug_file('Decoding JSON has failed, invalid input format')
        message.command = OS_INVALID
        return message

    message.alert = data

    command = data.get("command")

    if command == "add":
        message.command = ADD_COMMAND
    elif command == "delete":
        message.command = DELETE_COMMAND
    else:
        message.command = OS_INVALID
        write_debug_file('Not valid command: ' + command)

    return message

def send_keys_and_check_message(keys):

    # build and send message with keys
    keys_msg = json.dumps({"version": 1,"origin":{"name": ar_name,"module":"active-response"},"command":"check_keys","parameters":{"keys":keys}})
    write_debug_file(keys_msg)
 
    print(keys_msg)
    sys.stdout.flush()
 
    # read the response of previous message
    input_str = ""
    while True:
        line = sys.stdin.readline()
        if line:
            input_str = line
            break
 
    # write_debug_file(input_str)
 
    try:
        data = json.loads(input_str)
    except ValueError:
        write_debug_file('Decoding JSON has failed, invalid input format')
        return message
 
    action = data.get("command")
 
    if "continue" == action:
        ret = CONTINUE_COMMAND
    elif "abort" == action:
        ret = ABORT_COMMAND
    else:
        ret = OS_INVALID
        write_debug_file("Invalid value of 'command'")
 
    return ret
 
def main(argv):
    global ar_name
    ar_name = argv[0]

    write_debug_file("Started")
 
    # validate json and get command
    msg = setup_and_check_message()

    if msg.command < 0:
        sys.exit(OS_INVALID)

    if msg.command == ADD_COMMAND:
        alert = msg.alert["parameters"]["alert"]
        keys = [alert["rule"]["id"]]
        action = send_keys_and_check_message(keys)
        # if necessary, abort execution
        if action != CONTINUE_COMMAND:
            if action == ABORT_COMMAND:
                write_debug_file("Aborted")
                sys.exit(OS_SUCCESS)
            else:
                write_debug_file( "Invalid command")
                sys.exit(OS_INVALID)
        try:
            sts = False
            if "virustotal" in alert["data"]["integration"]:
                os.remove(alert["data"]["virustotal"]["source"]["file"])
                sts = True
            elif "hybrid_analysis" in alert["data"]["integration"]:
                os.remove(alert["data"]["hybrid_analysis"]["source"]["file"])
                sts = True
            elif "lnkparse" in alert["data"]["integration"]:
                os.remove(alert["data"]["lnk_data"]["file_path"])
                sts = True
            
            
            if sts:
                write_debug_file( json.dumps(msg.alert) + " Successfully removed threat")
            else:
                write_debug_file("Error")
        except OSError as error:
            write_debug_file( json.dumps(msg.alert) + "Error removing threat")
    else:
        write_debug_file( "Invalid command")

    write_debug_file( "Ended")

    sys.exit(OS_SUCCESS)

if __name__ == "__main__":
    main(sys.argv)

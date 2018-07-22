import os, sys, requests

##################################
# START CONFIGURATION SETTINGS
##################################

# User token for Pushover. You can find this on this page: https://pushover.net/
USER_TOKEN = os.environ.get('USER_TOKEN')
if not USER_TOKEN:
    print('No USER_TOKEN provided')
    sys.exit(0)

# Token for this script. You will need to add the app on this page: https://pushover.net/apps
APP_TOKEN = os.environ.get('APP_TOKEN')
if not APP_TOKEN:
    print('No APP_TOKEN provided')
    sys.exit(0)

# Set the thresholds to be notified here. Start with lowest and continue up, otherwise you could strange notifications
THRESHOLDS = os.environ.get('THRESHOLDS')
if not type(THRESHOLDS) is list:
    THRESHOLDS = [10, 25, 50]

# Set the disk partition to check
PARTITION = os.environ.get('CHECK_PART')
if not PARTITION:
    PARTITION = '/mnt/data'

##################################
# END CONFIGURATION SETTINGS
##################################

def sendNotification(message):
    data = {
        "token": APP_TOKEN,
        "user": USER_TOKEN,
        "message": message
    }
    print(message)
    result = requests.post("https://api.pushover.net/1/messages.json", data)

def main():
    diskStat = os.statvfs(PARTITION)
    totalDiskSize = diskStat.f_blocks * diskStat.f_frsize
    freeSpace = diskStat.f_bavail * diskStat.f_frsize
    freeSpacePercentage = round(float(freeSpace) / float(totalDiskSize), 2) * 100
    for threshold in THRESHOLDS:
        if (freeSpacePercentage < threshold):
            hostname = os.uname()[1]
            message = "{0}: Less than {1}% free space remaining on disk {2}".format(hostname, threshold, PARTITION)
            sendNotification(message)
            break;

if __name__ == "__main__":
    main()
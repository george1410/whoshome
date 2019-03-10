# Heavily modified, but originally based on code from https://github.com/initialstate/pi-sensor-free-presence-detector
# George McCarron 2019 - http://georgemccarron.com
import subprocess
from time import sleep
from threading import Thread
import requests
import datetime

# List of the names of people to track
occupant = ["XXXXXX", "XXXXXX", "XXXXXX"]

# MAC addresses for each of the people above's phones in the same order
# Use lowercase letters!
address = ["xx:xx:xx:xx:xx:xx", "xx:xx:xx:xx:xx:xx", "xx:xx:xx:xx:xx:xx"]

url = 'URL_TO_SEND_POST_REQUESTS_TO'

# When we first start up, wait for 60secs to allow the machine to connect to the network
sleep(60)

# The function to be run in each child thread that checks for device presence
def whosHere(i):

    # Wait 15 seconds, just to let the ARP scan finish in the main thread
    sleep(15)

    # This loop runs every 15 seconds and is where we check for device presence
    while True:

        # If the main thread got a ctrl-c, then exit this child thread
        if stop == True:
            print "Exiting Thread"
            exit()

        # If the MAC address of the person that this thread is responsible for
        # was present in the ARP scan output, then send the current timestamp to the server
        if (address[i] in output):
            # Get the current date and time
            dt = datetime.datetime.now()
            # This is just for logging purposes
            dtLog = '[{:02d}:{:02d}:{:02d}] '.format(dt.hour, dt.minute, dt.second)
            print(dtLog + occupant[i] + "'s device is connected to your network")
            # Send the data to the server. If for some reason the request fails,
            # we don't care, just loop round again in 15 seconds
            try:
                r = requests.post(url, json={'name': occupant[i], 'timestamp': str(dt)})
            except:
                pass

        # Wait for 15 seconds before looping again
        sleep(15)

# Main thread
try:

    # This variable is just to stop the child threads when we press ctrl+c
    # if you use ctrl-z, then you end up with loads of background python processes...
    global stop
    stop = False

    # Start a thread for each person to track,
    # running the whosHere function, passing it the index of the person in the list
    for i in range(len(occupant)):
        t = Thread(target=whosHere, args=(i,))
        t.start()

    # Every 10 seconds, run an ARP scan, and store the output from it
    while True:
        global output
        output = subprocess.check_output("sudo arp-scan -l", shell=True)
        sleep(10)

except KeyboardInterrupt:
    # If we press ctrl-c, make sure all the child threads exit
    # as well as the main thread
    stop = True
    exit()
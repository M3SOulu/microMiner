import time
import os

def runTest():
    os.system('./tests/kubernetes/sock-shop/test/runLocust.sh -h 192.168.56.20:30001 -l ./tests/kubernetes/sock-shop/testLog -r 2')
    time.sleep(3)
    os.system('./tests/kubernetes/sock-shop/test/runLocust.sh -h 192.168.56.20:30001 -l ./tests/kubernetes/sock-shop/testLog -r 2')

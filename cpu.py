import time
import os
import psutil
from DevIoTGateway.gateway import Gateway


account = raw_input("--Please enter DevIot email account(someone@domain.com):\n")
gatewayname = account + "_gateway"
prefix = raw_input("--Please enter a Prefix for Sensor names:\n")
app = Gateway("gatewayname", "52.38.220.120:9000", "iot.eclipse.org:1883", account)

# register input sensors
# the parameters are: sensor kind, sensor id, sensor display name
app.register("cpu", "cpu", prefix+"-CPU")

# register output sensors
# the parameters are: sensor kind, sensor id, sensor display name, action call back function
#app.register_action("led", "groveled", prefix+"-Led", trigger_grove_led)

# run service
app.run()
    
pid = os.getpid()
print pid
p = psutil.Process(pid)
print p.get_cpu_percent(interval=1.0)
print p.get_memory_percent()
print p.get_memory_info()
print p.get_cpu_times()
print p.get_open_files()
print p.get_connections()
print p.get_threads()

while True:
    try:
        # get sensor value
        cpu_value = p.get_cpu_percent(interval=1.0)
	print("cpu =", cpu_value) 	

        # update the sensor value, the parameters are: sensor id, new sensor value
        app.set_value("cpu", cpu_value * 100)

        time.sleep(.5)

    except IOError:
        print ("Error")

import serial

import threading
import time
import Queue
import math
import json
from deviot.gateway import Gateway

global sender 
global host_server
global host_port
stop_cmd = '0\r\n' # to stop action
global com_port 

com_port = '/dev/cu.usbserial-DA01L1AU'

host = "iot.eclipse.org:1883"

temperature_cmd = '1\r\n'
touch_cmd = '2\r\n'
button_cmd = '3\r\n'
sound_cmd = '4\r\n'
light_cmd = '5\r\n'
angle_cmd = '6\r\n'

led_cmd = '50\r\n'
buzzer_cmd = '51\r\n'
relayon_cmd = '52\r\n'
relayoff_cmd = '53\r\n'


baudrate = 9600

sensor_cmds = {'temperature':(temperature_cmd,),
                    'touch':(touch_cmd,),
                    'button':(button_cmd,),
                    'sound':(sound_cmd,),
                    'light':(light_cmd,),
                    'led':(led_cmd,),
                    'buzzer':(buzzer_cmd,),
                    'angle':(angle_cmd,),
                    'relay':(relayoff_cmd, relayon_cmd),
                    }

data_cmds = [temperature_cmd, touch_cmd, button_cmd, sound_cmd, light_cmd, angle_cmd]
ctrl_cmds = [led_cmd, buzzer_cmd]

class SensorController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cmd_queue = Queue.Queue()
        self.resp_queue = Queue.Queue()
        self.prev_cmd = None
        self.curr_cmd = None
        self.running = True
        self.locker = threading.Lock()
        self.ser = serial.Serial(com_port, baudrate)
        print self.ser.name
        time.sleep(3) # wait for the board is ready.

    def run(self):
        while self.running:
            try:
                self.curr_cmd = self.cmd_queue.get(block=True, timeout=5)
            except:
                continue

            if self.is_ctrl_cmd(self.prev_cmd):
                #print 'send stop cmd', stop_cmd
                if self.is_data_cmd(self.curr_cmd):
                    # if previous control command is still running, we need to stop it to exec current data command
                    self.ser.write(stop_cmd)
                # wait for the end of previous control command
                ret = self.ser.readline()

            self.ser.write(self.curr_cmd)

            if self.is_data_cmd(self.curr_cmd):
                data = self.ser.readline()
                resp = int(data)
            else:
                resp = 'ok'

            self.prev_cmd = self.curr_cmd
            self.resp_queue.put(resp)

    def is_data_cmd(self, cmd):
        if cmd in data_cmds:
            return True
        else:
            return False

    def is_ctrl_cmd(self, cmd):
        if cmd in ctrl_cmds:
            return True
        else:
            return False

    def push_cmd(self, cmd):
        self.locker.acquire()
        self.cmd_queue.put(cmd)
        resp = self.resp_queue.get()
        self.locker.release()
        return resp

class SensorManager(object):
    def __init__(self):
        self.ctrler = SensorController()
        self.ctrler.start()

    def exec_cmd(self, sensor, *atuple, **adict):
        if sensor in sensor_cmds.keys():
            if sensor == 'relay':
                if "state" in adict.keys():
                    cmd = sensor_cmds[sensor][int(adict['state'])]
                else:
                    cmd = sensor_cmds[sensor][0]
            else:
                cmd = sensor_cmds[sensor][0]
            return self.ctrler.push_cmd(cmd)
        else:
            return "error: no such sensor"

def test_temp():
    sm = SensorManager()

    while True:
        data = sm.exec_cmd('temperature')
        print 'temperature is %d' % data
        time.sleep(2)


def test():
    sm = SensorManager()

    while True:
        #data = sm.exec_cmd('temperature')
        #print 'temperature is %d' % data

        #data = sm.exec_cmd('sound')
        #print 'sound is %d' % data

        data = sm.exec_cmd('light')
        #print 'light is %d' % data
	json_string = '{"light-1":{"value":0}}'
	devIoTData = {}
        devIoTData.update({str("light-1"):{'value':data}})


	print devIoTData
        app.set_value("arduinoLight", data)

        #data = sm.exec_cmd('angle')
        #print 'angle is %d' % data

        #ret = sm.exec_cmd('led')
        #print 'control led', ret
        #time.sleep(1)

        #sm.exec_cmd('buzzer')
        #print 'control buzzer', ret
        time.sleep(0.5)

def test_relay():
    sm = SensorManager()

    while True:
        sm.exec_cmd('relay', state=1)
        time.sleep(2)
        sm.exec_cmd('relay', state=0)
        time.sleep(2)

def cal_temp():
    B = [3100, 3250, 3650, 3950, 3380, 3900, 4485, 4050, 4500]

    val = 372
    for b in B:
        resistance= (1023L-val)*10000.0/val
        temperature=1/(math.log(resistance/10000.0)/b+1/298.15)-273.15
        print b, temperature


if __name__ == '__main1__':
    try:
        if len(sys.argv) > 1:
            host = str(sys.argv[1])
    except:
        print("mqtt host are needed!")

    account = raw_input("--Please input DevIot email account(someone@domain.com):\n")
    gateway_name = raw_input("--Please input gateway service account:\n")
    topic = "{0:s}/{1:s}".format(gateway_name, account)
    host_server = ""
    host_port = 0

    try:
        host_info = host.split(":")
        host_server = host_info[0]
        host_port = int(host_info[1])
    except:
        print("mqtt host should be with the format: ip:port")

    print("listen the host %s and communication with topic: %s" % (host, topic))

    if len(host_server) > 0 and host_port > 0 and len(topic) > 0:
        str_action = raw_input("--Please input your action:\n")
        data = json.loads(str_action)
	print(host_server)
	print(host_port)
	print(sender)
	test()
        #sender.send_data(host_server, host_port, str_action)
        #sender.run(host_server, host_port)

if __name__ == '__main__':
    account = raw_input("--Please enter DevIot email account(someone@domain.com):\n")
    gatewayname = account + "_gateway"

    app = Gateway(gatewayname, "52.38.220.120:9000", "iot.eclipse.org:1883", account)
    com_port = raw_input("--Please enter Serial PORT name: eg: /dev/cu.usbserial-DA01L1AU \n")
    app.register("light", "arduinoLight", "ArduinoLight")
    # run service
    app.run()
    test()

# /etc/snmp/snmpd 에서 agent의 ip를 수정해야 함 (기본은 127.0.0.1로 되어있고, localhost로 인식안됨)
# /etc/snmp/snmpd 에 sysContact, sysLocation, sysServices 정보가 들어가 있음
# /etc/snmp/snmpd 의 Manager에 들어가는 커뮤니티명은 rocommunity에서 정보를 바꿈

from pysnmp.hlapi import *
import mqttConfig
import json
host = '127.0.0.1'
port = 161

oidList = ["1.3.6.1.4.1.30960.2.1.5.1.1.9.1", "1.3.6.1.4.1.30960.2.1.5.1.1.9.2", "1.3.6.1.4.1.30960.2.1.5.1.1.9.3", 
           "1.3.6.1.4.1.30960.2.1.5.1.1.9.4", "1.3.6.1.4.1.30960.2.1.5.1.1.9.5", "1.3.6.1.4.1.30960.2.1.5.1.1.9.6"]
mqttTopic = '/oneM2M/req/SiotTestAE/iotCore'

#sample data
data = {
    'to': '/iotCore/AEe2c8236c-7d26-48d2-9cc7-29e79129c811/vm',
    'fr': 'SiotTestAE',
    'rqi': 'fe38396ed4564d8db19f34377f49f6f3',
    'pc': {"m2m:cin":{"con":0}},
    'op': 1,
    'ty': 4,
    'sec': 0
}


def sendData(topic, payload, qos):
    mqttConfig.mqClient.publish(topic=topic, payload=json.dumps(payload), qos=qos)


def getData(oids):
    for oid in oids:
        iterator = getCmd(SnmpEngine(), CommunityData('public'), UdpTransportTarget((host, port)), ContextData(),
                      ObjectType(ObjectIdentity(oid)))
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication:  # SNMP engine errors
            print(errorIndication)
        else:
            if errorStatus:  # SNMP agent errors
                print('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex)-1] if errorIndex else '?'))
            else:
                for varBind in varBinds:  # SNMP response contents
                    # data[str(varBind).split('=')[0]] = str(varBind).split('=')[1]
                    data['pc']['m2m:cin']['con'] = str(varBind).split('=')[1]
                    data['rqi'] = data['rqi'][0:8] + '-' + data['rqi'][8:12] + '-' + data['rqi'][12:16] + '-' + \
                                  data['rqi'][16:20] + '-' + data['rqi'][20:]
                    sendData(mqttTopic, json.dumps(data), 0)
                    print(data)
                    # print("success")
    return data


if __name__ == '__main__':
    mqttPayload = getData(oidList)
    sendData(mqttTopic, mqttPayload, 0)


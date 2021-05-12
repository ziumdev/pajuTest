# /etc/snmp/snmpd 에서 agent의 ip를 수정해야 함 (기본은 127.0.0.1로 되어있고, localhost로 인식안됨)
# /etc/snmp/snmpd 에 sysContact, sysLocation, sysServices 정보가 들어가 있음
# /etc/snmp/snmpd 의 Manager에 들어가는 커뮤니티명은 rocommunity에서 정보를 바꿈

from pysnmp.hlapi import *
import mqttConfig
import json
host = '127.0.0.1'
port = 161

oidList = ["1.3.6.1.2.1.1.4.0", "1.3.6.1.2.1.1.5.0", "1.3.6.1.2.1.1.6.0", "1.3.6.1.2.1.1.7.0"]
mqttTopic = 'snmp/test'


def getData(oids):
    data = {}
    for oid in oids:
        iterator = getCmd(SnmpEngine(), CommunityData('test'), UdpTransportTarget((host, port)), ContextData(),
                      ObjectType(ObjectIdentity(oid)))
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication:  # SNMP engine errors
            print(errorIndication)
        else:
            if errorStatus:  # SNMP agent errors
                print('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex)-1] if errorIndex else '?'))
            else:
                for varBind in varBinds:  # SNMP response contents
                    data[str(varBind).split('=')[0]] = str(varBind).split('=')[1]
                    print(varBind)
    return data


def sendData(topic, payload, qos):
    mqttConfig.mqClient.publish(topic=topic, payload=json.dumps(payload), qos=qos)
    print("success")

if __name__ == '__main__':
    mqttPayload = getData(oidList)
    sendData(mqttTopic, mqttPayload, 0)


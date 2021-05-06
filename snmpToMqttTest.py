# /etc/snmp/snmpd 에서 agent의 ip를 수정해야 함 (기본은 127.0.0.1로 되어있고, localhost로 인식안됨)
# /etc/snmp/snmpd 에 sysContact, sysLocation, sysServices 정보가 들어가 있음
# /etc/snmp/snmpd 의 Manager에 들어가는 커뮤니티명은 rocommunity에서 정보를 바꿈

import time
from snmp import Manager
from snmp.exceptions import Timeout
import mqttConfig
import json

# REPLACE 'public' with your community string
manager = Manager(b'test')

try:
    hosts = ["127.0.0.1"]                    # REPLACE these IPs with real IPs      localhost로 입력하면 안됨
    oids = ["1.3.6.1.2.1.1.4.0", "1.3.6.1.2.1.1.5.0", "1.3.6.1.2.1.1.6.0", "1.3.6.1.2.1.1.7.0"]   # [SNMPv2-MIB::sysDescr.0, SNMPv2-MIB::sysName.0]

    start = time.time()

    # removing this loop will increase run time on average
    for host in hosts:
        manager.get(host, *oids, block=False, timeout=1)
        manager.get(host, *oids, block=False, timeout=1, next=True)

    for host in hosts:
        vars = manager.get(host, *oids)
        print(host)
        for var in vars:
            print(var)
            mqttConfig.mqClient.publish(topic='snmp/test', payload=str(var), qos=0) # 차후 json 형태로 바꿔야함

        # vars = manager.get(host, *oids, next=True)
        # for var in vars:
        #     print(var)

    end = time.time()
    print("Took {} seconds".format(end - start))

except Timeout as e:
    print("Request for {} from host {} timed out".format(e, host))

finally:
    manager.close()

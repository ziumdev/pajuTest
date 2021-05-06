# import socket
# import sys
#
# port = 50000
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.bind(('', port))
#
# while 1:
#         data, addr = [s.recv(1024), s.recv(1024)]
#         print(data)


#reference ADDR : https://github.com/etingof/pysnmp/blob/master/examples/v3arch/asyncore/manager/ntfrcv/multiple-usm-users.py
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import logging

from pysnmp.proto.api import v2c


snmpEngine = engine.SnmpEngine()

TrapAgentAddress='127.0.0.1' #Trap listerner address
Port=50003  #trap listerner port

logging.basicConfig(filename='received_traps.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

logging.info("Agent is listening SNMP Trap on "+TrapAgentAddress+" , Port : " +str(Port))
logging.info('--------------------------------------------------------------------------')

print("Agent is listening SNMP Trap on "+TrapAgentAddress+" , Port : " +str(Port))

config.addTransport(
    snmpEngine,
    udp.domainName + (1,),
    udp.UdpTransport().openServerMode((TrapAgentAddress, Port))
)

# SNMPv3/USM setup
# SNMPv3으로 정보를 가져오기 위한 usm 정보 필요.
# user: usr-md5-des, auth: MD5, priv DES, securityEngineId: 8000000001020304
# this USM entry is configured for TRAP receiving purposes

# trap test 명령어
# sudo snmptrap -v3 -u usr-md5-des -l authPriv -A authkey1 -X privkey1 -e 8000000001020304 127.0.0.1:50003 123 1.3.6.1.6.3.1.1.5.1
config.addV3User(
    snmpEngine, 'usr-md5-des',
    config.usmHMACMD5AuthProtocol, 'authkey1',
    config.usmDESPrivProtocol, 'privkey1',
    securityEngineId=v2c.OctetString(hexValue='8000000001020304')
)

# user: usr-md5-none, auth: MD5, priv NONE, securityEngineId: 8000000001020304
# this USM entry is configured for TRAP receiving purposes
config.addV3User(
    snmpEngine, 'usr-md5-none',
    config.usmHMACMD5AuthProtocol, 'authkey1',
    securityEngineId=v2c.OctetString(hexValue='8000000001020304')
)

# user: usr-sha-aes128, auth: SHA, priv AES, securityEngineId: 8000000001020304
# this USM entry is configured for TRAP receiving purposes
config.addV3User(
    snmpEngine, 'usr-sha-aes128',
    config.usmHMACSHAAuthProtocol, 'authkey1',
    config.usmAesCfb128Protocol, 'privkey1',
    securityEngineId=v2c.OctetString(hexValue='8000000001020304')
)


#Configure community here
# config.addV1System(snmpEngine, 'my-area', 'test') SNMP v3로 날릴 때는 이 부분을 주석처리하고, SNMP v2는 주석을 개방하고 v3 유저정보를 삭제함


def cbFun(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
    print("Received new Trap message");
    logging.info("Received new Trap message")
    for name, val in varBinds:
        logging.info('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
        print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))

    logging.info("==== End of Incoming Trap ====")


ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)

try:
    snmpEngine.transportDispatcher.runDispatcher()
except Exception as e:
    snmpEngine.transportDispatcher.closeDispatcher()
    print(e)
    raise

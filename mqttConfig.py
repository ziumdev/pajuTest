import paho.mqtt.client as mqtt

brkIp = '192.168.0.103'
brkPort = 1883
brkKeepalive = 60

mqClient=mqtt.Client()
mqClient.max_inflight_messages_set(inflight=20)
mqClient.message_retry_set(retry=5)
try:
    mqClient.connect(host=brkIp, port=brkPort, keepalive=brkKeepalive, bind_address="")
    # mqClient.reconnect()
except ConnectionError as e:
    print(e)
    print("cannot connect with MQTT server")

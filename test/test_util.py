from src.mqtt_bridge.bridge import RosToMqttBridge
from src.mqtt_bridge.util import extract_values, populate_instance, lookup_object, instantiate_message
from sensor_msgs.msg import Temperature
from std_msgs.msg import Header
import pytest

def test_lookup_object():
    obj = lookup_object('src.mqtt_bridge.bridge:RosToMqttBridge', 'src.mqtt_bridge')
    assert obj == RosToMqttBridge

def test_extract_values():
    msg = Temperature(
        header=Header(),
        temperature=25.2,
        variance=0.0,
    )
    expected = {'header': {'stamp': {'secs': 0, 'nsecs': 0}, 'frame_id': '', 'seq': 0}, 'temperature': 25.2, 'variance': 0.0}
    actual = extract_values(msg)
    assert expected == actual


def test_populate_instance():
    msg_dict = {'header': {'stamp': {'secs': 0, 'nsecs': 0}, 'frame_id': '', 'seq': 0}, 'temperature': 25.2, 'variance': 0.0}
    msg = Temperature()
    populate_instance(msg_dict, msg)
    assert msg.temperature == 25.2
    assert msg.variance == 0.0

def test_instantiate_message_should_instantiate_if_message_correct_typed():
    inst = instantiate_message('sensor_msgs.msg:Temperature')
    assert inst._type == 'sensor_msgs/Temperature'

def test_instantiate_message_should_rise_an_error_if_message_incorrect_typed():
    with pytest.raises(TypeError):
        instantiate_message('src.mqtt_bridge.bridge:RosToMqttBridge')
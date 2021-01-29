# -*- coding: utf-8 -*-
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod

import inject
import paho.mqtt.client as mqtt
import rospy
import time

from .util import lookup_object, extract_values, populate_instance, instantiate_message
from .enricher import create_enricher

def create_bridge(factory, msg_type, topic_from, topic_to, **kwargs):
    u""" bridge generator function

    :param (str|class) factory: Bridge class
    :param (str|class) msg_type: ROS message type
    :param str topic_from: incoming topic path
    :param str topic_to: outgoing topic path
    :param (float|None) frequency: publish frequency
    :return Bridge: bridge object
    """
    if isinstance(factory, basestring):
        factory = lookup_object(factory)
    if not issubclass(factory, Bridge):
        raise ValueError("factory should be Bridge subclass")
    msg_type = instantiate_message(msg_type)
    time.sleep(10)
    return factory(
        topic_from=topic_from, topic_to=topic_to, msg_type=msg_type, **kwargs)


class Bridge(object):
    u""" Bridge base class

    :param mqtt.Client _mqtt_client: MQTT client
    :param _serialize: message serialize callable
    :param _deserialize: message deserialize callable
    """
    __metaclass__ = ABCMeta

    _mqtt_client = inject.attr(mqtt.Client)
    _serialize = inject.attr('serializer')
    _deserialize = inject.attr('deserializer')
    _extract_private_path = inject.attr('mqtt_private_path_extractor')


class RosToMqttBridge(Bridge):
    u""" Bridge from ROS topic to MQTT

    :param str topic_from: incoming ROS topic path
    :param str topic_to: outgoing MQTT topic path
    :param class msg_type: subclass of ROS Message
    :param (float|None) frequency: publish frequency
    """

    def __init__(self, topic_from, topic_to, msg_type, frequency=None, **kwargs):
        self._topic_from = topic_from
        self._topic_to = self._extract_private_path(topic_to)
        self._last_published = rospy.get_time()
        self._interval = 0 if frequency is None else 1.0 / frequency
        self._use_bytes = kwargs.get('use_bytes', False)
        self._enricher = create_enricher((topic_from, msg_type), self._callback_ros, kwargs.get('enricher', []))

    def _callback_ros(self, msg):
        rospy.logdebug("ROS received from {}".format(self._topic_from))
        now = rospy.get_time()
        if now - self._last_published >= self._interval:
            self._publish(msg)
            self._last_published = now

    def _publish(self, msg):
        payload = self._serialize(msg if self._enricher else extract_values(msg))
        if self._use_bytes:
            payload = bytearray(payload)
        self._mqtt_client.publish(topic=self._topic_to, payload=payload)

class MqttToRosBridge(Bridge):
    u""" Bridge from MQTT to ROS topic

    :param str topic_from: incoming MQTT topic path
    :param str topic_to: outgoing ROS topic path
    :param class msg_type: subclass of ROS Message
    :param (float|None) frequency: publish frequency
    :param int queue_size: ROS publisher's queue size
    """

    def __init__(self, topic_from, topic_to, msg_type, frequency=None,
                 queue_size=10, **kwargs):
        self._topic_from = self._extract_private_path(topic_from)
        self._topic_to = topic_to
        self._msg_type = msg_type
        self._queue_size = queue_size
        self._last_published = rospy.get_time()
        self._interval = None if frequency is None else 1.0 / frequency
        # Adding the correct topic to subscribe to
        self._mqtt_client.subscribe(self._topic_from)
        self._mqtt_client.message_callback_add(self._topic_from, self._callback_mqtt)
        self._publisher = rospy.Publisher(
            self._topic_to, self._msg_type, queue_size=self._queue_size)

    def _callback_mqtt(self, client, userdata, mqtt_msg):
        u""" callback from MQTT

        :param mqtt.Client client: MQTT client used in connection
        :param userdata: user defined data
        :param mqtt.MQTTMessage mqtt_msg: MQTT message
        """
        rospy.logdebug("MQTT received from {}".format(mqtt_msg.topic))
        now = rospy.get_time()

        if self._interval is None or now - self._last_published >= self._interval:
            try:
                ros_msg = self._create_ros_message(mqtt_msg)
                self._publisher.publish(ros_msg)
                self._last_published = now
            except Exception as e:
                rospy.logerr(e)

    def _create_ros_message(self, mqtt_msg):
        u""" create ROS message from MQTT payload

        :param mqtt.Message mqtt_msg: MQTT Message
        :return rospy.Message: ROS Message
        """
        msg_dict = self._deserialize(mqtt_msg.payload)
        return populate_instance(msg_dict, self._msg_type())


__all__ = ['create_bridge', 'Bridge', 'RosToMqttBridge', 'MqttToRosBridge']

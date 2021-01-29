# -*- coding: utf-8 -*-

from message_filters import Subscriber, ApproximateTimeSynchronizer
from .util import instantiate_message, extract_values
import functools

class Enricher(object):
    def __init__(self, source_topic, callback, enrich_config, **kwargs):
        source_topic, source_msg = source_topic
        self.__props_config = Enricher.__process_config(enrich_config)
        subscribers = list([ Subscriber(t.get('topic'), t.get('msg_inst')) for t in self.__props_config.values() ])
        subscribers.append(Subscriber(source_topic, source_msg))
        self.synchronizer = ApproximateTimeSynchronizer(subscribers, 2, 1, True)
        self.__source_msg = source_msg._type
        self.__callback = callback
        self.synchronizer.registerCallback(self.__enricherCallback)

    def __enricherCallback(self, *args):
        result_bag = dict()
        for message in args:
            if message._type == self.__source_msg:
                result_bag.update(extract_values(message)) 
            else:
                prop_config = self.__props_config[message._type]
                Enricher.__set_props(prop_config, result_bag, message)
        print(result_bag)
        self.__callback(result_bag)

    @staticmethod
    def __process_config(enrich_config):
        for x in enrich_config:
            x['msg_inst'] = instantiate_message(x.get('msg_type'))

        return dict(
            (
                x['msg_inst']._type, 
                { 
                    'msg_inst': x['msg_inst'],
                    'topic': x['topic'],
                    'source_props': x['source_props'], 
                    'target_props': x['target_props']
                }
            ) for x in enrich_config
        )
    
    @staticmethod
    def __set_props(prop_config, bag, msg):
        for s,t in zip(prop_config['source_props'], prop_config['target_props']):
            bag[t] = getattr(msg, s)

def create_enricher(source_topic, callback, enricher_config=None):
    return Enricher(source_topic, callback, enricher_config) if enricher_config else None

__all__ = ['create_enricher', 'Enricher']
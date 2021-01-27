# -*- coding: utf-8 -*-

from message_filters import Subscriber, ApproximateTimeSynchronizer

class Enricher(object)
    def __init__(self, source_topic, enrich_config, callback, **kwargs):
        self.__topics = topics
        self.__source_props = source_props
        self.__target_props = target_props
        subscribers = list([ Subscriber(t[0], t[1]) for t in enrich_topics ])
        subscribers.append(Subscriber(source_topic[0], source_topic[1]))
        self.synchronizer = ApproximateTimeSynchronizer(subscribers, 2, 1, True)
        self.__callback = callback
        self.synchronizer.registerCallback(self.__enricherCallback)

    def __enricherCallback(self, *args):
        print(args)

def create_enricher(source_topic, callback, enricher_config):
    return Enricher(source_topic, callback, enricher_config)

__all__ = ['create_enricher', 'Enricher']
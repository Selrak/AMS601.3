#!/usr/bin/env python3
#-*- Coding: utf-8 -*-

import json
import logging

version = "0.1"
logging.basicConfig(level = logging.DEBUG)

NATURE="nature"
OBJECT="object"
OBJECTS="objects"
RELATION="relation"
RELATIONS="relations"
EXTENDS="extends"
FROM="from"
TO="to"
PROPERTIES="properties"
DIRECTIONAL="directional"
LIBRARY="library"

class RPickle(object):
    @staticmethod
    def text_to_dict(text):
        return json.loads(text)
    @staticmethod
    def file_to_dict(filename):
        with open(filename, 'r') as myfile:
            text = myfile.read()
            return RPickle.text_to_dict(text)


class RException(Exception):
    pass

class RObject(object):
    def __init__(self):
        self.prototype = None
        self.objects = {}
        self.relations = {}
        self.properties = {}

    def __repr__(self):
        return self.objects.__repr__() + "\n" + self.relations.__repr__()

    @staticmethod
    def parse(data):
        obj = RObject()

        if not data.has_key(NATURE) or data[NATURE] != OBJECT:
            raise RException("object must have a nature of object")


        if data.has_key(EXTENDS) and data[EXTENDS] is not None:
            prototype_name = data[EXTENDS]
            logging.debug("TODO: implement extends")

        if data.has_key(OBJECTS) and data[OBJECTS] is not None:
            objects = data[OBJECTS]
            for name in objects:
                logging.debug("loading object " + name)
                obj.objects[name] = RObject.parse(objects[name])

        if data.has_key(RELATIONS) and data[RELATIONS] is not None:
            relations = data[RELATIONS]
            for name in relations:
                logging.debug("loading relation " + relation)
                obj.relations[name] = RRelation.parse(relations[name])

        if data.has_key(PROPERTIES) and data[PROPERTIES] is not None:
            properties = data[PROPERTIES]
            for name in properties:
                logging.debug("loading property " + property)
                obj.properties[name] = properties[name]

        return obj

class RRelation(object):
    def __self__(self):
        self.prototype = None
        self.from_ids = []
        self.to_ids = []
        self.directional = None
        self.properties = []
    @staticmethod
    def parse(data):
        relation = RRelation()

        if not data.has_key(NATURE) or data[NATURE] != RELATION:
            raise RException("relation must have nature of relation")

        if data.has_key(EXTENDS) and data[EXTENDS] is not None:
            relation.prototype = data[EXTENDS]
            logging.debug("todo: implement extends")

        if data.has_key(DIRECTIONAL) and data[DIRECTIONAL] is not None:
            relation.directional = data[DIRECTIONAL]

        for id in data[FROM]:
            logging.debug("todo: implement relation from")
            relation.from_ids += [id]

        for id in data[TO]:
            logging.debug("todo: implement relation to")
            relation.to_ids += [id]

        return relation

class RModel(RObject):
    @staticmethod
    def parse(data):
        model = RObject.parse(data)

        if data.has_key(LIBRARY) and data[LIBRARY] is not None:
            logging.debug("library field is not empty, loading library")
            library = RPickle.file_to_dict(data[LIBRARY])

            if library[NATURE] != LIBRARY:
                raise RException("library must have nature of library")

            library[NATURE] = OBJECT
            library = RObject.parse(library)

            model.objects.update(library.objects)
            model.relations.update(library.relations)

        return model

logging.info('loading rauzy module ' + version)

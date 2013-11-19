#!/usr/bin/env python3
#-*- Coding: utf-8 -*-

import json
import logging
import pprint

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

def json_pretty_format(js):
    return json.dumps(js, sort_keys=True, indent=4, cls=REncoder)

class REncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

class RPickle(object):
    "Persistance layer utility class"
    @staticmethod
    def text_to_dict(text):
        return json.loads(text)
    @staticmethod
    def file_to_dict(filename):
        with open(filename, 'r') as myfile:
            text = myfile.read()
            return RPickle.text_to_dict(text)

class RException(Exception):
    "Base exception class for the Rauzy language project"
    pass

class REntity(object):
    "Base entity object that contains methods common to RObject, RRelation and any other object of a similar structure"
    def get_relation(self, name):
        try:
            return self.relations[name]
        except KeyError:
            rel = None
            for obj_name in self.objects:
                     rel = self.objects[obj_name].get_relation(name)
                     if rel is not None:
                         break
            return rel

    def get_object(self, name):
        try:
            return self.objects[name]
        except KeyError:
            obj = None
            for obj_name in self.objects:
                     obj = self.objects[obj_name].get_object(name)
                     if obj is not None:
                         break
            return obj

    def get_property(self, name):
        try:
            return self.properties[name]
        except KeyError:
            if self.proto is not None:
                return self.proto.get_property(name)
        return None


class RObject(REntity):
    "RObject represents Rauzy object"
    def __init__(self):
        self.proto_name = None
        self.proto = None
        self.objects = {}
        self.relations = {}
        self.properties = {}

    def __repr__(self):
        model = {"objects": self.objects,
                "relations": self.relations,
                "properties": self.properties,
                "extends": self.proto_name}
        return json_pretty_format(model)

    # method to recursively traverse the object
    # tree and substitute string extends, from and to
    # fields with actual references (to be done on
    # second pass when whole the structure of the model is built
    def update_references(self, root):
        if self.proto_name is not None:
            self.proto = root.get_object(self.proto_name)
            if self.proto is None:
                raise RException("proto_name " + self.proto_name + " cannot be found")
        for obj_name, obj in self.objects.iteritems():
            obj.update_references(root)
        for rel_name, rel in self.relations.iteritems():
            rel.update_references(root)

    @staticmethod
    def parse(data):
        obj = RObject()

        if not data.has_key(NATURE) or data[NATURE] != OBJECT:
            raise RException("object must have a nature of object")

        if data.has_key(EXTENDS) and data[EXTENDS] is not None:
            obj.proto_name = data[EXTENDS]

        if data.has_key(RELATIONS) and data[RELATIONS] is not None:
            relations = data[RELATIONS]
            for name in relations:
                logging.debug("loading relation " + name)
                obj.relations[name] = RRelation.parse(relations[name])

        if data.has_key(OBJECTS) and data[OBJECTS] is not None:
            objects = data[OBJECTS]
            for name in objects:
                logging.debug("loading object " + name)
                obj.objects[name] = RObject.parse(objects[name])

        if data.has_key(PROPERTIES) and data[PROPERTIES] is not None:
            properties = data[PROPERTIES]
            for name in properties:
                logging.debug("loading property " + name)
                obj.properties[name] = properties[name]

        return obj

class RRelation(REntity):
    "RRelation represents Rauzy relation"
    def __init__(self):
        self.proto_name = None
        self.proto = None
        self.from_ids = []
        self.to_ids = []
        self.directional = None
        self.properties = {}

    def __repr__(self):

        model = {"extends": self.proto_name,
                "from": self.from_ids,
                "to": self.to_ids,
                "directional": self.directional,
                "properties": self.properties}
        return json_pretty_format(model)

    def update_references(self, root):
        if self.proto_name is not None:
            self.proto = root.get_relation(self.proto_name)
            if self.proto is None:
                raise RException("relation " + self.proto_name + " cannot be found")

    @staticmethod
    def parse(data):
        relation = RRelation()

        if not data.has_key(NATURE) or data[NATURE] != RELATION:
            raise RException("relation must have nature of relation")

        if data.has_key(EXTENDS) and data[EXTENDS] is not None:
            relation.proto_name = data[EXTENDS]
            logging.debug("todo: implement extends")

        if data.has_key(DIRECTIONAL) and data[DIRECTIONAL] is not None:
            relation.directional = data[DIRECTIONAL]

        if data.has_key(PROPERTIES) and data[PROPERTIES] is not None:
            properties = data[PROPERTIES]
            for name in properties:
                logging.debug("loading property " + name)
                obj.properties[name] = properties[name]

        if data.has_key(FROM) and data[FROM] is not None:
            from_ids = data[FROM]
            for id in from_ids:
                logging.debug("todo: implement relation from")
                relation.from_ids += [id]
        else:
            raise RException("relation must have 'from'")

        if data.has_key(TO) and data[TO] is not None:
            to_ids = data[TO]
            for id in to_ids:
                logging.debug("todo: implement relation to")
                relation.to_ids += [id]
        else:
            raise RException("relation must have 'to'")

        return relation

class RModel(RObject):
    "RModel encapsulates whole the model and allows linking between objects and relation (including amoung relations and objects)"
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

        model.update_references(model)

        return model

logging.info('loading rauzy module ' + version)

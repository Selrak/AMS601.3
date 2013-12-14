#!/usr/bin/env python3
#-*- Coding: utf-8 -*-

import json
import logging
import copy

version = "0.1"
logging.basicConfig(level=logging.DEBUG)

NATURE = "nature"
OBJECT = "object"
OBJECTS = "objects"
RELATION = "relation"
RELATIONS = "relations"
EXTENDS = "extends"
FROM = "from"
TO = "to"
PROPERTIES = "properties"
DIRECTIONAL = "directional"
LIBRARY = "library"


class REncoder(json.JSONEncoder):
    def default(self, o):
        d = o.__dict__.copy()
        block = ("id_to_obj", "extends_ref")
        for key in block:
            try:
                del d[key]
            except KeyError:
                pass
        substitutions = (("from_ids", "from"), ("to_ids", "to"))
        for f, t in [(v[0], v[1]) for v in substitutions]:
            if f in d:
                d[t] = d.pop(f)
        return d


class RPickle(object):
    """Persistence layer utility class"""

    @staticmethod
    def text_to_dict(text):
        return json.loads(text)

    @staticmethod
    def file_to_text(filename):
        with open(filename, 'r') as myfile:
            text = myfile.read()
            return text

    @staticmethod
    def file_to_dict(filename):
        text = RPickle.file_to_text(filename)
        return RPickle.text_to_dict(text)

    @staticmethod
    def to_text(rentity):
        return RPickle.json_pretty_format(rentity)

    @staticmethod
    def text_to_file(filename, text):
        with open(filename, 'w') as myfile:
            myfile.write(text)

    @staticmethod
    def json_pretty_format(js):
        return json.dumps(js, sort_keys=True, indent=4, cls=REncoder)


class RException(Exception):
    """Base exception class for the Rauzy language project"""
    pass


class REntity(object):
    """Base entity object that contains methods common to RObject, RRelation
    and any other object of a similar structure"""

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
            if self.extends_ref is not None:
                return self.extends_ref.get_property(name)
        return None


class RObject(REntity):
    """RObject represents Rauzy object"""

    def __init__(self):
        self.nature = "object"
        self.extends = None
        self.extends_ref = None
        self.objects = {}
        self.relations = {}
        self.properties = {}

    def __repr__(self):
        return RPickle.json_pretty_format(self)

    # method to recursively traverse the object
    # tree and substitute string extends, from and to
    # fields with actual references (to be done on
    # second pass when whole the structure of the model is built
    def update_references(self, root=None):
        if root is None:
            root = self
        if self.extends is not None:
            self.extends_ref = root.get_object(self.extends)
            if self.extends_ref is None:
                raise RException("extends " + self.extends + " cannot be found")
        for obj_name, obj in self.objects.items():
            obj.update_references(root)
        for rel_name, rel in self.relations.items():
            rel.update_references(root)

    @staticmethod
    def parse(data):
        obj = RObject()

        if not NATURE in data or data[NATURE] != OBJECT:
            raise RException("object must have a nature of object")

        if EXTENDS in data and data[EXTENDS] is not None:
            obj.extends = data[EXTENDS]

        if RELATIONS in data and data[RELATIONS] is not None:
            relations = data[RELATIONS]
            for name in relations:
                logging.debug("loading relation " + name)
                obj.relations[name] = RRelation.parse(relations[name])

        if OBJECTS in data and data[OBJECTS] is not None:
            objects = data[OBJECTS]
            for name in objects:
                logging.debug("loading object " + name)
                obj.objects[name] = RObject.parse(objects[name])

        if PROPERTIES in data and data[PROPERTIES] is not None:
            properties = data[PROPERTIES]
            for name in properties:
                logging.debug("loading property " + name)
                obj.properties[name] = properties[name]

        return obj


class RRelation(REntity):
    """"RRelation represents Rauzy relation"""

    def __init__(self):
        self.nature = "relation"
        self.extends = None
        self.extends_ref = None
        self.id_to_obj = {}
        self.from_ids = []
        self.to_ids = []
        self.directional = None
        self.properties = {}

    def __repr__(self):
        return RPickle.json_pretty_format(self)

    def update_references(self, root=None):
        if root is None:
            root = self
        if self.extends is not None:
            self.extends_ref = root.get_relation(self.extends)
            if self.extends_ref is None:
                raise RException("relation " + self.extends + " cannot be found")
        for id in self.from_ids:
            obj = root.get_object(id)
            if obj is None:
                raise RException("object " + id + " cannot be found")
            self.id_to_obj[id] = obj


    @staticmethod
    def parse(data):
        relation = RRelation()

        if not NATURE in data or data[NATURE] != RELATION:
            raise RException("relation must have nature of relation")

        if EXTENDS in data and data[EXTENDS] is not None:
            relation.extends = data[EXTENDS]

        if DIRECTIONAL in data and data[DIRECTIONAL] is not None:
            relation.directional = data[DIRECTIONAL]

        if PROPERTIES in data and data[PROPERTIES] is not None:
            properties = data[PROPERTIES]
            for name in properties:
                logging.debug("loading property " + name)
                relation.properties[name] = properties[name]

        if FROM in data and data[FROM] is not None:
            from_ids = data[FROM]
            for id in from_ids:
                relation.from_ids += [id]

        if TO in data and data[TO] is not None:
            to_ids = data[TO]
            for id in to_ids:
                relation.to_ids += [id]

        return relation


class RModel(RObject):
    """RModel encapsulates whole the model and allows linking between objects and relation"""

    def __init__(self, obj=RObject()):
        super().__init__()
        self.__dict__ = obj.__dict__
        self.library = ""

    @staticmethod
    def parse(data):
        model = RModel(RObject.parse(data))

        if LIBRARY in data and data[LIBRARY] is not None:
            logging.debug("library field is not empty, loading library")
            library = RPickle.file_to_dict(data[LIBRARY])
            model.library = data[LIBRARY]
            model.load_library(library)

        model.update_references(model)
        return model

    def load_library(self, library):
        if library[NATURE] != LIBRARY:
            raise RException("library must have nature of library")

        library[NATURE] = OBJECT
        library = RObject.parse(library)

        self.objects.update(library.objects)
        self.relations.update(library.relations)


    def compare(self, other):
        return RModelComparison.compare_object(self, other)

    def flatten(self):
        return RModelFlattening.flatten(self)

    def abstract(self, levels):
        return RModelAbstraction.abstract(self, levels)

class RModelComparison(object):
    @staticmethod
    def key_changes(keys1, keys2):
        added = []
        deleted = []
        common = []

        for k in keys1:
            if k in keys2:
                common.append(k)
            else:
                deleted.append(k)
        for k in keys2:
            if k not in keys1:
                added.append(k)

        return added, deleted, common

    @staticmethod
    def print_added(nature, path):
        print(nature + " " + path + " was added")

    @staticmethod
    def print_removed(nature, path):
        print(nature + " " + path + " was deleted")

    @staticmethod
    def compare_relation(rel1, rel2, path=''):

        to_added, to_removed, to_common \
            = RModelComparison.key_changes(rel1.to_ids, rel2.to_ids)

        from_added, from_removed, from_common \
            = RModelComparison.key_changes(rel1.from_ids, rel2.from_ids)

        for k in to_added:
            RModelComparison.print_added("relation 'to'", path + '/' + k)
        for k in from_added:
            RModelComparison.print_added("relation 'from'", path + '/' + k)
        for k in to_removed:
            RModelComparison.print_removed("relation 'to'", path + '/' + k)
        for k in from_removed:
            RModelComparison.print_removed("relation 'from'", path + '/' + k)

        RModelComparison.compare_properties(rel1.properties, rel2.properties, path)

    @staticmethod
    def compare_properties(props1, props2, path=''):
        prop_added, prop_removed, prop_common \
            = RModelComparison.key_changes(list(props1.keys()), list(props2.keys()))

        for k in prop_added:
            RModelComparison.print_added("property", path + '/' + k)

        for k in prop_removed:
            RModelComparison.print_removed("property", path + '/' + k)

        for k in prop_common:
            if props1[k] != props2[k]:
                print("property " + path + '/' + k + " changed from " + props1[k] + " to " + props2[k])

    @staticmethod
    def compare_object(model1, model2, path=''):

        obj_added, obj_removed, obj_common \
            = RModelComparison.key_changes(list(model1.objects.keys()), list(model2.objects.keys()))

        rel_added, rel_removed, rel_common \
            = RModelComparison.key_changes(list(model1.relations.keys()), list(model2.relations.keys()))

        for k in obj_added + rel_added:
            RModelComparison.print_added("object", path + '/' + k)

        for k in obj_removed + rel_removed:
            RModelComparison.print_removed("object", path + '/' + k)

        for k in obj_common:
            RModelComparison.compare_object(model1.objects[k], model2.objects[k], path + '/' + k)

        for k in rel_common:
            RModelComparison.compare_relation(model1.relations[k], model2.relations[k], path + '/' + k)

        RModelComparison.compare_properties(model1.properties, model2.properties, path)

class RModelFlattening(object):
    @staticmethod
    def process(model_ref, model):
        try:
            for obj_name in list(model_ref.objects.keys()):
                obj = model_ref.objects[obj_name]
                RModelFlattening.process(obj, model)
                model.objects[obj_name] = model_ref.objects.pop(obj_name)
        except AttributeError:
            pass

        try:
            for rel_name in list(model_ref.relations.keys()):
                rel = model_ref.relations[rel_name]
                RModelFlattening.process(rel, model)
                model.relations[rel_name] = model_ref.relations.pop(rel_name)
        except AttributeError:
            pass

        try:
            for prop_name in list(model_ref.properties.keys()):
                model.properties[prop_name] = model_ref.properties.pop(prop_name)
        except AttributeError:
            pass

    @staticmethod
    def flatten(model_ref):
        model_ref = copy.deepcopy(model_ref)
        model = RModel()
        RModelFlattening.process(model_ref, model)
        return model


class RModelAbstraction(object):
    @staticmethod
    def process(model, level):
        if level > 0:
            try:
                for obj_name, obj in model.objects.items():
                    RModelAbstraction.process(obj, level - 1)
            except AttributeError:
                pass
            try:
                for rel_name, rel in model.relations.items():
                    RModelAbstraction.process(rel, level - 1)
            except AttributeError:
                pass
        else:
            model.objects = {}
            model.relations = {}
            model.properties = {}

    @staticmethod
    def abstract(model_ref, levels):
        model = copy.deepcopy(model_ref)
        RModelAbstraction.process(model, levels)
        return model


logging.info('loading Rauzy module ' + version)

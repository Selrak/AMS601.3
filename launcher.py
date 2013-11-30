#!/usr/bin/env python3
#-*- Coding: utf-8 -*-

from rauzy import RModel, RPickle, RObject, RRelation
from unittest import TestCase
import logging

logging.basicConfig(level=logging.DEBUG)


class Test(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test0(self):
        root = """
        {
            "nature": "object",
            "extends": null,
            "objects": {},
            "relations": {},
            "properties": {
                "prop1": "value1",
                "prop2": "value2"
                },
            "library": "./inputFileExamples/library.json"
        }
        """
        model = RModel.parse(RPickle.text_to_dict(root))
        logging.debug(model)

    def test1(self):
        root = """
        {
            "nature": "object",
            "extends": "object1",
            "objects": {
                "obj1": {
                    "nature": "object",
                    "extends": "object1",
                    "properties": {
                        "prop_child1": "prop_child1_value",
                        "prop_child2": "prop_child2_value"
                    },
                    "relations": {
                            "internal_relation1": {
                            "nature": "relation",
                            "from": [],
                            "to": []
                            }
                        }
                },
                "obj3": {
                    "nature": "object"
                }
            },
            "relations": {
                "rel1": {
                    "nature": "relation",
                    "extends": "relation1",
                    "from": ["obj1"],
                    "to": ["obj3"]
                }
            },
            "properties": {},
            "library": "./inputFileExamples/library.json"
        }
        """
        model = RModel.parse(RPickle.text_to_dict(root))
        self.assertIsNotNone(model.get_object("obj1"))
        self.assertIsNone(model.get_object("obj2"))
        self.assertIsNotNone(model.get_relation("rel1"))
        self.assertIsNone(model.get_relation("rel2"))
        logging.debug(model)

    def test2(self):
        root = RPickle.file_to_text("inputFileExamples/geo.json")
        model = RModel.parse(RPickle.text_to_dict(root))
        logging.debug(model)

    def test3(self):
        root = RPickle.file_to_text("inputFileExamples/sechecheveuxkekwa.json")
        model = RModel.parse(RPickle.text_to_dict(root))
        logging.debug(model)

    def test4(self):
        model = RModel()
        obj = RObject.parse(RPickle.text_to_dict("""
        {
            "nature": "object"
        }
        """))
        obj.properties["prop1"] = "property1"
        rel = RRelation.parse(RPickle.text_to_dict("""
        {
            "nature": "relation",
            "from": ["obj1"],
            "to": ["obj1"]
        }
        """))
        rel.properties["prop1"] = "property1"
        model.objects["obj1"] = obj
        model.relations["rel1"] = rel
        model.update_references()
        logging.debug(model)

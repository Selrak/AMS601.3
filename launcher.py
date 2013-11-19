#!/usr/bin/env python3
#-*- Coding: utf-8 -*-

from rauzy import RModel, RPickle
import unittest
import logging

logging.basicConfig(level = logging.DEBUG)

class Test(unittest.TestCase):
    def setUp(self):
        logging.debug("setUp")
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
                    }
                }
            },
            "relations": {
                "rel1": {
                    "nature": "relation",
                    "extends": "relation1",
                    "from": [],
                    "to": []
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


unittest.main()

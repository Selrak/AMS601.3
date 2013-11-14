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
        print(model)

    def test1(self):
        root = """
        {
            "nature": "object",
            "extends": null,
            "objects": {
                "obj1": {
                    "nature": "object"
                    }
                },
            "relations": {},
            "properties": {},
            "library": null
        }
        """
        model = RModel.parse(RPickle.text_to_dict(root))
        print(model)


unittest.main()

#!/usr/bin/env python3
#-*- Coding: utf-8 -*-

from unittest import TestCase, main
import logging

from rauzy import RModel, RPickle, RObject, RRelation


logging.basicConfig(level=logging.DEBUG)


class Test(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test0_basicparsing1(self):
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

    def test1_basicparsing2(self):
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

    def test2_example1(self):
        root = RPickle.file_to_text("inputFileExamples/geo.json")
        model = RModel.parse(RPickle.text_to_dict(root))
        logging.debug(model)

    def test3_example2(self):
        root = RPickle.file_to_text("inputFileExamples/sechecheveuxkekwa.json")
        model = RModel.parse(RPickle.text_to_dict(root))
        logging.debug(model)

    def test4_manual_model_building(self):
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

    def test5_abstract(self):
        root = RPickle.file_to_text("inputFileExamples/geo.json")
        model = RModel.parse(RPickle.text_to_dict(root))
        logging.debug(model.abstract(1))

    def test6_flatten(self):
        root = RPickle.file_to_text("inputFileExamples/geo.json")
        model = RModel.parse(RPickle.text_to_dict(root))
        logging.debug(model.flatten())

    def test7_comparison(self):
        root = RPickle.file_to_text("inputFileExamples/geo.json")
        model1 = RModel.parse(RPickle.text_to_dict(root))
        model2 = RModel.parse(RPickle.text_to_dict(root))

        # changing property in an object
        model1.properties["prop1"] = "old_prop"
        model2.properties["prop1"] = "changed_prop"

        # adding property in an object
        model2.properties["prop2"] = "new_prop"

        # removing property in an object
        del model2.objects["Europe"].properties["population"]

        # changing property in a relation
        model1.objects["Europe"].objects["France"].relations["postIndependencePeace"].properties["duration"] = "230 years"
        model2.objects["Europe"].objects["France"].relations["postIndependencePeace"].properties["duration"] = "100 years"

        # adding property in a relation
        model2.objects["Europe"].objects["France"].relations["postIndependencePeace"].properties["duration2"] = "300 years"

        # removing property in a relation
        del model2.objects["Europe"].objects["France"].relations["postIndependencePeace"].properties["treaty"]

        # todo: changes in objects, relations (incl. to and from)

        model1.compare(model2)


if __name__ == '__main__':
    main()

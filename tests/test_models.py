# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -----------------------------------------------------------
# Modified by DevOps Course Fall 2021 Squad - Inventory Team
# Members:
#      Chen, Peng-Yu | pyc305@nyu.edu | New York | UTC-5
#      Lai, Yu-Wen   | yl8332@nyu.edu | New York | UTC-5
#      Zhang, Haoran | hz2613@nyu.edu | New York | UTC-5
#      Wen, Xuezhou  | xw2447@nyu.edu | New York | UTC-5
#      Hung, Ginkel  | ch3854@nyu.edu | New York | UTC-5
#
# Resource URL: /inventory
# Description:
#      The inventory resource keeps track of how many of each product we
#      have in our warehouse. At a minimum it should reference a product and the
#      quantity on hand. Inventory should also track restock levels and the condition
#      of the item (i.e., new, open box, used). Restock levels will help you know
#      when to order more products. Being able to query products by their condition
#      (e.g., new, used) could be very useful.
# -----------------------------------------------------------

"""
Test cases for Inventory Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_models.py:TestInventoryModel
"""
import logging
import os
import unittest

from service import app
from service.models import Condition, DataValidationError, Inventory, db
from werkzeug.exceptions import NotFound

from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  I N V E N T O R Y   M O D E L   T E S T   C A S E S
######################################################################


class TestInventoryModel(unittest.TestCase):
    """ Test Cases for Inventory Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Inventory.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    def test_repr_of_an_inventory(self):
        product_id = 1
        condition = Condition.NEW
        inventory = Inventory(product_id=product_id,
                              condition=condition, quantity=2, restock_level=3)
        self.assertIsNot(inventory, None)
        self.assertEqual(
            str(inventory), f"<Inventory product_id=[{product_id}] with condition=[{condition}] condition>")

    def test_create_an_inventory(self):
        """ Create an inventory and assert that it exists """
        inventory = Inventory(
            product_id=1, condition=Condition.NEW, quantity=2, restock_level=3)
        self.assertTrue(inventory != None)
        self.assertEqual(inventory.product_id, 1)
        self.assertEqual(inventory.condition, Condition.NEW)
        self.assertEqual(inventory.quantity, 2)
        self.assertEqual(inventory.restock_level, 3)

    def test_update_inventory(self):
        """ Update an existing record in inventory """
        inventory = Inventory(
            product_id=1, condition=Condition.NEW, quantity=100, restock_level=40)
        inventory.create()
        orininal_product_id = inventory.product_id
        original_condition = inventory.condition
        inventory.quantity = 70
        inventory.restock_level = 50
        inventory.update()
        latest_inventory = Inventory.all()
        self.assertEqual(len(latest_inventory), 1)
        self.assertEqual(latest_inventory[0].product_id, orininal_product_id)
        self.assertEqual(latest_inventory[0].condition, original_condition)
        self.assertEqual(latest_inventory[0].quantity, 70)
        self.assertEqual(latest_inventory[0].restock_level, 50)

    def test_add_an_inventory(self):
        """ Create an inventory and add it to the database """
        inventories = Inventory.all()
        self.assertEqual(inventories, [])
        inventory = Inventory(
            product_id=1, condition=Condition.NEW, quantity=2, restock_level=3)
        self.assertTrue(inventory != None)
        self.assertEqual(inventory.product_id, 1)
        inventory.create()
        # Assert that it shows up in the database
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)

    def test_delete_an_inventory(self):
        """ Delete an inventory """
        inventory = InventoryFactory()
        inventory.create()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the inventory and make sure it isn't in the database
        inventory.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_find_by_pid_condition(self):
        """ Find an Inventory by [product_id] and [condition] """
        inventory = Inventory(
            product_id=123, condition=Condition.NEW, quantity=2, restock_level=10)
        if not Inventory.find_by_pid_condition(inventory.product_id, inventory.condition):
            inventory.create()
        result = Inventory.find_by_pid_condition(
            inventory.product_id, inventory.condition)
        self.assertIsNot(result, None)
        self.assertEqual(result.product_id, inventory.product_id)
        self.assertEqual(result.condition, inventory.condition)
        self.assertEqual(result.quantity, inventory.quantity)
        self.assertEqual(result.restock_level, inventory.restock_level)

    def test_find_by_pid(self):
        """ Find Inventory by [product_id] """
        inventory = Inventory(
            product_id=124, condition=Condition.NEW, quantity=1, restock_level=10)
        if not Inventory.find_by_pid_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=124, condition=Condition.USED, quantity=4)
        if not Inventory.find_by_pid_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventories = Inventory.find_by_pid(inventory.product_id)
        self.assertEqual(len(list(inventories)), 2)

    def test_find_by_condition(self):
        """ Find an Inventory by [condition] """
        inventory = Inventory(
            product_id=333, condition=Condition.NEW, quantity=1, restock_level=10)
        if not Inventory.find_by_pid_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=344, condition=Condition.NEW, quantity=1, restock_level=10)
        if not Inventory.find_by_pid_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventories = Inventory.find_by_condition(inventory.condition)
        self.assertEqual(len(list(inventories)), 2)

    def test_serialize_an_inventory(self):
        """Test serialization of an inventory"""
        inventory = InventoryFactory()
        data = inventory.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], inventory.product_id)
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], inventory.condition.name)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], inventory.quantity)
        self.assertIn("restock_level", data)
        self.assertEqual(data["restock_level"], inventory.restock_level)

    def test_deserialize_an_inventory(self):
        """ Test deserialization of an Inventory """
        data = {
            "product_id": 1,
            "condition": "NEW",
            "quantity": 2,
            "restock_level": 3,
        }
        inventory = Inventory()
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.product_id, 1)
        self.assertEqual(inventory.condition.name, "NEW")
        self.assertEqual(inventory.quantity, 2)
        self.assertEqual(inventory.restock_level, 3)

    def test_deserialize_missing_data(self):
        """ Test deserialization of an Inventory with missing data """
        data = {
            "product_id": 1,
            "quantity": 2,
            "restock_level": 3,
        }
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_gender(self):
        """ Test deserialization of bad condition attribute """
        test_inventory = InventoryFactory()
        data = test_inventory.serialize()
        data["condition"] = "new"  # wrong case
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

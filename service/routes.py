# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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

"""
Inventory Store Service

Paths:
------
GET /inventory
    - Returns a list all of the Inventory
GET /inventory/{int:product_id}/condition/{enum:condition}
    - Returns the Inventory with the given product_id and condition

POST /inventory
    - Creates a new Inventory record in the database

PUT /inventory/{int:product_id}/condition/{enum:condition}
    - Updates the Inventory with the given product_id and condition

DELETE /inventory/{int:product_id}/condition/{enum:condition}
    - Deletes the Inventory with the given product_id and condition
"""

from . import app  # Import Flask application

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL


@app.route("/")
def index():
    return "Hello, World!"
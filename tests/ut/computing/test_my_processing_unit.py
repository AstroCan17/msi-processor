# Copyright 2026 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import pytest
from eopf.product import EOGroup, EOProduct, EOVariable

# You might have to reformat the imports depending on the length
# of the package name that is given when generating your project.
from s2_msi_processor.computing.my_processing_unit import MyProcessingUnit


class MyProcessingUnitTest(unittest.TestCase):
    """My Processor Unit's Test

    This class contains several tests considered as unit tests.

    It is an example of how to code a unit test.
    """

    @pytest.mark.unit
    def test_my_processing_unit_nominal(self):
        """
        Unit test that call My Processing Unit.
        """

        # Initialize inputs
        product_a = EOProduct(name="PRODUCT.A")
        product_a["measurements"] = EOGroup()
        attrs = {"id": "001"}
        product_a["measurements/id"] = EOVariable(attrs=attrs)

        product_b = EOProduct(name="PRODUCT.B")
        product_b["measurements"] = EOGroup()
        attrs = {"id": "002"}
        product_b["measurements/id"] = EOVariable(attrs=attrs)

        products = {"a": product_a, "b": product_b}

        # Run test
        myProcessingUnit = MyProcessingUnit()
        output_dict = myProcessingUnit.run(products, name="MY_PRODUCT.UNITTEST")
        output = output_dict["output"]

        # Expected Output
        expected_output_name = "MY_PRODUCT.UNITTEST"

        # Validate the returned object
        self.assertEqual(expected_output_name, output._name)
        self.assertEqual("001", output["measurements/PRODUCT.A/id"].attrs["id"])
        self.assertEqual("002", output["measurements/PRODUCT.B/id"].attrs["id"])

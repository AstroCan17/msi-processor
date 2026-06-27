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
from eopf.product.conveniences import init_product

# You might have to reformat the imports depending on the length
# of the package name that is given when generating your project.
from msi_processor.computing.my_processor import MyProcessor
from msi_processor.exceptions.errors import MyError
from msi_processor.exceptions.warnings import MyWarning


class MyProcessorTest(unittest.TestCase):
    """My Processor's Test

    This class contains several tests considered as unit tests.

    It is an example of how to code an unit test.
    """

    @pytest.mark.unit
    def test_my_processor_errors(self):
        """
        Unit test that call My Processor and expect an error.
        """

        # Run test for mandatory input
        myProcessor = MyProcessor()

        # Initialize inputs for mandatory input
        product_a: EOProduct = init_product("PRODUCT.A")
        products = {"a": product_a}

        # Run test for mandatory input
        myProcessor = MyProcessor()
        with self.assertRaises(MyError):
            myProcessor.run(products, missing_parameter="you should add name")

    @pytest.mark.unit
    def test_my_processor_nominal(self):
        """
        Unit test that call My Processor with a nominal run without any warnings.
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
        myProcessor = MyProcessor()
        output_dict = myProcessor.run(products, name="MY_PRODUCT.UNITTEST")
        output = output_dict["output"]

        # Expected Output
        expected_output_name = "MY_PRODUCT.UNITTEST"

        # Comparison
        self.assertEqual(expected_output_name, output._name)
        self.assertEqual("001", output["measurements/PRODUCT.A/id"].attrs["id"])
        self.assertEqual("002", output["measurements/PRODUCT.B/id"].attrs["id"])

    @pytest.mark.unit
    def test_my_processor_nominal_without_optional(self):
        """
        Unit test that call My Processor with a successful execution and raised warning.
        """

        # Initialize inputs
        product_a = EOProduct(name="PRODUCT.A")
        product_a["measurements"] = EOGroup()
        attrs = {"id": "001"}
        product_a["measurements/id"] = EOVariable(attrs=attrs)

        products = {"a": product_a}

        # Run test
        myProcessor = MyProcessor()
        with self.assertWarns(MyWarning):
            output_dict = myProcessor.run(products, name="MY_PRODUCT.UNITTEST")
            output = output_dict["output"]

        # Expected Output
        expected_output_name = "MY_PRODUCT.UNITTEST"

        # Comparison
        self.assertEqual(expected_output_name, output._name)
        self.assertEqual("001", output["measurements/PRODUCT.A/id"].attrs["id"])

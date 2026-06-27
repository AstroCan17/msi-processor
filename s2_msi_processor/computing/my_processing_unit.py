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

from collections.abc import Mapping
from typing import Any, Optional, cast

from eopf.computing.abstract import ADF, DataType, EOProcessingUnit
from eopf.product import EOGroup, EOProduct


class MyProcessingUnit(EOProcessingUnit):
    """My Processing Unit

    Methods
    -------
    run:
        Execute this processing unit.

    """

    def run(
        self,
        inputs: Mapping[str, Any],
        adfs: Optional[Mapping[str, ADF]] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> Mapping[str, DataType]:
        """Runs the processing unit

        A more complete description can be added here.

        Parameters
        ----------
        inputs: dict[str, DataType]
            all the product to process in this processing unit
        adfs: Optional[dict[str, ADF]]
            all the ADFs needed to process
        **kwargs: any
            any needed kwargs (parameters etc)

        Returns
        -------
        dict[str, DataType]

        Examples
        --------
        Usage examples can be added as Jupyter notebook cells.

        .. code-block:: python

          # All required imports
          from eopf.product import EOProduct
          from s2_msi_processor.computing.my_processing_unit import MyProcessingUnit

          # Simple example to demonstrate how to create and run the
          # processing unit.
          my_processing_unit = MyProcessingUnit()
          input = EOProduct("PRODUCT.A")
          input_dict: dict[str, DataType] = {"a": input}
          my_processing_unit.run(input_dict, name="MY_PRODUCT.UNITTEST")

        """

        # Create valid EOProduct
        # See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/quickstart/start-with-code.html#start-with-code
        # for more information
        output_product = EOProduct(kwargs["name"])
        output_product["measurements"] = EOGroup()
        output_dict: dict[str, DataType] = {"output": output_product}

        # Add mandatory groups to this empty product
        # Create a top level common structure by adding
        # measurements, quality and conditions groups to our product
        output_product["measurements"] = EOGroup()  # Mandatory group

        # Simulate some processing: This is only dummy code.
        for product_key in inputs:
            print("Input product key:", product_key)
            input_product = cast(EOProduct, inputs[product_key])
            print("Input product:", input_product.name, input_product)
            subgroup = EOGroup(product_key)
            output_product.measurements[input_product.name] = subgroup

            for attrKey in input_product.measurements.keys():
                print("Key/value:", attrKey, "=", input_product.measurements[attrKey])
                eoVariable = input_product.measurements[attrKey]
                subgroup[attrKey] = eoVariable

        return output_dict

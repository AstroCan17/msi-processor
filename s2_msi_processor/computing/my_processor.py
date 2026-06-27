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

import warnings
from typing import Any, Optional

from eopf.computing.abstract import ADF, DataType, EOProcessingUnit
from eopf.logging import EOLogging

# You might have to reformat the imports depending on the
# length of the package name that is given when generating your project.
from s2_msi_processor.computing.my_processing_unit import MyProcessingUnit
from s2_msi_processor.exceptions.errors import MyError
from s2_msi_processor.exceptions.warnings import MyWarning


class MyProcessor(EOProcessingUnit):
    """My Processor

    Methods
    -------
    run:
        Execute the processor.
    """

    def run(
        self,
        inputs: dict[str, DataType],
        adfs: Optional[dict[str, ADF]] = None,
        **kwargs: Any,
    ) -> dict[str, DataType]:
        """Runs the processor.

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
        This is an example demonstrating how doctest
        can be used to illustrate the usage of the source code.
        See https://numpydoc.readthedocs.io/en/latest/example.html
        for numpydoc examples.

        >>> from s2_msi_processor.computing.my_processor import (
        >>>    MyProcessor,
        >>> )
        >>> myProcessor = MyProcessor()
        >>> myProcessor.run()

        """
        logger = EOLogging().get_logger()
        my_processing_unit = MyProcessingUnit()

        logger.info("Validating input")
        # At least one product is expected
        if len(inputs) < 1:
            raise MyError("Missing mandatory input product for the processor run.")
        if "name" not in kwargs:
            raise MyError("Missing mandatory parameter for the processor run.")
        if len(inputs) < 2:
            warnings.warn("Missing optional product", MyWarning)

        logger.info("Running 'my processing unit'")
        product_dict = my_processing_unit.run(inputs, **kwargs)

        return product_dict

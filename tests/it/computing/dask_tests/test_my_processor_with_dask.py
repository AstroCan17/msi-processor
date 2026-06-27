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

import os
import unittest
import warnings

import dask.array as da
import pytest
from dask_gateway import Gateway
from eopf.logging import EOLogging

from msi_processor.exceptions.warnings import MyWarning


class MyProcessorDaskTest(unittest.TestCase):
    """My Processor's Test with Dask

    This class contains tests considered as integration tests.

    It is an example of how to code an integration test.

    The test demonstrates how to use a remote Dask cluster.
    The Dask environment variables must be set to access the Dask cluster.
    If the variables are not set, then the test will report a warning.
    Please see the source code for the required environment variables.
    """

    @pytest.mark.integration
    def test_my_processor_with_dask(self):
        """
        Integration test that runs a simple
        without any warning on a distributed Dask cluster.
        """

        logger = EOLogging().get_logger()

        useGateway = True
        msg = ""
        # The following Dask environment variables are required
        # to connect to the Dask cluster.
        # When the test is run by GitLab CI, these variables
        # must be set in the test environment using GitLab's WebUI.
        daskEnvVars = [
            "DASK_GATEWAY__ADDRESS",
            "DASK_GATEWAY__AUTH__TYPE",
            "DASK_GATEWAY__PROXY_ADDRESS",
            "DASK_GATEWAY__PUBLIC_ADDRESS",
            "JUPYTERHUB_API_TOKEN",
        ]
        for var in daskEnvVars:
            try:
                os.environ[var]
            except KeyError:
                useGateway = False
                msg = msg + "\n  Please set the '" + var + "' environment variable"

        if not useGateway:
            msg = "At least one mandatory environment variable is missing:" + msg
            logger.warning(msg)
            warnings.warn(msg, MyWarning)

        try:
            if useGateway:
                # The gateway is created based on the environment variables
                # checked above
                logger.info("Creating Dask gateway")
                gateway = Gateway()

                # The Dask cluster is deployed using a default image.
                # However, it is possible to specify the image to be used for the
                # scheduler and workers when creating the cluster.
                # In this example, the 'project template' image is used.
                # Please use the default one or specify your own dedicated image.
                image = "registry.eopf.copernicus.eu/sde/project-template:latest"
                logger.info("Creating Dask cluster, using image: %s", image)
                cluster = gateway.new_cluster(image=image)

                # To get the URL of the Dask dashboard
                logger.info("Cluster created, dashboard: %s", cluster.dashboard_link)
                cluster.scale(2)
                client = cluster.get_client()

            x = da.random.random((10000, 10000), chunks=(10000, 1000))
            y = x + x.T
            z = y[::2, 5000:].mean(axis=1)

            logger.info("Computing ...")
            array = z.compute()

            self.assertTrue(array[0] > 0.9 and array[0] < 1.1)
        finally:
            if useGateway:
                logger.info("Shutting down cluster")

                client.close()
                cluster.close()
                gateway.close()

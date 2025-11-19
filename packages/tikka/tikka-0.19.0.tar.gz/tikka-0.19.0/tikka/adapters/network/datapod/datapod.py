# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import annotations

import json

from tikka.adapters.network.datapod.connection import DataPodConnection
from tikka.adapters.network.datapod.profiles import DataPodProfiles
from tikka.domains.entities.datapod import DataPod
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.datapod.datapod import (
    NetworkDataPodException,
    NetworkDataPodInterface,
)


class NetworkDataPod(NetworkDataPodInterface):
    """
    NetworkDataPod class
    """

    def __init__(self):
        """
        Init NetworkDataPod instance
        """
        self._connection = DataPodConnection()
        self._profiles = DataPodProfiles(self)

    @property
    def connection(self) -> DataPodConnection:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkDataPodInterface.connection.__doc__
        )
        return self._connection

    def get(self) -> DataPod:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkDataPodInterface.get.__doc__
        )
        if not self.connection.is_connected() or self.connection.client is None:
            raise NetworkDataPodException(NetworkConnectionError())

        connection: DataPodConnection = self.connection
        if not connection.is_connected() or connection.client is None:
            raise NetworkDataPodException(NetworkConnectionError())
        try:
            result = connection.execute_query(endpoint="/g1/block/current/_source")
        except Exception as exception:
            raise NetworkDataPodException(exception)

        # {
        #          "version" : 10,
        #          "currency" : "g1",
        #          "number" : 29003,
        #          "issuer" : "H1yTj77m946f52u64FvR36o9SmD38Ye2j1H4XCvwBFXK",
        #          "hash" : "0000024FD141E2DA5E3BCAC15CD558EF47BD9CB38DE022F2E0E8727AA885FCD4",
        #          "medianTime" : 1498016342,
        #          "membersCount" : 161,
        #          "monetaryMass" : 10533000,
        #          "unitbase" : 0,
        #          "dividend" : null,
        #          "txCount" : 1,
        #          "txAmount" : 2500,
        #          "txChangeCount" : 0,
        #          "certCount" : 0
        #        }
        data = json.loads(result)

        return DataPod(self.connection.url, data["number"])

    def get_genesis_hash(self) -> str:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkDataPodInterface.get_genesis_hash.__doc__
        )
        if not self.connection.is_connected() or self.connection.client is None:
            raise NetworkDataPodException(NetworkConnectionError())

        connection: DataPodConnection = self.connection
        if not connection.is_connected() or connection.client is None:
            raise NetworkDataPodException(NetworkConnectionError())
        try:
            result = connection.execute_query(endpoint="/g1/block/0/_source")
        except Exception as exception:
            raise NetworkDataPodException(exception)

        #
        # {
        #          "version" : 10,
        #          "currency" : "g1",
        #          "number" : 29003,
        #          "issuer" : "H1yTj77m946f52u64FvR36o9SmD38Ye2j1H4XCvwBFXK",
        #          "hash" : "0000024FD141E2DA5E3BCAC15CD558EF47BD9CB38DE022F2E0E8727AA885FCD4",
        #          "medianTime" : 1498016342,
        #          "membersCount" : 161,
        #          "monetaryMass" : 10533000,
        #          "unitbase" : 0,
        #          "dividend" : null,
        #          "txCount" : 1,
        #          "txAmount" : 2500,
        #          "txChangeCount" : 0,
        #          "certCount" : 0
        #        }
        data = json.loads(result)

        return data["hash"].lower()

    @property
    def profiles(self) -> DataPodProfiles:
        """
        Return DataPodProfilesInterface instance

        :return:
        """
        return self._profiles

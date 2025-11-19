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
from gql import gql

from tikka.adapters.network.indexer.accounts import IndexerAccounts
from tikka.adapters.network.indexer.connection import IndexerConnection
from tikka.adapters.network.indexer.identities import IndexerIdentities
from tikka.adapters.network.indexer.transfers import IndexerTransfers
from tikka.domains.entities.indexer import Indexer
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.indexer.indexer import (
    NetworkIndexerException,
    NetworkIndexerInterface,
)


class NetworkIndexer(NetworkIndexerInterface):
    """
    NetworkIndexer class
    """

    def __init__(self):
        """
        Init NetworkIndexer instance
        """
        self._connection = IndexerConnection()
        self._transfers = IndexerTransfers(self)
        self._identities = IndexerIdentities(self)
        self._accounts = IndexerAccounts(self)

    @property
    def connection(self) -> IndexerConnection:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkIndexerInterface.connection.__doc__
        )
        return self._connection

    def get(self) -> Indexer:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkIndexerInterface.get.__doc__
        )
        if not self.connection.is_connected() or self.connection.client is None:
            raise NetworkIndexerException(NetworkConnectionError())

        query = gql(
            """
            query {
                blocks (
                    orderBy: HEIGHT_DESC
                    first: 1
                ) {
                    nodes {
                        height
                    }
                }
            }
            """
        )
        try:
            result = self.connection.client.execute(query)
        except Exception as exception:
            raise NetworkIndexerException(exception)

        last_block = result["blocks"]["nodes"][0]["height"]
        return Indexer(self.connection.url, block=last_block)

    def get_genesis_hash(self) -> str:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkIndexerInterface.get_genesis_hash.__doc__
        )
        if not self.connection.is_connected() or self.connection.client is None:
            raise NetworkIndexerException(NetworkConnectionError())

        query = gql(
            """
            query {
                blocks (
                    filter: {
                      height: {
                        equalTo: 0
                      }
                      }
                    
                ) {
                    nodes {
                        hash
                    }
                }
            }
            """
        )
        try:
            result = self.connection.client.execute(query)
        except Exception as exception:
            raise NetworkIndexerException(exception)
        raw_hash = result["blocks"]["nodes"][0]["hash"]
        return f"0{raw_hash[1:]}"

    @property
    def identities(self) -> IndexerIdentities:
        """
        Return IndexerIdentities instance

        :return:
        """
        return self._identities

    @property
    def transfers(self) -> IndexerTransfers:
        """
        Return IndexerTransfers instance

        :return:
        """
        return self._transfers

    @property
    def accounts(self) -> IndexerAccounts:
        """
        Return IndexerAccounts instance

        :return:
        """
        return self._accounts

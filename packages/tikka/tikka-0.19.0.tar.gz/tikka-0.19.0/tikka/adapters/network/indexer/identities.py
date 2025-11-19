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

from typing import Dict, List

from gql import gql

from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.indexer.identities import (
    IndexerIdentitiesException,
    IndexerIdentitiesInterface,
)


class IndexerIdentities(IndexerIdentitiesInterface):
    """
    IndexerIdentities class
    """

    def get_identity_name(self, identity_index: int) -> str:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexerIdentitiesInterface.get_identity_name.__doc__
        )
        if (
            not self.indexer.connection.is_connected()
            or self.indexer.connection.client is None
        ):
            raise IndexerIdentitiesException(NetworkConnectionError())

        query = f"""
                query {{
                    identities(
                        filter: {{
                            index: {{
                                equalTo: {identity_index}
                             }}
                        }}
                        ) {{
                            nodes {{
                                name
                            }}
                    }}
                }}
                """

        try:
            result = self.indexer.connection.client.execute(gql(query))
        except Exception as exception:
            raise IndexerIdentitiesException(exception)

        #
        #    {
        #         "identity": [
        #             {
        #                 "name": "vit"
        #             }
        #         ]
        #     }
        #
        return result["identities"]["nodes"][0]["name"]

    def get_identity_names(self, index_list: List[int]) -> Dict[int, str]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexerIdentitiesInterface.get_identity_names.__doc__
        )
        if (
            not self.indexer.connection.is_connected()
            or self.indexer.connection.client is None
        ):
            raise IndexerIdentitiesException(NetworkConnectionError())

        query = """
            query GetNamesByIndex($indices: [Int!]!) {
                    identities(filter: { index: { in: $indices } }) {
                        nodes{
                          index
                          name
                        }
                        
                    }
                }
                """

        variables = {"indices": index_list}
        try:
            result = self.indexer.connection.client.execute(
                gql(query), variable_values=variables
            )
        except Exception as exception:
            raise IndexerIdentitiesException(exception)

        #
        #    {
        #   "data": {
        #     "identities": {
        #       "nodes": [
        #         {
        #           "index": 1,
        #           "name": "Alfybe"
        #         },
        #         {
        #           "index": 2,
        #           "name": "AnneAmbles"
        #         },
        #         {
        #           "index": 3,
        #           "name": "Ariane"
        #         }
        #       ]
        #     }
        #   }
        # }
        #
        names = {}
        for row in result["identities"]["nodes"]:
            names[row["index"]] = row["name"]
        return names

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
import json

# import re
# from copy import copy
# from hashlib import sha256
from typing import Optional

from tikka.adapters.network.datapod.connection import DataPodConnection
from tikka.domains.entities.profile import Profile
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.datapod.profiles import (
    DataPodProfilesException,
    DataPodProfilesInterface,
)


class DataPodProfiles(DataPodProfilesInterface):
    """
    DataPodProfiles class
    """

    def get(self, address: str) -> Optional[Profile]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            DataPodProfilesInterface.get.__doc__
        )
        connection: DataPodConnection = self.datapod.connection
        if not connection.is_connected() or connection.client is None:
            raise DataPodProfilesException(NetworkConnectionError())
        try:
            result_string = connection.execute_query(
                endpoint=f"/user/profile/{address}/_source"
            )
        except Exception as exception:
            raise DataPodProfilesException(exception)
        #
        # {
        #    'title': 'Jean Dupond',
        #    'description': 'boulanger',
        #    'socials': [
        #       {
        #           'type': 'web',
        #           'url': 'http://jean.boulanger.fr'
        #        }
        #     ],
        #     'avatar': {
        #       '_content_type': 'image/png',
        #       '_content': 'iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAgAuOuLp3zkbkD/w8GeTbwGV2uCwAAAABJRU5ErkJggg=='
        #     },
        #     'time': 1584271238,
        #     'issuer': 'xxx',
        #     'hash': 'yyy',
        #     'signature': 'xYPDg==',
        #     'city': 'Paris, 75020',
        #     'geoPoint': {
        #       'lon': 1.0,
        #       'lat': 48.0
        #     },
        #     'version': 2
        #  }
        #

        # # check hash
        # # Regex pour supprimer "hash": "xxx" (avec différents formats d'espaces)
        # pattern1 = r"\"hash\"\s*:\s*\"[^\"]*\"\s*,?"
        # # Regex pour supprimer "signature": "xxx"
        # pattern2 = r"\"signature\"\s*:\s*\"[^\"]*\"\s*,?"
        #
        # # Supprimer les champs sensibles
        # cleaned_json = re.sub(pattern1, "", result_string, flags=re.MULTILINE)
        # cleaned_json = re.sub(pattern2, "", cleaned_json, flags=re.MULTILINE)
        #
        # # Nettoyer les virgules orphelines (qui pourraient casser le JSON)
        # cleaned_json = re.sub(r",\s*}", "}", cleaned_json)  # Virgule avant }
        # cleaned_json = re.sub(r",\s*,", ",", cleaned_json)  # Double virgule
        #
        # check_hash = sha256(cleaned_json.encode()).hexdigest()
        result = json.loads(result_string)
        # if check_hash != result["hash"].lower():
        #     return None

        # check signature

        return Profile(address=address, data=result)

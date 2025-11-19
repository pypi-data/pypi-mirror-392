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
import logging
from typing import Any, Dict, Optional

import urllib3

from tikka.interfaces.adapters.network.connection import ConnectionInterface
from tikka.interfaces.entities.Server import ServerInterface


class DataPodConnection(ConnectionInterface):
    """
    DataPodConnection class with urllib3 REST client
    """

    client: Optional[urllib3.PoolManager] = None

    def __init__(self) -> None:
        """
        Init DataPodConnection instance
        """
        self.client: Optional[urllib3.PoolManager] = None

    def connect(self, server: ServerInterface) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.connect.__doc__
        )
        self.url = server.url.rstrip("/")  # Nettoyer l'URL
        logging.debug(
            "CONNECTING TO DATAPOD %s......................................", self.url
        )

        # Créer le client HTTP
        self.client = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=5.0, read=10.0), retries=urllib3.Retry(3)
        )

        try:
            # Test de connexion avec une requête REST
            endpoint = f"{self.url}/node/summary"

            response = self.client.request("GET", endpoint)

            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {response.data.decode()}")

            result = json.loads(response.data.decode())

            # Vérifier la structure de la réponse
            if (
                "duniter" not in result
                or "status" not in result["duniter"]
                or result["duniter"]["status"] != 200
            ):
                self.client = None
                logging.debug(
                    "CONNECTION TO DATAPOD %s......................................FAILED !",
                    self.url,
                )
            else:
                logging.debug(
                    "CONNECTION TO DATAPOD %s......................................SUCCESS !",
                    self.url,
                )

        except Exception as exception:
            logging.exception(exception)
            self.client = None
            logging.debug(
                "CONNECTION TO DATAPOD %s......................................FAILED !",
                self.url,
            )

    def disconnect(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.disconnect.__doc__
        )
        if self.client is not None:
            self.client.clear()
            self.client = None
            logging.debug("REST connection closed.")

    def is_connected(self) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.is_connected.__doc__
        )
        return self.client is not None

    def execute_query(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Exécute une requête REST

        :param endpoint: Point d'accès (ex: "/blocks")
        :param method: Méthode HTTP (GET, POST, etc.)
        :param params: Paramètres de query string
        :param data: Données pour les requêtes POST
        :return: Réponse JSON décodée
        """
        if self.client is None or not self.is_connected():
            raise Exception("Not connected to server")

        url = f"{self.url}/{endpoint.lstrip('/')}"

        # Préparer les paramètres
        if params:
            from urllib.parse import urlencode

            url += "?" + urlencode(params)

        # Préparer le body pour POST
        body = None
        headers = {}
        if data and method in ["POST", "PUT", "PATCH"]:
            body = json.dumps(data).encode("utf-8")
            headers = {"Content-Type": "application/json"}

        try:
            response = self.client.request(method, url, body=body, headers=headers)

            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {response.data.decode()}")

            return response.data.decode()

        except Exception as e:
            logging.error(f"Query failed: {e}")
            raise

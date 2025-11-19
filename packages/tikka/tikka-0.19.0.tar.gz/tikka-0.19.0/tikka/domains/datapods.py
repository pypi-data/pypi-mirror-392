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
from typing import List, Optional

from tikka.adapters.network.datapod.datapod import NetworkDataPod
from tikka.domains.currencies import Currencies
from tikka.domains.entities.constants import (
    DATAPODS_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY,
)
from tikka.domains.entities.datapod import DataPod
from tikka.domains.entities.events import DataPodsEvent
from tikka.domains.events import EventDispatcher
from tikka.domains.preferences import Preferences
from tikka.interfaces.adapters.network.datapod.datapod import NetworkDataPodInterface
from tikka.interfaces.adapters.repository.datapods import DataPodsRepositoryInterface


class DataPods:
    """
    DataPods domain class
    """

    CONFIG_DATAPOD_ENDPOINTS_KEYWORD = "datapod"

    def __init__(
        self,
        repository: DataPodsRepositoryInterface,
        preferences: Preferences,
        network_datapod: NetworkDataPodInterface,
        currencies: Currencies,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init DataPods domain instance

        :param repository: DataPodsRepositoryInterface instance
        :param preferences: Preferences domain instance
        :param network_datapod: Network adapter instance for handling datapods
        :param currencies: Currencies instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.preferences = preferences
        self.network_datapod = network_datapod
        self.currencies = currencies
        self.event_dispatcher = event_dispatcher

        self._current_url = self.currencies.get_entry_point_urls()[
            self.CONFIG_DATAPOD_ENDPOINTS_KEYWORD
        ][0]

        self.init_repository()

    def init_repository(self):
        """
        Init repository with default entry points from config

        :return:
        """
        repository_urls = self.repository.get_urls()
        currency_endpoints = self.currencies.get_entry_point_urls()

        # init repository with current currency entry point urls
        for url in currency_endpoints[self.CONFIG_DATAPOD_ENDPOINTS_KEYWORD]:
            if url not in repository_urls:
                self.repository.add(DataPod(url))

        self._current_url = self.repository.list(0, 1)[0].url

        current_url_in_preferences = self.preferences.get(
            DATAPODS_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY
        )
        if (
            current_url_in_preferences is None
            or current_url_in_preferences not in self.repository.get_urls()
        ):
            self.preferences.set(
                DATAPODS_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY, self.get_current_url()
            )
        else:
            self._current_url = current_url_in_preferences

    def add(self, datapod: DataPod) -> None:
        """
        Add datapod in repository

        :param datapod: DataPod instance
        :return:
        """
        self.repository.add(datapod)

        self.event_dispatcher.dispatch_event(
            DataPodsEvent(DataPodsEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def get(self, url: str) -> Optional[DataPod]:
        """
        Get DataPod instance by url

        :param url: Url
        :return:
        """
        return self.repository.get(url)

    def update(self, datapod: DataPod) -> None:
        """
        Update datapod in repository

        :param datapod: DataPod instance
        :return:
        """
        self.repository.update(datapod)

        self.event_dispatcher.dispatch_event(
            DataPodsEvent(DataPodsEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def list(self) -> List[DataPod]:
        """
        Return all DataPods from repository

        :return:
        """
        return self.repository.list()

    def count(self) -> int:
        """
        Return total datapods count

        :return:
        """
        return self.repository.count()

    def delete(self, url: str) -> None:
        """
        Delete DataPod by url

        :param url: DataPod url
        :return:
        """
        # do not delete default entry points from config
        if (
            url
            in self.currencies.get_entry_point_urls()[
                self.CONFIG_DATAPOD_ENDPOINTS_KEYWORD
            ]
        ):
            return

        self.repository.delete(url)
        # switch current entry point to first in list
        self.set_current_url(self.repository.list(0, 1)[0].url)
        # set new entry point in preferences
        self.preferences.set(
            DATAPODS_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY, self.get_current_url()
        )

        self.event_dispatcher.dispatch_event(
            DataPodsEvent(DataPodsEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def delete_all(self) -> None:
        """
        Delete all DataPods in repository

        :return:
        """
        self.repository.delete_all()

    def get_current_url(self) -> str:
        """
        Return current entry point url

        :return:
        """
        return self._current_url

    def set_current_url(self, url: str) -> None:
        """
        Set current entry point url

        :return:
        """
        self._current_url = url
        # update preference
        self.preferences.set(
            DATAPODS_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY,
            self._current_url,
        )

    def network_fetch_current_datapod(self) -> None:
        """
        Update datapod from network

        :return:
        """
        current_datapod = self.repository.get(self.get_current_url())
        network_datapod = self.network_datapod.get()
        if network_datapod is None:
            return None

        if current_datapod is not None:
            # update only changing properties
            current_datapod.block = network_datapod.block

            self.repository.update(current_datapod)

        return None

    def network_get_genesis_hash(self) -> str:
        """
        Get from network and return datapod genesis hash

        :return:
        """
        return self.network_datapod.get_genesis_hash()

    @staticmethod
    def network_test_and_get_datapod(url: str) -> Optional[DataPod]:
        """
        Try to open connection on url and return data pod if successful

        Then close connection

        :param url: Entry point url
        :return:
        """
        datapod = None

        network_datapod = NetworkDataPod()
        network_datapod.connection.connect(DataPod(url))
        if network_datapod.connection.is_connected():
            datapod = network_datapod.get()
        network_datapod.connection.disconnect()

        return datapod

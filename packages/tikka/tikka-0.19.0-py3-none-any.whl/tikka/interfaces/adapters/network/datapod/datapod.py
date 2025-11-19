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

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tikka.adapters.network.datapod.connection import DataPodConnection
    from tikka.domains.entities.datapod import DataPod
    from tikka.interfaces.adapters.network.datapod.profiles import (
        DataPodProfilesInterface,
    )


class NetworkDataPodInterface(abc.ABC):
    """
    NetworkDataPodInterface class
    """

    @property
    def connection(self) -> DataPodConnection:
        """
        Return ConnectionsInterface instance

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self) -> DataPod:
        """
        Return the datapod instance with infos from connection

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_genesis_hash(self) -> str:
        """
        Return the genesis_hash of indexed chain

        :return:
        """
        raise NotImplementedError

    @property
    def profiles(self) -> DataPodProfilesInterface:
        """
        Return DataPodProfilesInterface instance

        :return:
        """
        raise NotImplementedError


class NetworkDataPodException(Exception):
    """
    NetworkDataPodException class
    """

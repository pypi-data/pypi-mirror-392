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

import abc
from typing import Optional

from tikka.domains.entities.profile import Profile
from tikka.interfaces.adapters.network.datapod.datapod import NetworkDataPodInterface


class DataPodProfilesInterface(abc.ABC):
    """
    DataPodProfilesInterface class
    """

    def __init__(self, datapod: NetworkDataPodInterface) -> None:
        """
        Init DataPodProfilesInterface instance

        :param datapod: NetworkDataPodInterface instance
        :return:
        """
        self.datapod = datapod

    @abc.abstractmethod
    def get(self, address: str) -> Optional[Profile]:
        """
        Return json profile by address from datapod or None

        :param address: Profile account address
        :return:
        """
        raise NotImplementedError


class DataPodProfilesException(Exception):
    """
    DataPodProfilesException class
    """

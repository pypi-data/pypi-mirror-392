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


class ProfilesRepositoryInterface(abc.ABC):
    """
    ProfilesRepositoryInterface class
    """

    COLUMN_ADDRESS = "address"
    COLUMN_DATA = "data"

    @abc.abstractmethod
    def add(self, profile: Profile) -> None:
        """
        Add a new profile in repository

        :param profile: Profile instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, address: str) -> Optional[Profile]:
        """
        Return Profile instance from repository

        :param address: Profile account address
        :return:
        """
        raise NotImplementedError

    def update(self, profile: Profile) -> None:
        """
        Update profile in repository

        :param profile: Profile instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, address: str) -> None:
        """
        Delete profile in repository

        :param address: Profile account address to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all profiles in repository

        :return:
        """
        raise NotImplementedError

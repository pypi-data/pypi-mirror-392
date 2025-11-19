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
from typing import Optional

from tikka.domains.currencies import Currencies
from tikka.domains.entities.account import Account
from tikka.domains.entities.profile import Profile
from tikka.interfaces.adapters.network.datapod.profiles import DataPodProfilesInterface
from tikka.interfaces.adapters.repository.profiles import ProfilesRepositoryInterface


class Profiles:

    """
    Profiles domain class
    """

    def __init__(
        self,
        repository: ProfilesRepositoryInterface,
        datapod_profiles: DataPodProfilesInterface,
        currencies: Currencies,
    ):
        """
        Init Profiles domain

        :param repository: ProfilesRepositoryInterface instance
        :param datapod_profiles: DataPodProfilesInterface instance
        :param currencies: Currencies domain instance
        """
        self.repository = repository
        self.datapod_profiles = datapod_profiles
        self.currencies = currencies

    def add(self, profile: Profile) -> None:
        """
        Add a new profile in repository

        :param profile: Profile instance
        :return:
        """
        self.repository.add(profile)

    def get(self, address: str) -> Optional[Profile]:
        """
        Return Profile instance from repository

        :param address: Profile account address
        :return:
        """
        return self.repository.get(address)

    def update(self, profile: Profile) -> None:
        """
        Update profile in repository

        :param profile: Profile instance
        :return:
        """
        self.repository.update(profile)

    def delete(self, address: str) -> None:
        """
        Delete profile in repository

        :param address: Profile account address to delete
        :return:
        """
        self.repository.delete(address)

    def delete_all(self) -> None:
        """
        Delete all profiles in repository

        :return:
        """
        self.repository.delete_all()

    def network_update(self, account: Account) -> Optional[Profile]:
        """
        Return Profile instance by account address from network if any

        :param account: Profile account address
        :return:
        """
        v1_address = account.get_v1_address(
            self.currencies.get_current().ss58_format
        ).split(":")[0]
        profile = self.datapod_profiles.get(v1_address)
        if profile is not None:
            # fixme: We get profiles from v1 datapod for now.
            #        But we store them with the v2 address as primary key
            profile.address = account.address
            if self.get(account.address) is not None:
                self.update(profile)
            else:
                self.add(profile)
        elif self.get(account.address) is not None:
            self.delete(account.address)

        return profile

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
from typing import Any, List, Optional

from tikka.domains.entities.profile import Profile
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface
from tikka.interfaces.adapters.repository.profiles import ProfilesRepositoryInterface

TABLE_NAME = "profiles"


class DBProfilesRepository(ProfilesRepositoryInterface, DBRepositoryInterface):
    """
    DBProfilesRepository class
    """

    def add(self, profile: Profile) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ProfilesRepositoryInterface.add.__doc__
        )

        # insert only non hidden fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_profile(profile),
        )

    def get(self, address: str) -> Optional[Profile]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ProfilesRepositoryInterface.get.__doc__
        )

        row = self.client.select_one(
            f"SELECT * FROM {TABLE_NAME} WHERE address=?", (address,)
        )
        if row is None:
            return None

        return get_profile_from_row(row)

    def update(self, profile: Profile) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ProfilesRepositoryInterface.update.__doc__
        )

        # update only non-hidden fields
        self.client.update(
            TABLE_NAME,
            f"address='{profile.address}'",
            **get_fields_from_profile(profile),
        )

    def delete(self, address: str) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ProfilesRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, address=address)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ProfilesRepositoryInterface.delete_all.__doc__
        )

        self.client.clear(TABLE_NAME)


def get_fields_from_profile(profile: Profile) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param profile: Profile instance
    :return:
    """
    fields = {}
    for (key, value) in profile.__dict__.items():
        if key.startswith("_"):
            continue
        if key == "data":
            # convert dict into json string
            value = json.dumps(value)
        fields[key] = value

    return fields


def get_profile_from_row(row: tuple) -> Profile:
    """
    Return a Profile instance from a result set row

    :param row: Result set row
    :return:
    """
    values: List[Any] = []
    count = 0
    for value in row:
        if count == 1:
            # convert json string into dict
            values.append(json.loads(value))
        else:
            values.append(value)
        count += 1

    return Profile(*values)  # pylint: disable=no-value-for-parameter

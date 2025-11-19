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
from typing import List, Optional

from tikka.domains.entities.datapod import DataPod


class DataPodsRepositoryInterface(abc.ABC):
    """
    DataPodsRepositoryInterface class
    """

    COLUMN_URL = "datapod_url"
    COLUMN_BLOCK = "datapod_block"

    DEFAULT_LIST_OFFSET = 0
    DEFAULT_LIST_LIMIT = 1000

    SORT_ORDER_ASCENDING = "ASC"
    SORT_ORDER_DESCENDING = "DESC"

    @abc.abstractmethod
    def add(self, datapod: DataPod) -> None:
        """
        Add a new datapod in repository

        :param datapod: DataPod instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, url: str) -> Optional[DataPod]:
        """
        Return DataPod by url from repository

        :param url: DataPod url
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, datapod: DataPod) -> None:
        """
        Update datapod in repository

        :param datapod: DataPod instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(
        self,
        offset: int = DEFAULT_LIST_OFFSET,
        limit: int = DEFAULT_LIST_LIMIT,
        sort_column: str = COLUMN_URL,
        sort_order: str = SORT_ORDER_ASCENDING,
    ) -> List[DataPod]:
        """
        List datapods from repository

        :param offset: Offset index to get rows from
        :param limit: Number of rows to return
        :param sort_column: Sort column, default to DataPodsRepositoryInterface.COLUMN_URL
        :param sort_order: Sort order, default to DataPodsRepositoryInterface.ASC
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, url: str) -> None:
        """
        Delete datapod by url in repository

        :param url: Url of DataPod to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all datapods in repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self) -> int:
        """
        Return number of datapods in repository

        :return:
        """
        raise NotImplementedError

    def get_urls(self) -> List[str]:
        """
        Get all urls of datapods from repository

        :return:
        """
        raise NotImplementedError

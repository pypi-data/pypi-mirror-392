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
import logging
import sys
from typing import Optional

from PyQt5.QtCore import QMutex
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QMainWindow, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.events import CurrencyEvent
from tikka.domains.entities.node import Node
from tikka.slots.pyqt.entities.constants import (
    ICON_LOADER,
    TECHNICAL_COMMITTEE_SELECTED_ACCOUNT_ADDRESS,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.widgets.technical_committee_rc import (
    Ui_technicalCommitteeWidget,
)
from tikka.slots.pyqt.widgets.technical_committee_proposal import (
    TechnicalCommitteeProposalWidget,
)


class TechnicalCommitteeWidget(QWidget, Ui_technicalCommitteeWidget):
    """
    TechnicalCommitteeWidget class
    """

    def __init__(
        self, application: Application, mutex: QMutex, parent: Optional[QWidget] = None
    ) -> None:
        """
        Init TechnicalCommitteeWidget instance

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: MainWindow instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.mutex = mutex
        self.proposals_list_current_index = 0

        # animated loading icon
        self.loader_movie = QMovie(ICON_LOADER)
        self.loader_movie.start()
        self.loaderIconLabel.setMovie(self.loader_movie)
        loader_icon_size_policy = self.loaderIconLabel.sizePolicy()
        loader_icon_size_policy.setRetainSizeWhenHidden(True)
        self.loaderIconLabel.setSizePolicy(loader_icon_size_policy)
        self.loaderIconLabel.hide()

        ##############################
        # ASYNC METHODS
        ##############################
        self.fetch_members_from_network_async_worker = AsyncQWorker(
            self.fetch_members_from_network, self.mutex
        )
        self.fetch_members_from_network_async_worker.finished.connect(
            self._on_fetch_members_from_network_async_worker_finished
        )
        self.fetch_proposals_from_network_async_worker = AsyncQWorker(
            self.fetch_proposals_from_network, self.mutex
        )
        self.fetch_proposals_from_network_async_worker.finished.connect(
            self._on_fetch_proposals_from_network_async_worker_finished
        )

        # events
        self.accountComboBox.activated.connect(self.on_account_combobox_index_changed)
        self.refreshButton.clicked.connect(self._on_refresh_button_clicked)

        # subscribe to application events
        self.application.event_dispatcher.add_event_listener(
            CurrencyEvent.EVENT_TYPE_CHANGED, self._on_currency_event
        )

        self.init_member_list()
        self.init_proposal_list()

    def init_member_list(self) -> None:
        """
        Init list of members

        :return:
        """
        self.membersListWidget.clear()

        for member in self.application.technical_committee.list_members():
            if member.identity_index is not None:
                label = (
                    f"{member.address} - {member.identity_name}#{member.identity_index}"
                )
            else:
                label = f"{member.address}"
            account = self.application.accounts.get_by_address(member.address)
            if account is not None and account.name is not None:
                label += f" - {account.name}"

            self.membersListWidget.addItem(label)

    def init_proposal_list(self) -> None:
        """
        Init list of proposals

        :return:
        """

        scrollbar = self.proposalsListWidget.verticalScrollBar()
        if scrollbar.maximum() > 0:
            scroll_ratio = scrollbar.value() / scrollbar.maximum()
        else:
            scroll_ratio = 0
        current_row = self.proposalsListWidget.currentRow()

        self.proposalsListWidget.clear()

        for proposal in sorted(
            self.application.technical_committee.list_proposals(),
            key=lambda proposal: proposal.voting.index,
        ):
            item = QListWidgetItem(self.proposalsListWidget)
            self.proposalsListWidget.addItem(item)
            widget = TechnicalCommitteeProposalWidget(
                self.application, proposal, self.mutex, parent=self
            )
            item.setSizeHint(widget.minimumSizeHint())

            # connect slot self.update_proposals to proposal item event
            widget.vote_for_proposal_start.connect(self.on_vote_for_proposal_start)
            widget.vote_for_proposal_done.connect(self.update_proposals)

            # Associate the custom widget to the list entry
            self.proposalsListWidget.setItemWidget(item, widget)

        if scrollbar.maximum() > 0:
            new_value = int(scroll_ratio * scrollbar.maximum())
            scrollbar.setValue(new_value)

        if 0 <= current_row < self.proposalsListWidget.count():
            self.proposalsListWidget.setCurrentRow(current_row)

    def init_account_combo_box(self) -> None:
        """
        Init combobox with technical committee member accounts (with wallets)

        :return:
        """
        self.accountComboBox.clear()

        accounts = self.application.accounts.get_list()
        for account in accounts:
            if account.address in [
                member.address
                for member in self.application.technical_committee.list_members()
            ] and self.application.wallets.exists(account.address):
                self.accountComboBox.addItem(
                    account.name if account.name is not None else account.address,
                    userData=account.address,
                )

        preference_account_address_selected = self.application.preferences.get(
            TECHNICAL_COMMITTEE_SELECTED_ACCOUNT_ADDRESS
        )
        if preference_account_address_selected is not None:
            preference_account_selected = self.application.accounts.get_by_address(
                preference_account_address_selected
            )
            if preference_account_selected is not None:
                index = self.accountComboBox.findData(
                    preference_account_address_selected
                )
                if index > -1:
                    self.accountComboBox.setCurrentIndex(index)
                else:
                    self.application.preferences.set(
                        TECHNICAL_COMMITTEE_SELECTED_ACCOUNT_ADDRESS, None
                    )

    def _on_refresh_button_clicked(self, _):
        """
        Refresh data from network when refresh button is clicked

        :param _:
        :return:
        """
        self.errorLabel.setText("")
        self.loader_movie.start()
        self.loaderIconLabel.show()
        self.fetch_members_from_network_async_worker.start()
        self.fetch_proposals_from_network_async_worker.start()

    def on_account_combobox_index_changed(self):
        """
        Triggered when account selection is changed

        :return:
        """
        address = self.accountComboBox.currentData()

        self.application.repository.preferences.set(
            TECHNICAL_COMMITTEE_SELECTED_ACCOUNT_ADDRESS,
            address,
        )

    def fetch_members_from_network(self):
        """
        Fetch members of technical committee from network

        :return:
        """
        try:
            self.application.technical_committee.network_update_members()
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_fetch_members_from_network_async_worker_finished(self):
        """
        Triggered when async worker is finished

        :return:
        """
        logging.debug("Technical committee widget members update")

        self.init_member_list()
        self.init_account_combo_box()
        self.loader_movie.stop()
        self.loaderIconLabel.hide()

    def fetch_proposals_from_network(self):
        """
        Fetch proposals of technical committee from network

        :return:
        """
        try:
            self.application.technical_committee.network_update_proposals()
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_fetch_proposals_from_network_async_worker_finished(self):
        """
        Triggered when async worker is finished

        :return:
        """
        logging.debug("Technical committee widget proposals update")
        self.init_proposal_list()
        self.loader_movie.stop()
        self.loaderIconLabel.hide()

    def _on_currency_event(self, _):
        """
        When a currency event is triggered

        :param _: CurrencyEvent instance
        :return:
        """
        self.fetch_members_from_network_async_worker.start()
        self.fetch_proposals_from_network_async_worker.start()

    def on_vote_for_proposal_start(self):
        """
        Vote request send, display loader waiting for vote done

        :return:
        """
        self.loader_movie.start()
        self.loaderIconLabel.show()
        self.proposals_list_current_index = (
            self.proposalsListWidget.currentIndex().row()
        )

    def update_proposals(self):
        """
        After a vote, update proposals list with new votes

        :return:
        """
        self.fetch_proposals_from_network_async_worker.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.show()
    validator_node = Node(url="wss://gdev.cgeek.fr")
    if application_.nodes.get(validator_node.url) is None:
        application_.nodes.add(validator_node)
    application_.nodes.set_current_url(validator_node.url)
    application_.connections.node.connect(validator_node)
    main_window.setCentralWidget(
        TechnicalCommitteeWidget(application_, QMutex(), main_window)
    )

    sys.exit(qapp.exec_())

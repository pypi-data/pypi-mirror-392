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
from typing import Optional

from PyQt5.QtCore import QLocale, QMutex, pyqtSignal
from PyQt5.QtWidgets import QDialog, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.technical_committee import TechnicalCommitteeProposal
from tikka.slots.pyqt.entities.constants import (
    TECHNICAL_COMMITTEE_SELECTED_ACCOUNT_ADDRESS,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.widgets.technical_committee_proposal_rc import (
    Ui_TechnicalCommitteeProposalWidget,
)
from tikka.slots.pyqt.windows.account_unlock import AccountUnlockWindow


class TechnicalCommitteeProposalWidget(QWidget, Ui_TechnicalCommitteeProposalWidget):
    """
    TechnicalCommitteeProposalWidget class
    """

    vote_for_proposal_start = pyqtSignal()
    vote_for_proposal_done = pyqtSignal()

    def __init__(
        self,
        application: Application,
        proposal: TechnicalCommitteeProposal,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Init TechnicalCommitteeWidget instance

        :param application: TechnicalCommitteeProposal instance
        :param proposal: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.mutex = mutex

        self.proposal = proposal
        self.vote = False

        self.callIndexValueLabel.setText(str(self.proposal.call.index))
        self.callHashValueLabel.setText(self.proposal.call.hash)
        self.callModuleValueLabel.setText(str(self.proposal.call.module))
        self.callFunctionValueLabel.setText(str(self.proposal.call.function))
        self.callArgumentsValueTextBrowser.setPlainText(str(self.proposal.call.args))

        self.votingIndexValueLabel.setText(str(self.proposal.voting.index))
        self.votingThresholdValueLabel.setText(str(self.proposal.voting.threshold))
        yes_address_names = []
        for address in self.proposal.voting.ayes:
            label = f"{address}"
            member = self.application.technical_committee.get_member_by_address(address)
            if member is not None:
                if member.identity_index is not None:
                    if member.identity_name is not None:
                        label += f" - {member.identity_name}#{member.identity_index}"
                    else:
                        label += f" - #{member.identity_index}"
            account = self.application.accounts.get_by_address(address)
            if account is not None and account.name is not None:
                label += f" - {account.name}"
            yes_address_names.append(label)
        self.votingAyesValueLabel.setText("\n".join(yes_address_names))
        no_address_names = []
        for address in self.proposal.voting.nays:
            label = f"{address}"
            member = self.application.technical_committee.get_member_by_address(address)
            if member is not None:
                if member.identity_index is not None:
                    if member.identity_name is not None:
                        label += f" - {member.identity_name}#{member.identity_index}"
                    else:
                        label += f" - #{member.identity_index}"
            account = self.application.accounts.get_by_address(address)
            if account is not None and account.name is not None:
                label += f" - {account.name}"
            no_address_names.append(label)
        self.votingNaysValueLabel.setText("\n".join(no_address_names))
        end_localized_datetime_string = self.locale().toString(
            self.proposal.voting.end,
            QLocale.dateTimeFormat(self.locale(), QLocale.ShortFormat),
        )
        self.votingEndValueLabel.setText(end_localized_datetime_string)

        # events
        self.yesButton.clicked.connect(self._on_yes_button_clicked)
        self.noButton.clicked.connect(self._on_no_button_clicked)

        # async method
        self.network_vote_async_worker = AsyncQWorker(
            self.network_vote_for_proposal, self.mutex
        )
        self.network_vote_async_worker.finished.connect(
            self._on_network_vote_async_worker_finished
        )

    def _on_yes_button_clicked(self, _):
        """
        Triggered when user click on Yes Button

        :param _:
        :return:
        """
        self.vote = True
        self.vote_for_proposal_start.emit()

        if self.check_voting_account_password():
            self.network_vote_async_worker.start()

    def _on_no_button_clicked(self, _):
        """
        Triggered when user click on No Button

        :param _:
        :return:
        """
        self.vote = False
        self.vote_for_proposal_start.emit()

        if self.check_voting_account_password():
            self.network_vote_async_worker.start()

    def check_voting_account_password(self) -> bool:
        """
        Check account lock and ask password if necessary,
        return True if unlocked account is ok

        :return:
        """
        logging.debug("Starting network_vote_for_proposal")
        self.errorLabel.setText("")
        preference_account_address_selected = self.application.preferences.get(
            TECHNICAL_COMMITTEE_SELECTED_ACCOUNT_ADDRESS
        )
        if preference_account_address_selected is None:
            self.errorLabel.setText(self._("No technical committee account selected"))
            return False

        account = self.application.accounts.get_by_address(
            preference_account_address_selected
        )
        if account is None:
            self.errorLabel.setText(self._("Unknown account"))
            return False

        # if account is locked...
        if not self.application.wallets.is_unlocked(
            preference_account_address_selected
        ):
            logging.debug("Opening AccountUnlockWindow")
            dialog = AccountUnlockWindow(self.application, account)
            logging.debug("Executing dialog")
            dialog_code = dialog.exec_()
            logging.debug(f"Dialog finished with code: {dialog_code}")

            if dialog_code == QDialog.Rejected:
                logging.debug("Dialog rejected")
                return False

        return True

    def network_vote_for_proposal(self):
        """
        Vote and refresh data of technical committee from network

        :return:
        """
        logging.debug("Performing network vote")
        preference_account_address_selected = self.application.preferences.get(
            TECHNICAL_COMMITTEE_SELECTED_ACCOUNT_ADDRESS
        )
        try:
            self.application.technical_committee.network_vote(
                self.application.wallets.get_keypair(
                    preference_account_address_selected
                ),
                self.proposal,
                self.vote,
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_network_vote_async_worker_finished(self):
        """
        Triggered when async worker is finished

        :return:
        """
        self.vote_for_proposal_done.emit()

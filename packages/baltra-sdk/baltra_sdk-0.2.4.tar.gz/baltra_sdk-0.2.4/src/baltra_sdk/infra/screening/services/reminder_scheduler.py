from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from baltra_sdk.domain.screening.entities import ReminderSchedule
from baltra_sdk.domain.screening.ports import ReminderNotifier, ReminderRepository


@dataclass
class ReminderScheduler:
    """Coordinates reminder dispatching through the SOLID adapters."""

    repository: ReminderRepository
    notifier: ReminderNotifier

    def send_application_reminders(self) -> int:
        """Dispatch pending application reminders."""
        count = 0
        for job in self.repository.list_application_jobs():
            self.notifier.send(job)
            self.repository.mark_sent(job)
            count += 1
        return count

    def send_interview_reminders(self, schedules: Iterable[ReminderSchedule]) -> int:
        """Dispatch interview reminders for the provided schedules."""
        count = 0
        for schedule in schedules:
            for job in self.repository.list_interview_jobs(schedule):
                self.notifier.send(job)
                self.repository.mark_sent(job)
                count += 1
        return count

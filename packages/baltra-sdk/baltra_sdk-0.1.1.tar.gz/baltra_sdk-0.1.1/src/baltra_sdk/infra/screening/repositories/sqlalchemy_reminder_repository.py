from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from typing import Callable, Iterable, List
from zoneinfo import ZoneInfo

from baltra_sdk.domain.screening.entities import ReminderJob, ReminderSchedule
from baltra_sdk.domain.screening.ports import ReminderRepository
from baltra_sdk.legacy.dashboards_folder.models import Candidates, CompaniesScreening, db


def _naive_iso(dt: datetime) -> str:
    """Serialize datetimes (timezone-aware or naive) into naive ISO strings."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None).isoformat()
    return dt.isoformat()


@dataclass
class SqlAlchemyReminderRepository(ReminderRepository):
    """SQLAlchemy-backed implementation for reminder jobs."""

    session_factory: Callable[[], object] = lambda: db.session  # type: ignore[assignment]
    application_cutoff_hours: int = 23

    def list_application_jobs(self) -> Iterable[ReminderJob]:
        session = self.session_factory()
        cutoff = datetime.utcnow() - timedelta(hours=self.application_cutoff_hours)
        rows: List[tuple[Candidates, str]] = (
            session.query(Candidates, CompaniesScreening.wa_id)
            .join(CompaniesScreening, Candidates.company_id == CompaniesScreening.company_id)
            .filter(
                Candidates.funnel_state == "screening_in_progress",
                Candidates.application_reminder_sent.is_(False),
                Candidates.phone.isnot(None),
                Candidates.created_at <= cutoff,
            )
            .all()
        )
        for candidate, wa_id_system in rows:
            schedule = ReminderSchedule(
                company_id=candidate.company_id,
                schedule_type="application",
                metadata={"cutoff_iso": cutoff.isoformat()},
            )
            yield ReminderJob(
                candidate_id=candidate.candidate_id,
                wa_id_user=candidate.phone,
                wa_id_system=wa_id_system,
                kind="application",
                schedule=schedule,
                context={"company_id": candidate.company_id},
            )

    def list_interview_jobs(self, schedule: ReminderSchedule) -> Iterable[ReminderJob]:
        window_start = schedule.metadata.get("window_start_iso")
        window_end = schedule.metadata.get("window_end_iso")
        if window_start is None or window_end is None:
            return []
        start_dt = datetime.fromisoformat(window_start)
        end_dt = datetime.fromisoformat(window_end)
        session = self.session_factory()
        rows: List[tuple[Candidates, str]] = (
            session.query(Candidates, CompaniesScreening.wa_id)
            .join(CompaniesScreening, Candidates.company_id == CompaniesScreening.company_id)
            .filter(
                Candidates.company_id == schedule.company_id,
                Candidates.interview_date_time >= start_dt,
                Candidates.interview_date_time <= end_dt,
                Candidates.interview_reminder_sent.is_(False),
                Candidates.funnel_state == "scheduled_interview",
                Candidates.phone.isnot(None),
            )
            .all()
        )
        for candidate, wa_id_system in rows:
            yield ReminderJob(
                candidate_id=candidate.candidate_id,
                wa_id_user=candidate.phone,
                wa_id_system=wa_id_system,
                kind="interview",
                schedule=schedule,
                context={"interview_date_time": candidate.interview_date_time.isoformat() if candidate.interview_date_time else None},
            )

    def mark_sent(self, job: ReminderJob) -> None:
        session = self.session_factory()
        candidate: Candidates | None = (
            session.query(Candidates).filter(Candidates.candidate_id == job.candidate_id).first()
        )
        if candidate is None:
            return
        if job.kind == "application":
            candidate.application_reminder_sent = True
        else:
            candidate.interview_reminder_sent = True
        session.commit()


@dataclass
class CompanyReminderScheduleProvider:
    """Builds ReminderSchedule objects based on CompaniesScreening configuration."""

    session_factory: Callable[[], object] = lambda: db.session  # type: ignore[assignment]
    timezone: str = "America/Mexico_City"
    window_minutes: int = 10

    def iter_due_schedules(self, now_utc: datetime | None = None) -> Iterable[ReminderSchedule]:
        now_utc = now_utc or datetime.now(timezone.utc)
        tz = ZoneInfo(self.timezone)
        now_local = now_utc.astimezone(tz)
        for company in self._iter_companies():
            schedule_config = company.reminder_schedule or {}
            schedule_type = schedule_config.get("type")
            if schedule_type == "fixed":
                schedule = self._build_fixed_schedule(company, schedule_config, now_local, tz)
                if schedule:
                    yield schedule
            elif schedule_type == "flexible":
                schedule = self._build_flexible_schedule(company, schedule_config, now_local, tz)
                if schedule:
                    yield schedule

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _iter_companies(self):
        session = self.session_factory()
        return (
            session.query(CompaniesScreening)
            .filter(CompaniesScreening.reminder_schedule.isnot(None))
            .all()
        )

    def _build_fixed_schedule(self, company, config, now_local: datetime, tz: ZoneInfo) -> ReminderSchedule | None:
        schedule_time = config.get("time")
        if not schedule_time:
            return None
        hour, minute = map(int, schedule_time.split(":"))
        scheduled = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
        diff_minutes = abs((now_local - scheduled).total_seconds() / 60)
        if diff_minutes > self.window_minutes:
            return None
        when = config.get("when", "night_before")
        target_date = now_local.date() + (timedelta(days=1) if when == "night_before" else timedelta())
        start_local = datetime.combine(target_date, time.min, tz)
        end_local = datetime.combine(target_date, time.max, tz)
        return ReminderSchedule(
            company_id=company.company_id,
            schedule_type="fixed",
            time_of_day=schedule_time,
            metadata={
                "window_start_iso": _naive_iso(start_local),
                "window_end_iso": _naive_iso(end_local),
                "raw_config": json.dumps(config),
            },
        )

    def _build_flexible_schedule(self, company, config, now_local: datetime, tz: ZoneInfo) -> ReminderSchedule | None:
        hours_before = config.get("hours_before", 3)
        offset = timedelta(minutes=self.window_minutes)
        start_local = now_local + timedelta(hours=hours_before) - offset
        end_local = now_local + timedelta(hours=hours_before) + offset
        return ReminderSchedule(
            company_id=company.company_id,
            schedule_type="flexible",
            metadata={
                "window_start_iso": _naive_iso(start_local),
                "window_end_iso": _naive_iso(end_local),
                "hours_before": hours_before,
            },
        )

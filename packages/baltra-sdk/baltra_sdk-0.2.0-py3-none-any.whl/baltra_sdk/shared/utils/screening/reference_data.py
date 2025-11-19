from baltra_sdk.legacy.dashboards_folder.models import (CandidateReferences, ReferenceMessages, CompaniesScreening, db)
import logging
from datetime import datetime
from flask import current_app
"""
 Purpose: Manage reference retrieval/creation, thread handling, and question tracking for screening process.
 This class abstracts logic needed to initialize conversation context with a candidate.
"""

class ReferenceDataFetcher:
    """
    Handles retrieval or creation of candidate reference records,
    message history, and thread context for WhatsApp-based reference checks.

    - If the wa_id is already linked to an incomplete reference, it reuses that reference.
    - If not, it creates a new fallback reference linked to a dummy candidate.
    - Also handles thread creation and candidate name resolution.
    """

    def __init__(self, wa_id_user, client):
        """
        Initialize ReferenceDataFetcher with WhatsApp user ID and OpenAI client.

        Loads or creates:
        - A CandidateReferences object
        - The latest ReferenceMessages for that reference
        - An OpenAI thread ID
        - The candidate's name (if linked)
        """
        self.wa_id_user = wa_id_user
        self.client = client
        self.reference = self._get_or_create_reference()
        self.latest_message = self._get_latest_message()
        self.thread_id = self._get_thread_id()
        self.candidate_name = self.get_candidate_name()

    def _get_or_create_reference(self):
        """
        Attempts to find the most recent incomplete reference for the given wa_id.
        If none exists, falls back to the most recent completed one.
        If still none exists, creates a new fallback reference for a dummy candidate.
        """
        # Step 1: Try incomplete reference
        reference = (
            db.session.query(CandidateReferences)
            .filter_by(reference_wa_id=self.wa_id_user, reference_complete=False)
            .order_by(CandidateReferences.reference_id.desc())
            .first()
        )
        if reference:
            logging.info(f"Incomplete reference found: ID {reference.reference_id}")
            return reference

        # Step 2: Try any reference (fallback to latest completed one)
        reference = (
            db.session.query(CandidateReferences)
            .filter_by(reference_wa_id=self.wa_id_user)
            .order_by(CandidateReferences.reference_id.desc())
            .first()
        )
        if reference:
            logging.info(f"No incomplete reference. Using most recent completed reference: ID {reference.reference_id}")
            return reference

        # Step 3: No reference at all — create fallback
        logging.info(f"No references found for wa_id {self.wa_id_user}, creating fallback.")
        try:
            dummy_reference = CandidateReferences(
                reference_wa_id=self.wa_id_user,
                candidate_id=9999,  # Dummy candidate
                set_id=9999,        # Dummy question set
                question_id=9999    # Dummy question
            )
            db.session.add(dummy_reference)
            db.session.commit()
            logging.info(f"Fallback reference created for wa_id {self.wa_id_user}")
            return dummy_reference
        except Exception as e:
            logging.error(f"Error creating fallback reference: {e}")
            return None


    def _get_latest_message(self):
        """
        Returns the most recent message for the current reference (if any).
        Used to restore conversation context and fetch existing thread ID.
        """
        if not self.reference:
            return None

        return (
            db.session.query(ReferenceMessages)
            .filter_by(reference_id=self.reference.reference_id)
            .order_by(ReferenceMessages.time_stamp.desc())
            .first()
        )

    def _get_thread_id(self):
        """
        Returns an existing thread ID if available from the latest message.
        Otherwise creates a new thread using the OpenAI client.
        """
        if self.latest_message and self.latest_message.thread_id:
            return self.latest_message.thread_id
        try:
            thread = self.client.beta.threads.create()
            return thread.id
        except Exception as e:
            logging.error(f"Error creating thread: {e}")
            return None

    def get_candidate_name(self):
        """
        Returns the name of the candidate linked to this reference, if available.
        """
        if self.reference and hasattr(self.reference, 'candidate') and self.reference.candidate:
            return self.reference.candidate.name
        return None

    def get_data(self):
        if not self.reference or not self.thread_id:
            logging.warning("Missing reference or thread ID during data fetch.")
            return None

        candidate = self.reference.candidate
        company_screening = (
            db.session.query(CompaniesScreening)
            .filter_by(company_id=candidate.company_id)
            .first()
            if candidate else None
        )

        return {
            "wa_id": self.wa_id_user,
            "reference_id": self.reference.reference_id,
            "first_name": self.candidate_name,
            "candidate_id": self.reference.candidate_id,
            "question_id": self.reference.question_id,
            "company_name": company_screening.name if company_screening else "Empresa no disponible",
            "thread_id": self.thread_id,
            "reference_assistant": current_app.config["REFERENCE_ASSISTANT_ID"],
            "reference_classifier": current_app.config["REFERENCE_CLASSIFIER_ASSISTANT_ID"],
            "company_context": company_screening.description if company_screening else "",
            "role_context": "Baltra ayuda a empresas a encontrar el mejor talento para sus puestos de trabajo.",
            "company_phone": company_screening.phone if company_screening else "",
            "company_benefits": company_screening.benefits if company_screening else [],
            "interview_address_json": company_screening.interview_address_json if company_screening else {}
        }
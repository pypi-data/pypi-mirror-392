from typing import Optional, Dict, Any
from baltra_sdk.domain.document_verification.ports import CandidateMediaRepository
from baltra_sdk.legacy.dashboards_folder.models import db, Candidates, CandidateMedia


class CandidateMediaSQLRepo(CandidateMediaRepository):
    def create_text_media(self, candidate_id: int, company_id: int, subtype: str, value: str) -> int:
        media = CandidateMedia(
            candidate_id=candidate_id,
            company_id=company_id,
            media_type="text",
            media_subtype=subtype,
            string_submission=value,
            verified=False,
        )
        db.session.add(media)
        db.session.commit()
        return media.media_id

    def update_verification(self, media_id: int, verified: bool, result: Dict[str, Any]) -> None:
        media = db.session.query(CandidateMedia).filter_by(media_id=media_id).first()
        if not media:
            return
        media.verified = bool(verified)
        media.verification_result = result
        db.session.commit()

    def set_media_tags(self, media_id: int, *, media_subtype: Optional[str] = None, media_type: Optional[str] = None) -> None:
        """Update media_type/media_subtype for a candidate_media row (idempotent)."""
        media = db.session.query(CandidateMedia).filter_by(media_id=media_id).first()
        if not media:
            return
        if media_subtype:
            media.media_subtype = media_subtype
        if media_type:
            media.media_type = media_type
        db.session.commit()

    def get_media_s3_url(self, media_id: int) -> Optional[str]:
        media = db.session.query(CandidateMedia).filter_by(media_id=media_id).first()
        return media.s3_url if media else None

    def get_candidate_company_id(self, candidate_id: int) -> int:
        c = db.session.query(Candidates).filter_by(candidate_id=candidate_id).first()
        if not c:
            raise ValueError("Candidate not found")
        return c.company_id

    # SOLID-friendly method to persist file media with full metadata
    def create_file_media(
        self,
        *,
        candidate_id: int,
        company_id: int,
        file_name: str,
        mime_type: Optional[str],
        file_size: int,
        s3_bucket: str,
        s3_key: str,
        s3_url: str,
        whatsapp_media_id: Optional[str] = None,
        sha256_hash: Optional[str] = None,
        flow_token: Optional[str] = None,
        media_type: Optional[str] = None,
        media_subtype: Optional[str] = None,
        question_id: Optional[int] = None,
        set_id: Optional[int] = None,
    ) -> int:
        media = CandidateMedia(
            candidate_id=candidate_id,
            company_id=company_id,
            question_id=question_id,
            set_id=set_id,
            media_type=media_type,
            media_subtype=media_subtype,
            file_name=file_name,
            mime_type=mime_type,
            file_size=file_size,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            s3_url=s3_url,
            whatsapp_media_id=whatsapp_media_id,
            sha256_hash=sha256_hash,
            flow_token=flow_token,
            verified=False,
        )
        db.session.add(media)
        db.session.commit()
        return media.media_id

    # NSS helpers (used by webhook service)
    def find_nss_media_id_by_verification(self, verification_id: str) -> Optional[int]:
        row = (
            db.session.query(CandidateMedia.media_id)
            .filter(CandidateMedia.media_subtype == "NSS", CandidateMedia.string_submission == verification_id)
            .first()
        )
        return row.media_id if row else None

    def update_nss_by_verification(self, verification_id: str, verified: bool, result: Dict[str, Any]) -> bool:
        media = (
            db.session.query(CandidateMedia)
            .filter(CandidateMedia.media_subtype == "NSS", CandidateMedia.string_submission == verification_id)
            .first()
        )
        if not media:
            return False
        media.verified = bool(verified)
        media.verification_result = result
        # If verification provided an NSS number, replace string_submission with the actual NSS
        try:
            nss = (result or {}).get("nss_data", {}).get("nss")
            if nss and isinstance(nss, str):
                media.string_submission = nss
        except Exception:
            pass
        db.session.commit()
        return True

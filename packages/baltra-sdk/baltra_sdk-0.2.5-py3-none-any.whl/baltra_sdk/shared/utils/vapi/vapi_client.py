import requests
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class VAPIClient:
    """
    Basic VAPI client for integrating with VAPI voice agent platform.
    This is a foundation for future integration when real VAPI webhooks are set up.
    """
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.vapi.ai"):
        self.api_key = api_key or os.getenv('VAPI_API_KEY')
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
    
    def get_call_details(self, call_id: str) -> Optional[Dict]:
        """
        Retrieve call details from VAPI
        
        Args:
            call_id: The VAPI call ID
            
        Returns:
            Call details dictionary or None if not found
        """
        if not self.api_key:
            logger.warning("VAPI API key not configured")
            return None
            
        try:
            url = f"{self.base_url}/call/{call_id}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Call {call_id} not found in VAPI")
                return None
            else:
                logger.error(f"Error fetching call {call_id}: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Network error fetching call {call_id}: {str(e)}")
            return None
    
    def get_call_transcript(self, call_id: str) -> Optional[str]:
        """
        Retrieve call transcript from VAPI
        
        Args:
            call_id: The VAPI call ID
            
        Returns:
            Transcript text or None if not available
        """
        call_details = self.get_call_details(call_id)
        if call_details:
            return call_details.get('transcript')
        return None
    
    def list_calls(self, 
                   page: int = 1, 
                   limit: int = 100,
                   status: str = None) -> List[Dict]:
        """
        List calls from VAPI
        
        Args:
            page: Page number (1-based)
            limit: Number of calls per page
            status: Filter by call status
            
        Returns:
            List of call dictionaries
        """
        if not self.api_key:
            logger.warning("VAPI API key not configured")
            return []

    def start_call(self,
                   assistant_id: str,
                   to_number: str,
                   questions_text: str,
                   phone_number_id: Optional[str] = None,
                   system_prompt: Optional[str] = None,
                   metadata: Optional[Dict] = None) -> Optional[Dict]:
        """
        Initiate a VAPI phone call, injecting dynamic questions via variableValues.

        Args:
            assistant_id: The VAPI assistant ID to use
            to_number: E.164 phone number for the candidate
            questions_text: Newline-separated, numbered questions in Spanish
            phone_number_id: Optional VAPI phone number ID to originate from
            system_prompt: Optional override system prompt (if not stored in assistant)
            metadata: Extra fields to round-trip via webhook (e.g., candidate_id)

        Returns:
            Response JSON including callId or None on error.
        """
        if not self.api_key:
            logger.warning("VAPI API key not configured")
            return None
        try:
            url = f"{self.base_url}/call/phone"
            payload: Dict = {
                "assistantId": assistant_id,
                "customer": {"number": to_number},
                "assistantOverrides": {
                    "variableValues": {
                        "questions": questions_text
                    }
                }
            }
            if phone_number_id:
                payload["phoneNumberId"] = phone_number_id
            if system_prompt:
                payload["assistantOverrides"]["systemPrompt"] = system_prompt
            if metadata:
                payload["metadata"] = metadata

            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            if response.status_code in (200, 201):
                return response.json()
            logger.error(f"Error starting VAPI call: {response.status_code} {response.text}")
            return None
        except requests.RequestException as e:
            logger.error(f"Network error starting VAPI call: {str(e)}")
            return None
            
        try:
            params = {
                'page': page,
                'limit': limit
            }
            if status:
                params['status'] = status
                
            url = f"{self.base_url}/call"
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('calls', [])
            else:
                logger.error(f"Error listing calls: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Network error listing calls: {str(e)}")
            return []
    
    def process_webhook_event(self, webhook_data: Dict) -> Optional[Dict]:
        """
        Process VAPI webhook event and extract relevant data.
        Supports multiple payload shapes observed in VAPI:
        - type: 'call.ended' with message.call
        - type: 'status-update' with message.status == 'ended' and message.artifact
        - type: 'end-of-call-report' with detailed message.artifact and top-level fields
        """
        try:
            event_type = webhook_data.get('type')
            logger.info(f"🔄 VAPI CLIENT: Processing webhook event type: {event_type}")

            # Normalize common fields across possible payload shapes
            normalized = self._normalize_webhook(webhook_data)
            if not normalized:
                logger.warning("VAPI CLIENT: Could not normalize webhook payload; skipping")
                return None

            return {
                'vapi_call_id': normalized.get('call_id'),
                'call_status': normalized.get('call_status') or 'completed',
                'call_duration': normalized.get('duration_seconds'),
                'started_at': self._parse_timestamp(normalized.get('started_at')),
                'ended_at': self._parse_timestamp(normalized.get('ended_at')),
                'transcript': normalized.get('transcript'),
                'summary': normalized.get('summary'),
                'ai_score': self._extract_score(normalized.get('analysis', {})) or self._extract_score(normalized),
                'ai_recommendation': self._extract_recommendation(normalized.get('analysis', {})) or self._extract_recommendation(normalized),
                # Pass through for upstream matching when possible
                'phone_number': normalized.get('phone_number'),
                'candidate_id': normalized.get('candidate_id'),
            }
        except Exception as e:
            logger.error(f"Error processing webhook event: {str(e)}")
            return None

    def _normalize_webhook(self, payload: Dict) -> Optional[Dict]:
        """Normalize differing VAPI webhook payloads into a common structure."""
        try:
            def find_first(obj: Dict, candidate_keys):
                # breadth-first search for any of the candidate keys
                from collections import deque
                queue = deque([obj])
                seen = set()
                while queue:
                    node = queue.popleft()
                    node_id = id(node)
                    if node_id in seen:
                        continue
                    seen.add(node_id)
                    if isinstance(node, dict):
                        for k, v in node.items():
                            if k in candidate_keys and v is not None:
                                return v
                            if isinstance(v, (dict, list, tuple)):
                                queue.append(v)
                    elif isinstance(node, (list, tuple)):
                        for v in node:
                            if isinstance(v, (dict, list, tuple)):
                                queue.append(v)
                return None

            message = payload.get('message', {}) or {}
            artifact = message.get('artifact', {}) or {}
            call_block = message.get('call', {}) or payload.get('call', {}) or {}

            # Attempt to extract phone number from multiple possible locations
            phone_number = (
                call_block.get('customer', {}).get('number')
                or artifact.get('customer', {}).get('number')
                or payload.get('customer', {}).get('number')
                or payload.get('phoneNumber')
            )

            # Attempt to extract candidate id if sent via variables/metadata
            variables = payload.get('variables') or message.get('variables') or {}
            variable_values = payload.get('variableValues') or message.get('variableValues') or {}
            metadata = payload.get('metadata') or message.get('metadata') or {}
            candidate_id = (
                variables.get('candidate_id')
                or variable_values.get('candidate_id')
                or metadata.get('candidate_id')
            )

            # Transcript: prefer explicit transcript fields, fallback to building from messages
            transcript = (
                artifact.get('transcript')
                or payload.get('transcript')
                or find_first(payload, {'transcript'})
                or self._extract_transcript(artifact.get('messages', []) or call_block.get('messages', []) or find_first(payload, {'messages'}) or [])
            )

            # Summary and analysis
            summary = (
                artifact.get('analysis', {}).get('summary')
                or payload.get('summary')
                or find_first(payload, {'summary'})
            )
            analysis = artifact.get('analysis') or payload.get('analysis') or find_first(payload, {'analysis'}) or {}

            # Duration/Timing
            duration_seconds = (
                payload.get('durationSeconds')
                or artifact.get('durationSeconds')
                or call_block.get('durationSeconds')
                or find_first(payload, {'durationSeconds'})
            )
            # Some payloads only include startedAt/endedAt at top-level
            started_at = (
                payload.get('startedAt') or call_block.get('startedAt')
                or artifact.get('startedAt') or find_first(payload, {'startedAt'})
            )
            ended_at = (
                payload.get('endedAt') or call_block.get('endedAt')
                or artifact.get('endedAt') or find_first(payload, {'endedAt'})
            )

            # Determine status (prefer explicit ended signals)
            message_status = message.get('status') if isinstance(message.get('status'), str) else None
            status = (
                (message.get('status') if isinstance(message.get('status'), str) else None)
                or call_block.get('status')
                or ('completed' if payload.get('endedReason') else None)
            )

            # If event type indicates end-of-call, force completed
            event_type = payload.get('type') or message.get('type')
            if event_type in ['end-of-call-report', 'call.ended']:
                status = 'completed'

            # If we have timing/duration signals, prefer completed
            if (ended_at or duration_seconds) and status in (None, 'ringing', 'in-progress', 'in_progress'):
                status = 'completed'

            # Compute duration if missing but we have timestamps
            if not duration_seconds and started_at and ended_at:
                try:
                    start_dt = self._parse_timestamp(started_at)
                    end_dt = self._parse_timestamp(ended_at)
                    if start_dt and end_dt:
                        duration_seconds = max(0, int((end_dt - start_dt).total_seconds()))
                except Exception:
                    pass

            # Map successEvaluation to recommendation when available
            success_eval = None
            if isinstance(analysis, dict):
                success_eval = analysis.get('successEvaluation')

            return {
                'call_id': call_block.get('id') or payload.get('callId'),
                'call_status': 'completed' if (status in ['ended', 'completed']) else (status or 'completed'),
                'duration_seconds': int(duration_seconds) if duration_seconds is not None else None,
                'started_at': started_at,
                'ended_at': ended_at,
                'transcript': transcript,
                'summary': summary,
                'analysis': analysis,
                'phone_number': self._normalize_phone(phone_number) if phone_number else None,
                'candidate_id': int(candidate_id) if isinstance(candidate_id, (int, str)) and str(candidate_id).isdigit() else None,
            }
        except Exception as e:
            logger.error(f"Error normalizing VAPI webhook payload: {str(e)}")
            return None

    def _normalize_phone(self, phone: str) -> str:
        """Basic phone normalization: keep only digits, re-add leading + if present originally."""
        if not phone:
            return phone
        has_plus = phone.startswith('+')
        digits = ''.join(ch for ch in phone if ch.isdigit())
        if has_plus:
            return f"+{digits}"
        return digits
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse ISO timestamp string to datetime object"""
        if not timestamp_str:
            return None
            
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            logger.warning(f"Invalid timestamp format: {timestamp_str}")
            return None
    
    def _extract_score(self, call_data: Dict) -> Optional[int]:
        """
        Extract AI score from call data
        If no score is available from VAPI, returns None (handled gracefully by frontend)
        """
        # Check multiple possible locations for score data
        analysis = call_data.get('analysis', {})
        score = analysis.get('score')
        
        # Also check other possible score locations in VAPI response
        if score is None:
            score = call_data.get('score')
        if score is None:
            score = call_data.get('rating')
            
        if isinstance(score, (int, float)):
            return max(0, min(100, int(score)))  # Ensure score is between 0-100
        
        # If no score available, return None - frontend will show "N/A" or default value
        logger.info("No AI score found in call data - this is OK if VAPI doesn't provide scoring")
        return None
    
    def _extract_transcript(self, messages: List[Dict]) -> str:
        """
        Extract and format transcript from VAPI call messages
        
        Args:
            messages: List of message objects from VAPI call
            
        Returns:
            Formatted transcript string
        """
        transcript_parts = []
        
        for message in messages:
            role = message.get('role', '')
            content = message.get('message', '') or message.get('content', '')
            
            if role == 'assistant':
                transcript_parts.append(f"Entrevistador: {content}")
            elif role == 'user':
                transcript_parts.append(f"Candidato: {content}")
        
        return '\n\n'.join(transcript_parts)
    
    def _extract_recommendation(self, call_data: Dict) -> Optional[str]:
        """
        Extract AI recommendation from call data
        This would depend on how VAPI provides recommendation information
        """
        # Check for analysis data
        analysis = call_data.get('analysis', {})
        recommendation = analysis.get('recommendation')
        
        if recommendation in ['recommended', 'not_recommended', 'pending_review']:
            return recommendation
        
        # Check other possible locations for recommendation
        if recommendation is None:
            recommendation = call_data.get('recommendation')
            
        if recommendation in ['recommended', 'not_recommended', 'pending_review']:
            return recommendation
        
        # Check summary for keywords if no explicit recommendation
        summary = call_data.get('summary', '').lower()
        if summary:
            if any(word in summary for word in ['recomendado', 'recommended', 'excelente', 'calificado', 'bueno']):
                return 'recommended'
            elif any(word in summary for word in ['no recomendado', 'not recommended', 'rechazado', 'inadecuado', 'malo']):
                return 'not_recommended'
        
        # Try to infer from score if available
        score = self._extract_score(call_data)
        if score is not None:
            if score >= 70:
                return 'recommended'
            elif score >= 50:
                return 'pending_review'
            else:
                return 'not_recommended'
        
        # If no recommendation can be determined, default to pending_review
        # This is safe and allows manual review
        logger.info("No AI recommendation found in call data - defaulting to 'pending_review'")
        return 'pending_review'
    
    def validate_webhook_signature(self, payload: bytes, signature: str, secret: str, timestamp: str = None) -> bool:
        """
        Validate VAPI webhook signature for security
        
        Args:
            payload: Raw webhook payload
            signature: Signature from webhook headers
            secret: Webhook secret from VAPI
            timestamp: Optional timestamp for signature validation
            
        Returns:
            True if signature is valid, False otherwise
        """
        import hmac
        import hashlib
        
        try:
            # Method 1: Standard payload-only signature
            expected_signature_1 = hmac.new(
                secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature_1):
                logger.info("✅ HMAC validation successful with payload-only method")
                return True
            
            # Method 2: Try with timestamp if provided (some providers do this)
            if timestamp:
                timestamp_payload = f"{timestamp}.{payload.decode('utf-8')}"
                expected_signature_2 = hmac.new(
                    secret.encode('utf-8'),
                    timestamp_payload.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                
                if hmac.compare_digest(signature, expected_signature_2):
                    logger.info("✅ HMAC validation successful with timestamp method")
                    return True
            
            logger.error(f"❌ HMAC validation failed. Expected (payload): {expected_signature_1}")
            if timestamp:
                logger.error(f"❌ HMAC validation failed. Expected (timestamp): {expected_signature_2}")
            return False
            
        except Exception as e:
            logger.error(f"Error validating webhook signature: {str(e)}")
            return False


def create_vapi_client() -> VAPIClient:
    """Factory function to create VAPI client with environment configuration"""
    # Use VAPI_PRIVATE_KEY as the main API key for server-side operations
    return VAPIClient(
        api_key=os.getenv('VAPI_PRIVATE_KEY'),
        base_url=os.getenv('VAPI_BASE_URL', 'https://api.vapi.ai')
    )

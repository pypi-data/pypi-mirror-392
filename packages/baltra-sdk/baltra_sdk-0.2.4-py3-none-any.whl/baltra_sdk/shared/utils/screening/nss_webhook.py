"""
NSS Webhook Handler for Tu Identidad async verification results.
Handles incoming webhook notifications when NSS verification completes.
"""
import logging
import json
from flask import request, jsonify
from baltra_sdk.legacy.dashboards_folder.models import db, CandidateMedia

def handle_nss_webhook(webhook_data):
    """
    Process NSS verification webhook from Tu Identidad.
    
    Args:
        webhook_data (dict): Webhook payload from Tu Identidad
        
    Returns:
        dict: Response indicating success/failure
    """
    try:
        logging.info(f"Received NSS webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Extract webhook data
        verification_id = webhook_data.get('verificationId')
        verification_type = webhook_data.get('verificationType')
        verification_status = webhook_data.get('verificationStatus')
        verification_result = webhook_data.get('verification')
        warnings = webhook_data.get('warnings', [])
        
        # Validate this is an NSS verification (type 3)
        if verification_type != 3:
            logging.warning(f"Received non-NSS webhook (type {verification_type}), ignoring")
            return {"completed": True, "message": "Non-NSS verification ignored"}
        
        # Validate verification ID
        if not verification_id:
            logging.error("NSS webhook missing verification ID")
            return {"completed": False, "error": "Missing verification ID"}
        
        # Parse verification result JSON string
        nss_data = {}
        if verification_result:
            try:
                nss_data = json.loads(verification_result)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse NSS verification result: {e}")
                nss_data = {"error": "Invalid JSON in verification result"}
        
        # Find the NSS tracking record in database
        nss_media = db.session.query(CandidateMedia).filter(
            CandidateMedia.media_subtype == 'NSS',
            CandidateMedia.string_submission == verification_id
        ).first()
        
        if not nss_media:
            logging.error(f"NSS tracking record not found for verification_id: {verification_id}")
            return {"completed": False, "error": "NSS tracking record not found"}
        
        # Determine verification success
        is_verified = _is_nss_verification_successful(verification_status, nss_data, warnings)
        
        # Prepare complete verification result
        complete_result = {
            "verification_id": verification_id,
            "verification_type": verification_type,
            "verification_status": verification_status,
            "nss_data": nss_data,
            "warnings": warnings,
            "webhook_received_at": db.func.now()
        }
        
        # Update NSS record
        nss_media.verified = is_verified
        nss_media.verification_result = complete_result
        # If NSS number provided, replace string_submission with actual NSS (even if not verified yet)
        try:
            nss_value = nss_data.get('nss')
            if nss_value:
                nss_media.string_submission = str(nss_value)
        except Exception:
            pass
        
        db.session.commit()
        
        # Log result
        candidate_id = nss_media.candidate_id
        nss_number = nss_data.get('nss', 'Unknown')
        
        if is_verified:
            logging.info(f"✅ NSS verification completed successfully for candidate {candidate_id}: NSS={nss_number}")
        else:
            logging.warning(f"❌ NSS verification failed for candidate {candidate_id}: {_get_nss_error_message(nss_data, warnings)}")
        
        return {"completed": True, "message": f"NSS verification updated for candidate {candidate_id}"}
        
    except Exception as e:
        logging.error(f"Error processing NSS webhook: {e}")
        db.session.rollback()
        return {"completed": False, "error": str(e)}

def _is_nss_verification_successful(verification_status, nss_data, warnings):
    """
    Determine if NSS verification was successful based on status and data.
    
    Args:
        verification_status (int): Status from webhook (4 = completed)
        nss_data (dict): Parsed NSS verification data
        warnings (list): Warning messages
        
    Returns:
        bool: True if verification successful
    """
    # Status 4 = Completed (successful)
    if verification_status != 4:
        return False
    
    # Check if NSS number was found
    nss_number = nss_data.get('nss')
    if not nss_number or nss_number.strip() == "":
        return False
    
    # Check for critical warnings that indicate failure
    for warning in warnings:
        warning_code = warning.get('code', '')
        if warning_code in ['NSS005', 'NSS006', 'NSS007']:  # CURP mismatch, invalid format, IMSS unavailable
            return False
    
    return True

def _get_nss_error_message(nss_data, warnings):
    """
    Generate human-readable error message for failed NSS verification.
    
    Args:
        nss_data (dict): NSS verification data
        warnings (list): Warning messages
        
    Returns:
        str: Error message
    """
    if warnings:
        return warnings[0].get('message', 'Unknown NSS error')
    
    if 'error' in nss_data:
        return nss_data['error']
    
    return "NSS verification failed - no NSS number found"

def validate_nss_webhook_data(data):
    """
    Validate incoming NSS webhook data structure.
    
    Args:
        data (dict): Webhook payload
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['verificationId', 'verificationType', 'verificationStatus']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate verification type is NSS (3)
    if data.get('verificationType') != 3:
        return False, f"Invalid verification type: {data.get('verificationType')} (expected 3 for NSS)"
    
    # Validate status is valid
    valid_statuses = [1, 2, 3, 4]  # Processing, Retrying, Delivering, Completed
    if data.get('verificationStatus') not in valid_statuses:
        return False, f"Invalid verification status: {data.get('verificationStatus')}"
    
    return True, None

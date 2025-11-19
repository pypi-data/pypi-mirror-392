import logging
import boto3
import base64
from datetime import datetime
from flask import current_app
from .whatsapp_utils import get_media_url, download_media_file_from_meta
from .sql_utils import store_candidate_media


class ScreeningMediaHandler:
    """
    Handles media uploads from WhatsApp Flows during candidate screening.
    Downloads media from WhatsApp and uploads to S3.
    """
    
    def __init__(self):
        # Use IAM roles for authentication (same approach as report_generator.py)
        # boto3 automatically uses EC2 instance IAM roles when available
        aws_config = {}
        
        if current_app.config.get('AWS_REGION'):
            aws_config['region_name'] = current_app.config.get('AWS_REGION')
        
        self.s3_client = boto3.client('s3', **aws_config)
        self.bucket_name = current_app.config.get('S3_BUCKET_SCREENING', 'screeningbucket')
    
    def process_flow_media(self, candidate_data, flow_data):
        """
        Process media from WhatsApp Flow response.
        
        Args:
            candidate_data (dict): Candidate information
            flow_data (dict): Flow response containing images/documents
            
        Returns:
            dict: Processing results with success count and errors
        """
        results = {
            'processed_count': 0,
            'failed_count': 0,
            'media_ids': [],
            'errors': []
        }
        
        try:
            # Process images if present
            if 'images' in flow_data:
                for image in flow_data['images']:
                    success, media_id, error = self._process_single_media(
                        candidate_data, 
                        image, 
                        'image',
                        flow_data.get('flow_token', 'unknown')
                    )
                    
                    if success:
                        results['processed_count'] += 1
                        results['media_ids'].append(media_id)
                    else:
                        results['failed_count'] += 1
                        results['errors'].append(error)
            
            # Process documents if present (for future use)
            if 'documents' in flow_data:
                for document in flow_data['documents']:
                    success, media_id, error = self._process_single_media(
                        candidate_data, 
                        document, 
                        'document',
                        flow_data.get('flow_token', 'unknown')
                    )
                    
                    if success:
                        results['processed_count'] += 1
                        results['media_ids'].append(media_id)
                    else:
                        results['failed_count'] += 1
                        results['errors'].append(error)
            
            logging.info(f"Media processing complete for candidate {candidate_data['candidate_id']}: "
                        f"{results['processed_count']} successful, {results['failed_count']} failed")
            
            return results
            
        except Exception as e:
            logging.error(f"Error processing flow media for candidate {candidate_data['candidate_id']}: {e}")
            results['errors'].append(str(e))
            return results
    
    def _process_single_media(self, candidate_data, media_item, media_type, flow_token):
        """
        Process a single media item: download from WhatsApp and upload to S3.
        
        Args:
            candidate_data (dict): Candidate information
            media_item (dict): Single media item from flow response
            media_type (str): 'image' or 'document'
            flow_token (str): Flow token for tracking
            
        Returns:
            tuple: (success: bool, media_id: int or None, error: str or None)
        """
        try:
            # Extract media info
            whatsapp_media_id = str(media_item.get('id', ''))
            file_name = media_item.get('file_name', f'{media_type}_{whatsapp_media_id}')
            mime_type = media_item.get('mime_type', 'application/octet-stream')
            sha256_hash = media_item.get('sha256', '')
            
            logging.info(f"Processing {media_type} {whatsapp_media_id} for candidate {candidate_data['candidate_id']}")
            
            # Get WhatsApp media URL
            media_url = get_media_url(whatsapp_media_id)
            if not media_url:
                return False, None, f"Failed to get media URL for {whatsapp_media_id}"
            
            # Download media from WhatsApp
            file_content, file_extension, file_size = download_media_file_from_meta(media_url, whatsapp_media_id)
            if not file_content:
                return False, None, f"Failed to download media {whatsapp_media_id}"
            
            # Try to parse flow_token to derive a descriptive base name
            descriptive_prefix = None
            try:
                import json
                if isinstance(flow_token, str):
                    token_obj = json.loads(flow_token) if flow_token.startswith('{') else {"flow_type": flow_token}
                elif isinstance(flow_token, dict):
                    token_obj = flow_token
                else:
                    token_obj = {"flow_type": str(flow_token)}
                flow_type = token_obj.get('flow_type') or token_obj.get('flow_name')
                if flow_type:
                    # Normalize flow_type into a filesystem-friendly slug
                    import re
                    flow_slug = re.sub(r'[^A-Za-z0-9_\-]+', '_', str(flow_type)).strip('_')
                    descriptive_prefix = f"{flow_slug}"
            except Exception:
                descriptive_prefix = None

            # If we have a descriptive prefix, replace the incoming file_name with a normalized pattern
            if descriptive_prefix:
                # Include candidate id and media type for uniqueness
                base_name = f"{descriptive_prefix}_{media_type}_candidate_{candidate_data['candidate_id']}"
                # We will append the extension after cleaning
                file_name = base_name

            # Generate S3 key with organized folder structure
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            company_id = candidate_data['company_id']
            candidate_id = candidate_data['candidate_id']
            
            # Clean filename for S3
            clean_filename = self._clean_filename(file_name, file_extension)
            s3_key = f"company_{company_id}/candidate_{candidate_id}/{media_type}s/{timestamp}_{clean_filename}"
            
            # Upload to S3
            s3_url = self._upload_to_s3(file_content, s3_key, mime_type)
            if not s3_url:
                return False, None, f"Failed to upload {whatsapp_media_id} to S3"
            
            # Store metadata in database
            media_data = {
                'candidate_id': candidate_data['candidate_id'],
                'company_id': candidate_data['company_id'],
                'question_id': candidate_data.get('question_id'),
                'set_id': candidate_data.get('set_id'),
                'file_name': clean_filename,
                'mime_type': mime_type,
                'file_size': file_size,
                's3_bucket': self.bucket_name,
                's3_key': s3_key,
                's3_url': s3_url,
                'whatsapp_media_id': whatsapp_media_id,
                'sha256_hash': sha256_hash,
                'flow_token': flow_token
            }
            
            media_id = store_candidate_media(media_data)
            if not media_id:
                return False, None, f"Failed to store metadata for {whatsapp_media_id}"
            
            logging.info(f"✅ Successfully processed {media_type} {whatsapp_media_id} -> media_id {media_id}")
            return True, media_id, None
            
        except Exception as e:
            error_msg = f"Error processing {media_type} {media_item.get('id', 'unknown')}: {e}"
            logging.error(error_msg)
            return False, None, error_msg
    
    def _upload_to_s3(self, file_content, s3_key, mime_type):
        """
        Upload file content to S3.
        
        Args:
            file_content (bytes): File content to upload
            s3_key (str): S3 object key
            mime_type (str): File MIME type
            
        Returns:
            str: S3 URL if successful, None otherwise
        """
        try:
            # Upload with server-side encryption (public access via bucket policy)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=mime_type,
                ServerSideEncryption='AES256',
                Metadata={
                    'uploaded_by': 'whatsapp_screening',
                    'upload_timestamp': datetime.now().isoformat()
                }
            )
            
            # Generate S3 URL (public for now as per your setup)
            s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            logging.info(f"✅ Uploaded to S3: {s3_key}")
            return s3_url
            
        except Exception as e:
            logging.error(f"❌ S3 upload failed for {s3_key}: {e}")
            return None
    
    def _clean_filename(self, filename, extension):
        """
        Clean filename for S3 storage.
        
        Args:
            filename (str): Original filename
            extension (str): File extension
            
        Returns:
            str: Cleaned filename
        """
        import re
        
        # Remove or replace problematic characters
        cleaned = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Ensure it has the right extension
        if not cleaned.lower().endswith(f'.{extension.lower()}'):
            name_part = cleaned.rsplit('.', 1)[0] if '.' in cleaned else cleaned
            cleaned = f"{name_part}.{extension}"
        
        # Remove invisible characters like \u200e
        cleaned = ''.join(char for char in cleaned if ord(char) >= 32)
        
        return cleaned[:100]  # Limit length 
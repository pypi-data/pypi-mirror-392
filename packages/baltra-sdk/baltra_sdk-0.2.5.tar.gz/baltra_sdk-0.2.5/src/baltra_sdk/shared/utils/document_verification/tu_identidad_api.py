import requests
import logging
import os
from typing import Dict, Any, Optional, Tuple
import json

class TuIdentidadAPI:
    """
    Tu Identidad API client for document verification services.
    Supports INE and RFC verification with plans for CURP and IMSS.
    """
    
    def __init__(self):
        self.base_url_business = "https://web-prod01.tuidentidad.com/api/Business"  # For INE
        self.base_url = "https://web-prod01.tuidentidad.com/api"  # For RFC
        self.api_key = os.getenv('TU_IDENTIDAD_API_KEY', 'HomttL1G')  # Fallback for testing
        
        if not self.api_key:
            raise ValueError("TU_IDENTIDAD_API_KEY environment variable is required")
            
        self.headers_ine = {
            "ApiKey": self.api_key,
            "x-Version": "4.0"
        }
        
        self.headers_rfc = {
            "apiKey": self.api_key  # Note: lowercase 'a' for RFC endpoint
        }
        
        self.headers_curp_nss = {
            "apiKey": self.api_key  # Note: lowercase 'a' for CURP+NSS endpoint
        }
        
    def verify_ine_documents(self, front_image_url: str, back_image_url: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify INE documents using Tu Identidad API V4.
        
        Args:
            front_image_url (str): S3 URL to front image of INE
            back_image_url (str): S3 URL to back image of INE
            
        Returns:
            Tuple[bool, Dict]: (is_verified, result_data)
        """
        try:
            logging.info(f"Starting INE verification for images: {front_image_url}, {back_image_url}")
            
            # Download images from S3
            front_response = requests.get(front_image_url, stream=True)
            back_response = requests.get(back_image_url, stream=True)
            
            if front_response.status_code != 200 or back_response.status_code != 200:
                error_msg = f"Failed to download images. Front: {front_response.status_code}, Back: {back_response.status_code}"
                logging.error(error_msg)
                return False, {"error": error_msg, "error_type": "download_failed"}
            
            # Prepare files for API
            files = {
                "FrontFile": ("ine_front.jpg", front_response.raw, "image/jpeg"),
                "BackFile": ("ine_back.jpg", back_response.raw, "image/jpeg")
            }
            
            # API parameters
            data = {
                "checkInfo": "true",
                "checkQuality": "true",
                "checkPatterns": "true",
                "checkCurp": "true",
                "checkFace": "true",
                "debugRenapo": "false",
                "v": "4.0"
            }

            # Make API call
            response = requests.post(
                f"{self.base_url_business}/ine",
                headers=self.headers_ine,
                files=files,
                data=data,
                timeout=30
            )
            
            # Close streams
            front_response.close()
            back_response.close()
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                # Be tolerant to casing/nesting differences from provider
                is_verified = bool(
                    result.get('valid') or
                    result.get('Valid') or
                    (isinstance(result.get('data'), dict) and (
                        result['data'].get('valid') or result['data'].get('Valid')
                    ))
                )
                
                logging.info(f"INE verification completed. Valid: {is_verified}")
                return is_verified, result
            else:
                error_msg = f"API call failed with status {response.status_code}: {response.text}"
                logging.error(error_msg)
                return False, {"error": error_msg, "error_type": "api_error", "status_code": response.status_code}
                
        except requests.exceptions.Timeout:
            error_msg = "Tu Identidad API timeout"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "timeout"}
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during verification: {str(e)}"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "network_error"}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from API: {str(e)}"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "json_error"}
        except Exception as e:
            error_msg = f"Unexpected error during INE verification: {str(e)}"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "unexpected_error"}
    
    
    def verify_rfc_string(self, rfc_string: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify RFC using 13-character string via Tu Identidad RFC API.
        Uses the "RFC by RFC" endpoint specifically designed for string validation.
        
        Args:
            rfc_string (str): 13-character RFC string
            
        Returns:
            Tuple[bool, Dict]: (is_verified, result_data)
        """
        try:
            logging.info(f"Starting RFC string verification for: {rfc_string}")
            
            # Validate RFC string format (13 characters for physical person)
            if not rfc_string or len(rfc_string) != 13:
                error_msg = f"RFC debe tener exactamente 13 caracteres. Recibido: '{rfc_string}' ({len(rfc_string)} caracteres)"
                logging.error(error_msg)
                return False, {"error": error_msg, "error_type": "invalid_format"}
            
            # Prepare data for the RFC validation endpoint
            data = {
                "rfc": rfc_string.upper().strip()
            }
            
            # Use the specific "RFC by RFC" endpoint for string validation
            # Note: Using POST method as the endpoint returns 405 for GET
            response = requests.post(
                f"{self.base_url}/rfc/validate",
                headers=self.headers_rfc,
                data=data,
                timeout=30
            )
            
            logging.info(f"RFC API request: POST {self.base_url}/rfc/validate with data: {data}")
            logging.info(f"RFC API response status: {response.status_code}")
            
            # Log response body for debugging
            if response.status_code != 200:
                logging.error(f"RFC API error response: {response.text}")
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                is_verified = result.get('valid', False)
                
                logging.info(f"RFC string verification completed for {rfc_string}. Valid: {is_verified}")
                logging.info(f"RFC API response: {json.dumps(result, indent=2)}")
                return is_verified, result
            else:
                error_msg = f"RFC string API call failed with status {response.status_code}: {response.text}"
                logging.error(error_msg)
                return False, {"error": error_msg, "error_type": "api_error", "status_code": response.status_code}
                
        except requests.exceptions.Timeout:
            error_msg = "Tu Identidad RFC string API timeout"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "timeout"}
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during RFC string verification: {str(e)}"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "network_error"}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from RFC string API: {str(e)}"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "json_error"}
        except Exception as e:
            error_msg = f"Unexpected error during RFC string verification: {str(e)}"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "unexpected_error"}
    
    def verify_curp_nss(self, curp_string: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify CURP and initiate NSS verification using Tu Identidad CURP+IMSS API.
        
        Args:
            curp_string (str): 18-character CURP string
            
        Returns:
            Tuple[bool, Dict]: (is_verified, result_data)
        """
        try:
            logging.info(f"Starting CURP+NSS verification for: {curp_string}")
            
            # Validate CURP string format (18 characters)
            if not curp_string or len(curp_string) != 18:
                error_msg = f"CURP debe tener exactamente 18 caracteres. Recibido: '{curp_string}' ({len(curp_string)} caracteres)"
                logging.error(error_msg)
                return False, {"error": error_msg, "error_type": "invalid_format"}
            
            # Prepare data for the CURP+NSS validation endpoint
            data = {
                "CURP": curp_string.upper().strip()
            }
            
            # Use the CURP+IMSS endpoint for validation
            response = requests.post(
                f"{self.base_url}/ImssCurp/validate",
                headers=self.headers_curp_nss,
                json=data,  # Using JSON format as per documentation
                timeout=30
            )
            
            logging.info(f"CURP+NSS API request: POST {self.base_url}/ImssCurp/validate with data: {data}")
            logging.info(f"CURP+NSS API response status: {response.status_code}")
            
            # Log response body for debugging
            if response.status_code != 200:
                logging.error(f"CURP+NSS API error response: {response.text}")
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                is_verified = result.get('valid', False)
                
                logging.info(f"CURP+NSS verification completed for {curp_string}. Valid: {is_verified}")
                logging.info(f"CURP+NSS API response: {json.dumps(result, indent=2)}")
                return is_verified, result
            else:
                error_msg = f"CURP+NSS API call failed with status {response.status_code}: {response.text}"
                logging.error(error_msg)
                return False, {"error": error_msg, "error_type": "api_error", "status_code": response.status_code}
                
        except requests.exceptions.Timeout:
            error_msg = "Tu Identidad CURP+NSS API timeout"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "timeout"}
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during CURP+NSS verification: {str(e)}"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "network_error"}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from CURP+NSS API: {str(e)}"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "json_error"}
        except Exception as e:
            error_msg = f"Unexpected error during CURP+NSS verification: {str(e)}"
            logging.error(error_msg)
            return False, {"error": error_msg, "error_type": "unexpected_error"}
    
    def get_validation_message(self, verification_result: Dict[str, Any], document_type: str = "INE") -> str:
        """
        Generate human-readable validation message based on verification result.
        
        Args:
            verification_result (Dict): Result from verification API
            document_type (str): Type of document ("INE" or "RFC")
            
        Returns:
            str: Human-readable message
        """
        if verification_result.get('valid'):
            data = verification_result.get('data', {})
            
            if document_type.upper() == "RFC":
                person_type = data.get('personType', '')
                rfc = data.get('rfc', '')
                
                if person_type == "1":  # Physical person
                    name = data.get('name', '')
                    
                    # For the "RFC by RFC" endpoint, we only get the name field for physical persons
                    if name:
                        return f"✅ RFC personal verificado exitosamente para {name} ({rfc})"
                    else:
                        return f"✅ RFC personal verificado exitosamente ({rfc})"
                        
                elif person_type == "2":  # Juridical person (company)
                    business_name = data.get('businessName', '')
                    if business_name:
                        return f"✅ RFC empresarial verificado exitosamente para {business_name} ({rfc})"
                    else:
                        return f"✅ RFC empresarial verificado exitosamente ({rfc})"
                else:
                    # Unknown person type or missing data
                    return f"✅ RFC verificado exitosamente ({rfc})"
            elif document_type.upper() == "CURP":
                curp_data = verification_result.get('curpData', {})
                curp = curp_data.get('curp', '')
                names = curp_data.get('names', '')
                last_name = curp_data.get('lastName', '')
                
                if names and last_name:
                    return f"✅ CURP verificado exitosamente para {names} {last_name} ({curp})"
                else:
                    return f"✅ CURP verificado exitosamente ({curp})"
            else:  # INE
                name = data.get('name', '')
                return f"✅ INE verificado exitosamente para {name}"
        else:
            if document_type.upper() == "RFC":
                # RFC-specific error handling
                warnings = verification_result.get('warnings', [])
                if warnings:
                    error_msg = warnings[0].get('message', 'Error de verificación desconocido')
                else:
                    error_msg = "Error de verificación desconocido"
                return f"❌ RFC no válido: {error_msg}"
            elif document_type.upper() == "CURP":
                # CURP-specific error handling
                warnings = verification_result.get('warnings', [])
                if warnings:
                    error_msg = warnings[0].get('message', 'Error de verificación CURP desconocido')
                else:
                    error_msg = "Error de verificación CURP desconocido"
                return f"❌ CURP no válido: {error_msg}"
            else:  # INE
                # Check for specific error messages
                validations = verification_result.get('validations', {})
                messages = []
                
                if not validations.get('quality'):
                    messages.append("La calidad de la imagen no es adecuada")
                if not validations.get('info'):
                    messages.append("Los datos del INE no pudieron ser validados")
                if not validations.get('curp'):
                    messages.append("El CURP no pudo ser verificado")
                if not validations.get('patternCheck'):
                    messages.append("El patrón del INE no es válido")
                if not validations.get('nominalListCheck'):
                    messages.append("El INE no se encuentra en la lista nominal")
                    
                error_msg = "; ".join(messages) if messages else "Error de verificación desconocido"
                return f"❌ INE no válido: {error_msg}"

# Legacy function for backward compatibility - can be removed later
def verify_ine_legacy():
    """Legacy function for testing - will be removed"""
    front_url = "https://screeningbucket.s3.us-east-2.amazonaws.com/company_10/candidate_1890/images/20250812_155933_documents_INE_image_candidate_1890.jpg"
    
    # This is just for testing - replace with actual back image URL
    api = TuIdentidadAPI()
    is_verified, result = api.verify_ine_documents(front_url, front_url)
    
    print(f"Verification result: {is_verified}")
    print(f"Details: {json.dumps(result, indent=2)}")
    
    return is_verified, result

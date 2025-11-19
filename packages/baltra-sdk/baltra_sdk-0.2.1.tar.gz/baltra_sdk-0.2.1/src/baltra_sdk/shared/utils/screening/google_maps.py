import os
import math
import requests
import logging
import json
from typing import Optional, Dict, Any
from .company_data import get_company_location


logger = logging.getLogger(__name__)


class LocationService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY")
        
        # Validate API key on initialization
        if not self.api_key:
            logger.error("Google Maps API key not provided. Set GOOGLE_MAPS_API_KEY environment variable or pass api_key parameter.")
            raise ValueError("Google Maps API key is required")
        
        logger.info(f"LocationService initialized with API key: {'*' * (len(self.api_key) - 4)}{self.api_key[-4:]}")

    def autocomplete(self, search: str) -> Dict[str, Any]:
        """
        Retrieve autocomplete predictions for a given search string using the Google Maps API.

        Args:
            search (str): The search input to be autocompleted.

        Returns:
            dict: A dictionary containing place IDs as keys and address info as values.

        Raises:
            ValueError: If the response status is not OK.
        """
        logger.info(f"Starting autocomplete search for: '{search}'")
        
        if not search or not search.strip():
            logger.warning("Empty search string provided to autocomplete")
            raise ValueError("Search string cannot be empty")
        
        url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        params = {
            "input": search.strip(),
            "key": self.api_key,
        }
        
        logger.debug(f"Making autocomplete request to: {url}")
        logger.debug(f"Request parameters: {dict(params, key='***HIDDEN***')}")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses
            logger.debug(f"HTTP response status: {response.status_code}")
            
            data = response.json()
            logger.debug(f"Response data status: {data.get('status', 'NO_STATUS')}")
            
        except requests.exceptions.Timeout:
            logger.error("Request timeout while calling autocomplete API")
            raise ValueError("Request timeout - Google Maps API is not responding")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error in autocomplete request: {e}")
            raise ValueError(f"HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception in autocomplete: {e}")
            raise ValueError(f"Network error: {e}")
        except ValueError as e:
            logger.error(f"JSON decode error in autocomplete response: {e}")
            raise ValueError("Invalid JSON response from Google Maps API")
        except Exception as e:
            logger.error(f"Unexpected error in autocomplete: {e}")
            raise ValueError(f"Unexpected error: {e}")

        # Check if we got valid data
        if not data:
            logger.error("No data received from autocomplete API")
            raise ValueError("No data received from Google Maps API")

        status = data.get("status")
        if status != "OK":
            error_msg = data.get("error_message", "Unknown error")
            logger.error(f"Autocomplete API returned status: {status}, error: {error_msg}")
            
            # Handle specific API error statuses
            if status == "ZERO_RESULTS":
                logger.info(f"No autocomplete results found for: '{search}'")
                return {"results": {}}
            elif status == "INVALID_REQUEST":
                raise ValueError(f"Invalid request to autocomplete API: {error_msg}")
            elif status == "OVER_QUERY_LIMIT":
                raise ValueError("Google Maps API quota exceeded")
            elif status == "REQUEST_DENIED":
                raise ValueError(f"Request denied by Google Maps API: {error_msg}")
            else:
                raise ValueError(f"Google Maps API error: {status} - {error_msg}")

        predictions = data.get("predictions", [])
        logger.info(f"Successfully retrieved {len(predictions)} autocomplete predictions")
        
        if not predictions:
            logger.info(f"No predictions found for search: '{search}'")
            return {"results": {}}

        results = {}
        for item in predictions:
            try:
                place_id = item["place_id"]
                description = item["description"]
                results[place_id] = {
                    "address": description,
                    "id": place_id
                }
                logger.debug(f"Added prediction: {place_id} -> {description}")
            except KeyError as e:
                logger.warning(f"Missing key in prediction item: {e}")
                continue
        
        logger.info(f"Autocomplete completed successfully with {len(results)} results")
        return {"results": results}

    def get_directions_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Get place details including location coordinates for a given place ID.

        Args:
            place_id (str): The place ID to get details for.

        Returns:
            dict or None: A dictionary with position, shortAddress, and address if successful; otherwise, None.
        """
        logger.info(f"Getting place details for place_id: {place_id}")
        
        if not place_id or not place_id.strip():
            logger.warning("Empty place_id provided to get_directions_details")
            return None
        
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id.strip(),
            "key": self.api_key,
        }
        
        logger.debug(f"Making place details request to: {url}")
        logger.debug(f"Request parameters: {dict(params, key='***HIDDEN***')}")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            logger.debug(f"HTTP response status: {response.status_code}")
            
            data = response.json()
            logger.debug(f"Response data status: {data.get('status', 'NO_STATUS')}")
            
        except requests.exceptions.Timeout:
            logger.error("Request timeout while calling place details API")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error in place details request: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception in place details: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON decode error in place details response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in place details: {e}")
            return None

        if not data:
            logger.error("No data received from place details API")
            return None

        status = data.get("status")
        if status != "OK":
            error_msg = data.get("error_message", "Unknown error")
            logger.error(f"Place details API returned status: {status}, error: {error_msg}")
            return None

        result = data.get("result")
        if not result:
            logger.error("No result data in place details response")
            return None

        try:
            geometry = result.get("geometry", {})
            location = geometry.get("location", {})
            
            if not location:
                logger.error("No location data in place details response")
                return None
            
            place_details = {
                "position": {
                    "lat": location["lat"],
                    "lng": location["lng"]
                },
                "shortAddress": result.get("name", "Unknown"),
                "address": result.get("formatted_address", "Unknown")
            }
            
            logger.info(f"Successfully retrieved place details for {place_id}")
            logger.debug(f"Place details: {place_details}")
            return place_details
            
        except KeyError as e:
            logger.error(f"Missing required key in place details response: {e}")
            return None

    def get_geolocation(self, search_query: str = "florida", type_: str = "address") -> Optional[Dict[str, Any]]:
        """
        Get geolocation data for a given address, lat/lng, or place ID.

        Args:
            search_query (str): The query to search (address, coordinates, or place ID).
            type_ (str): Type of the query. Accepted values: "latlng", "address", "place_id".

        Returns:
            dict or None: A dictionary with geolocation and address details if successful; otherwise, None.
        """
        logger.info(f"Getting geolocation for query: '{search_query}', type: '{type_}'")
        
        if not search_query or not search_query.strip():
            logger.warning("Empty search_query provided to get_geolocation")
            return None
        
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        query_types = ["latlng", "address", "place_id"]
        query_type = type_ if type_ in query_types else "address"
        
        if type_ != query_type:
            logger.warning(f"Invalid query type '{type_}' provided, defaulting to 'address'")
        
        params = {
            query_type: search_query.strip(),
            "key": self.api_key,
        }
        
        logger.debug(f"Making geocoding request to: {url}")
        logger.debug(f"Request parameters: {dict(params, key='***HIDDEN***')}")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            logger.debug(f"HTTP response status: {response.status_code}")
            
            data = response.json()
            logger.debug(f"Response data status: {data.get('status', 'NO_STATUS')}")
            
        except requests.exceptions.Timeout:
            logger.error("Request timeout while calling geocoding API")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error in geocoding request: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception in geocoding: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON decode error in geocoding response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in geocoding: {e}")
            return None

        if not data:
            logger.error("No data received from geocoding API")
            return None

        status = data.get("status")
        if status != "OK":
            error_msg = data.get("error_message", "Unknown error")
            logger.error(f"Geocoding API returned status: {status}, error: {error_msg}")
            return None

        results = data.get("results", [])
        if not results:
            logger.warning(f"No geocoding results found for: '{search_query}'")
            return None

        result = results[0]
        logger.debug(f"Using first geocoding result: {result.get('formatted_address', 'Unknown')}")

        try:
            # Parse address components
            details = {}
            address_components = result.get("address_components", [])
            
            for component in address_components:
                types = component.get("types", [])
                long_name = component.get("long_name", "")
                
                if "street_number" in types:
                    details["street"] = long_name
                elif "locality" in types:
                    details["city"] = long_name
                elif "administrative_area_level_1" in types:
                    details["state"] = long_name
                elif "postal_code" in types:
                    details["postal_code"] = long_name
                elif "country" in types:
                    details["country"] = long_name

            # Get geometry data
            geometry = result.get("geometry", {})
            location = geometry.get("location", {})
            
            if not location:
                logger.error("No location data in geocoding response")
                return None

            formatted_address = result.get("formatted_address", "Unknown")
            place_id = result.get("place_id", "")
            
            geolocation_data = {
                "details": details,
                "position": {
                    "lat": location["lat"],
                    "lng": location["lng"]
                },
                "shortAddress": formatted_address.split(",")[0] if formatted_address else "Unknown",
                "address": formatted_address,
                "id": place_id
            }
            
            logger.info(f"Successfully retrieved geolocation data for '{search_query}'")
            logger.debug(f"Geolocation data: {geolocation_data}")
            return geolocation_data
            
        except KeyError as e:
            logger.error(f"Missing required key in geocoding response: {e}")
            return None
      
      
    def get_travel_time_by_coords(self, origin: dict, destination: dict, mode: str = "transit") -> Optional[Dict[str, Any]]:
        """
        Get travel time between two coordinates using Google Maps Routes API.

        Args:
            origin (dict): Dictionary with 'latitude' and 'longitude' for the origin.
            destination (dict): Dictionary with 'latitude' and 'longitude' for the destination.
            mode (str): Travel mode: 'DRIVE', 'WALK', 'BICYCLE', or 'TRANSIT'.

        Returns:
            dict or None: A dictionary with duration and distance if successful; otherwise, None.
        """
        logger.info(f"Getting travel time from {origin} to {destination} using mode: {mode}")
        
        # Validate inputs
        if not origin or not destination:
            logger.error("Origin or destination coordinates not provided")
            return None
            
        required_keys = ['latitude', 'longitude']
        for coord_dict, name in [(origin, 'origin'), (destination, 'destination')]:
            if not all(key in coord_dict for key in required_keys):
                logger.error(f"Missing required coordinates in {name}: {coord_dict}")
                return None
            
            # Validate coordinate ranges
            lat, lng = coord_dict['latitude'], coord_dict['longitude']
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                logger.error(f"Invalid coordinates in {name}: lat={lat}, lng={lng}")
                return None
        
        # Map legacy mode names to new Routes API travel modes
        mode_mapping = {
            "driving": "DRIVE",
            "walking": "WALK", 
            "bicycling": "BICYCLE",
            "transit": "TRANSIT"
        }
        
        # Convert mode to new format
        original_mode = mode
        if mode.lower() in mode_mapping:
            travel_mode = mode_mapping[mode.lower()]
        elif mode.upper() in ["DRIVE", "WALK", "BICYCLE", "TRANSIT"]:
            travel_mode = mode.upper()
        else:
            logger.warning(f"Invalid travel mode '{mode}', defaulting to 'TRANSIT'")
            travel_mode = "TRANSIT"
        
        if mode != original_mode:
            logger.info(f"Travel mode converted from '{original_mode}' to '{travel_mode}'")

        # New Routes API endpoint
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        
        # Build request body for Routes API
        request_body = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": origin['latitude'],
                        "longitude": origin['longitude']
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": destination['latitude'],
                        "longitude": destination['longitude']
                    }
                }
            },
            "travelMode": travel_mode,
            "computeAlternativeRoutes": False,
            "languageCode": "es",  # Spanish language for responses
            "units": "METRIC"
        }
        
        # Add routing preferences only for non-transit modes
        if travel_mode != "TRANSIT":
            request_body["routingPreference"] = "TRAFFIC_AWARE"
            request_body["routeModifiers"] = {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            }
        
        # Add transit-specific options if using transit mode
        if travel_mode == "TRANSIT":
            request_body["transitPreferences"] = {
                "allowedTravelModes": ["BUS", "SUBWAY", "TRAIN", "LIGHT_RAIL"],
                "routingPreference": "FEWER_TRANSFERS"
            }
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.staticDuration,routes.legs.duration,routes.legs.distanceMeters"
        }
        
        logger.debug(f"Making Routes API request to: {url}")
        logger.debug(f"Request body: {json.dumps(request_body, indent=2)}")
        logger.debug(f"Request headers: {dict(headers, **{'X-Goog-Api-Key': '***HIDDEN***'})}")

        try:
            response = requests.post(url, json=request_body, headers=headers, timeout=15)
            response.raise_for_status()
            logger.debug(f"HTTP response status: {response.status_code}")
            
            data = response.json()
            logger.debug(f"Routes API response received")
            
        except requests.exceptions.Timeout:
            logger.error("Request timeout while calling Routes API")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error in Routes API request: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Error response body: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception in Routes API: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON decode error in Routes API response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Routes API: {e}")
            return None

        if not data:
            logger.error("No data received from Routes API")
            return None

        # Check if routes are available in the response
        routes = data.get("routes", [])
        if not routes:
            logger.warning("No routes found in Routes API response")
            return None

        try:
            route = routes[0]  # Use the first (primary) route
            
            # Get overall route duration and distance
            route_duration = route.get("duration")
            route_distance_meters = route.get("distanceMeters")
            route_static_duration = route.get("staticDuration")  # Duration without traffic
            
            # Get leg information (first leg for simple origin-destination)
            legs = route.get("legs", [])
            if not legs:
                logger.error("No legs found in route")
                return None
                
            leg = legs[0]
            leg_duration = leg.get("duration")
            leg_distance_meters = leg.get("distanceMeters")
            
            # Use leg data as primary, fallback to route data
            duration_seconds = None
            distance_meters = None
            
            # Parse duration from leg or route
            if leg_duration:
                duration_str = leg_duration.rstrip('s')  # Remove 's' suffix
                duration_seconds = int(float(duration_str))
            elif route_duration:
                duration_str = route_duration.rstrip('s')
                duration_seconds = int(float(duration_str))
            
            # Get distance from leg or route
            if leg_distance_meters is not None:
                distance_meters = int(leg_distance_meters)
            elif route_distance_meters is not None:
                distance_meters = int(route_distance_meters)
            
            if duration_seconds is None or distance_meters is None:
                logger.error("Missing duration or distance data in Routes API response")
                return None
            
            # Format duration text (convert seconds to human readable format)
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            
            # Calculate hours and minutes text
            if hours > 0:
                duration_text = f"{hours} h {minutes} min"
            else:
                duration_text = f"{minutes} min"

            # Format distance text (convert meters to km if > 1000m)
            if distance_meters >= 1000:
                distance_km = distance_meters / 1000
                distance_text = f"{distance_km:.1f} km"
            else:
                distance_text = f"{distance_meters} m"
            
            # Build travel info dictionary
            travel_info = {
                # Store total duration in minutes (not just remainder minutes)
                "duration_minutes": duration_seconds // 60,
                "duration_seconds": duration_seconds,
                "duration_text": duration_text,
                "distance_text": distance_text,
                "distance_meters": distance_meters,
                "travel_mode": travel_mode
            }
            
            # Add static duration (without traffic) if available for driving mode
            if route_static_duration and travel_mode == "DRIVE":
                static_duration_str = route_static_duration.rstrip('s')
                static_duration_seconds = int(float(static_duration_str))
                travel_info["static_duration_seconds"] = static_duration_seconds
                
                # Calculate traffic delay
                traffic_delay = duration_seconds - static_duration_seconds
                travel_info["traffic_delay_seconds"] = max(0, traffic_delay)
            
            logger.info(f"Successfully retrieved travel time: {travel_info['duration_text']}, {travel_info['distance_text']}")
            logger.debug(f"Travel info: {travel_info}")
            return travel_info
            
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing Routes API response: {e}")
            logger.debug(f"Response data: {json.dumps(data, indent=2)}")
            return None

    def _parse_duration_seconds(self, duration_str: str) -> Optional[int]:
        try:
            return int(float(duration_str.rstrip('s'))) if isinstance(duration_str, str) else None
        except Exception:
            return None

    def compute_transit_route_matrix(self, origin: Dict, destinations: list) -> list:
        """
        origin: {"lat": float, "lng": float}
        destinations: [{"id": int, "lat": float, "lng": float}, ...]
        Returns list of elements:
          [{ "id": int, "duration_seconds": int, "distance_meters": int|None, "status": "OK"|"NO_ROUTE"|... }, ...]
        """
        logger.info(
            f"Computing transit route matrix for 1 origin and {len(destinations)} destination(s)"
        )

        # Basic validation and element cap for TRANSIT (<= 100 elements). We use 1xN, so ensure N<=100
        if not origin or not isinstance(origin, dict):
            logger.error("Invalid origin for compute_transit_route_matrix")
            return []
        if not isinstance(destinations, list) or len(destinations) == 0:
            logger.warning("No destinations provided to compute_transit_route_matrix")
            return []
        if len(destinations) > 100:
            logger.warning("Destination count exceeds 100 for TRANSIT matrix; truncating to first 100")
            destinations = destinations[:100]

        # Build request body
        body = {
            "origins": [
                {
                    "waypoint": {
                        "location": {
                            "latLng": {
                                "latitude": origin.get("lat"),
                                "longitude": origin.get("lng"),
                            }
                        }
                    }
                }
            ],
            "destinations": [
                {
                    "waypoint": {
                        "location": {
                            "latLng": {"latitude": d.get("lat"), "longitude": d.get("lng")}
                        }
                    }
                }
                for d in destinations
            ],
            "travelMode": "TRANSIT",
        }

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,status,condition,travelAdvisory.transitFare",
        }

        url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"

        logger.debug(f"Matrix request body: {json.dumps(body)[:500]}...")
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=15)
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            logger.error("Request timeout while calling Route Matrix API")
            return []
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error in Route Matrix API request: {e}")
            try:
                logger.error(f"Error response body: {resp.text}")
            except Exception:
                pass
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception in Route Matrix API: {e}")
            return []

        # Parse as JSON array; if fails, try NDJSON
        elements = []
        try:
            data = resp.json()
            elements = data if isinstance(data, list) else []
        except ValueError:
            pass
        if not elements:
            text_payload = (resp.text or "").strip()
            for line in text_payload.splitlines():
                try:
                    if line.strip():
                        elements.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        if not elements:
            logger.warning("Empty Route Matrix response")
            return []

        output = []
        rejected_elements = []
        for el in elements:
            try:
                status_obj = el.get("status", {}) or {}
                condition = el.get("condition")
                dest_idx = el.get("destinationIndex")
                duration = el.get("duration")
                distance_meters = el.get("distanceMeters")

                is_ok = (not status_obj) and condition == "ROUTE_EXISTS" and duration is not None
                mapped_id = destinations[dest_idx]["id"] if dest_idx is not None and 0 <= dest_idx < len(destinations) else None

                entry = {
                    "id": mapped_id,
                    "duration_seconds": self._parse_duration_seconds(duration) if duration else None,
                    "distance_meters": int(distance_meters) if distance_meters is not None else None,
                    "status": "OK" if is_ok else (status_obj.get("code") or "NO_ROUTE"),
                }

                if is_ok and mapped_id is not None:
                    output.append(entry)
                else:
                    # Log detailed reason for rejection to help debug
                    rejected_elements.append({
                        "id": mapped_id,
                        "status_obj": status_obj,
                        "condition": condition,
                        "duration": duration,
                        "reason": f"status_empty={not status_obj}, condition={condition}, has_duration={duration is not None}"
                    })
            except Exception as parse_err:
                logger.debug(f"Skipping malformed matrix element: {parse_err}")
                continue

        # Log rejection details when no OK elements found
        if len(output) == 0 and rejected_elements:
            logger.warning(f"All {len(rejected_elements)} matrix elements were rejected:")
            for i, rejected in enumerate(rejected_elements, 1):
                logger.warning(f"  {i}. ID {rejected['id']}: {rejected['reason']}")
                if rejected['status_obj']:
                    logger.warning(f"     Status object: {rejected['status_obj']}")

        logger.info(f"Matrix computed with {len(output)} OK element(s)")
        return output

    @staticmethod
    def haversine(distance_init: dict, distance_final: dict) -> float:
        """
        Calculate the distance in kilometers between two geographic points using the Haversine formula.

        Args:
            distance_init (dict): A dictionary with keys 'latitude' and 'longitude' for the initial point.
            distance_final (dict): A dictionary with keys 'latitude' and 'longitude' for the final point.

        Returns:
            float: The distance in kilometers.
        """
        logger.debug(f"Calculating haversine distance between {distance_init} and {distance_final}")
        
        # Validate inputs
        required_keys = ['latitude', 'longitude']
        for coord_dict, name in [(distance_init, 'distance_init'), (distance_final, 'distance_final')]:
            if not coord_dict or not all(key in coord_dict for key in required_keys):
                logger.error(f"Missing required coordinates in {name}: {coord_dict}")
                raise ValueError(f"Invalid coordinates in {name}")
            
            # Validate coordinate ranges
            lat, lng = coord_dict['latitude'], coord_dict['longitude']
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                logger.error(f"Invalid coordinate values in {name}: lat={lat}, lng={lng}")
                raise ValueError(f"Invalid coordinate values in {name}")
        
        R = 6371  # Radius of the Earth in kilometers

        def to_radians(angle):
            return angle * (math.pi / 180)

        try:
            lat1 = to_radians(distance_init['latitude'])
            lon1 = to_radians(distance_init['longitude'])
            lat2 = to_radians(distance_final['latitude'])
            lon2 = to_radians(distance_final['longitude'])

            dLat = lat2 - lat1
            dLon = lon2 - lon1

            a = (
                math.sin(dLat / 2) ** 2 +
                math.cos(lat1) * math.cos(lat2) * math.sin(dLon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance_in_km = R * c
            
            logger.debug(f"Calculated haversine distance: {distance_in_km:.2f} km")
            return distance_in_km
            
        except Exception as e:
            logger.error(f"Error calculating haversine distance: {e}")
            raise ValueError(f"Error calculating distance: {e}")

def get_location_json(employee_data: dict, message: dict, message_body: str, message_type: str):
    """
    Generates a JSON object with travel time and distance to the company location using the new Routes API.
    Always returns employee coordinates, even if company location is missing.

    Args:
    - employee_data (dict): Contains employee information such as the candidate ID and company ID.
    - message (dict): The message object containing the location data (for WhatsApp locations).
    - message_body (str): The text content of the message (for text addresses).
    - message_type (str): The type of message ("location" or "text").

    Returns:
    - dict: A JSON object with travel time, distance, employee coordinates, and company coordinates (if available).
    """
    try:
        # --- Extract employee coordinates first ---
        employee_location = None
        location_source = "unknown"

        if message_type == "location" and message.get('location'):
            employee_location = message['location']
            location_source = "whatsapp_coordinates"
            logging.info(f"Processing WhatsApp location coordinates: {employee_location}")
            if not all(key in employee_location for key in ['latitude', 'longitude']):
                logging.error(f"Invalid WhatsApp location format: {employee_location}")
                employee_location = {"latitude": None, "longitude": None}

        elif message_body and message_body.strip():
            location_source = "text_address"
            logging.info(f"Processing text address: {message_body}")
            try:
                geolocation_data = LocationService().get_geolocation(message_body.strip(), "address")
                if geolocation_data and geolocation_data.get("position"):
                    employee_location = {
                        "latitude": geolocation_data["position"]["lat"],
                        "longitude": geolocation_data["position"]["lng"]
                    }
                    logging.info(f"Successfully geocoded address '{message_body}' to coordinates: {employee_location}")
            except Exception as geocoding_error:
                logging.error(f"Error geocoding address '{message_body}': {geocoding_error}")
                employee_location = {"latitude": None, "longitude": None}

        if not employee_location:
            employee_location = {"latitude": None, "longitude": None}

        # --- Fetch company location ---
        company_location = get_company_location(employee_data.get('company_id'))
        if not company_location:
            logging.warning(f"Missing company location for company {employee_data.get('company_id')}")
            # Return object with employee_coordinates even if company location missing
            return {
                "duration_text": None,
                "duration_seconds": None,
                "distance_text": None,
                "distance_meters": None,
                "travel_mode": None,
                "calculated_at": None,
                "candidate_id": employee_data.get('candidate_id'),
                "company_id": employee_data.get('company_id'),
                "employee_coordinates": employee_location,
                "company_coordinates": {"latitude": None, "longitude": None},
                "location_source": location_source,
                "input_data": message_body if message_body else "WhatsApp Location",
            }

        # --- Compute travel time ---
        location_service = LocationService()
        travel_modes = ["transit", "driving"]

        for mode in travel_modes:
            travel_data = location_service.get_travel_time_by_coords(employee_location, company_location, mode)
            if travel_data:
                if mode == "transit" and travel_data.get("duration_minutes", 0) > 200:
                    continue
                travel_data.update({
                    "candidate_id": employee_data.get('candidate_id'),
                    "company_id": employee_data.get('company_id'),
                    "employee_coordinates": employee_location,
                    "company_coordinates": company_location,
                    "location_source": location_source,
                    "input_data": message_body if location_source == "text_address" else "WhatsApp Location",
                })
                logging.info(f"Successfully calculated travel time for candidate {employee_data['candidate_id']}: {travel_data.get('duration_text')} by {mode} (source: {location_source})")
                return travel_data

        # --- Fallback: straight line distance ---
        try:
            distance_km = LocationService.haversine(employee_location, company_location)
            return {
                "duration_text": "No disponible",
                "duration_seconds": None,
                "distance_text": f"{distance_km:.1f} km (línea recta)",
                "distance_meters": int(distance_km * 1000),
                "travel_mode": "STRAIGHT_LINE",
                "calculated_at": json.dumps({"timestamp": "now"}),
                "candidate_id": employee_data.get('candidate_id'),
                "company_id": employee_data.get('company_id'),
                "employee_coordinates": employee_location,
                "company_coordinates": company_location,
                "location_source": location_source,
                "input_data": message_body if location_source == "text_address" else "WhatsApp Location",
                "note": "Distancia calculada en línea recta - no se pudo obtener ruta de transporte"
            }
        except Exception as distance_error:
            logging.error(f"Failed to calculate fallback distance for candidate {employee_data['candidate_id']}: {distance_error}")
            return {
                "error": "distance_calculation_failed",
                "message": "No se pudo calcular la distancia",
                "candidate_id": employee_data.get('candidate_id'),
                "company_id": employee_data.get('company_id'),
                "employee_coordinates": employee_location,
                "company_coordinates": company_location,
                "location_source": location_source,
                "input_data": message_body if location_source == "text_address" else "WhatsApp Location",
                "error_details": str(distance_error)
            }

    except Exception as e:
        logging.error(f"Error in get_location_json for candidate {employee_data.get('candidate_id', 'unknown')}: {e}")
        return {
            "error": "general_error",
            "message": "Error general al procesar ubicación",
            "candidate_id": employee_data.get('candidate_id', 'unknown'),
            "company_id": employee_data.get('company_id', 'unknown'),
            "employee_coordinates": employee_location if 'employee_location' in locals() else {"latitude": None, "longitude": None},
            "company_coordinates": company_location if 'company_location' in locals() else {"latitude": None, "longitude": None},
            "error_details": str(e)
        }

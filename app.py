"""
Flask Web API wrapper for LBC (Le Bon Coin) client
Deploy this to Render to use LBC API in your web applications
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import lbc
from lbc.models import Category, AdType, OwnerType, Sort, Region, Department, City
from lbc.exceptions import DatadomeError, RequestError, NotFoundError
import logging
import os
from typing import Optional, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize LBC client
client = lbc.Client()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    return jsonify({"status": "healthy", "service": "lbc-api"})

@app.route('/api/search', methods=['POST'])
def search_ads():
    """
    Search for ads on Le Bon Coin
    
    Expected JSON payload:
    {
        "text": "search term",
        "category": "IMMOBILIER",
        "sort": "NEWEST",
        "locations": [
            {
                "type": "city",
                "lat": 48.85994982004764,
                "lng": 2.33801967847424,
                "radius": 10000,
                "city": "Paris"
            }
        ],
        "page": 1,
        "limit": 35,
        "ad_type": "OFFER",
        "owner_type": "ALL",
        "search_in_title_only": true,
        "square": [200, 400],
        "price": [300000, 700000]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract search parameters
        text = data.get('text')
        category_name = data.get('category', 'TOUTES_CATEGORIES')
        sort_name = data.get('sort', 'RELEVANCE')
        locations_data = data.get('locations', [])
        page = data.get('page', 1)
        limit = data.get('limit', 35)
        ad_type_name = data.get('ad_type', 'OFFER')
        owner_type_name = data.get('owner_type')
        search_in_title_only = data.get('search_in_title_only', False)
        
        # Convert string enums to actual enum values
        try:
            category = getattr(Category, category_name.upper())
        except AttributeError:
            category = Category.TOUTES_CATEGORIES
            
        try:
            sort = getattr(Sort, sort_name.upper())
        except AttributeError:
            sort = Sort.RELEVANCE
            
        try:
            ad_type = getattr(AdType, ad_type_name.upper())
        except AttributeError:
            ad_type = AdType.OFFER
            
        owner_type = None
        if owner_type_name:
            try:
                owner_type = getattr(OwnerType, owner_type_name.upper())
            except AttributeError:
                pass
        
        # Process locations
        locations = []
        for loc_data in locations_data:
            loc_type = loc_data.get('type', 'city')
            
            if loc_type == 'city':
                location = City(
                    lat=loc_data['lat'],
                    lng=loc_data['lng'],
                    radius=loc_data.get('radius', 10000),
                    city=loc_data['city']
                )
            elif loc_type == 'region':
                try:
                    location = getattr(Region, loc_data['name'].upper())
                except AttributeError:
                    continue
            elif loc_type == 'department':
                try:
                    location = getattr(Department, loc_data['name'].upper())
                except AttributeError:
                    continue
            else:
                continue
                
            locations.append(location)
        
        # Prepare additional filters
        filters = {}
        if 'square' in data:
            filters['square'] = data['square']
        if 'price' in data:
            filters['price'] = data['price']
        if 'rooms' in data:
            filters['rooms'] = data['rooms']
        if 'bedrooms' in data:
            filters['bedrooms'] = data['bedrooms']
        if 'real_estate_type' in data:
            filters['real_estate_type'] = data['real_estate_type']
        if 'shippable' in data:
            filters['shippable'] = data['shippable']
        
        # Perform search
        result = client.search(
            text=text,
            category=category,
            sort=sort,
            locations=locations if locations else None,
            page=page,
            limit=limit,
            ad_type=ad_type,
            owner_type=owner_type,
            search_in_title_only=search_in_title_only,
            **filters
        )
        
        # Convert result to JSON-serializable format
        response_data = {
            "total": result.total,
            "total_all": result.total_all,
            "total_pro": result.total_pro,
            "total_private": result.total_private,
            "total_active": result.total_active,
            "total_inactive": result.total_inactive,
            "total_shippable": result.total_shippable,
            "max_pages": result.max_pages,
            "ads": []
        }
        
        for ad in result.ads:
            ad_data = {
                "id": ad.id,
                "title": ad.subject,
                "description": ad.body,
                "price": ad.price,
                "url": ad.url,
                "images": ad.images,
                "category_name": ad.category_name,
                "ad_type": ad.ad_type,
                "first_publication_date": ad.first_publication_date,
                "expiration_date": ad.expiration_date,
                "location": {
                    "city": ad.location.city,
                    "region_name": ad.location.region_name,
                    "department_name": ad.location.department_name,
                    "zipcode": ad.location.zipcode,
                    "lat": ad.location.lat,
                    "lng": ad.location.lng
                },
                "attributes": [
                    {
                        "key": attr.key,
                        "key_label": attr.key_label,
                        "value": attr.value,
                        "value_label": attr.value_label
                    }
                    for attr in ad.attributes
                ],
                "has_phone": ad.has_phone,
                "user_id": ad._user_id
            }
            response_data["ads"].append(ad_data)
        
        return jsonify(response_data)
        
    except DatadomeError as e:
        logger.error(f"Datadome error: {e}")
        return jsonify({"error": "Access blocked by Datadome protection. Please try again later."}), 403
    except RequestError as e:
        logger.error(f"Request error: {e}")
        return jsonify({"error": "Request failed. Please try again."}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/search-url', methods=['POST'])
def search_by_url():
    """
    Search using a Le Bon Coin URL
    
    Expected JSON payload:
    {
        "url": "https://www.leboncoin.fr/recherche?category=9&text=maison&...",
        "page": 1,
        "limit": 35
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        page = data.get('page', 1)
        limit = data.get('limit', 35)
        
        # Perform search using URL
        result = client.search(url=url, page=page, limit=limit)
        
        # Convert result to JSON-serializable format
        response_data = {
            "total": result.total,
            "total_all": result.total_all,
            "total_pro": result.total_pro,
            "total_private": result.total_private,
            "total_active": result.total_active,
            "total_inactive": result.total_inactive,
            "total_shippable": result.total_shippable,
            "max_pages": result.max_pages,
            "ads": []
        }
        
        for ad in result.ads:
            ad_data = {
                "id": ad.id,
                "title": ad.subject,
                "description": ad.body,
                "price": ad.price,
                "url": ad.url,
                "images": ad.images,
                "category_name": ad.category_name,
                "ad_type": ad.ad_type,
                "first_publication_date": ad.first_publication_date,
                "expiration_date": ad.expiration_date,
                "location": {
                    "city": ad.location.city,
                    "region_name": ad.location.region_name,
                    "department_name": ad.location.department_name,
                    "zipcode": ad.location.zipcode,
                    "lat": ad.location.lat,
                    "lng": ad.location.lng
                },
                "attributes": [
                    {
                        "key": attr.key,
                        "key_label": attr.key_label,
                        "value": attr.value,
                        "value_label": attr.value_label
                    }
                    for attr in ad.attributes
                ],
                "has_phone": ad.has_phone,
                "user_id": ad._user_id
            }
            response_data["ads"].append(ad_data)
        
        return jsonify(response_data)
        
    except DatadomeError as e:
        logger.error(f"Datadome error: {e}")
        return jsonify({"error": "Access blocked by Datadome protection. Please try again later."}), 403
    except RequestError as e:
        logger.error(f"Request error: {e}")
        return jsonify({"error": "Request failed. Please try again."}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/ad/<ad_id>', methods=['GET'])
def get_ad(ad_id):
    """
    Get detailed information about a specific ad
    
    URL parameter: ad_id - The ID of the ad
    """
    try:
        ad = client.get_ad(ad_id)
        
        # Convert ad to JSON-serializable format
        ad_data = {
            "id": ad.id,
            "title": ad.subject,
            "description": ad.body,
            "price": ad.price,
            "url": ad.url,
            "images": ad.images,
            "category_name": ad.category_name,
            "ad_type": ad.ad_type,
            "first_publication_date": ad.first_publication_date,
            "expiration_date": ad.expiration_date,
            "location": {
                "city": ad.location.city,
                "region_name": ad.location.region_name,
                "department_name": ad.location.department_name,
                "zipcode": ad.location.zipcode,
                "lat": ad.location.lat,
                "lng": ad.location.lng
            },
            "attributes": [
                {
                    "key": attr.key,
                    "key_label": attr.key_label,
                    "value": attr.value,
                    "value_label": attr.value_label
                }
                for attr in ad.attributes
            ],
            "has_phone": ad.has_phone,
            "favorites": ad.favorites,
            "user": {
                "id": ad.user.id,
                "name": ad.user.name,
                "pro": ad.user.pro,
                "account_type": ad.user.account_type,
                "creation_date": ad.user.creation_date,
                "phone_verified": ad.user.phone_verified,
                "email_verified": ad.user.email_verified
            }
        }
        
        return jsonify(ad_data)
        
    except NotFoundError:
        return jsonify({"error": "Ad not found"}), 404
    except DatadomeError as e:
        logger.error(f"Datadome error: {e}")
        return jsonify({"error": "Access blocked by Datadome protection. Please try again later."}), 403
    except RequestError as e:
        logger.error(f"Request error: {e}")
        return jsonify({"error": "Request failed. Please try again."}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get detailed information about a specific user
    
    URL parameter: user_id - The ID of the user
    """
    try:
        user = client.get_user(user_id)
        
        # Convert user to JSON-serializable format
        user_data = {
            "id": user.id,
            "name": user.name,
            "pro": user.pro,
            "account_type": user.account_type,
            "creation_date": user.creation_date,
            "phone_verified": user.phone_verified,
            "email_verified": user.email_verified
        }
        
        # Add professional data if available
        if user.pro:
            user_data["professional"] = {
                "online_store_name": user.pro.online_store_name,
                "siret": user.pro.siret,
                "website_url": user.pro.website_url,
                "description": user.pro.description,
                "phone": user.pro.phone,
                "email": user.pro.email
            }
        
        return jsonify(user_data)
        
    except NotFoundError:
        return jsonify({"error": "User not found"}), 404
    except DatadomeError as e:
        logger.error(f"Datadome error: {e}")
        return jsonify({"error": "Access blocked by Datadome protection. Please try again later."}), 403
    except RequestError as e:
        logger.error(f"Request error: {e}")
        return jsonify({"error": "Request failed. Please try again."}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

def serialize_enum(enum_class):
    """Helper function to serialize enum values to JSON"""
    items = []
    for attr_name in dir(enum_class):
        if not attr_name.startswith('_'):
            value = getattr(enum_class, attr_name)
            # Convert enum value to JSON-serializable format
            if hasattr(value, 'value'):
                items.append({
                    "name": attr_name,
                    "value": str(value.value)
                })
            else:
                items.append({
                    "name": attr_name,
                    "value": str(value)
                })
    return items

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get list of available categories"""
    categories = serialize_enum(Category)
    return jsonify({"categories": categories})

@app.route('/api/sort-options', methods=['GET'])
def get_sort_options():
    """Get list of available sort options"""
    sort_options = serialize_enum(Sort)
    return jsonify({"sort_options": sort_options})

@app.route('/api/ad-types', methods=['GET'])
def get_ad_types():
    """Get list of available ad types"""
    ad_types = serialize_enum(AdType)
    return jsonify({"ad_types": ad_types})

@app.route('/api/owner-types', methods=['GET'])
def get_owner_types():
    """Get list of available owner types"""
    owner_types = serialize_enum(OwnerType)
    return jsonify({"owner_types": owner_types})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

#!/usr/bin/env python3
"""
Test script for the LBC API
Run this to test the API locally before deploying to Render
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"  # Change this to your deployed URL

def test_health():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_search():
    """Test the search endpoint"""
    print("\n🔍 Testing search endpoint...")
    
    search_data = {
        "text": "maison",
        "category": "IMMOBILIER",
        "sort": "NEWEST",
        "locations": [{
            "type": "city",
            "lat": 48.85994982004764,
            "lng": 2.33801967847424,
            "radius": 10000,
            "city": "Paris"
        }],
        "page": 1,
        "limit": 5,  # Small limit for testing
        "ad_type": "OFFER"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Search successful")
            print(f"   Found {data.get('total', 0)} total ads")
            print(f"   Returned {len(data.get('ads', []))} ads")
            
            # Show first ad if available
            if data.get('ads'):
                first_ad = data['ads'][0]
                print(f"   First ad: {first_ad.get('title', 'N/A')} - €{first_ad.get('price', 'N/A')}")
            
            return data.get('ads', [])
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    return []

def test_get_ad(ad_id):
    """Test getting ad details"""
    print(f"\n🔍 Testing get ad endpoint for ID: {ad_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/ad/{ad_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get ad successful")
            print(f"   Title: {data.get('title', 'N/A')}")
            print(f"   Price: €{data.get('price', 'N/A')}")
            print(f"   Location: {data.get('location', {}).get('city', 'N/A')}")
        else:
            print(f"❌ Get ad failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Get ad error: {e}")

def test_get_user(user_id):
    """Test getting user details"""
    print(f"\n🔍 Testing get user endpoint for ID: {user_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/user/{user_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get user successful")
            print(f"   Name: {data.get('name', 'N/A')}")
            print(f"   Account type: {data.get('account_type', 'N/A')}")
            print(f"   Pro: {data.get('pro', False)}")
        else:
            print(f"❌ Get user failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Get user error: {e}")

def test_categories():
    """Test getting available categories"""
    print("\n🔍 Testing categories endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/categories")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Categories endpoint successful")
            print(f"   Found {len(data.get('categories', []))} categories")
        else:
            print(f"❌ Categories failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting LBC API Tests")
    print(f"   Testing against: {BASE_URL}")
    print("=" * 50)
    
    # Test health check
    test_health()
    
    # Test categories
    test_categories()
    
    # Test search
    ads = test_search()
    
    # Test get ad if we have ads
    if ads:
        first_ad_id = ads[0].get('id')
        if first_ad_id:
            test_get_ad(first_ad_id)
            
            # Test get user if we have user_id
            user_id = ads[0].get('user_id')
            if user_id:
                test_get_user(user_id)
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")
    print("\nIf all tests passed, your API is ready for deployment to Render!")

if __name__ == "__main__":
    main()

# LBC API - Deployment Guide

This guide will help you deploy the Le Bon Coin API client to Render as a web service.

## 🚀 Quick Deployment to Render

### Method 1: Using Render Dashboard (Recommended)

1. **Fork/Clone this repository** to your GitHub account
2. **Go to [Render Dashboard](https://dashboard.render.com)**
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub repository**
5. **Configure the service:**
   - **Name**: `lbc-api` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or upgrade for better performance)

6. **Click "Create Web Service"**
7. **Wait for deployment** (usually takes 2-3 minutes)
8. **Your API will be available at**: `https://your-service-name.onrender.com`

### Method 2: Using render.yaml (Infrastructure as Code)

1. **Push your code to GitHub**
2. **Go to [Render Dashboard](https://dashboard.render.com)**
3. **Click "New +" → "Blueprint"**
4. **Connect your GitHub repository**
5. **Render will automatically detect the `render.yaml` file**
6. **Click "Apply" to deploy**

## 📚 API Documentation

### Base URL
```
https://your-service-name.onrender.com
```

### Health Check
```http
GET /health
```
Returns the service status.

### Search Ads
```http
POST /api/search
```

**Request Body:**
```json
{
  "text": "maison",
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
```

**Response:**
```json
{
  "total": 150,
  "total_all": 150,
  "total_pro": 45,
  "total_private": 105,
  "max_pages": 5,
  "ads": [
    {
      "id": 123456789,
      "title": "Beautiful house in Paris",
      "description": "3 bedroom house with garden...",
      "price": 450000,
      "url": "https://www.leboncoin.fr/...",
      "images": ["https://...", "https://..."],
      "category_name": "Immobilier",
      "ad_type": "offer",
      "first_publication_date": "2024-01-15T10:30:00Z",
      "expiration_date": "2024-02-15T10:30:00Z",
      "location": {
        "city": "Paris",
        "region_name": "Île-de-France",
        "department_name": "Paris",
        "zipcode": "75001",
        "lat": 48.85994982004764,
        "lng": 2.33801967847424
      },
      "attributes": [
        {
          "key": "rooms",
          "key_label": "Pièces",
          "value": "4",
          "value_label": "4"
        }
      ],
      "has_phone": true,
      "user_id": "user-123"
    }
  ]
}
```

### Search by URL
```http
POST /api/search-url
```

**Request Body:**
```json
{
  "url": "https://www.leboncoin.fr/recherche?category=9&text=maison&locations=Paris__48.86023250788424_2.339006433295173_9256",
  "page": 1,
  "limit": 35
}
```

### Get Ad Details
```http
GET /api/ad/{ad_id}
```

**Response:**
```json
{
  "id": 123456789,
  "title": "Beautiful house in Paris",
  "description": "3 bedroom house with garden...",
  "price": 450000,
  "url": "https://www.leboncoin.fr/...",
  "images": ["https://...", "https://..."],
  "category_name": "Immobilier",
  "ad_type": "offer",
  "first_publication_date": "2024-01-15T10:30:00Z",
  "expiration_date": "2024-02-15T10:30:00Z",
  "location": {
    "city": "Paris",
    "region_name": "Île-de-France",
    "department_name": "Paris",
    "zipcode": "75001",
    "lat": 48.85994982004764,
    "lng": 2.33801967847424
  },
  "attributes": [...],
  "has_phone": true,
  "favorites": 12,
  "user": {
    "id": "user-123",
    "name": "John Doe",
    "pro": false,
    "account_type": "private",
    "creation_date": "2020-01-01T00:00:00Z",
    "phone_verified": true,
    "email_verified": true
  }
}
```

### Get User Details
```http
GET /api/user/{user_id}
```

**Response:**
```json
{
  "id": "user-123",
  "name": "John Doe",
  "pro": false,
  "account_type": "private",
  "creation_date": "2020-01-01T00:00:00Z",
  "phone_verified": true,
  "email_verified": true,
  "professional": {
    "online_store_name": "Real Estate Pro",
    "siret": "12345678901234",
    "website_url": "https://example.com",
    "description": "Professional real estate agent",
    "phone": "+33123456789",
    "email": "contact@example.com"
  }
}
```

### Get Available Options
```http
GET /api/categories
GET /api/sort-options
GET /api/ad-types
GET /api/owner-types
```

## 🔧 Configuration Options

### Categories
- `TOUTES_CATEGORIES` - All categories
- `IMMOBILIER` - Real estate
- `VEHICULES` - Vehicles
- `MULTIMEDIA` - Multimedia
- `MAISON` - Home & Garden
- `LOISIRS` - Leisure
- `MATERIEL_PROFESSIONNEL` - Professional equipment
- `EMPLOI` - Jobs
- `SERVICES` - Services
- `VACANCES` - Holidays

### Sort Options
- `RELEVANCE` - Most relevant
- `NEWEST` - Newest first
- `OLDEST` - Oldest first
- `PRICE_ASC` - Price ascending
- `PRICE_DESC` - Price descending
- `DISTANCE` - Closest first

### Ad Types
- `OFFER` - Offers only
- `REQUEST` - Requests only

### Owner Types
- `ALL` - All owners
- `PRIVATE` - Private individuals only
- `PRO` - Professionals only

## 🌐 Usage in Your Web App

### JavaScript/TypeScript Example
```javascript
// Search for houses in Paris
const searchHouses = async () => {
  const response = await fetch('https://your-service-name.onrender.com/api/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: 'maison',
      category: 'IMMOBILIER',
      sort: 'NEWEST',
      locations: [{
        type: 'city',
        lat: 48.85994982004764,
        lng: 2.33801967847424,
        radius: 10000,
        city: 'Paris'
      }],
      page: 1,
      limit: 20,
      ad_type: 'OFFER',
      price: [300000, 700000]
    })
  });
  
  const data = await response.json();
  console.log('Found', data.total, 'ads');
  return data.ads;
};

// Get ad details
const getAdDetails = async (adId) => {
  const response = await fetch(`https://your-service-name.onrender.com/api/ad/${adId}`);
  return await response.json();
};
```

### Python Example
```python
import requests

# Search for houses
def search_houses():
    url = 'https://your-service-name.onrender.com/api/search'
    data = {
        'text': 'maison',
        'category': 'IMMOBILIER',
        'sort': 'NEWEST',
        'locations': [{
            'type': 'city',
            'lat': 48.85994982004764,
            'lng': 2.33801967847424,
            'radius': 10000,
            'city': 'Paris'
        }],
        'page': 1,
        'limit': 20,
        'ad_type': 'OFFER',
        'price': [300000, 700000]
    }
    
    response = requests.post(url, json=data)
    return response.json()

# Get ad details
def get_ad_details(ad_id):
    url = f'https://your-service-name.onrender.com/api/ad/{ad_id}'
    response = requests.get(url)
    return response.json()
```

## ⚠️ Important Notes

### Rate Limiting & Datadome Protection
- Le Bon Coin uses Datadome protection that may block requests
- The API includes automatic retry logic for 403 errors
- For production use, consider:
  - Adding delays between requests
  - Using residential proxies
  - Implementing request queuing

### Free Tier Limitations
- Render's free tier has limitations:
  - Service sleeps after 15 minutes of inactivity
  - Cold start takes ~30 seconds
  - Limited CPU and memory
- Consider upgrading to paid plans for production use

### Error Handling
The API returns appropriate HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `403` - Forbidden (Datadome protection)
- `404` - Not Found (ad/user doesn't exist)
- `500` - Internal Server Error

## 🔒 Security Considerations

- The API is read-only (no data modification)
- CORS is enabled for web app integration
- No authentication required (public Le Bon Coin data)
- Consider implementing rate limiting for production use

## 📞 Support

If you encounter issues:
1. Check the Render service logs
2. Verify your request format matches the API documentation
3. Test with the `/health` endpoint first
4. Check for Datadome protection errors (403 status)

## 🚀 Next Steps

1. **Deploy to Render** using the instructions above
2. **Test the API** with the provided examples
3. **Integrate into your web app** using the JavaScript/Python examples
4. **Monitor usage** and consider upgrading to a paid Render plan if needed
5. **Implement caching** for better performance in your web app

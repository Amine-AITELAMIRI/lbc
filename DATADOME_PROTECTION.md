# 🛡️ Datadome Protection Workarounds

This guide explains how to work around Datadome protection when using the LBC API.

## 🔍 **What is Datadome?**

Datadome is a sophisticated bot protection system used by Le Bon Coin that:
- Detects automated requests
- Blocks suspicious traffic patterns
- Uses browser fingerprinting
- Implements rate limiting

## 🚀 **Built-in Protection Strategies**

The API now includes several built-in strategies:

### **1. Rate Limiting**
- Automatic delays between requests (2-5 seconds)
- Random jitter to avoid detection
- Configurable timing

### **2. Retry Mechanism**
- Exponential backoff on Datadome errors
- Automatic retry with new client instances
- Up to 3 retry attempts

### **3. User Agent Rotation**
- Rotates between realistic browser user agents
- Includes Chrome, Firefox, Safari, Edge
- Updates automatically

### **4. Proxy Support**
- Built-in proxy rotation system
- Support for authenticated proxies
- Automatic failover

## ⚙️ **Configuration**

### **Get Current Settings**
```bash
curl https://lbc-x8h8.onrender.com/api/protection/config
```

### **Update Settings**
```bash
curl -X POST https://lbc-x8h8.onrender.com/api/protection/config \
  -H "Content-Type: application/json" \
  -d '{"min_delay": 3, "max_delay": 8}'
```

## 🔧 **Advanced Configuration**

### **Adding Proxies**

To add proxies, modify the `_load_proxies()` method in `app.py`:

```python
def _load_proxies(self):
    """Load proxies from environment variables or return empty list"""
    proxies = [
        {
            "host": "proxy1.example.com",
            "port": 8080,
            "username": "your_username",
            "password": "your_password"
        },
        {
            "host": "proxy2.example.com", 
            "port": 8080,
            "username": "your_username",
            "password": "your_password"
        }
    ]
    return proxies
```

### **Environment Variables**

You can also load proxies from environment variables:

```python
def _load_proxies(self):
    """Load proxies from environment variables"""
    proxies = []
    
    # Load from environment variables
    proxy_hosts = os.environ.get('PROXY_HOSTS', '').split(',')
    proxy_ports = os.environ.get('PROXY_PORTS', '').split(',')
    proxy_users = os.environ.get('PROXY_USERS', '').split(',')
    proxy_passwords = os.environ.get('PROXY_PASSWORDS', '').split(',')
    
    for i, host in enumerate(proxy_hosts):
        if host.strip():
            proxies.append({
                "host": host.strip(),
                "port": int(proxy_ports[i]) if i < len(proxy_ports) else 8080,
                "username": proxy_users[i].strip() if i < len(proxy_users) else None,
                "password": proxy_passwords[i].strip() if i < len(proxy_passwords) else None
            })
    
    return proxies
```

## 🌐 **Recommended Proxy Providers**

### **Residential Proxies (Best)**
- **Bright Data** (formerly Luminati) - High quality, expensive
- **Smartproxy** - Good balance of quality/price
- **Oxylabs** - Enterprise-grade
- **ProxyMesh** - Simple setup

### **Datacenter Proxies (Cheaper)**
- **ProxyRack** - Good performance
- **Storm Proxies** - Affordable
- **Proxy-Seller** - Budget option

### **Free Options (Limited)**
- **Free Proxy Lists** - Unreliable, often blocked
- **Tor Network** - Slow, may be blocked

## 📊 **Best Practices**

### **1. Request Patterns**
```javascript
// Good: Add delays between requests
const searchWithDelay = async (query) => {
  const result = await fetch('/api/search', {
    method: 'POST',
    body: JSON.stringify(query)
  });
  
  // Wait 3-5 seconds before next request
  await new Promise(resolve => setTimeout(resolve, 3000 + Math.random() * 2000));
  
  return result;
};
```

### **2. Batch Requests**
```javascript
// Good: Process requests in small batches
const processBatch = async (queries) => {
  const results = [];
  
  for (let i = 0; i < queries.length; i += 3) {
    const batch = queries.slice(i, i + 3);
    
    // Process batch
    const batchResults = await Promise.all(
      batch.map(query => searchWithDelay(query))
    );
    
    results.push(...batchResults);
    
    // Longer delay between batches
    if (i + 3 < queries.length) {
      await new Promise(resolve => setTimeout(resolve, 10000));
    }
  }
  
  return results;
};
```

### **3. Error Handling**
```javascript
// Good: Handle Datadome errors gracefully
const searchWithRetry = async (query, maxRetries = 3) => {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        body: JSON.stringify(query)
      });
      
      if (response.ok) {
        return await response.json();
      }
      
      if (response.status === 403) {
        // Datadome protection
        const waitTime = Math.pow(2, attempt) * 1000;
        console.log(`Datadome error, retrying in ${waitTime}ms...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
        continue;
      }
      
      throw new Error(`HTTP ${response.status}`);
      
    } catch (error) {
      if (attempt === maxRetries - 1) {
        throw error;
      }
      
      const waitTime = Math.pow(2, attempt) * 1000;
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
};
```

## 🎯 **Proxy Configuration Examples**

### **Render Environment Variables**
Add these to your Render service environment variables:

```
PROXY_HOSTS=proxy1.example.com,proxy2.example.com,proxy3.example.com
PROXY_PORTS=8080,8080,8080
PROXY_USERS=user1,user2,user3
PROXY_PASSWORDS=pass1,pass2,pass3
```

### **Local Development**
```bash
export PROXY_HOSTS="proxy1.example.com,proxy2.example.com"
export PROXY_PORTS="8080,8080"
export PROXY_USERS="user1,user2"
export PROXY_PASSWORDS="pass1,pass2"
```

## 📈 **Monitoring & Debugging**

### **Check Protection Status**
```bash
curl https://lbc-x8h8.onrender.com/api/protection/config
```

### **Test Search with Protection**
```bash
curl -X POST https://lbc-x8h8.onrender.com/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "text": "test",
    "category": "IMMOBILIER",
    "limit": 1
  }'
```

### **Monitor Logs**
Check Render logs for:
- Rate limiting messages
- Proxy usage
- Retry attempts
- Datadome errors

## ⚠️ **Important Notes**

### **Legal Considerations**
- Respect Le Bon Coin's terms of service
- Don't overload their servers
- Use reasonable request rates
- Consider contacting them for API access

### **Performance Impact**
- Rate limiting increases response times
- Proxy usage adds latency
- Retry mechanisms can cause delays

### **Cost Considerations**
- Residential proxies are expensive
- Free proxies are unreliable
- Consider your usage volume

## 🚀 **Quick Start**

1. **Test current protection:**
   ```bash
   curl https://lbc-x8h8.onrender.com/api/protection/config
   ```

2. **Make a test request:**
   ```bash
   curl -X POST https://lbc-x8h8.onrender.com/api/search \
     -H "Content-Type: application/json" \
     -d '{"text": "maison", "limit": 1}'
   ```

3. **If you get 403 errors, add proxies:**
   - Sign up for a proxy service
   - Add proxy credentials to the code
   - Redeploy the API

4. **Monitor and adjust:**
   - Check logs for success rates
   - Adjust delays if needed
   - Scale proxy usage

## 📞 **Support**

If you're still experiencing Datadome issues:
1. Check the logs for specific error messages
2. Try different proxy providers
3. Increase delay times
4. Consider upgrading to paid proxy services
5. Contact the proxy provider for assistance

Remember: Datadome protection is constantly evolving, so strategies may need updates over time.

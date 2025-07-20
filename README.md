# Edlio Customer Map

This project displays an interactive map of Edlio customers.  It can load client data from a static `data.js` file or pull live records from HubSpot using a simple proxy server.  The repository also contains Python scripts to geocode customer addresses.

## Serve the Static Site Locally

Any basic web server can host the files in this repo.  One quick option is Python's built‑in server:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/index.html` in your browser.

## HubSpot API Configuration

The web pages expect an `api-config.js` file (ignored in Git) that exports your HubSpot API key:

```javascript
window.API_CONFIG = {
    HUBSPOT_API_KEY: 'pat-xxxxxx'
};
```


Place this file at the project root when running locally.  In production you can set the `HUBSPOT_API_KEY` environment variable for the `hubspot-proxy.js` server or Vercel function.  See [VERCEL_ENV_SETUP.md](VERCEL_ENV_SETUP.md) for details.

## Run the Local HubSpot Proxy

Start the proxy with Node to relay requests to HubSpot:

```bash
node hubspot-proxy.js
```

It listens on port `3001` by default.  Provide your API key via the `api-config.js` file or the `HUBSPOT_API_KEY` environment variable.  Client code should call paths like:

```
/api/hubspot?path=/crm/v3/objects/companies&limit=5
```

The proxy forwards the request and returns the JSON response.

## Running Geocoding Scripts

Python helpers under this repo geocode school addresses and produce JSON output.  Install the requirements and execute the desired script:

```bash
pip install -r requirements.txt
python3 geocode_apptegy_schools.py
```

The [GEOCODING_USAGE.md](GEOCODING_USAGE.md) guide covers additional options and usage notes.

## Additional Documentation

* [GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md) – enabling Google SSO
* [SIMPLE_AUTH_README.md](SIMPLE_AUTH_README.md) – simple password authentication
* [LIVE_DATA_INTEGRATION.md](LIVE_DATA_INTEGRATION.md) – integrating live CRM data
* [VERCEL_ENV_SETUP.md](VERCEL_ENV_SETUP.md) – storing keys in Vercel

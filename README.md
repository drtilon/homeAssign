# Geo IP Service

A web app that provides geolocation services with attack protection.

## Project Structure

The project consists of three main components:
- **geoBackend**: Flask API for IP geolocation
- **nginx-reverse-proxy**: Protects the backend from attacks
- **attackService**: CLI tool with various attack methods

## Setup and Running

### Prerequisites
- Docker and Docker Compose
- Python 3.9+

### Starting the Application
```
docker-compose up -d
```

This will start all services:
- Web API on port 5000
- Nginx reverse proxy on port 80
- MySQL database on port 3306

## API Endpoints

### Authentication
- POST `/api/auth/login` - Login to get JWT token

### Geolocation
- GET `/api/geo/lookup?ip=<ip_address>` - Get country for an IP
- GET `/api/geo/country/<country_name>/ips` - Get IPs from a specific country
- GET `/api/geo/top-countries` - Get top countries by request count

All endpoints require JWT authentication.

## Attack Service

Run the attack service with:
```
cd attackService
# SYN Flood attack
python attack.py --target 127.0.0.1 --port 80 --attack synflood

# URL Brute Force attack
python attack.py --target 127.0.0.1 --port 80 --attack bruteforce --wordlist wordlist.txt

# Slowloris attack
python attack.py --target 127.0.0.1 --port 80 --attack slowloris
```


Available attacks:
- `bruteforce` - URL brute force
- `synFlood` - TCP SYN flood
- `slowloris` - Slowloris DoS attack

## Default Credentials

Username: admin
Password: admin123

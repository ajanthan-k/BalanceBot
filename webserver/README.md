# BalanceBot Webserver

This README provides instructions for setting up the BalanceBot webserver.

### Prerequisites
- Python 3.7 or higher
- Docker and Docker Compose
- Nginx (and appropriate cert manager e.g. CertBot)

### Setup

1. Clone repo and cd into it.
2. Create Python virtual env, and activate it 
    ```  
    python -m venv venv
    source venv/bin/activate  # For Linux/Mac
    venv\Scripts\activate.bat  # For Windows
    ```
3. Install dependencies 
    ```
    pip install -r requirements.txt
    ```
4. Create a .env file in the webserver directory with the following content
    ```
    MONGO_USERNAME=username
    MONGO_PASSWORD=password
    MONGO_DATABASE=database
    ```
  Replace `username`, `password`, and `database` with own MongoDB credentials. Also adjust uri in `maze/maze_db.py`

5. Start the MongoDB container using Docker Compose
    ```
    docker compose up -d
    ```
6. Start webserver (run from top-level of balancebot directory)
    ```
    uvicorn webserver.main:app --host 0.0.0.0 --port 8000
    ```
7. Configure NGiNX (see [below](#nginx-setup)) 
8. If DNS records of domain configured correctly, webserver should now be accessible and should show `hello world` message.

---

## NGiNX setup

1. Create a new Nginx configuration file named `balancebot.conf` in the appropriate directory (e.g., `/etc/nginx/conf.d/` or `/etc/nginx/sites-available/`).

    ```nginx
    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    server {
        listen 80;
        server_name api.balancebot.site;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name api.balancebot.site;

        ssl_certificate /path/to/certificate.crt;
        ssl_certificate_key /path/to/certificate.key;

        location / {
            # local webserver running on port 8000
            proxy_pass http://localhost:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # for websockets
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
        }
    }
    ```
    - Replace `/path/to/certificate.crt` and `/path/to/certificate.key` with the actual paths to SSL/TLS certificate and private key files.
    - Adjust domain name and server port if needed

2. Test configuration with `nginx -t` which should output ok / success
3. Reload nginx with `sudo nginx -s reload`



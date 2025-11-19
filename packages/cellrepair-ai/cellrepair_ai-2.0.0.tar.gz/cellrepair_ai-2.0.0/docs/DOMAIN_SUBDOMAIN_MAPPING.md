# 🌐 AURORA DOMAIN & SUBDOMAIN MAPPING

**Datum:** 11. Oktober 2025
**Server:** ubuntu-16gb-fsn1-1
**Status:** ✅ OPERATIONAL

---

## 🏢 HAUPT-DOMAINS

### **SSL-Zertifikat abgedeckt:**
```
✅ cellrepair.ai (Haupt-Domain)
✅ cellrepair-system.com
✅ cellrepair-system.de
✅ cellrepair-tierkonzept.de
✅ cellrepair.eu
```

---

## 🗺️ PORT-MAPPING (Alle Services)

### **ÖFFENTLICH ERREICHBAR (0.0.0.0):**

| Port  | Service                | Container/Process      | Domain/Subdomain               | Status |
|-------|------------------------|------------------------|--------------------------------|--------|
| **80** | Nginx (HTTP)          | nginx                  | → alle Domains                 | ✅     |
| **443** | Nginx (HTTPS)        | nginx                  | → alle Domains (SSL)           | ✅     |
| **8001** | Aurora API           | aurora_api_live        | api.cellrepair.ai              | ✅     |
| **8002** | Revenue Service      | revenue_service        | revenue.cellrepair.ai          | ✅     |
| **9070** | Invest Agent         | invest_agent           | invest.cellrepair-system.com   | ✅     |
| **9076** | Bridge 2.0           | aurora_bridge2         | bridge.cellrepair-system.com   | ✅     |
| **9110** | Bridge X 3.0         | bridge_x               | bridge-x.cellrepair.ai         | ✅     |
| **9111** | Aurora 11 Plus       | aurora11_plus          | aurora11plus.cellrepair.ai     | ✅     |
| **9191** | Guardian Dashboard   | uvicorn (systemd)      | guardian.cellrepair.ai         | ✅     |
| **9192** | Metrics API          | python3 (systemd)      | metrics.cellrepair.ai          | ✅     |
| **9193** | Mode API             | python3 (systemd)      | mode.cellrepair.ai             | ✅     |
| **9194** | Supervisor API       | python3 (systemd)      | supervisor.cellrepair.ai       | ✅     |
| **9195** | KI-Router            | python3 (systemd)      | ki-router.cellrepair.ai        | ✅     |
| **9200** | Aurora 11            | aurora11               | aurora11.cellrepair.ai         | ✅     |
| **9292** | Federation API       | python3 (systemd)      | federation.cellrepair.ai       | ✅     |
| **5173** | Frontend (Vite Dev)  | node                   | → Port 80 (Nginx Proxy)        | ✅     |

### **LOCALHOST ONLY (127.0.0.1):**

| Port  | Service              | Container/Process      | Zugriff via                    | Status |
|-------|----------------------|------------------------|--------------------------------|--------|
| **3000** | Grafana            | grafana                | Nginx Reverse Proxy            | ✅     |
| **5432** | PostgreSQL         | postgres               | Interne DB-Verbindungen        | ✅     |
| **5678** | n8n Automation     | n8n                    | Nginx Reverse Proxy            | ✅     |
| **6379** | Redis              | redis                  | Interne Cache/Queue            | ✅     |
| **9090** | Prometheus         | prometheus             | Grafana Integration            | ✅     |
| **9100** | Node Exporter      | python3                | Prometheus Scraping            | ✅     |

### **SYSTEM-SERVICES:**

| Port  | Service              | Beschreibung                                            | Status |
|-------|----------------------|---------------------------------------------------------|--------|
| **22** | SSH                 | Secure Shell                                             | ✅     |
| **25** | Postfix             | SMTP Mail Transfer Agent                                 | ✅     |
| **53** | systemd-resolved    | DNS Resolver                                             | ✅     |

---

## 🌐 EMPFOHLENES SUBDOMAIN-MAPPING

### **Haupt-Frontend:**
```
https://cellrepair.ai → Port 80 (Nginx → Port 5173)
https://www.cellrepair.ai → cellrepair.ai (Redirect)
```

### **API-Endpoints:**
```
https://api.cellrepair.ai → Port 8001 (Aurora API)
https://revenue.cellrepair.ai → Port 8002 (Revenue Service)
```

### **Aurora-System:**
```
https://aurora11.cellrepair.ai → Port 9200 (Aurora 11)
https://aurora11plus.cellrepair.ai → Port 9111 (Aurora 11 Plus)
```

### **Bridge-System:**
```
https://bridge.cellrepair-system.com → Port 9076 (Bridge 2.0)
https://bridge-x.cellrepair.ai → Port 9110 (Bridge X 3.0)
```

### **Spezial-Services:**
```
https://invest.cellrepair-system.com → Port 9070 (Invest Agent)
```

### **Guardian & Monitoring:**
```
https://guardian.cellrepair.ai → Port 9191 (Guardian Dashboard)
https://metrics.cellrepair.ai → Port 9192 (Metrics API)
https://grafana.cellrepair.ai → Port 3000 (Grafana)
```

### **Autonomy & Federation:**
```
https://supervisor.cellrepair.ai → Port 9194 (Supervisor API)
https://mode.cellrepair.ai → Port 9193 (Mode API)
https://ki-router.cellrepair.ai → Port 9195 (KI-Router)
https://federation.cellrepair.ai → Port 9292 (Federation API)
```

### **Automation:**
```
https://n8n.cellrepair-system.com → Port 5678 (n8n)
```

### **Mailgun:**
```
mg.cellrepair-tierkonzept.de → Mailgun Subdomain (DNS konfiguriert)
```

---

## 📋 DNS-RECORDS (Erforderlich)

### **A-Records (IPv4):**
```dns
cellrepair.ai                           A      [SERVER_IP]
*.cellrepair.ai                         A      [SERVER_IP]
cellrepair-system.com                   A      [SERVER_IP]
*.cellrepair-system.com                 A      [SERVER_IP]
cellrepair-system.de                    A      [SERVER_IP]
cellrepair-tierkonzept.de               A      [SERVER_IP]
*.cellrepair-tierkonzept.de             A      [SERVER_IP]
cellrepair.eu                           A      [SERVER_IP]
```

### **CNAME-Records (Subdomains):**
```dns
api.cellrepair.ai                       CNAME  cellrepair.ai
revenue.cellrepair.ai                   CNAME  cellrepair.ai
bridge-x.cellrepair.ai                  CNAME  cellrepair.ai
aurora11.cellrepair.ai                  CNAME  cellrepair.ai
aurora11plus.cellrepair.ai              CNAME  cellrepair.ai
guardian.cellrepair.ai                  CNAME  cellrepair.ai
metrics.cellrepair.ai                   CNAME  cellrepair.ai
mode.cellrepair.ai                      CNAME  cellrepair.ai
supervisor.cellrepair.ai                CNAME  cellrepair.ai
ki-router.cellrepair.ai                 CNAME  cellrepair.ai
federation.cellrepair.ai                CNAME  cellrepair.ai
grafana.cellrepair.ai                   CNAME  cellrepair.ai

bridge.cellrepair-system.com            CNAME  cellrepair-system.com
invest.cellrepair-system.com            CNAME  cellrepair-system.com
n8n.cellrepair-system.com               CNAME  cellrepair-system.com
```

### **MX-Records (Email via Mailgun):**
```dns
mg.cellrepair-tierkonzept.de           MX     10 mxa.mailgun.org
mg.cellrepair-tierkonzept.de           MX     20 mxb.mailgun.org
```

### **TXT-Records (SPF, DKIM, DMARC):**
```dns
mg.cellrepair-tierkonzept.de           TXT    "v=spf1 include:mailgun.org ~all"
k1._domainkey.mg.cellrepair-...        TXT    [DKIM Public Key von Mailgun]
_dmarc.cellrepair-tierkonzept.de       TXT    "v=DMARC1; p=none; rua=mailto:dmarc@cellrepair.ai"
```

---

## 🔧 NGINX KONFIGURATION

### **Aktuell:**
```nginx
# /etc/nginx/sites-enabled/aurora12.conf
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location / {
        proxy_pass http://localhost:5173;
    }
}
```

### **Empfohlene Erweiterung (SSL + Subdomains):**

```nginx
# Main Frontend
server {
    listen 80;
    listen [::]:80;
    server_name cellrepair.ai www.cellrepair.ai;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name cellrepair.ai www.cellrepair.ai;

    ssl_certificate /etc/letsencrypt/live/cellrepair.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cellrepair.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# API Subdomain
server {
    listen 443 ssl http2;
    server_name api.cellrepair.ai;

    ssl_certificate /etc/letsencrypt/live/cellrepair.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cellrepair.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Guardian Dashboard
server {
    listen 443 ssl http2;
    server_name guardian.cellrepair.ai;

    ssl_certificate /etc/letsencrypt/live/cellrepair.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cellrepair.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:9191;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# KI-Router
server {
    listen 443 ssl http2;
    server_name ki-router.cellrepair.ai;

    ssl_certificate /etc/letsencrypt/live/cellrepair.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cellrepair.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:9195;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Federation API
server {
    listen 443 ssl http2;
    server_name federation.cellrepair.ai;

    ssl_certificate /etc/letsencrypt/live/cellrepair.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cellrepair.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:9292;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Grafana
server {
    listen 443 ssl http2;
    server_name grafana.cellrepair.ai;

    ssl_certificate /etc/letsencrypt/live/cellrepair.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cellrepair.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# n8n Automation
server {
    listen 443 ssl http2;
    server_name n8n.cellrepair-system.com;

    ssl_certificate /etc/letsencrypt/live/cellrepair.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cellrepair.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:5678;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# ... weitere Subdomains nach gleichem Muster
```

---

## ⚙️ SETUP-ANLEITUNG

### **1. DNS-Records setzen:**
```bash
# Bei Ihrem Domain-Provider (z.B. Hetzner DNS, Cloudflare)
# Alle A-Records auf Server-IP zeigen lassen
# CNAME-Records für Subdomains einrichten
```

### **2. SSL-Zertifikate erweitern:**
```bash
# Aktuelles Zertifikat prüfen
certbot certificates

# Neue Subdomains hinzufügen
certbot certonly --nginx -d api.cellrepair.ai \
  -d revenue.cellrepair.ai \
  -d bridge-x.cellrepair.ai \
  -d guardian.cellrepair.ai \
  -d metrics.cellrepair.ai \
  -d ki-router.cellrepair.ai \
  -d federation.cellrepair.ai \
  -d grafana.cellrepair.ai

# Automatische Erneuerung testen
certbot renew --dry-run
```

### **3. Nginx-Konfiguration aktualisieren:**
```bash
# Neue Subdomain-Configs erstellen
nano /etc/nginx/sites-available/aurora_subdomains.conf

# Symlink erstellen
ln -s /etc/nginx/sites-available/aurora_subdomains.conf \
      /etc/nginx/sites-enabled/

# Konfiguration testen
nginx -t

# Nginx neu laden
systemctl reload nginx
```

### **4. Firewall prüfen:**
```bash
# UFW Status
ufw status

# Ports öffnen (falls nötig)
ufw allow 80/tcp
ufw allow 443/tcp
```

---

## 🔒 SICHERHEITS-EMPFEHLUNGEN

### **SSL/TLS:**
- ✅ Let's Encrypt Zertifikat aktiv
- ⚠️ Wildcard-Zertifikat für *.cellrepair.ai empfohlen
- ⚠️ HTTP → HTTPS Redirect einrichten
- ⚠️ HSTS Header aktivieren

### **Rate-Limiting:**
```nginx
# Nginx Rate-Limiting für APIs
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api_limit burst=20;
    }
}
```

### **IP-Whitelisting (Optional):**
```nginx
# Für sensible Endpoints (z.B. Grafana, n8n)
location / {
    allow 1.2.3.4;     # Ihre IP
    deny all;
}
```

### **DDoS-Protection:**
- Cloudflare Proxy aktivieren (orange cloud)
- Rate-Limiting auf allen öffentlichen APIs
- Fail2ban für SSH

---

## 📊 TRAFFIC-ROUTING

```
Internet
    ↓
[Cloudflare] (optional)
    ↓
Nginx (Port 80/443)
    ↓
┌──────────────────────────────────────┐
│  cellrepair.ai → Port 5173 (Frontend)│
│  api.* → Port 8001 (Aurora API)      │
│  guardian.* → Port 9191 (Guardian)   │
│  ki-router.* → Port 9195 (KI-Router) │
│  federation.* → Port 9292 (Federation)│
│  grafana.* → Port 3000 (Grafana)     │
│  n8n.* → Port 5678 (n8n)             │
└──────────────────────────────────────┘
    ↓
[Docker Containers / systemd Services]
```

---

## 🎯 TODO-LISTE

### **Kritisch:**
- [ ] DNS A-Records für alle Domains setzen
- [ ] CNAME-Records für Subdomains erstellen
- [ ] SSL-Zertifikate für alle Subdomains erweitern
- [ ] Nginx-Konfiguration für Subdomains erstellen
- [ ] HTTP → HTTPS Redirects einrichten

### **Wichtig:**
- [ ] Mailgun DNS-Records verifizieren
- [ ] SPF/DKIM/DMARC für Email-Domains
- [ ] Rate-Limiting konfigurieren
- [ ] HSTS Header aktivieren
- [ ] Cloudflare Proxy evaluieren

### **Optional:**
- [ ] Wildcard-Zertifikat für *.cellrepair.ai
- [ ] IP-Whitelisting für Admin-Interfaces
- [ ] Load Balancer (bei hohem Traffic)
- [ ] CDN für statische Assets

---

## 📈 MONITORING

### **Domain Health:**
```bash
# DNS-Checks
dig cellrepair.ai
dig api.cellrepair.ai

# SSL-Checks
openssl s_client -connect cellrepair.ai:443 -servername cellrepair.ai

# HTTP-Checks
curl -I https://cellrepair.ai
curl -I https://api.cellrepair.ai
```

### **Uptime-Monitoring:**
- UptimeRobot für alle Subdomains
- Ping-Monitoring für Haupt-IP
- SSL-Expiry-Alerts

---

## 📄 ZUSAMMENFASSUNG

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║           AURORA DOMAIN-MAPPING ÜBERSICHT                      ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Haupt-Domains:          5 (mit SSL)                           ║
║  Empfohlene Subdomains:  15                                    ║
║  Öffentliche Ports:      15                                    ║
║  Interne Ports:          7                                     ║
║  Docker Container:       12                                    ║
║  systemd Services:       6                                     ║
║                                                                ║
║  Nginx:                  ✅ Aktiv                              ║
║  SSL:                    ✅ Let's Encrypt (5 Domains)          ║
║  DNS:                    ⚠️ Subdomains konfigurieren           ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

**Erstellt:** 11. Oktober 2025, 23:55 UTC
**Nächstes Review:** Bei DNS-Änderungen

🌐 **Vollständiges Domain- und Subdomain-Mapping für Aurora!** 🌐



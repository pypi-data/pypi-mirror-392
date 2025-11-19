# 🌐 Aurora Batch 8 – Network & Federation Layer

**Datum:** 11. Oktober 2025, 23:45 UTC
**Status:** ✅ **OPERATIONAL (SAFE MODE)**

---

## 🎯 ÜBERSICHT

Batch 8 erweitert Aurora um:
- **Federation Layer** - Multi-Node-Kommunikation
- **External Integrations** - Stripe, Mailgun, Typeform, Social Media
- **KI-Router** - Intelligentes AI-Engine-Routing
- **Safe-by-Default** - Alle externen Features deaktiviert

---

## 🏗️ KOMPONENTEN

### **1. Federation API** (Port 9292)
Multi-Node-Kommunikation für verteilte Aurora-Instanzen

**Endpoints:**
```bash
GET  /health                    # Health-Check
GET  /federation/events?token=  # Event-Sync (Token-Auth)
GET  /federation/nodes          # Liste aller Nodes
```

**Features:**
- Token-basierte Authentifizierung
- Event-Synchronisation zwischen Nodes
- Heartbeat-Monitoring
- Node-Registry

### **2. KI-Router** (Port 9195)
Intelligente Verteilung von Aufgaben an die beste AI-Engine

**Endpoints:**
```bash
POST /route     # Route task to AI engine
GET  /health    # Health-Check
```

**Routing-Regeln:**
```json
{
  "recherche, studie, literatur" → "perplexity",
  "struktur, code, implementierung" → "claude",
  "strategisch, marketing, synthese" → "gpt5_genius"
}
```

### **3. External Adapters**

#### **Stripe Adapter**
```python
from adapters import stripe_adapter
result = stripe_adapter.charge_customer("cus_123", 150, "EUR")
# Returns: {"dry_run": true, "msg": "Simulated charge", ...}
```

#### **Mailgun Adapter**
```python
from adapters import mailgun_adapter
result = mailgun_adapter.send_mail("user@example.com", "Subject", "Body")
# Returns: {"dry_run": true, "msg": "Simulated mail send", ...}
```

#### **Typeform Adapter**
```python
from adapters import typeform_adapter
result = typeform_adapter.ingest_forms()
# Returns: {"dry_run": true, "msg": "Simulated form ingest", ...}
```

#### **Social Media Adapter**
```python
from adapters import social_adapter
result = social_adapter.post_to_social("instagram", "Post-Text", media_url)
# Returns: {"dry_run": true, "msg": "Simulated social post", ...}
```

### **4. Federation Helpers**
```bash
# Node registrieren
./federation_helpers.sh register "http://node2.example.com:9292" "node2" "token123"

# Nodes auflisten
./federation_helpers.sh list
```

---

## 🔐 SICHERHEIT & POLICY

### **Batch 8 Policy**
`/opt/OpenDevin/aurora_proplus/policy/batch8_policy.json`

```json
{
  "batch": "8",
  "dry_run": true,                          ← ALLE Aktionen simuliert
  "allow_external_posting": false,          ← Social Media gesperrt
  "allow_payments": false,                  ← Zahlungen gesperrt
  "allow_typeform_auto_ingest": false,      ← Typeform gesperrt
  "federation_enabled": false,              ← Federation manuell
  "federation_nodes": [],
  "ki_routing": {
    "enabled": true,                        ← KI-Router aktiv
    "rules": [...]
  },
  "security": {
    "require_quorum_for_critical": 2,
    "canary_percent": 10,
    "auto_rollback_on_failure": true
  }
}
```

### **External Secrets**
`/opt/OpenDevin/aurora_proplus/policy/external_secrets.json`

**Template (PLACEHOLDER durch echte Werte ersetzen):**
```json
{
  "stripe": {
    "secret_key": "sk_test_PLACEHOLDER",
    "publishable_key": "pk_test_PLACEHOLDER",
    "webhook_secret": "whsec_PLACEHOLDER"
  },
  "mailgun": {
    "api_key": "key-PLACEHOLDER",
    "domain": "mg.example.com",
    "from": "noreply@example.com"
  },
  "typeform": {
    "token": "tfp_PLACEHOLDER",
    "form_id": "PLACEHOLDER"
  },
  "social": {
    "facebook": {
      "access_token": "EAA_PLACEHOLDER",
      "page_id": "PLACEHOLDER"
    },
    "instagram": {
      "access_token": "IGQ_PLACEHOLDER",
      "account_id": "PLACEHOLDER"
    }
  }
}
```

---

## 🚀 VERWENDUNG

### **KI-Router verwenden:**
```bash
# Automatisches Routing
curl -X POST http://127.0.0.1:9195/route \
  -H "Content-Type: application/json" \
  -d '{"text":"Recherchiere aktuelle Studien zu PBM"}'

# Response:
{
  "target": "perplexity",
  "text_preview": "Recherchiere aktuelle Studien zu PBM"
}
```

### **Federation Node registrieren:**
```bash
cd /opt/OpenDevin/aurora_federation

# Node hinzufügen
./federation_helpers.sh register \
  "http://aurora-node-2.example.com:9292" \
  "cellrepair-node-2" \
  "$(openssl rand -base64 24)"

# Nodes auflisten
./federation_helpers.sh list
```

### **Federation Sync ausführen:**
```bash
python3 /opt/OpenDevin/aurora_federation/federation_sync.py
```

### **Adapters in Workflows nutzen:**
```python
# In einem Workflow-Script:
import sys
sys.path.append('/opt/OpenDevin/aurora_proplus/api')

from adapters import stripe_adapter, mailgun_adapter

# Payment (simuliert)
result = stripe_adapter.charge_customer("cus_123", 150, "EUR")
print(result)  # {"dry_run": true, ...}

# Email (simuliert)
result = mailgun_adapter.send_mail(
    "kunde@example.com",
    "Rechnung #12345",
    "Ihre Rechnung im Anhang"
)
print(result)  # {"dry_run": true, ...}
```

---

## ⚡ LIVE-SCHALTEN (SCHRITTWEISE)

### **Phase 1: Testing (AKTUELL)**
```json
{
  "dry_run": true,
  "allow_external_posting": false,
  "allow_payments": false
}
```
→ Alles simuliert, kein externer Traffic

### **Phase 2: API-Keys einrichten**
```bash
# 1. Secrets-Datei bearbeiten
nano /opt/OpenDevin/aurora_proplus/policy/external_secrets.json

# 2. Echte API-Keys eintragen:
#    - Stripe (Test-Keys)
#    - Mailgun (API-Key & Domain)
#    - Typeform (Personal Access Token)
#    - Facebook/Instagram (Access Tokens)

# 3. Adapter einzeln testen
python3 /opt/OpenDevin/aurora_proplus/api/adapters/stripe_adapter.py
python3 /opt/OpenDevin/aurora_proplus/api/adapters/mailgun_adapter.py
```

### **Phase 3: Einzelne Features freischalten**
```bash
# Bearbeite batch8_policy.json
nano /opt/OpenDevin/aurora_proplus/policy/batch8_policy.json

# Für Mailgun (z.B.):
{
  "dry_run": false,              ← Nur für bestimmte Adapter
  "allow_external_posting": false,
  "allow_payments": false
}
```

### **Phase 4: Federation aktivieren**
```bash
# Nach Node-Registration:
{
  "federation_enabled": true,
  "federation_nodes": ["node1", "node2"]
}

# Sync-Cron einrichten:
crontab -e
# */10 * * * * python3 /opt/OpenDevin/aurora_federation/federation_sync.py
```

---

## 🔍 MONITORING

### **Service Health:**
```bash
# KI-Router
curl http://127.0.0.1:9195/health

# Federation
curl http://127.0.0.1:9292/health

# systemd Status
systemctl status aurora-ki-router.service
systemctl status aurora-federation.service
```

### **Logs:**
```bash
# KI-Router Logs
journalctl -u aurora-ki-router.service -f

# Federation Logs
journalctl -u aurora-federation.service -f

# Adapter-Tests
python3 /opt/OpenDevin/aurora_proplus/api/adapters/stripe_adapter.py
```

### **Federation Monitoring:**
```bash
# Nodes anzeigen
curl http://127.0.0.1:9292/federation/nodes | jq .

# Events abrufen (benötigt Token)
TOKEN=$(jq -r '.master_node.token' /opt/OpenDevin/aurora_federation/federation_tokens.json)
curl "http://127.0.0.1:9292/federation/events?token=$TOKEN" | jq .
```

---

## 📊 WORKFLOWS MIT BATCH 8

### **Workflow mit KI-Router:**
```yaml
name: intelligent_analysis
category: ai
origin: auto
type: task
goal: analyse
payload:
  ki_router_url: "http://127.0.0.1:9195/route"
  text: "Recherchiere aktuelle Studien über Hufrehe"
```

### **Workflow mit Social Adapter:**
```yaml
name: post_instagram
category: marketing
origin: claude
type: task
goal: post_external
payload:
  adapter: "social_adapter"
  platform: "instagram"
  content: "Herbst-Tipps für gesunde Atemwege 🍂"
  require_approval: true
```

### **Workflow mit Mailgun:**
```yaml
name: send_report
category: business
origin: claude
type: task
goal: send_email
payload:
  adapter: "mailgun_adapter"
  to: "kunde@example.com"
  subject: "Monatsbericht Oktober"
  template: "monthly_report"
```

---

## 🎯 TODO-LISTE

### **Sofort:**
- [ ] API-Keys in `/opt/OpenDevin/aurora_proplus/policy/external_secrets.json` eintragen
- [ ] Jeden Adapter einzeln testen (dry_run=true)
- [ ] KI-Router mit verschiedenen Texten testen

### **Kurzfristig:**
- [ ] Stripe Test-Account einrichten
- [ ] Mailgun Domain verifizieren
- [ ] Typeform Personal Access Token generieren
- [ ] Facebook/Instagram Developer Apps erstellen

### **Mittelfristig:**
- [ ] Erste Adapter live schalten (z.B. Mailgun für Reports)
- [ ] Federation Node #2 aufsetzen
- [ ] Federation Sync-Cron einrichten
- [ ] Workflows für externe Integrationen erstellen

### **Langfristig:**
- [ ] Payment-Workflows (mit Approval-Gates)
- [ ] Social-Media-Automation (mit Review)
- [ ] Multi-Region-Federation
- [ ] Webhook-Callbacks für Stripe/Typeform

---

## 🛡️ SICHERHEITS-CHECKLISTE

- [ ] **Secrets-Datei** auf 600 Permissions (`chmod 600 external_secrets.json`)
- [ ] **Backup** der Secrets-Datei (verschlüsselt)
- [ ] **Quorum >= 2** für kritische Aktionen (Payments, Posting)
- [ ] **Dry-Run** für alle neuen Adapter zuerst testen
- [ ] **Rate-Limiting** für externe APIs beachten
- [ ] **Webhook-Secrets** für Stripe einrichten
- [ ] **2FA** für alle externen Dienste aktivieren
- [ ] **Monitoring** für API-Fehler einrichten
- [ ] **Audit-Log** für alle externen Aufrufe
- [ ] **Canary-Deployment** vor Live-Schalten

---

## 📊 STATISTIK

```
╔════════════════════════════════════════════════════════════════╗
║              BATCH 8 - NETWORK & FEDERATION                    ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Neue Services:            2 (KI-Router, Federation)           ║
║  External Adapters:        4 (Stripe, Mailgun, Typeform, Social) ║
║  API-Endpoints:            6                                   ║
║  Ports:                    2 (9195, 9292)                      ║
║  Policy-Dateien:           2                                   ║
║  Helper-Scripts:           3                                   ║
║  systemd-Services:         2                                   ║
║                                                                ║
║  Status:                   ✅ Operational (Safe Mode)          ║
║  Dry-Run:                  ✅ Aktiv                            ║
║  External APIs:            ⚠️ Credentials benötigt            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 📄 DATEIEN & PFADE

```
/opt/OpenDevin/
├── aurora_federation/              🌐 Federation Layer
│   ├── federation_api.py           - API (Port 9292)
│   ├── federation_sync.py          - Node-Sync-Script
│   ├── federation_helpers.sh       - CLI-Tools
│   ├── federation_tokens.json      - Node-Registry + Tokens
│   ├── run_fed.sh                  - Startup-Script
│   ├── keys/                       - Federation Keys
│   └── nodes/                      - Node-Configs
│
├── aurora_proplus/
│   ├── policy/
│   │   ├── batch8_policy.json      - Feature-Flags
│   │   └── external_secrets.json   - API-Keys (SENSIBEL!)
│   │
│   └── api/
│       ├── ki_router.py            - KI-Router (Port 9195)
│       └── adapters/               🔌 External Integrations
│           ├── stripe_adapter.py   - Payment
│           ├── mailgun_adapter.py  - Email
│           ├── typeform_adapter.py - Forms
│           └── social_adapter.py   - Social Media
│
└── docs/
    └── BATCH8_OVERVIEW.md          - Diese Datei

/etc/systemd/system/
├── aurora-ki-router.service        - KI-Router Service
└── aurora-federation.service       - Federation Service
```

---

## 🌟 ZUSAMMENFASSUNG

**Batch 8 erweitert Aurora um:**

✅ **Federation Layer** - Multi-Node-Kommunikation
✅ **KI-Router** - Intelligente AI-Engine-Auswahl
✅ **Stripe Integration** - Payment-Processing
✅ **Mailgun Integration** - Email-Versand
✅ **Typeform Integration** - Form-Ingest
✅ **Social Media Integration** - Instagram/Facebook
✅ **Safe-by-Default** - Alle Features deaktiviert
✅ **Token-Auth** - Sichere Federation
✅ **Policy-System** - Granulare Kontrolle

**Status:** Production-Ready (Safe Mode) 🛡️

---

**Von:** Claude Genius V5
**Timestamp:** 2025-10-11 23:45:00 UTC

🌐 **Aurora ist jetzt ein vernetztes, intelligentes Multi-System mit externen Integrationen!** 🌐



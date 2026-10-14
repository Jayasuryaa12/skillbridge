# SkillBridge Production Deployment Guide 🚀

This document provides exact, step-by-step instructions for deploying all three components of the **SkillBridge** microservices architecture:

1. **MongoDB Atlas** — Managed cloud databases (`skill_db` and `opportunity_db`)
2. **Opportunity Service** — Python/Flask API hosted on **Render** (Port assigned dynamically)
3. **Skill Service** — Python/Flask API hosted on **Render** (Port assigned dynamically)
4. **Frontend Dashboard** — React 18 + Vite SPA hosted on **Vercel**

---

## Architecture & Dependency Flow

```
                      +-----------------------------+
                      |      Vercel Frontend        |
                      | (https://skillbridge.app)   |
                      +--------------+--------------+
                                     |
               +---------------------+---------------------+
               | HTTP (ALLOWED_ORIGINS)                    | HTTP (ALLOWED_ORIGINS)
               v                                           v
+-------------------------------+             +-------------------------------+
|     Skill Service (Render)    |             | Opportunity Service (Render)  |
|  https://skillbridge-skill... |             | https://skillbridge-opp...    |
+---------------+---------------+             +---------------+---------------+
                |                                             |
                | Inter-Service REST (X-Service-Key)          |
                +-------------------------------------------->+
                |                                             |
                v                                             v
+-------------------------------+             +-------------------------------+
|      MongoDB Atlas Cluster    |             |      MongoDB Atlas Cluster    |
|       Database: skill_db      |             |   Database: opportunity_db    |
+-------------------------------+             +-------------------------------+
```

> [!IMPORTANT]
> **Deployment Order:**
> 1. MongoDB Atlas (Setup database user and network access)
> 2. Opportunity Service (Must be deployed and healthy first)
> 3. Skill Service (Requires Opportunity Service URL and Secret Key)
> 4. Vercel Frontend (Requires both API URLs)
> 5. Update CORS on both Render services with the final Vercel domain.

---

## Step 1: MongoDB Atlas Setup

### 1.1 Create Cluster
1. Log in to [MongoDB Atlas](https://cloud.mongodb.com/).
2. Create a new project named `SkillBridge`.
3. Click **Create Deployment** -> Select **M0 Free Tier** (Shared).
4. Choose a region closest to your Render services (e.g. `us-east-1` or `eu-central-1`) and click **Create**.

### 1.2 Create Database User
1. In the left navigation, go to **Security** -> **Database Access**.
2. Click **Add New Database User**.
3. Choose **Password** authentication:
   - **Username**: `skillbridge_admin`
   - **Password**: Generate a secure password (save this; e.g. `StrongPass123!`).
4. Under **Database User Privileges**, select **Read and write to any database**.
5. Click **Add User**.

### 1.3 Configure Network Access (IP Allowlist)
1. In the left navigation, go to **Security** -> **Network Access**.
2. Click **Add IP Address**.
3. Click **Allow Access from Anywhere** (`0.0.0.0/0`) since Render containers have dynamic outgoing IP addresses.
4. Click **Confirm**.

### 1.4 Obtain Connection Strings
1. In the left navigation, go to **Database** -> Click **Connect** on your cluster.
2. Select **Drivers** (Python, version 3.11 or later).
3. Copy the standard connection string format:
   ```
   mongodb+srv://skillbridge_admin:<password>@<cluster-address>.mongodb.net/?retryWrites=true&w=majority&appName=SkillBridge
   ```
4. Prepare your two distinct connection strings by appending the respective database names:
   - **Skill Service URI**:
     ```
     mongodb+srv://skillbridge_admin:YOUR_PASSWORD@cluster0.abcde.mongodb.net/skill_db?retryWrites=true&w=majority
     ```
   - **Opportunity Service URI**:
     ```
     mongodb+srv://skillbridge_admin:YOUR_PASSWORD@cluster0.abcde.mongodb.net/opportunity_db?retryWrites=true&w=majority
     ```

---

## Step 2: Deploy Opportunity Service on Render

### 2.1 Create the Web Service
1. Log in to [Render](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your Git repository (`skillbridge`).
4. Configure the service settings:
   - **Name**: `skillbridge-opportunity-service`
   - **Region**: Choose the region closest to your MongoDB Atlas cluster (e.g., Oregon or Frankfurt).
   - **Branch**: `main` (or your active deployment branch)
   - **Root Directory**: `opportunity-service`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Instance Type**: `Free`

5. Under **Advanced** -> **Health Check Path**, enter:
   ```
   /health
   ```

### 2.2 Configure Environment Variables
Add the following key-value pairs in the **Environment Variables** section:

| Key | Value | Notes |
|-----|-------|-------|
| `FLASK_ENV` | `production` | Disables debug mode, enforces strict configs |
| `MONGO_URI` | `mongodb+srv://skillbridge_admin:.../opportunity_db?...` | Your Atlas Opportunity DB string |
| `DB_NAME` | `opportunity_db` | Collection database name |
| `ALLOWED_ORIGINS` | `*` | Temporary allow-all until Vercel domain is deployed |
| `INTER_SERVICE_KEY` | `sk_live_prod_sec_9948271a` | Generate a 32+ character random secret token |

6. Click **Create Web Service**.
7. Wait ~2–3 minutes for the build and deployment to complete.
8. Note the deployed URL (e.g. `https://skillbridge-opportunity-service.onrender.com`).

### 2.3 Verify Health & Seed Opportunity Database
Once the service shows **Live**, verify health:
```bash
curl https://skillbridge-opportunity-service.onrender.com/health
```
Expected output:
```json
{"data":{"database":"connected","service":"opportunity-service","status":"ok","version":"1.0.0"},"message":"Opportunity service is healthy","success":true}
```

Now seed the 32+ opportunities directly into your Atlas database:
```bash
# In your local terminal:
cd opportunity-service

# Set the production Atlas URI for the seed script
$env:MONGO_URI="mongodb+srv://skillbridge_admin:YOUR_PASSWORD@cluster0.abcde.mongodb.net/opportunity_db?retryWrites=true&w=majority"
$env:DB_NAME="opportunity_db"

python scripts/seed.py
```
*(On macOS/Linux use `export MONGO_URI="..."`)*

---

## Step 3: Deploy Skill Service on Render

### 3.1 Create the Web Service
1. In Render, click **New +** -> **Web Service**.
2. Select the same Git repository.
3. Configure the service settings:
   - **Name**: `skillbridge-skill-service`
   - **Region**: Same region as Opportunity Service
   - **Branch**: `main`
   - **Root Directory**: `skill-service`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Instance Type**: `Free`

4. Under **Advanced** -> **Health Check Path**, enter:
   ```
   /health
   ```

### 3.2 Configure Environment Variables
Add the following key-value pairs:

| Key | Value | Notes |
|-----|-------|-------|
| `FLASK_ENV` | `production` | Disables debug mode |
| `MONGO_URI` | `mongodb+srv://skillbridge_admin:.../skill_db?...` | Your Atlas Skill DB string |
| `DB_NAME` | `skill_db` | Collection database name |
| `ALLOWED_ORIGINS` | `*` | Temporary allow-all until Vercel URL is ready |
| `OPPORTUNITY_SERVICE_URL` | `https://skillbridge-opportunity-service.onrender.com` | Deployed Opportunity Service URL |
| `INTER_SERVICE_KEY` | `sk_live_prod_sec_9948271a` | Must EXACTLY match the key from Opportunity Service |
| `OPPORTUNITY_CONNECT_TIMEOUT` | `20.0` | Handles Render free-tier cold starts |
| `OPPORTUNITY_READ_TIMEOUT` | `30.0` | Prevents premature timeouts |
| `COLD_START_TIMEOUT` | `45.0` | Maximum wake-up ping duration |

5. Click **Create Web Service**.
6. Wait for the build and deployment to complete.
7. Note the deployed URL (e.g. `https://skillbridge-skill-service.onrender.com`).

### 3.3 Verify Health & Seed Skill Database
Verify health:
```bash
curl https://skillbridge-skill-service.onrender.com/health
```

Seed the default careers, students, and learning resources into Atlas:
```bash
# In your local terminal:
cd skill-service

$env:MONGO_URI="mongodb+srv://skillbridge_admin:YOUR_PASSWORD@cluster0.abcde.mongodb.net/skill_db?retryWrites=true&w=majority"
$env:DB_NAME="skill_db"

python scripts/seed.py
```

### 3.4 Verify Inter-Service Communication
Check the composite system status endpoint to ensure Skill Service can communicate with Opportunity Service:
```bash
curl https://skillbridge-skill-service.onrender.com/api/system/status
```
Expected output:
```json
{
  "data": {
    "overall_status": "healthy",
    "skill_service": {"status": "healthy", "database": "connected"},
    "opportunity_service": {"status": "healthy", "reachable": true}
  },
  "success": true
}
```

---

## Step 4: Deploy Frontend on Vercel

### 4.1 Import Repository
1. Log in to [Vercel](https://vercel.com/).
2. Click **Add New...** -> **Project**.
3. Import your `skillbridge` repository.

### 4.2 Configure Build & Output
1. Under **Project Name**, enter `skillbridge`.
2. Under **Framework Preset**, select **Vite**.
3. Under **Root Directory**, click **Edit** and select `frontend`.
4. Ensure the **Build Command** is `npm run build` and **Output Directory** is `dist`.

### 4.3 Configure Environment Variables
Expand the **Environment Variables** section and add:

| Key | Value | Example |
|-----|-------|---------|
| `VITE_SKILL_API_URL` | `https://<your-skill-service>.onrender.com/api` | `https://skillbridge-skill-service.onrender.com/api` |
| `VITE_OPPORTUNITY_API_URL` | `https://<your-opportunity-service>.onrender.com/api` | `https://skillbridge-opportunity-service.onrender.com/api` |

5. Click **Deploy**.
6. Deployment will take ~45–60 seconds.
7. Copy your production Vercel domain (e.g. `https://skillbridge.vercel.app`).

---

## Step 5: Lock Down CORS on Both Render Services

Now that your frontend is live on Vercel, restrict CORS origins to prevent unauthorized cross-origin requests.

1. Go to **Render Dashboard** -> `skillbridge-opportunity-service` -> **Environment**.
2. Edit `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://skillbridge.vercel.app,http://localhost:5173
   ```
3. Save changes (Render will trigger a zero-downtime redeploy).
4. Go to `skillbridge-skill-service` -> **Environment**.
5. Edit `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://skillbridge.vercel.app,http://localhost:5173
   ```
6. Save changes.

---

## Step 6: Post-Deployment Smoke Verification

Run the automated smoke test script locally against the live production URLs:

```bash
python scripts/smoke_test.py \
  --skill-url https://skillbridge-skill-service.onrender.com \
  --opp-url https://skillbridge-opportunity-service.onrender.com \
  --key sk_live_prod_sec_9948271a
```

The script will test all critical integration paths and output a formatted verification report:
- `[PASS]` Skill Service `/health`
- `[PASS]` Opportunity Service `/health`
- `[PASS]` Inter-Service Communication (`/api/system/status`)
- `[PASS]` Student CRUD Round-Trip
- `[PASS]` Opportunity Matching & Recommendation Engine

---

## Troubleshooting Guide

### 1. CORS Errors in Browser Console
* **Symptom:** `Access to XMLHttpRequest at '...' from origin 'https://skillbridge.vercel.app' has been blocked by CORS policy`.
* **Fix:**
  - Verify that `ALLOWED_ORIGINS` in Render contains your exact Vercel URL without trailing slashes.
  - Remember that CORS headers are evaluated on HTTP preflight (`OPTIONS`). Ensure `r"/*"` is covered.

### 2. Render Free-Tier Cold Starts (Spin-Up Delays)
* **Symptom:** First request after 15+ minutes takes 30–50 seconds to complete.
* **Explanation:** Render free tier spins down idle instances.
* **Mitigations built into SkillBridge:**
  - **Frontend:** Automatically detects requests taking > 2.5s and displays a friendly animated banner: *"Waking up cloud microservices... Render free tier instances sleep after inactivity."*
  - **Inter-service client:** `OpportunityClient` contains a `wake_up()` retry strategy with an extended 45-second timeout, ensuring Skill Service does not timeout while Opportunity Service is booting.

### 3. MongoDB Atlas IP Allowlist Issues
* **Symptom:** `pymongo.errors.ServerSelectionTimeoutError: No replica set members match selector`.
* **Fix:**
  - Render services run on dynamically allocated IP addresses.
  - In MongoDB Atlas -> **Network Access**, ensure `0.0.0.0/0` (Allow Access from Anywhere) is active.
  - Verify your database user password has no unencoded special characters (e.g. `@`, `:`, `/` must be URL-encoded in standard MongoDB URIs).

### 4. Inter-Service Authentication Failure (HTTP 401)
* **Symptom:** `Opportunity Service rejected request: unauthorized or missing service key`.
* **Fix:**
  - Ensure `INTER_SERVICE_KEY` in `skill-service` matches `INTER_SERVICE_KEY` in `opportunity-service` character-for-character.

---

## Full Environment Variables Reference Table

### Skill Service (`skill-service`)
| Variable | Required | Default | Description |
|---|---|---|---|
| `FLASK_ENV` | Yes | `development` | Set to `production` in deployment |
| `SECRET_KEY` | Yes | `dev-secret` | Flask cryptographic session key |
| `MONGO_URI` | Yes | — | MongoDB Atlas connection string for `skill_db` |
| `DB_NAME` | Yes | `skill_db` | Target MongoDB database name |
| `ALLOWED_ORIGINS` | Yes | `*` | Comma-separated list of permitted origins |
| `OPPORTUNITY_SERVICE_URL` | Yes | `http://localhost:5002` | Deployed Opportunity Service URL |
| `INTER_SERVICE_KEY` | Optional | `None` | Shared token for authenticating inter-service calls |
| `OPPORTUNITY_CONNECT_TIMEOUT` | No | `15.0` | Socket connect timeout in seconds |
| `OPPORTUNITY_READ_TIMEOUT` | No | `25.0` | HTTP response read timeout in seconds |
| `COLD_START_TIMEOUT` | No | `45.0` | Maximum wait duration during cold-start wake-up |

### Opportunity Service (`opportunity-service`)
| Variable | Required | Default | Description |
|---|---|---|---|
| `FLASK_ENV` | Yes | `development` | Set to `production` in deployment |
| `SECRET_KEY` | Yes | `dev-secret` | Flask session secret key |
| `MONGO_URI` | Yes | — | MongoDB Atlas connection string for `opportunity_db` |
| `DB_NAME` | Yes | `opportunity_db` | Target MongoDB database name |
| `ALLOWED_ORIGINS` | Yes | `*` | Comma-separated list of permitted origins |
| `INTER_SERVICE_KEY` | Optional | `None` | Shared token required for `/api/opportunities/match` |

### Frontend (`frontend`)
| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_SKILL_API_URL` | Yes | `http://localhost:5001/api` | Full URL to Skill Service `/api` prefix |
| `VITE_OPPORTUNITY_API_URL` | Yes | `http://localhost:5002/api` | Full URL to Opportunity Service `/api` prefix |

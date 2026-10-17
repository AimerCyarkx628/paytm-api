# Paytm Order Status API - Complete Hosting & Monetization Guide

This guide explains how to host your own Paytm Order Status API service and sell API keys to clients (Telegram bot developers, shop owners, etc.).

---

## 📁 Project Structure

```text
paytm_payment_api/
├── api/
│   └── index.py               # Vercel Serverless Function (Main API endpoint)
├── alternative_runtimes/
│   ├── node/index.js          # Node.js alternative
│   └── php/index.php          # PHP alternative (cPanel / Apache)
├── app.py                     # Standalone Python Server (Local / VPS / Render)
├── vercel.json                # Vercel routing configuration
├── .env.example               # Configuration template
├── test_api.py                # Live test script
├── HOSTING_GUIDE.md           # This guide
└── CLIENT_DOCS.md             # Clean documentation to hand over to paying buyers
```

---

## 🚀 Option 1: Host for FREE on Vercel (Recommended)

Vercel gives you:
- **100% Free** hosting with HTTPS (`https://your-api.vercel.app`)
- Auto-scaling (handles thousands of requests per minute)
- Zero server maintenance, zero cold starts

### Step-by-Step Instructions:

#### Step 1: Create a GitHub Repository
1. Go to [GitHub.com](https://github.com) and create a new repository (e.g., `paytm-status-api`).
2. Upload the contents of this `paytm_payment_api` folder to your GitHub repo.
   *(Make sure `vercel.json` and the `api/` folder are in the root of the repository).*

#### Step 2: Import into Vercel
1. Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
2. Click **"Add New..."** -> **"Project"**.
3. Select your `paytm-status-api` repository and click **Import**.
4. Leave Framework Preset as **Other**.
5. (Optional) In **Environment Variables**, you can set:
   * `REQUIRE_API_KEY`: `true` (if you want to sell keys) or `false` (if public).
   * `API_KEYS`: `key_client1,key_client2,key_client3`
6. Click **Deploy**.
7. In ~30 seconds, Vercel will give you a live URL, for example:
   `https://paytm-status-api.vercel.app`

#### Step 3: Test Your Live API
Run the included test script against your new live URL:
```bash
python test_api.py https://paytm-status-api.vercel.app
```

---

## 🌐 Option 2: Host on a VPS, Render, or Railway (24/7 Server)

If you prefer running a permanent Python server instead of serverless:

### Run on Local Machine or VPS:
```bash
cd paytm_payment_api
python app.py
```
The server will start on port `5000`.

### Run on Render / Railway:
1. Create a Web Service on [Render.com](https://render.com) or [Railway.app](https://railway.app).
2. Set Build Command: `pip install -r requirements.txt` (or none, standard library is used).
3. Set Start Command: `python app.py`
4. Set Environment Variable `PORT=10000` (Render binds to this automatically).

---

## 💰 How to Sell This API & Manage Clients

### 1. Enable Key Protection
In your Vercel Project Settings -> **Environment Variables** (or in `.env` on VPS):
* Set `REQUIRE_API_KEY` = `true`

### 2. How to Generate Keys for Buyers
Whenever a customer buys a subscription (e.g. ₹299/month or ₹499 lifetime):
1. Generate a unique key for them, for example:
   - `paytm_live_rahul_8921`
   - `paytm_live_aman_3145`
2. Add the key to `API_KEYS` in your Vercel dashboard environment variables:
   ```text
   API_KEYS=paytm_live_rahul_8921,paytm_live_aman_3145
   ```
3. Click **Redeploy** on Vercel (takes 10 seconds).
4. Send the key and [`CLIENT_DOCS.md`](file:///d:/Projects/Payment%20Bot%20@shein_vouchershoppiebot/paytm_payment_api/CLIENT_DOCS.md) to your customer.

### 3. Pricing Suggestions for Telegram / Bot Developers
- **Basic Plan**: ₹199 / month (1 Telegram bot)
- **Pro Plan**: ₹499 / 3 months (Unlimited bots)
- **Lifetime Access**: ₹999 one-time payment

### 4. How the Customer Connects to Your API
Your customer simply changes their bot's poller URL to your domain:
```text
https://your-api.vercel.app/?MID=MERCHANT_ID&ORDERID=ORDER_ID&api_key=paytm_live_rahul_8921
```

If their key is valid, they receive the full transaction details. If their key expires or is removed, they get:
```json
{
  "STATUS": "TXN_FAILURE",
  "RESPCODE": "401",
  "RESPMSG": "Unauthorized: Invalid or missing API Key."
}
```

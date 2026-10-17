# Paytm Payment Status API Service (SaaS Edition)

A high-performance, lightweight API proxy service designed to query real-time Paytm transaction statuses by Merchant ID (`MID`) and `ORDERID`. Built with monetization support (API key validation) so you can host and sell access to customers.

---

## ⚡ Quick Start

### 1. Test Locally (Right Now)
No installations required! Run directly using Python:
```bash
cd paytm_payment_api
python app.py
```
Open in browser or test via curl:
```text
http://localhost:5000/?MID=vDCrQS30435072738208&ORDERID=7987926989
```

Run test suite:
```bash
python test_api.py http://localhost:5000
```

---

## ☁️ Deploy to Vercel (100% Free)

1. Upload this folder to a GitHub repository.
2. Link your repo on [Vercel.com](https://vercel.com) and click **Deploy**.
3. You will receive a live URL: `https://your-api.vercel.app`.

For step-by-step instructions and pricing models, see [HOSTING_GUIDE.md](HOSTING_GUIDE.md).

---

## 💼 Selling & Monetization

* Set `REQUIRE_API_KEY=true` in environment variables.
* Generate and store client keys in `API_KEYS=key1,key2,key3`.
* Hand over [CLIENT_DOCS.md](CLIENT_DOCS.md) to your paying buyers.

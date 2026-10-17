# Paytm Transaction Status API - Developer Documentation

Welcome! This API allows you to query real-time transaction statuses directly from Paytm using your Paytm Merchant ID (`MID`) and `ORDERID`.

---

## 📌 Base Endpoint

```text
GET https://YOUR-API-DOMAIN.vercel.app/
```

---

## 🔑 Authentication

Include your API key either as a URL query parameter or as an HTTP header:

* **Query Parameter**: `?api_key=YOUR_API_KEY`
* **HTTP Header**: `X-API-Key: YOUR_API_KEY`

---

## 📥 Request Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `MID` | String | **Yes** | Your Paytm Merchant ID |
| `ORDERID` | String | **Yes** | Your unique Order ID generated during checkout |
| `api_key` | String | *Optional* | Your assigned API access key (if required) |

---

## 📤 Response Format

### Success Response (`200 OK` - Paid Order):
```json
{
  "TXNID": "20261017111100000318173114458593265",
  "BANKTXNID": "005954320257",
  "ORDERID": "7987926989",
  "TXNAMOUNT": "20.00",
  "STATUS": "TXN_SUCCESS",
  "TXNTYPE": "SALE",
  "GATEWAYNAME": "PPBL",
  "RESPCODE": "01",
  "RESPMSG": "Txn Success",
  "MID": "vDCrQS30435072738208",
  "PAYMENTMODE": "UPI",
  "REFUNDAMT": "0.0",
  "TXNDATE": "2026-10-17 11:09:20.0",
  "currentTxnCount": "4"
}
```

### Unpaid / Pending Order:
```json
{
  "TXNID": "",
  "BANKTXNID": "",
  "ORDERID": "7987926989",
  "TXNAMOUNT": "",
  "STATUS": "TXN_FAILURE",
  "RESPCODE": "334",
  "RESPMSG": "Invalid Order Id."
}
```

---

## 💻 Code Examples

### 1. Python (Requests)
```python
import requests

API_URL = "https://YOUR-API-DOMAIN.vercel.app"
API_KEY = "YOUR_API_KEY"

def check_payment(mid, order_id):
    params = {
        "MID": mid,
        "ORDERID": order_id,
        "api_key": API_KEY
    }
    response = requests.get(API_URL, params=params, timeout=10)
    data = response.json()
    
    if data.get("STATUS") == "TXN_SUCCESS":
        print(f"Payment Verified! Amount: {data.get('TXNAMOUNT')}")
        return True, data.get("BANKTXNID"), float(data.get("TXNAMOUNT"))
    else:
        print("Payment pending or failed.")
        return False, None, 0.0
```

### 2. Node.js (Fetch)
```javascript
async function checkPayment(mid, orderId, apiKey) {
  const url = `https://YOUR-API-DOMAIN.vercel.app/?MID=${mid}&ORDERID=${orderId}&api_key=${apiKey}`;
  const res = await fetch(url);
  const data = await res.json();

  if (data.STATUS === 'TXN_SUCCESS') {
    console.log('Payment Successful:', data.TXNAMOUNT);
    return true;
  }
  return false;
}
```

### 3. PHP (cURL)
```php
<?php
$mid = "YOUR_MID";
$orderId = "ORDER_12345";
$apiKey = "YOUR_API_KEY";

$url = "https://YOUR-API-DOMAIN.vercel.app/?MID={$mid}&ORDERID={$orderId}&api_key={$apiKey}";
$json = file_get_contents($url);
$data = json_decode($json, true);

if (isset($data['STATUS']) && $data['STATUS'] === 'TXN_SUCCESS') {
    echo "Payment verified! Amount: " . $data['TXNAMOUNT'];
}
?>
```

### 4. cURL
```bash
# Test with client credentials:
curl -X GET "https://YOUR-API-DOMAIN.vercel.app/?MID=fzpmIb05835944940347&ORDERID=T2610170101325427993215&api_key=YOUR_API_KEY"
```

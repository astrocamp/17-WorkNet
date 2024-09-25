# Create your views here.
import base64
import hashlib
import hmac
import json
import os
import uuid
from pathlib import Path

import dotenv
import requests
from django.shortcuts import redirect, render

# Create your views here.

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(os.path.join(BASE_DIR, ".env"))


def request(request):
    if request.method == "POST":
        url = f"{os.getenv('LINE_SANDBOX_URL')}/request"
        order_id = f"order_{str(uuid.uuid4())}"  # 生成一個長度為20的唯一訂單ID
        package_id = f"package_{str(uuid.uuid4())}"  # 生成一個長度為20的唯一包裹ID

        payload = {
            "amount": 200,
            "currency": "TWD",
            "orderId": order_id,
            "packages": [
                {
                    "id": package_id,
                    "name": "Premium",
                    "amount": 200,
                    "products": [{"name": "Premium", "quantity": 1, "price": 200}],
                }
            ],
            "redirectUrls": {
                "confirmUrl": f"http://{os.getenv('HOSTNAME')}/payments/confirm",
                "cancelUrl": f"http://{os.getenv('HOSTNAME')}/payments/cancel",
            },
        }

        signature_uri = os.getenv("LINE_SIGNATURE_REQUEST_URI")
        headers = create_headers(payload, signature_uri)
        body = json.dumps(payload)
        print("=====request=====")
        print(headers)
        print(body)
        print(url)
        response = requests.post(url, headers=headers, data=body)

        # print("-" * 10)
        # print(body)
        if response.status_code == 200:
            data = response.json()
            if data["returnCode"] == "0000":
                return redirect(data["info"]["paymentUrl"]["web"])
            else:
                print(data["returnMessage"])
                return render(request, "payments/checkout.html")
        else:
            print(f"Error: {response.status_code}")
            print(response)
            return render(request, "payments/checkout.html")

    else:
        return render(request, "payments/checkout.html")


def create_headers(body, uri):

    channel_id = os.getenv("LINE_CHANNEL_ID")
    nonce = str(uuid.uuid4())
    secret_key = os.getenv("LINE_CHANNEL_SECRET_KEY")
    body_to_json = json.dumps(body)
    message = secret_key + uri + body_to_json + nonce

    binary_message = message.encode()
    binary_secret_key = secret_key.encode()

    hash = hmac.new(binary_secret_key, binary_message, hashlib.sha256)

    signature = base64.b64encode(hash.digest()).decode()

    headers = {
        "Content-Type": "application/json",
        "X-LINE-ChannelId": channel_id,
        "X-LINE-Authorization-Nonce": nonce,
        "X-LINE-Authorization": signature,
    }

    return headers


def confirm(request):
    print("======confirm========")
    print(request.GET)
    transaction_id = request.GET.get("transactionId")
    order_id = request.GET.get("orderId")

    payload = {
        "amount": 200,
        "currency": "TWD",
        "orderId": order_id,
    }

    signature_uri = f"/v3/payments/{transaction_id}/confirm"
    headers = create_headers(payload, signature_uri)
    url = f"{os.getenv('LINE_SANDBOX_URL')}/{transaction_id}/confirm"

    body = json.dumps(payload)

    print(signature_uri)
    print(headers)
    print(url)
    print(body)
    response = requests.post(url, headers=headers, data=body)

    data = response.json()
    if data["returnCode"] == "0000":
        return render(request, "payments/success.html")
    else:
        print(data["returnMessage"])
        return render(request, "payments/fail.html")

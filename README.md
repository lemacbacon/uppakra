# uppakra

Daily stock checker for the IKEA Uppåkra sofa collection at IKEA Toulon - La Valette-du-Var.

Sends a [ntfy.sh](https://ntfy.sh) push notification when any Uppåkra model is available for cash & carry at store 315.

## How it works

A GitHub Actions workflow runs every day at 10am Paris time. It calls the IKEA Ingka availability API for all 17 Uppåkra sofa configurations and fires a push notification if any of them show stock > 0 at the Toulon store.

## Setup

### 1. Subscribe to your ntfy topic

Install the [ntfy app](https://ntfy.sh) (iOS, Android, or web) and subscribe to your chosen topic name.

### 2. Add the GitHub secret

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|---|---|
| `NTFY_TOPIC` | your topic name (treat it like a password) |

### 3. Push and you're done

The workflow triggers automatically every day. You can also run it manually from the **Actions** tab (restricted to `lemacbacon`).

## Local run

```bash
pip install -r requirements.txt
NTFY_TOPIC=your-topic python check_availability.py
```

## Customisation

Edit the `PRODUCTS` dict in `check_availability.py` to track only the models you care about.

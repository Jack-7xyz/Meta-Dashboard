from flask import Flask, jsonify
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import os
from dotenv import load_dotenv
import logging
from datetime import date, timedelta  # ← added

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
app_id       = os.getenv("META_APP_ID")
app_secret   = os.getenv("META_APP_SECRET")
access_token = os.getenv("META_ACCESS_TOKEN")
account_id   = os.getenv("AD_ACCOUNT_ID")

# Validate credentials
missing = [name for name, val in [
    ("META_APP_ID", app_id),
    ("META_APP_SECRET", app_secret),
    ("META_ACCESS_TOKEN", access_token),
    ("AD_ACCOUNT_ID", account_id),
] if not val]
if missing:
    logger.error(f"Missing environment variables: {missing}")
    raise RuntimeError(f"Missing environment variables: {missing}")

def create_app():
    app = Flask(__name__)

    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.route("/api/insights")
    def insights():
        logger.info("Received request to /api/insights")
        try:
            # compute rolling 30-day window
            today      = date.today()
            yesterday  = today - timedelta(days=1)
            since_date = (today - timedelta(days=30)).isoformat()
            until_date = yesterday.isoformat()

            fields = [
                "date_start", "impressions", "clicks", "spend", "purchase_roas", "actions"
            ]
            params = {
                "time_range": {"since": since_date, "until": until_date},
                "time_increment": 1,
                "action_attribution_windows": ["7d_click"]
            }

            FacebookAdsApi.init(app_id, app_secret, access_token)
            account = AdAccount(account_id)
            raw_data = account.get_insights(fields=fields, params=params)
            raw_data = account.get_insights(fields=fields, params=params)
            return jsonify([item.export_all_data() for item in raw_data])
        except Exception as e:
            logger.exception("Error fetching insights")
            return jsonify({"error": str(e)}), 500

    return app

app = create_app()

if __name__ == "__main__":
    # run on 5001 to avoid macOS AirPlay conflict
    app.run(debug=True, host="127.0.0.1", port=5001)

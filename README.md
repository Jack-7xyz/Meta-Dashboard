# Meta Ads Performance Dashboard

A simple Python project that connects to a Meta (Facebook) Ads account via the Marketing API, fetches daily performance data over a rolling 30-day window, and displays:

* A tabular view with aggregated metrics and a SUM row
* A Contribution Margin time-series chart
* A Spend vs. ROAS bar chart

Built with:

* **Flask** for the API backend
* **Dash** for the interactive frontend
* **facebook\_business** SDK to pull Meta Ads data
* **python-dotenv** for environment variable management

---

## Features

1. **Rolling 30-day window**: Automatically pulls data from today−30 days through yesterday.
2. **Metrics table**:
   * Daily rows: Spend, ROAS, Revenue, Impressions, CPM, Link Clicks, CTR, Contribution Margin
   * SUM row: aggregates (sum or average) for the selected month
   * Color‑coded styling and Calibri font
3. **Charts**:
   * **Contribution Margin** line chart
   * **Spend vs. ROAS** bar chart (hover shows date)
   * Custom colors and formatting (dark background, lime accents)

---

## Prerequisites

* Python 3.10+
* A Meta Business account with Ads data
* A valid Meta App (App ID, App Secret, Access Token) with `ads_read` permission
* Git (for cloning the repo)

---

## Setup & Installation

1. **Clone the repository**
   git clone https://github.com/Jack-7xyz/Meta-Dashboard.git
   cd Meta-Dashboard

2. **Create and activate a virtual environment**
   python3 -m venv venv
   source venv/bin/activate    # macOS/Linux
   # venv\Scripts\activate   # Windows PowerShell

3. **Install dependencies**
   pip install --upgrade pip
   pip install flask dash facebook_business python-dotenv

4. **Configure environment variables**
   Create a file named `.env` in the project root:
   ```ini
   META_APP_ID=your_meta_app_id
   META_APP_SECRET=your_meta_app_secret
   META_ACCESS_TOKEN=your_long_lived_access_token
   AD_ACCOUNT_ID=act_your_ads_account_id
   ```
   * Get your App ID & Secret from [https://developers.facebook.com/apps](https://developers.facebook.com/apps)
   * Generate a long‑lived access token via the Graph API Explorer or your app dashboard
   * AD\_ACCOUNT\_ID should be in the form `act_1234567890`

5. **Choose ports**
   * The Flask API runs on **port 5001** (configured to avoid macOS AirPlay conflicts).
   * The Dash frontend runs on **port 8050**.

---

## Running Locally

### 1. Start the Flask API
source venv/bin/activate
python app.py


You should see:
* Running on http://127.0.0.1:5001/ (Press CTRL+C to quit)

Verify the health endpoint:
curl http://127.0.0.1:5001/health
returns {"status":"ok"}

### 2. Launch the Dash frontend
In a new terminal (same project folder):
source venv/bin/activate
python dashboard.py

You should see:
Dash app running on http://127.0.0.1:8050/
Open your browser to **[http://127.0.0.1:8050/](http://127.0.0.1:8050/)** to view the dashboard.

---

## Project Structure

Meta-Dashboard/
├── app.py             # Flask API server
├── dashboard.py       # Dash frontend app
├── .env               # Environment variables
├── requirements.txt   # (optional) pinned dependencies
├── README.md          # This file
└── venv/              # Python virtual environment

---

## Implementation Details

* **app.py**:
  * Reads credentials from `.env` via `python-dotenv`
  * Computes dynamic dates using `datetime.date` and `timedelta`
  * Initializes the `facebook_business` SDK and calls `AdAccount.get_insights`
  * Requests fields: `date_start`, `impressions`, `clicks`, `spend`, `purchase_roas`, `actions`
  * Returns a JSON array of daily insight objects

* **dashboard.py**:
  * Fetches `/api/insights` on startup and via user‑selectable month filter
  * Parses out link clicks from the `actions` field for CTR calculation
  * Computes **Contribution Margin** per day and sums it in the header row
  * Uses **Dash DataTable** with custom styling for the table and SUM row
  * Renders two Plotly charts with custom colors and Calibri font

-- Please better format this readme file to include code blocks where applicable

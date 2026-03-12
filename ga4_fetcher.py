import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

def fetch_ga4_data(property_id, days_ago):
    """
    Fetches GA4 basic reporting data (Sessions, Active Users, Page Views) for the last N days.
    """
    # Environment variable check (Google auth client uses GOOGLE_APPLICATION_CREDENTIALS)
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path or not os.path.exists(credentials_path):
        print(f"警告: GOOGLE_APPLICATION_CREDENTIALS が設定されていないか、パスが見つかりません: {credentials_path}")
        # In a real scenario, this might raise an error, but let's allow the Google Auth library to try other default methods if available.

    try:
        # Initialize client
        client = BetaAnalyticsDataClient()

        # Construct request
        # We request data grouped by date, and fetch basic KPIs.
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="date")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="screenPageViews"),
            ],
            date_ranges=[DateRange(start_date=f"{days_ago}daysAgo", end_date="today")],
        )

        # Execute request
        response = client.run_report(request)

        # Parse response into a structured dictionary for the AI agent
        report_data = {
            "property_id": property_id,
            "period": f"Last {days_ago} days to today",
            "totals": {
                "sessions": 0,
                "active_users": 0,
                "page_views": 0
            },
            "daily_data": []
        }

        # Calculate totals from the row data
        for row in response.rows:
            date_str = row.dimension_values[0].value
            sessions = int(row.metric_values[0].value)
            active_users = int(row.metric_values[1].value)
            page_views = int(row.metric_values[2].value)

            report_data["daily_data"].append({
                "date": date_str,
                "sessions": sessions,
                "active_users": active_users,
                "page_views": page_views
            })

            report_data["totals"]["sessions"] += sessions
            report_data["totals"]["active_users"] += active_users
            report_data["totals"]["page_views"] += page_views

        # Sort daily data by date ascending
        report_data["daily_data"].sort(key=lambda x: x["date"])

        return report_data

    except Exception as e:
        print(f"GA4 Data fetch failed: {e}")
        return None

if __name__ == "__main__":
    # Test script (will fail if no property ID or auth is provided)
    test_property_id = os.getenv("GA4_PROPERTY_ID", "123456789")
    print(fetch_ga4_data(test_property_id, 7))
import plotly.express as px
import pandas as pd


def plot_route(
    tour,
    markets,
    *,
    annotate=True,
    title="Route Map",
    show=True,
    save_path=None,
):
    """
    Visualize the ordered tour on a 2D scatter plot using lat/lon coordinates using plotly.
    Vizualizes all days in the same plot with different colors.
    """
    
    rows = []
    for day, market_ids in tour.items():
        for market_id in market_ids:
            market = markets[str(market_id)]
            rows.append({
                "day": day,
                "market_id": market_id,
                "lat": market["latitude"],
                "lon": market["longitude"],
                "name": market["Name"],
                "opens": market["Opens"],
                "closes": market["Closes"],
            })
    df = pd.DataFrame(rows)
            
    fig = px.line_map(df, lat="lat", lon="lon", color="day", zoom=12, height=800, text="name")
    fig.show()
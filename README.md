# sos_tuwien

## Problem

The Christmas market problem is very similar to a generalization of the TSP problem, called [Orienteering Problemwith Time Windows](https://www.jstor.org/stable/2583018)

## Data Preparation

Fetching the travel times from [Google Directions API](https://console.cloud.google.com/marketplace/product/google/directions-backend.googleapis.com) requires an API key in the .env file with variable name GOOGLE_MAPS_API_KEY

2 entries from the assignment needed adaptations:

- [MQ](https://www.google.com/url?sa=E&q=https%3A%2F%2Fg.page%2Fweihnachtsquartier%3Fshare) is not the google maps link and location changed to Urania -> updated the entry to [Urania](https://maps.app.goo.gl/BgnZ8VBAJugrZ2pK6)
- [Belvedere](https://g.page/belvederemuseum?share) is not the google maps link -> updated the entry to [Belvedere](https://maps.app.goo.gl/uyTZiLbpsGLwvhH26)

Travel times for the dataset were calculated at 11/08/2025 12:20.

## Setup

sudo apt install libsqlite3-dev
pyenv install --force 3.11.10
poetry env remove python3.11
poetry install

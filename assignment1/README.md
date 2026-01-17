# Self-Organizing Systems Exercise 1

## Problem

The Christmas market problem is very similar to a generalization of the TSP problem, called [Orienteering Problem with Time Windows](https://www.jstor.org/stable/2583018)

## Data Preparation

Fetching the travel times from [Google Directions API](https://console.cloud.google.com/marketplace/product/google/directions-backend.googleapis.com) requires an API key in the .env file with variable name GOOGLE_MAPS_API_KEY. We provide a sample .env file in the root directory.

2 entries from the assignment needed adaptations:

- [MQ](https://www.google.com/url?sa=E&q=https%3A%2F%2Fg.page%2Fweihnachtsquartier%3Fshare) is not the google maps link and location changed to Urania -> updated the entry to [Urania](https://maps.app.goo.gl/BgnZ8VBAJugrZ2pK6)
- [Belvedere](https://g.page/belvederemuseum?share) is not the google maps link -> updated the entry to [Belvedere](https://maps.app.goo.gl/uyTZiLbpsGLwvhH26)
- [Messe](https://goo.gl/maps/mgUHYBriHmwAFcK19) has incorrect coordinates in Google Maps, as we only realized that after all of our experiments were done, we kept the original coordinates here.

Travel times for the dataset were calculated at 24/10/2025 19:12.

## How to run

To run the project, you can use `uv`, `poetry` or `pip` directly. We recommend using `uv` or `poetry` for simplicity.

With either of these installed, run the following commands to install the dependencies:

```bash
uv sync
poetry sync
```

`spade` requires sqlite to run the XMPP server, run these commands to install it

```bash
sudo apt install libsqlite3-dev
pyenv install --force 3.11.10
poetry env remove python3.11
poetry install
```

You can then start the XMPP server with the following command (using `poetry`, if you use `uv` or `pip` directly, simply modify the script to use the correct command):

```bash
./run_xmpp_server.sh
```

To run the project with the default parameters, use the following command:

With `poetry` installed:

```bash
./run.sh
```

if you want to use `uv` or `pip` directly, simply modify the script to use the correct command.

The run_grid_search.sh and run.sh scripts requires the XMPP server to be online when using ACO, start it with `run_xmpp_server.sh` in a separate terminal.

After a successful run, you can plot the pheromone matrices, use the following command:

```bash
./plot_pheromones.py <pheromone_matrices_file>
```

The pheromone matrices file is the one that was created by the run script, you can find it in the `out` directory under the respective run id.

#!/usr/bin/env python3
"""
Plot pheromone strength over iterations on a map with a slider.
Displays all markets and visualizes pheromone trails between them.
"""

import json
import sys
from pathlib import Path

import plotly.graph_objects as go


def load_pheromone_data(pheromone_file):
    """Load pheromone matrices from JSON file."""
    with open(pheromone_file, 'r') as f:
        data = json.load(f)
    return data


def load_markets(places_file):
    """Load market data from places.json file."""
    with open(places_file, 'r') as f:
        markets_raw = json.load(f)
    
    # Markets use string keys (for compatibility)
    markets = {str(m["id"]): m for m in markets_raw}
    return markets


def create_pheromone_plot(pheromone_file, places_file):
    """
    Create an interactive plot showing pheromone strength over iterations.
    
    Args:
        pheromone_file: Path to pheromone_matrices_day1.json
        places_file: Path to places.json
    """
    # Load data
    pheromone_data = load_pheromone_data(pheromone_file)
    markets = load_markets(places_file)
    
    # Get mappings
    index_to_market = {int(k): int(v) for k, v in pheromone_data["index_to_market"].items()}
    iterations = pheromone_data["iterations"]
    
    # Prepare market positions
    market_positions = {}
    for market_id_str, market in markets.items():
        market_id = int(market_id_str)
        market_positions[market_id] = {
            "lat": market["latitude"],
            "lon": market["longitude"],
            "name": market["Name"]
        }
    
    # Create figure
    fig = go.Figure()
    
    # Add all markets as markers (visible in all frames)
    market_ids = list(market_positions.keys())
    market_lats = [market_positions[mid]["lat"] for mid in market_ids]
    market_lons = [market_positions[mid]["lon"] for mid in market_ids]
    market_names = [market_positions[mid]["name"] for mid in market_ids]
    
    # Add market markers
    fig.add_trace(go.Scattermap(
        lat=market_lats,
        lon=market_lons,
        mode='markers+text',
        marker=dict(
            size=10,
            color='red',
            symbol='circle'
        ),
        text=market_names,
        textposition="top center",
        name="Markets",
        showlegend=True
    ))
    
    # Prepare frames for each iteration
    frames = []
    
    # Calculate global min/max for consistent scaling
    all_strengths = []
    for iter_data in iterations:
        all_strengths.extend(iter_data["matrix"].values())
    global_min_strength = min(all_strengths) if all_strengths else 0.95
    global_max_strength = max(all_strengths) if all_strengths else 1.0
    
    print(f"Pheromone strength range: {global_min_strength:.2f} - {global_max_strength:.2f}")
    
    # Process each iteration
    for iter_data in iterations:
        iteration = iter_data["iteration"]
        matrix = iter_data["matrix"]
        
        # Collect edges with pheromone strength
        edges = []
        for key, strength in matrix.items():
            from_idx, to_idx = map(int, key.split('_'))
            from_market = index_to_market.get(from_idx)
            to_market = index_to_market.get(to_idx)
            
            # Skip self-loops
            if from_market == to_market:
                continue
                
            if from_market and to_market and from_market in market_positions and to_market in market_positions:
                edges.append({
                    "from": from_market,
                    "to": to_market,
                    "strength": strength
                })
        
        # Create traces for edges in this iteration
        edge_traces = []
        
        # Show edges with strength above initial value (0.95) or top 20% strongest
        # This ensures we see the pheromone trails that have been reinforced
        threshold = max(global_min_strength, global_min_strength + (global_max_strength - global_min_strength) * 0.1)
        
        edges_shown = 0
        for edge in edges:
            if edge["strength"] >= threshold:
                from_pos = market_positions[edge["from"]]
                to_pos = market_positions[edge["to"]]
                
                # Normalize strength for line width (1 to 6) using global range
                normalized_strength = (edge["strength"] - global_min_strength) / (global_max_strength - global_min_strength + 1e-6)
                # Make lines clearly visible
                line_width = 1.0 + normalized_strength * 5.0
                # Opacity based on strength - stronger = more opaque
                opacity = 0.3 + normalized_strength * 0.7
                
                edge_traces.append(go.Scattermap(
                    lat=[from_pos["lat"], to_pos["lat"]],
                    lon=[from_pos["lon"], to_pos["lon"]],
                    mode='lines',
                    line=dict(
                        width=line_width,
                        color=f'rgba(0, 100, 200, {opacity})'
                    ),
                    showlegend=False,
                    hoverinfo='text',
                    text=f"Strength: {edge['strength']:.2f}",
                    name=f"Edge {edge['from']}-{edge['to']}"
                ))
                edges_shown += 1
        
        print(f"Iteration {iteration}: Showing {edges_shown} edges (threshold: {threshold:.2f})")
        
        # Create frame with market markers (trace 0) + edge traces
        # Need to copy the market marker trace for each frame
        market_trace = go.Scattermap(
            lat=market_lats,
            lon=market_lons,
            mode='markers+text',
            marker=dict(
                size=10,
                color='red',
                symbol='circle'
            ),
            text=market_names,
            textposition="top center",
            name="Markets",
            showlegend=False
        )
        
        frame_data = [market_trace] + edge_traces
        frames.append(go.Frame(
            data=frame_data,
            name=str(iteration)
        ))
    
    # Add initial edges from first iteration so something is visible from the start
    if frames and len(frames) > 0:
        first_frame = frames[0]
        # Add all edge traces from first frame to initial figure
        # This ensures edges are visible when the plot first loads
        for trace in first_frame.data[1:]:  # Skip market marker (index 0), add all edges
            fig.add_trace(trace)
    
    # Add frames to figure (must be after adding initial traces)
    fig.frames = frames
    
    # Add slider
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",  # Free style that doesn't require a token
            center=dict(
                lat=sum(market_lats) / len(market_lats),
                lon=sum(market_lons) / len(market_lons)
            ),
            zoom=12
        ),
        height=800,
        title="Pheromone Strength Over Iterations",
        updatemenus=[{
            "type": "buttons",
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": True,
            "x": 0.1,
            "xanchor": "left",
            "y": 0,
            "yanchor": "top",
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [None, {
                        "frame": {"duration": 500, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": 300}
                    }]
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }]
                }
            ]
        }],
        sliders=[{
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 20},
                "prefix": "Iteration:",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 300, "easing": "cubic-in-out"},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": [
                {
                    "args": [[f.name], {
                        "frame": {"duration": 300, "redraw": True},
                        "mode": "immediate",
                        "transition": {"duration": 300}
                    }],
                    "label": f"Iteration {f.name}",
                    "method": "animate"
                }
                for f in frames
            ]
        }]
    )
    
    return fig


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python plot_pheromones.py <pheromone_matrices_file> [places_file]")
        print("Example: python plot_pheromones.py out/20251121_183654/pheromone_matrices_day1.json")
        sys.exit(1)
    
    pheromone_file = Path(sys.argv[1])
    places_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/places.json")
    
    if not pheromone_file.exists():
        print(f"Error: Pheromone file not found: {pheromone_file}")
        sys.exit(1)
    
    if not places_file.exists():
        print(f"Error: Places file not found: {places_file}")
        sys.exit(1)
    
    print(f"Loading pheromone data from: {pheromone_file}")
    print(f"Loading market data from: {places_file}")
    
    fig = create_pheromone_plot(pheromone_file, places_file)
    fig.show()


if __name__ == "__main__":
    main()


import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import deque


# 1. GRAPH CREATION
def create_graph(traffic_mode: bool) -> nx.Graph:
    """
    Build a weighted undirected graph representing a city road network.
    Nodes  → intersections (A–F)
    Edges  → roads with a base travel cost (weight)
    If traffic_mode is True all weights are doubled to simulate rush-hour.
    """
    G = nx.Graph()
    # Base edge list: (node_u, node_v, weight)
    base_edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 5),
        ("B", "D", 10),
        ("C", "E", 3),
        ("E", "D", 4),
        ("D", "F", 11),
        ("E", "F", 7),
        ("B", "F", 15),
    ]
    multiplier = 2 if traffic_mode else 1
    for u, v, w in base_edges:
        G.add_edge(u, v, weight=w * multiplier)
    return G




# 2. ALGORITHM RUNNER

def run_algorithm(G: nx.Graph, source: str, target: str, algorithm: str):
    """
    Find the shortest path between source and target.
    algorithm = 'Dijkstra' → weighted shortest path via NetworkX
    algorithm = 'BFS'      → unweighted (hop-count) shortest path
                             implemented manually so the logic is transparent.
    Returns
    -------
    path  : list[str] | None
    cost  : int | None   (total weight; None for BFS since it is unweighted)
    error : str  | None
    """
    if source == target:
        return [source], 0, None
    try:
        if algorithm == "Dijkstra":
            path = nx.dijkstra_path(G, source, target, weight="weight")
            cost = nx.dijkstra_path_length(G, source, target, weight="weight")
            return path, cost, None
        else:  # BFS – unweighted
            # Manual BFS 
            visited = {source}
            queue = deque([[source]])          # queue of paths
            while queue:
                current_path = queue.popleft()
                current_node = current_path[-1]
                for neighbor in G.neighbors(current_node):
                    if neighbor == target:
                        return current_path + [neighbor], None, None
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(current_path + [neighbor])
            return None, None, "No path found (BFS)."
    except nx.NetworkXNoPath:
        return None, None, f"No path exists between {source} and {target}."
    except nx.NodeNotFound as e:
        return None, None, str(e)
    
    
    
    

# 3. GRAPH DRAWING
def draw_graph(G: nx.Graph, path: list, traffic_mode: bool) -> plt.Figure:
    """
    Draw the city graph using matplotlib.
    - All nodes are drawn in steel-blue.
    - Path nodes are highlighted in coral-red.
    - Path edges are drawn thicker and in red.
    - Edge weight labels are shown on every road.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("#0f1117")   # match Streamlit dark background
    ax.set_facecolor("#0f1117")
    # Fixed positions so the layout is reproducible across runs
    pos = {
        "A": (0.0, 1.0),
        "B": (1.0, 2.0),
        "C": (1.0, 0.0),
        "D": (3.0, 2.0),
        "E": (2.0, 0.5),
        "F": (4.0, 1.0),
    }
    # Identify path edges for highlighting
    path_edges = set()
    if path and len(path) > 1:
        path_edges = {(path[i], path[i + 1]) for i in range(len(path) - 1)}
        # Add reverse direction too (undirected graph)
        path_edges |= {(v, u) for u, v in path_edges}
    # Separate normal vs path nodes
    path_nodes   = set(path) if path else set()
    normal_nodes = [n for n in G.nodes() if n not in path_nodes]
    highlight_nodes = list(path_nodes)
    # Draw normal nodes
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=normal_nodes,
        node_color="#4c8eda",
        node_size=800,
        ax=ax,
    )
    # Draw highlighted (path) nodes
    if highlight_nodes:
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=highlight_nodes,
            node_color="#e05c5c",
            node_size=900,
            ax=ax,
        )
    # Draw node labels
    nx.draw_networkx_labels(
        G, pos,
        font_color="white",
        font_size=13,
        font_weight="bold",
        ax=ax,
    )
    # Draw normal edges (all edges first)
    normal_edges = [
        (u, v) for u, v in G.edges()
        if (u, v) not in path_edges and (v, u) not in path_edges
    ]
    nx.draw_networkx_edges(
        G, pos,
        edgelist=normal_edges,
        edge_color="#aaaaaa",
        width=2,
        ax=ax,
    )
    # Draw highlighted path edges
    highlighted = [
        (u, v) for u, v in G.edges()
        if (u, v) in path_edges or (v, u) in path_edges
    ]
    if highlighted:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=highlighted,
            edge_color="#e05c5c",
            width=4,
            ax=ax,
        )
    # Draw edge weight labels
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_color="#f0c040",
        font_size=10,
        ax=ax,
    )
    # Legend
    legend_items = [
        mpatches.Patch(color="#4c8eda", label="Intersection"),
        mpatches.Patch(color="#e05c5c", label="Shortest Path"),
    ]
    ax.legend(
        handles=legend_items,
        loc="upper left",
        facecolor="#1e1e2e",
        labelcolor="white",
        fontsize=9,
    )
    title = "City Road Network"
    if traffic_mode:
        title += "  🚦 [Rush Hour — weights ×2]"
    ax.set_title(title, color="white", fontsize=13, pad=12)
    ax.axis("off")
    plt.tight_layout()
    return fig


# 
# 4. STREAMLIT UI
def main():
    st.set_page_config(
        page_title="Traffic Navigation Simulator",
        page_icon="🗺️",
        layout="wide",
    )
    # ── Title 
    st.markdown(
        """
        <h1 style='text-align:center; color:#4c8eda;'>
              Traffic Navigation Simulator
        </h1>
        <p style='text-align:center; color:#aaaaaa; margin-top:-10px;'>
            Find the shortest route through a city road network
        </p>
        <hr style='border-color:#333'>
        """,
        unsafe_allow_html=True,
    )
    nodes = ["A", "B", "C", "D", "E", "F"]
    # ── Sidebar Controls ────────────────────────
    with st.sidebar:
        st.header("⚙️ Route Settings")
        start_node = st.selectbox("🟢 Start Intersection", nodes, index=0)
        end_node   = st.selectbox("🔴 End Intersection",   nodes, index=5)
        st.markdown("---")
        algorithm = st.radio(
            "🧭 Pathfinding Algorithm",
            options=["Dijkstra", "BFS"],
            help=(
                "**Dijkstra**: finds the minimum-weight path.\n\n"
                "**BFS**: finds the path with the fewest road segments (hops)."
            ),
        )
        st.markdown("---")
        traffic_mode = st.checkbox(
            "🚦 Traffic Mode (Rush Hour)",
            value=False,
            help="Doubles all road weights to simulate heavy traffic.",
        )
        st.markdown("---")
        find_btn = st.button("🔍 Find Path", use_container_width=True, type="primary")
    # ── Build graph (always draw even before search) ──
    G = create_graph(traffic_mode)
    # ── Run algorithm when button is clicked ──────
    path, cost, error = None, None, None
    if find_btn:
        if start_node == end_node:
            st.warning("⚠️ Start and end intersections are the same. Please choose different nodes.")
        else:
            path, cost, error = run_algorithm(G, start_node, end_node, algorithm)
    # ── Result Display ─────────────────────────────
    col_info, col_graph = st.columns([1, 2], gap="large")
    with col_info:
        st.subheader("📋 Result")
        if find_btn:
            if error:
                st.error(f"❌ {error}")
            elif path:
                st.success("✅ Path found!")
                st.markdown(
                    f"**Route:** `{'  →  '.join(path)}`"
                )
                st.markdown(f"**Algorithm:** `{algorithm}`")
                if cost is not None:
                    label = "Rush-Hour Cost" if traffic_mode else "Travel Cost"
                    st.metric(label, f"{cost} units")
                else:
                    # BFS returns hops, not weighted cost
                    st.metric("Hops (road segments)", len(path) - 1)
                if traffic_mode:
                    st.info("🚦 Rush-hour mode is active — all weights are doubled.")
            else:
                st.warning("No path could be found.")
        else:
            st.info("👈 Configure your route in the sidebar and click **Find Path**.")
        
        
        # Quick algorithm explanation
        st.markdown("---")
        st.markdown("### 📖 Algorithm Notes")
        if algorithm == "Dijkstra":
            st.markdown(
                "**Dijkstra's algorithm** explores edges by cumulative cost, "
                "guaranteeing the path with the *lowest total weight*."
            )
        else:
            st.markdown(
                "**BFS (Breadth-First Search)** explores layer by layer, "
                "guaranteeing the path with the *fewest road segments* "
                "(ignores weights)."
            )
    with col_graph:
        st.subheader("🗺️ City Road Map")
        fig = draw_graph(G, path if find_btn else None, traffic_mode)
        st.pyplot(fig)
        plt.close(fig)   # free memory
    # ── Footer ─────────────────────────────────────
    st.markdown(
        """
        <hr style='border-color:#333; margin-top:40px;'>
        <p style='text-align:center; color:#555; font-size:12px;'>
            Traffic Navigation Simulator · Built with NetworkX & Streamlit · zeyneppinarsoy
        </p>
        """,
        unsafe_allow_html=True,
    )
if __name__ == "__main__":
    main()
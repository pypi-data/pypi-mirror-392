import os

def visualize_graph(graph, output_path: str):
    try:
        # Use compiled graph’s internal structure
        if hasattr(graph, "get_graph"):
            g = graph.get_graph()
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Newest LangGraph API
            if hasattr(g, "draw_mermaid_png"):
                img_bytes = g.draw_mermaid_png()
                with open(output_path, "wb") as f:
                    f.write(img_bytes)
                print(f"Graph visualization saved at {output_path}")
                return

            # Older API
            elif hasattr(g, "save_mermaid_png"):
                g.save_mermaid_png(output_path)
                print(f"Graph visualization saved at {output_path}")
                return

        print("Graph visualization: unsupported LangGraph version.")

    except Exception as e:
        print(f"Graph visualization failed: {e}")

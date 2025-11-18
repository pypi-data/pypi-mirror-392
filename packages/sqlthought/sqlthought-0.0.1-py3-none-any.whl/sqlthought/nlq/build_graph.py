import os
from langgraph.graph import StateGraph, END

from .state import PipelineState
from .nodes import (
    node_schema_linking,
    node_subproblem,
    node_query_plan,
    node_sql_generation,
    node_db_execution,
    node_correction_plan,
    node_correction_sql,
)
from ..utils.visualizer import visualize_graph


def build_graph(groq_client, model_name: str, taxonomy: dict):
    """
    Build and compile a LangGraph pipeline for SQL-of-Thought reasoning.

    Parameters
    ----------
    groq_client : Groq
        Authenticated Groq client instance.
    model_name : str
        LLM model to use through Groq (e.g., "llama3-70b-8192").
    taxonomy : dict
        Error taxonomy used by correction nodes.

    Returns
    -------
    Compiled graph object ready to invoke().
    """

    graph = StateGraph(PipelineState, merge="dict")

    # -------------------------
    # Nodes
    # -------------------------
    graph.add_node("SchemaLinking",
                   lambda s: node_schema_linking(s, groq_client, model_name))

    graph.add_node("SubproblemDecomposition",
                   lambda s: node_subproblem(s, groq_client, model_name))

    graph.add_node("QueryPlan",
                   lambda s: node_query_plan(s, groq_client, model_name))

    graph.add_node("SQLGeneration",
                   lambda s: node_sql_generation(s, groq_client, model_name))

    graph.add_node("DBExecution",
                   lambda s: node_db_execution(s))

    graph.add_node("CorrectionPlan",
                   lambda s: node_correction_plan(s, groq_client, model_name, taxonomy))

    graph.add_node("CorrectionSQL",
                   lambda s: node_correction_sql(s, groq_client, model_name))

    # -------------------------
    # Edges
    # -------------------------

    graph.set_entry_point("SchemaLinking")
    graph.add_edge("SchemaLinking", "SubproblemDecomposition")
    graph.add_edge("SubproblemDecomposition", "QueryPlan")
    graph.add_edge("QueryPlan", "SQLGeneration")
    graph.add_edge("SQLGeneration", "DBExecution")

    # Correction loop logic
    def correction_condition(state: PipelineState):
        # Correction success
        if state.success is True:
            return END

        # Max retries
        if (state.correction_attempt or 0) >= 3:
            return END

        return "CorrectionPlan"

    graph.add_conditional_edges(
        "DBExecution",
        correction_condition,
        {
            "CorrectionPlan": "CorrectionPlan",
            END: END,
        }
    )

    graph.add_edge("CorrectionPlan", "CorrectionSQL")
    graph.add_edge("CorrectionSQL", "DBExecution")

    # Compile graph
    compiled = graph.compile()

    # Save diagram
    os.makedirs("_artifacts", exist_ok=True)
    visualize_graph(compiled, "_artifacts/sqlthought_graph.png")

    return compiled

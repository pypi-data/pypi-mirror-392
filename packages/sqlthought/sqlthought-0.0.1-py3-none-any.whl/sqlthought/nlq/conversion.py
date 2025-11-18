import os
import json
from groq import Groq

from .build_graph import build_graph
from ..utils.db_utils import extract_schema
from ..utils.logger import logger


CONFIG_PATH = os.path.expanduser("~/.sqlthought/config.json")


def _ensure_config():
    """Ensures Groq API config exists. If not, ask user via terminal."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    print("\nSQLThought: Groq configuration required.")

    api_key = input("Enter your GROQ_API_KEY: ").strip()
    model_name = input("Enter Groq model (default: llama3-70b-8192): ").strip() or "llama3-70b-8192"

    cfg = {"api_key": api_key, "model": model_name}
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

    print(f"Config saved to {CONFIG_PATH}")
    return cfg


def _make_groq_client(api_key: str):
    """Build Groq client."""
    return Groq(api_key=api_key)


def to_sql(question: str, db_path: str):
    """
    Public API exposed by package.

    Parameters
    ----------
    question : str
    db_path : str

    Returns
    -------
    dict : final pipeline state
    """
    logger.info("SQLThought NLQ → SQL pipeline starting")

    cfg = _ensure_config()
    groq_client = _make_groq_client(cfg["api_key"])
    model = cfg["model"]

    schema = extract_schema(db_path)
    taxonomy = {"sql_error_types": ["syntax", "semantic", "constraint", "runtime"]}

    graph = build_graph(groq_client, model, taxonomy)

    initial_state = {
        "question": question,
        "db_path": db_path,
        "schema": schema,
        "correction_attempt": 0
    }

    final_state = graph.invoke(initial_state)
    return final_state

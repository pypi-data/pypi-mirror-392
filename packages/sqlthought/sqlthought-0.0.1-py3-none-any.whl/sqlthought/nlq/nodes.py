import json
import os
import re

from ..utils.logger import logger
from ..utils.db_utils import execute_sql


MAX_CORRECTIONS = 3


# -----------------------------
# Helpers
# -----------------------------
def _load_prompt(name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "prompts", name)
    with open(path, "r") as f:
        return f.read()


def _clean_sql_output(raw: str) -> str:
    if not raw:
        return ""
    sql = re.search(r"((SELECT|WITH)\s.*?;)", raw, re.I | re.S)
    return sql.group(1).strip() if sql else raw.strip()


def _groq_invoke(groq_client, model, prompt: str) -> str:
    """Unified Groq invocation helper."""
    try:
        resp = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        # Groq returns: resp.choices[0].message.content
        message = resp.choices[0].message

        # Sometimes message is object, sometimes dict-like → normalize:
        if hasattr(message, "content"):
            return message.content
        elif isinstance(message, dict):
            return message.get("content", "")
        else:
            return str(message)

    except Exception as e:
        raise RuntimeError(f"Groq API call failed: {e}") from e


# -----------------------------
# Nodes
# -----------------------------
def node_schema_linking(state, groq_client, model):
    logger.info("🧩 SchemaLinking")

    prompt = _load_prompt("schema_prompt.txt").format(
        question=state.question,
        schema=state.schema,
    )

    out = _groq_invoke(groq_client, model, prompt)
    return {"schema_output": out}


def node_subproblem(state, groq_client, model):
    logger.info("🧩 SubproblemDecomposition")

    prompt = _load_prompt("subproblem_prompt.txt").format(
        question=state.question,
        schema_output=state.schema_output or ""
    )

    out = _groq_invoke(groq_client, model, prompt)
    return {"subproblem_output": out}


def node_query_plan(state, groq_client, model):
    logger.info("🧩 QueryPlan")

    prompt = _load_prompt("plan_prompt.txt").format(
        question=state.question,
        subproblem_output=state.subproblem_output or ""
    )

    out = _groq_invoke(groq_client, model, prompt)
    return {"plan_output": out}


def node_sql_generation(state, groq_client, model):
    logger.info("🧩 SQLGeneration")

    prompt = _load_prompt("sql_prompt.txt").format(
        question=state.question,
        plan_output=state.plan_output or ""
    )

    raw = _groq_invoke(groq_client, model, prompt)
    return {"sql": _clean_sql_output(raw)}


def node_db_execution(state):
    logger.info("🧩 DBExecution")

    sql = state.sql
    success, result = execute_sql(sql, state.db_path)

    if success:
        logger.info("   -> success")
    else:
        logger.info(f"   -> failed: {result}")

    return {"success": success, "result": result}


def node_correction_plan(state, groq_client, model, taxonomy):
    attempt = (state.correction_attempt or 0) + 1

    if attempt > MAX_CORRECTIONS:
        return {
            "success": False,
            "result": "Max correction attempts reached."
        }

    logger.info(f"🔁 CorrectionPlan (attempt {attempt})")

    prompt = _load_prompt("correction_plan_prompt.txt").format(
        taxonomy=json.dumps(taxonomy, indent=2),
        question=state.question,
        sql=state.sql or "",
        error=state.result or "",
        schema=state.schema or "",
    )

    out = _groq_invoke(groq_client, model, prompt)

    return {
        "correction_plan": out,
        "correction_attempt": attempt
    }


def node_correction_sql(state, groq_client, model):
    logger.info("🧩 CorrectionSQL")

    prompt = _load_prompt("correction_sql_prompt.txt").format(
        correction_plan=state.correction_plan or ""
    )

    raw = _groq_invoke(groq_client, model, prompt)
    return {"sql": _clean_sql_output(raw)}

# SQLThought

SQLThought is a modular, extensible multi-agent reasoning engine designed for intelligent interaction with structured data, databases, and analytical workflows. It currently ships with a complete natural-language-to-SQL reasoning pipeline, but its architecture is intentionally designed for future expansion into broader structured reasoning domains.

SQLThought is not just a tool—it is a foundation for agentic reasoning over data.
---

## Features

### Multi-Agent Reasoning

* Built using LangGraph to support:

* Stepwise planning

* State-aware execution

* Conditional branching

* Correction and retry loops

* Transparent, debuggable pipelines

### Groq-Powered LLM Execution

* Ultra-fast model inference using the Groq API.


### Modular Architecture

SQLThought is designed around interchangeable modules.
Each stage of the reasoning pipeline lives in its own file and can be extended:

```
nlq/
 ├── conversion.py
 ├── build_graph.py
 ├── nodes.py
 ├── state.py
 └── prompts/
```

### Command-Line Interface

Powerful terminal commands:

* sqlthought query

* sqlthought configure

* sqlthought version

### Local Secure Configuration

API keys and model selection stored at:

```
~/.sqlthought/config.json
```
---

## Installation

```
pip install sqlthought
```

---
## First-Time Setup

Run the configuration wizard:
```
sqlthought configure
```

You will be prompted for:

* Groq API key

* Model name (example: openai/gpt-oss-20b)

Configuration is remembered for all future commands.

---
## NLQ → SQL Conversion
The package currently includes a fully implemented NLQ→SQL reasoning engine featuring:

* Schema parsing

* Sub-problem decomposition

* Query plan generation

* SQL generation

* SQL execution

* Automatic error correction loop

* Structured JSON output

### CLI Example
```
sqlthought query "List employees earning above 70000" my.db
```

### Example Output
```
=== SQLThought Result ===
SQL: SELECT name, salary FROM employees WHERE salary > 70000;
Success: True
Result:
[("Alice", 90000), ("Bob", 75000)]
```

### Python Usage
```
from sqlthought import to_sql

result = to_sql("List high salary employees", db_path="company.db")

print(result["sql"])
print(result["result"])
```
---
## Project Structure
```
sqlthought/
├── nlq/
│   ├── conversion.py       # Public API
│   ├── build_graph.py      # LangGraph pipeline
│   ├── nodes.py            # Agent nodes
│   ├── state.py            # Pipeline state model
│   └── prompts/            # Prompt templates
├── utils/
│   ├── db_utils.py
│   ├── logger.py
│   └── visualizer.py
└── cli.py                  # Command-line interface

```
---
## Contributing

Issues and pull requests are welcome.
More documentation and developer guidelines will be added soon.

## License

MIT License
© 2025 Tiyasa Mukherjee
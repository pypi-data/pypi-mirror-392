<p align="center">
  <img src="/mnt/data/Query%20optimization.png" alt="Query Optimizer Logo" width="320" />
</p>

# Query Optimizer

> An AI-powered SQL query optimizer that analyzes slow database queries and suggests performance improvements. Achieve 10–100× faster queries with intelligent index recommendations, query rewrites, and execution-plan analysis.

[![CI](https://img.shields.io/badge/ci-passing-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](#)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-orange)](#)

---

## Table of Contents

* [Features](#-features)
* [Quickstart](#-quickstart)

  * [Hosted API (Recommended)](#hosted-api-recommended)
  * [Install CLI](#install-cli)
  * [Run with Docker](#run-with-docker)
* [Usage](#-usage)

  * [API Example](#api-example)
  * [CLI Example](#cli-example)
  * [Python Library](#python-library)
* [Demo](#%EF%B8%8F-demo)
* [Example Output](#-example-output)
* [Development](#%EF%B8%8F-development)

  * [Run tests](#run-tests)
* [Contributing](#contributing)
* [Enterprise & Support](#-enterprise--support)
* [License](#-license)
* [Acknowledgments](#-acknowledgments)

---

## 🚀 Features

* **Multi-Database Support** — PostgreSQL, MySQL, SQLite
* **Smart Analysis** — Identifies missing indexes, inefficient joins, suboptimal WHERE/GROUP patterns, and more
* **Actionable Recommendations** — Concrete SQL (e.g. `CREATE INDEX ...`) and rewritten queries
* **Multiple Access Methods** — REST API, CLI tool, Python library
* **Production Ready** — Containerized with Docker and CI/CD ready
* **Safety-first** — Dry-run mode, explicit `--apply` flag for changes that mutate schema

---

## 💡 Quickstart

### Hosted API (Recommended)

Use the hosted API when you want a no-ops, zero-maintenance start:

```bash
curl -s -X POST https://query-optimizer.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM users WHERE email = \'user@example.com\'",
    "db_type": "postgresql"
  }'
```

### Install CLI Tool

```bash
pip install git+https://github.com/makroumi/query-optimizer.git
```

**Usage after install:**

```bash
# Analyze a single ad-hoc query (no DB connection)
query-optimize "SELECT * FROM users WHERE created_at > '2023-01-01'" --db-type postgresql

# Analyze queries from a file
query-optimize --file slow_queries.sql --db-type mysql

# Connect to your DB for schema-aware analysis (safer + better recommendations)
query-optimize --connection "postgresql://user:pass@localhost/db" --analyze-schema
```

> ⚠️ By default the tool runs in read-only analysis mode. Use `--apply` with care to run any schema-changing recommendations.

### Run Locally with Docker

```bash
git clone https://github.com/makroumi/query-optimizer.git
cd query-optimizer
docker build -t query-optimizer .
docker run --rm -p 8000:8000 query-optimizer
```

The web UI + API will be available at `http://localhost:8000`.

---

## 🧭 Usage

### API Example

```python
import requests

payload = {
    "query": "SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.status = 'pending'",
    "db_type": "postgresql"
}

resp = requests.post("https://query-optimizer.onrender.com/analyze", json=payload)
print(resp.json())
```

Visit `https://query-optimizer.onrender.com/docs` for interactive API docs (OpenAPI/Swagger).

### CLI Example

```bash
# Analyze queries in a file and output JSON recommendations
query-optimize --file slow_queries.sql --db-type sqlite --output recommendations.json

# Analyze a live DB (requires connection string and proper credentials)
query-optimize --connection "postgresql://user:pass@host:5432/dbname" --analyze-schema --file slow_queries.sql
```

### Python Library

```python
from query_optimizer import QueryOptimizer

optimizer = QueryOptimizer(db_type="postgresql")
result = optimizer.analyze("""
    SELECT u.*, COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id
    HAVING COUNT(o.id) > 10
""")

# programmatic access to recommendations and the optimized query
print(result.recommendations)
print(result.optimized_query)
```

---

## 🧪 Demo

Run the included demo script to see the optimizer in action against a test SQLite DB:

```bash
python demo_optimizer.py
```

What the demo does:

* creates a sample SQLite database
* runs intentionally slow queries
* shows optimization recommendations and SQL to fix them
* (optionally) applies indexes in a sandbox

---

## 📊 Example Output

```json
{
  "original_query": "SELECT * FROM users WHERE email = 'user@example.com'",
  "issues": [
    {
      "type": "missing_index",
      "severity": "high",
      "description": "No index on users.email causing full table scan"
    }
  ],
  "recommendations": [
    {
      "type": "add_index",
      "sql": "CREATE INDEX idx_users_email ON users(email);",
      "impact": "~100x faster for email lookups"
    }
  ],
  "optimized_query": "SELECT id, name, email FROM users WHERE email = 'user@example.com'",
  "estimated_improvement": "95%"
}
```

---

## 🛠️ Development

Clone and set up a dev environment:

```bash
git clone https://github.com/makroumi/query-optimizer.git
cd query-optimizer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
pip install -r requirements.txt
```

### Run tests

```bash
pytest -q
```

Test coverage and linting are included in the CI pipeline. See `.github/workflows` for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m "Add amazing feature"`
4. Push to your branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please follow the project's coding standards and add unit tests for new functionality.

---

## 🏢 Enterprise & Support

* **Free Tier**: 3 API calls/day
* **Pro Tier**: Unlimited calls, priority support — $49/month
* **Enterprise**: Self-hosted, custom adapters, SLA

Contact: `elmehdi.makroumi@gmail.com`

---

## 📄 License

MIT License — see `LICENSE` file in repository.

---

## 🙏 Acknowledgments

Built with frustration-driven development after too many 3am debugging sessions with slow queries. Thanks to the open-source community and many hours of query plan spelunking.

---



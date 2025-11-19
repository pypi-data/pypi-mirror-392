# WaveflowDB SDK Starter

A lightweight launcher script for interacting with **WaveflowDB** and
performing **WaveQL (VQL) brace-based semantic retrieval**.

This starter project demonstrates how to:

-   Configure and initialize a Vector Lake client\
-   Ingest documents (direct or path-based)\
-   Refresh documents\
-   Run semantic chat (static + dynamic)\
-   Retrieve matching documents\
-   Query namespaces\
-   Use WaveQL-style logical filtering for agentic retrieval

------------------------------------------------------------------------

## 📌 Overview

Vector Lake is an unstructured semantic data platform enabling:

-   Natural-language structured filtering through **WaveQL (VQL)**
-   Hybrid ranking (Filter + Semantic)
-   Zero-schema ingestion (no JSON schemas required)
-   SQL-like logical joins on raw text
-   Automatic semantic fallback when filters fail

The included `starter.py` file provides ready-to-run function wrappers
to interact with the Vector Lake API.

------------------------------------------------------------------------

## 🚀 Getting Started

### 1. Install Dependencies

``` bash
pip install waveflowdb-client
```

### 2. Configure API Credentials

Edit the top section of `starter.py`:

``` python
API_KEY = "<<>>"                 
HOST = "https://waveflow-analytics.com"
VECTOR_LAKE_PATH = "<<>>"        
USER_ID = ""                     
NAMESPACE = ""                   
```

------------------------------------------------------------------------

## 🧠 Using WaveQL (VQL) Queries

WaveQL enables natural language filtering using **brace-based logical
groups**:

    {clinical trials or observational studies} {type 2 diabetes} {India}

### Key Rules

✔ Each `{}` is a logical filter group\
✔ Groups combine with implicit AND\
✔ Use `AND`, `OR`, `()` inside braces\
✔ Multi-word phrases **must** use parentheses when operators are used

Examples:

  -------------------------------------------------------------------------------------
  Correct                                     Incorrect
  ------------------------------------------- -----------------------------------------
  `{(machine learning) or (deep learning)}`   `{machine learning or deep learning}`

  `{(product manager) or (data scientist)}`   `{product manager or Delhi}`
  -------------------------------------------------------------------------------------

WaveQL supports **three-tier hybrid ranking**:

1.  Tier 1 -- Filter + Semantic match (best)\
2.  Tier 2 -- Filter-only match\
3.  Tier 3 -- Semantic-only fallback

------------------------------------------------------------------------

## 🧪 Using the Starter Script

The script exposes multiple ready-to-run functions.

### Run Health Check

``` python
run_health()
```

### Add Documents

``` python
run_add_direct()
run_add_path()
```

### Refresh Documents

``` python
run_refresh_direct()
run_refresh_path()
```

### Chat With Documents

``` python
run_chat_static("your question")
run_chat_dynamic("summarize this")
```

### Retrieve Matching Documents

``` python
run_match_static("your query")
run_match_dynamic("your query")
run_match_with_data("your query")
```

### Namespace & Document Inspection

``` python
run_namespace_details()
run_docs_info()
```

------------------------------------------------------------------------

## 🧩 Example WaveQL Queries

-   `{diabetes} {(clinical trial)} {India}`
-   `{(product manager)} {Python} {Delhi}`
-   `{genomics} {cancer}`
-   `{(supply chain)} {pharma}`


## 📝 Tips & Best Practices

### Do:

-   Use 1--2 keywords per brace\
-   Wrap multi-word phrases in `()` when using OR/AND\
-   Keep groups domain-consistent

### Don't:

-   Use long multi-word phrases\
-   Mix unrelated domains\
-   Forget parentheses for multi-word logic

------------------------------------------------------------------------

## 📧 Support

For API or platform support, visit:

**https://db.agentanalytics.ai**

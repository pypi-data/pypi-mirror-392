"""
run.py
Simple launcher for Vector Lake SDK (v1.0.0)

Allows you to:
  - configure client (host, port, key)
  - call ANY API: add, refresh, chat, match, health, namespace info, etc.
"""

from waveflowdb-client import Config, VectorLakeClient


# -------------------------------------------------------
# CONFIGURATION (EDIT THIS ONCE)
# -------------------------------------------------------
API_KEY = "<<>>"  # visit https://db.agentanalytics.ai/signup
HOST = "https://waveflow-analytics.com"       # OR "http://localhost"
VECTOR_LAKE_PATH = "<<>>"       # folder for path-based ingestion
USER_ID = ""   ## your email id used for registratoin
NAMESPACE = ""  ## database created via UI 


# -------------------------------------------------------
# INITIALIZE CLIENT
# -------------------------------------------------------
def get_client():
    cfg = Config(
        api_key=API_KEY,
        host=HOST,
        vector_lake_path=VECTOR_LAKE_PATH
    )
    return VectorLakeClient(cfg)


client = get_client()


# -------------------------------------------------------
# READY-TO-USE ACTION FUNCTIONS
# -------------------------------------------------------

def run_health():
    """Health check"""
    print("\n--- HEALTH CHECK ---")
    res = client.health_check(USER_ID, NAMESPACE)
    print(res)


def run_add_direct():
    """Add docs using files_name + files_data"""
    print("\n--- ADD DOCUMENTS (Direct Payload Mode) ---")
    res = client.add_documents(
        user_id=USER_ID,
        vector_lake_description=NAMESPACE,
        files_name=["test1.txt", "test2.txt"],
        files_data=["hello world", "this is test doc 2"]
    )
    print(res)


def run_add_path():
    """Add docs by reading actual files from disk"""
    print("\n--- ADD DOCUMENTS (Disk Path Mode) ---")
    res = client.add_documents(
        user_id=USER_ID,
        vector_lake_description=NAMESPACE
        # files=[""]   # must exist inside VECTOR_LAKE_PATH
    )
    print(res)


def run_refresh_direct():
    """Refresh docs using direct data (no disk read)"""
    print("\n--- REFRESH DOCUMENTS (Direct Data Mode) ---")
    res = client.refresh_documents(
        user_id=USER_ID,
        vector_lake_description=NAMESPACE,
        files_name=["test1.txt"],
        files_data=["UPDATED CONTENT FOR TEST1"]
    )
    print(res)


def run_refresh_path():
    """Refresh docs by reading actual files"""
    print("\n--- REFRESH DOCUMENTS (Path Mode) ---")
    res = client.refresh_documents(
        user_id=USER_ID,
        vector_lake_description=NAMESPACE
        # files=["file1.pdf"]     # must exist
    )
    print(res)


def run_chat_static(query):
    """Chat with stored index"""
    print("\n--- CHAT (STATIC MODE) ---")
    res = client.chat_with_docs(
        query=query,
        user_id=USER_ID,
        vector_lake_description=NAMESPACE,
        pattern="static"
    )
    print(res)


def run_chat_dynamic(query):
    """Chat using temporary files (dynamic mode)"""
    print("\n--- CHAT (DYNAMIC MODE) ---")
    res = client.chat_with_docs(
        query=query,
        user_id=USER_ID,
        vector_lake_description=NAMESPACE,
        pattern="dynamic",
        files_name=["dyn1.txt"],
        files_data=["This is dynamic content to summarize."]
    )
    print(res)


def run_match_static(query):
    """Top matching docs (static mode)"""
    print("\n--- TOP MATCHING DOCS (STATIC) ---")
    res = client.get_matching_docs(
        query=query,
        user_id=USER_ID,
        vector_lake_description=NAMESPACE,
        pattern="static",
        top_docs=5,
        threshold=0.1
    )
    print(res)


def run_match_dynamic(query):
    """Top matching docs (dynamic mode)"""
    print("\n--- TOP MATCHING DOCS (DYNAMIC) ---")
    res = client.get_matching_docs(
        query=query,
        user_id=USER_ID,
        vector_lake_description=NAMESPACE,
        pattern="dynamic",
        files_name=["temp.txt"],
        files_data=["Sample dynamic content"]
    )
    print(res)


def run_match_with_data(query):
    """Top matching docs including chunk data"""
    print("\n--- TOP MATCHING DOCS (WITH DATA) ---")
    res = client.get_matching_docs(
        query=query,
        user_id=USER_ID,
        vector_lake_description=NAMESPACE,
        pattern="static",
        top_docs=5,
        with_data=True
    )
    print(res)


def run_namespace_details():
    """Get namespace information"""
    print("\n--- GET NAMESPACE DETAILS ---")
    res = client.get_namespace_details(USER_ID, vector_lake_description=NAMESPACE)
    print(res)


def run_docs_info():
    """List all stored docs + info"""
    print("\n--- GET DOCS INFORMATION ---")
    res = client.get_docs_information(USER_ID, NAMESPACE)
    print(res)


# -------------------------------------------------------
# MAIN SELECTOR – RUN ANY FUNCTION YOU WANT
# -------------------------------------------------------
if __name__ == "__main__":
    query="<<>>"
    # --- UNCOMMENT ANY ONE OF THESE TO RUN THAT OPERATION ---
    # run_health()
    # run_add_direct()
    # run_add_path()
    # run_refresh_direct()
    # run_refresh_path()
    # run_chat_static(query)
    # run_chat_dynamic(query)
    # run_match_static(query)
    # run_match_dynamic(query)
    # run_match_with_data(query)
    run_namespace_details()
    # run_docs_info()


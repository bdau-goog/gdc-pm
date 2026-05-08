"""
ingest_manuals.py

Chunks docs/rag_source/*.md manuals by section (## heading), generates embeddings
using all-MiniLM-L6-v2, and loads them into the AlloyDB Omni rag_documents table.

Usage (run once, or after updating any manual):
  PGHOST=<host> PGUSER=<user> PGPASSWORD=<pass> PGDATABASE=grid_reliability \
    python scripts/ingest_manuals.py

Asset class is derived from the filename prefix: 
  esp_manual.md         → asset_class = "esp"
  gas_lift_manual.md    → asset_class = "gas_lift"
  mud_pump_manual.md    → asset_class = "mud_pump"
  top_drive_manual.md   → asset_class = "top_drive"

Convention: filename must end with _manual.md
"""

import os
import glob
import psycopg2

# ── Configuration ─────────────────────────────────────────────────────────────
DB_HOST = os.getenv("PGHOST", "localhost")
DB_USER = os.getenv("PGUSER", "postgres")
DB_PASS = os.getenv("PGPASSWORD", "postgres")
DB_NAME = os.getenv("PGDATABASE", "grid_reliability")


def init_db() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rag_documents (
              id SERIAL PRIMARY KEY,
              asset_class TEXT NOT NULL,
              doc_title TEXT NOT NULL,
              content TEXT NOT NULL,
              embedding vector(384)
            );
        """)
        # Create HNSW index for fast similarity search
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_rag_embedding
              ON rag_documents USING hnsw (embedding vector_cosine_ops);
        """)
        # Clear existing docs for idempotency
        cur.execute("TRUNCATE TABLE rag_documents;")
    return conn


def get_asset_class(filename: str) -> str:
    """
    Derive asset_class from filename by stripping the _manual.md suffix.
    
    Examples:
      esp_manual.md       → "esp"
      gas_lift_manual.md  → "gas_lift"
      mud_pump_manual.md  → "mud_pump"
      top_drive_manual.md → "top_drive"
    """
    basename = os.path.basename(filename)
    if basename.endswith("_manual.md"):
        return basename[: -len("_manual.md")]
    # Fallback: use everything before the first underscore
    return basename.split("_")[0]


def ingest_manuals(conn: psycopg2.extensions.connection) -> None:
    """Chunk manuals by ## headers, embed each section, insert into rag_documents."""
    # Import here to allow the script to run without sentence-transformers installed
    # (it will fail at this point with a clear ImportError rather than silently).
    from sentence_transformers import SentenceTransformer

    print("Loading embedding model all-MiniLM-L6-v2...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Model loaded")

    base_dir = os.path.join(os.path.dirname(__file__), "../docs/rag_source")
    manuals = sorted(glob.glob(f"{base_dir}/*.md"))

    if not manuals:
        print(f"⚠️  No .md files found in {base_dir}")
        return

    total_chunks = 0
    for manual in manuals:
        filename = os.path.basename(manual)
        asset_class = get_asset_class(filename)

        with open(manual, "r") as f:
            content = f.read()

        # Derive doc_title from the H1 heading
        title_chunk = content.split("\n## ")[0]
        doc_title = title_chunk.split("\n")[0].replace("# ", "").strip()

        # Chunk on H2 boundaries
        chunks = content.split("\n## ")
        section_chunks = chunks[1:]  # skip the H1 title block

        print(f"\n[{asset_class}] {doc_title}: {len(section_chunks)} sections")

        with conn.cursor() as cur:
            for chunk in section_chunks:
                section_title = chunk.split("\n")[0].strip()
                full_text = f"## {chunk}"

                # Generate embedding
                embedding = model.encode(full_text).tolist()
                # Format as pgvector literal [x, y, z]
                embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

                cur.execute(
                    """
                    INSERT INTO rag_documents (asset_class, doc_title, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (asset_class, doc_title, full_text, embedding_str),
                )
                print(f"  ✓ {section_title}")
                total_chunks += 1

    print(f"\n✅ Ingestion complete — {total_chunks} chunks loaded from {len(manuals)} manuals")


if __name__ == "__main__":
    print("Connecting to AlloyDB Omni...")
    conn = init_db()
    print(f"✅ Connected to {DB_HOST}/{DB_NAME}")
    ingest_manuals(conn)
    conn.close()

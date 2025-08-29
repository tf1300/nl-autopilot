BEGIN;

CREATE TABLE IF NOT EXISTS detection_runs (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    watermark_hash TEXT NOT NULL,
    is_false_positive BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS evidence_snippets (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES detection_runs(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ipfs_multihash TEXT NOT NULL,
    content_length_bytes BIGINT NOT NULL
);

COMMIT;

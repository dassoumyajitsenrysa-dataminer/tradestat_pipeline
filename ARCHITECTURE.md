# Trade Scraper Pipeline - Visual Architecture

## High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DAILY SCHEDULER (APScheduler)                     │
│                    Runs at 02:00 AM every day                        │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│              DATABASE: HS_CODES.DB (SQLite)                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ hs_code | status | export_status | import_status | error_ct│   │
│  │─────────────────────────────────────────────────────────────│   │
│  │ 61091000| pending  | pending      | pending      | 0      │   │
│  │ 03061710| completed| completed    | completed    | 0      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────┬─────────────────────────────────────────────┘
                       │
                       ▼
       ┌───────────────────────────────┐
       │   GET PENDING HS CODES        │
       │  (O(1) lookup from DB)        │
       └───────────────┬───────────────┘
                       │
                       ▼
       ┌───────────────────────────────┐
       │   BATCH CHUNKER               │
       │  Chunk into groups of 50      │
       └───────────────┬───────────────┘
                       │
       ┌───────────────┴───────────────┐
       │                               │
       ▼                               ▼
   CHUNK 1 (50 codes)             CHUNK 2 (50 codes)
   Parallel Processing            Parallel Processing
   └─ Worker 1                    └─ Worker 3
   └─ Worker 2                    └─ Worker 4


FOR EACH HS CODE:
════════════════════════════════════════════════════════════════════

    ┌─────────────────────────────────────────┐
    │    HS CODE: 61091000                    │
    └──────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼ (PARALLEL)          ▼ (PARALLEL)
    ┌─────────────┐       ┌─────────────┐
    │  EXPORT     │       │   IMPORT    │
    │  SCRAPER    │       │   SCRAPER   │
    └──────┬──────┘       └──────┬──────┘
           │ browser_1           │ browser_2
           │                     │
      ┌────▼────────────────────▼────┐
      │  FORM HANDLER                 │
      │  ├─ Fill HS Code              │
      │  ├─ Select Year               │
      │  └─ Submit Form               │
      └────┬──────────────────────────┘
           │
      ┌────▼──────────────────────────┐
      │  TABLE PARSER                  │
      │  ├─ Extract Headers            │
      │  ├─ Parse Data Rows            │
      │  └─ Get Summary                │
      └────┬──────────────────────────┘
           │
      ┌────▼──────────────────────────┐
      │  SCRAPED RESULT                │
      │  {                             │
      │    status: SUCCESS,            │
      │    metadata: {...},            │
      │    data_by_year: {...}         │
      │  }                             │
      └────┬──────────────────────────┘
           │
    ┌──────┴──────────────────────────┐
    │  STORAGE PIPELINE                │
    │                                  │
    ├─ Raw JSON Writer                │
    │  data/raw/export/2026-01-21/... │
    │  data/raw/import/2026-01-21/... │
    │                                  │
    ├─ Processor                       │
    │  (clean & normalize)             │
    │                                  │
    ├─ Processed JSON Writer           │
    │  data/processed/export/.../...  │
    │  data/processed/import/.../... │
    │                                  │
    ├─ Normalizer                      │
    │  (flatten & index)               │
    │                                  │
    └─ Database Update                │
       └─ Mark as completed           │
       └─ Update timestamps           │
```

---

## Component Details

### 1. SCHEDULER (daily_scheduler.py)
```
Function: Run batch scraping at specified time daily
Input: Time (e.g., 02:00)
Output: Triggers batch_runner
Config: APScheduler with cron job
```

### 2. BATCH RUNNER (engine/batch_runner.py)
```
Function: Orchestrate scraping pipeline
Steps:
  1. Load pending HS codes from DB
  2. Split into chunks (50 codes/chunk)
  3. Create 4 parallel workers
  4. Coordinate and track progress
```

### 3. WORKER (pipeline/worker.py)
```
For each HS code:
  1. Run export & import scraping IN PARALLEL
  2. Save raw JSON
  3. Process/clean data
  4. Save processed JSON
  5. Normalize for indexing
  6. Update database status
```

### 4. SCRAPER CONTROLLER (scraper/controller.py)
```
Single Playwright browser instance
Uses appropriate selectors (export/import)
Handles pagination
Extracts data
Returns structured result
```

### 5. STORAGE (storage/)
```
json_writer.py      → Write JSON to disk
processor.py        → Clean & normalize data
normalizer.py       → Flatten for indexing
```

### 6. DATABASE (utils/hs_code_db.py)
```
Tracks:
  - Which HS codes are pending
  - Which are completed
  - Export vs Import status separately
  - Error counts & messages
  - Last scraped timestamp
```

---

## Processing Speed

```
Single HS Code: 75 seconds
├─ Export scrape: 35 sec
├─ Import scrape: 35 sec (parallel)
├─ Storage/Processing: 5 sec
└─ Total: ~75 sec

Per Chunk (50 codes): 
├─ Time: 75 sec × 50 = 3,750 sec
├─ But PARALLEL workers: 3,750 / 4 ≈ 938 sec (15.6 min)
└─ Actual: ~20 min (with overhead)

Total for 10,000 codes:
├─ Chunks: 10,000 / 50 = 200 chunks
├─ Time: 200 × 20 min = 4,000 min
└─ ≈ 67 hours (2.8 days at 4 workers)
```

---

## Error Handling & Recovery

```
┌─ Scraper Error
├─ Log error
├─ Mark HS as failed
├─ Increment error_count
├─ Continue to next
└─ Retry tomorrow (via pending status)

┌─ Storage Error
├─ Rollback (remove partial files)
├─ Log error
├─ Mark as failed
└─ Retry tomorrow

┌─ Network Error
├─ Timeout handling
├─ Auto-retry with backoff
├─ Max retries: 3
└─ Mark failed if all retries exhausted
```

---

## Database Schema

```sql
CREATE TABLE hs_codes (
    hs_code TEXT PRIMARY KEY,
    status TEXT (pending|completed|failed),
    last_scraped_at TIMESTAMP,
    
    export_status TEXT,
    export_scraped_at TIMESTAMP,
    
    import_status TEXT,
    import_scraped_at TIMESTAMP,
    
    error_count INTEGER,
    last_error TEXT
)
```

---

## Data Directory Structure

```
data/
├── raw/                          # Original scraped data
│   ├── export/2026-01-21/
│   │   └── HS_61091000.json
│   └── import/2026-01-21/
│       └── HS_61091000.json
│
├── processed/                     # Cleaned & processed
│   ├── export/2026-01-21/
│   │   └── HS_61091000.json
│   └── import/2026-01-21/
│       └── HS_61091000.json
│
├── normalized/                    # Flattened for indexing
│   ├── v1/2026-01-21/
│   │   └── HS_61091000.json
│
├── logs/                          # Execution logs
│   └── pipeline_*.log
│
├── hs_codes.db                    # Progress tracking
│
└── failed/                        # Failed items for review
    └── HS_codes_failed.json
```


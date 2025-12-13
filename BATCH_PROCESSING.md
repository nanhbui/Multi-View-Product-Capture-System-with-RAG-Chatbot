# Batch Processing Guide

## Overview

The chatbot now supports **batch processing** of all unprocessed sessions in the `captured_images/` folder, not just the latest one.

## How It Works

When you run the chatbot, it will:

1. **Scan** all subdirectories in `captured_images/`
2. **Check** which sessions are already processed in MongoDB
3. **List** unprocessed sessions
4. **Ask** if you want to process all of them
5. **Process** each one sequentially with GPT-4o Vision
6. **Initialize** vector store with all data
7. **Start** chatbot ready to answer questions about ALL products

## Usage

### Interactive Mode (Default)

```bash
uv run python phase_2/run_chatbot.py
```

**Output:**
```
[INFO] Auto-detecting metadata files...
[INFO] Found 6 session(s) in captured_images/
   ○ 20251209_102617 - Not yet processed
   ○ 20251213_081830 - Not yet processed
   ○ 20251213_082128 - Not yet processed
   ○ 20251213_082719 - Not yet processed
   ○ 20251213_082835 - Not yet processed
   ○ 20251213_082930 - Not yet processed

[SUMMARY] Processed: 0, Unprocessed: 6

[INFO] Found 6 unprocessed session(s)
Process all 6 unprocessed sessions? [Y/n]:
```

Type **Y** and press Enter to process all.

### Automatic Mode (No Prompt)

```bash
uv run python phase_2/run_chatbot.py --process-all
```

This will automatically process all unprocessed sessions without asking for confirmation.

### Process Only Specific Session

```bash
uv run python phase_2/run_chatbot.py --process-metadata captured_images/20251213_082930/metadata.json
```

## Processing Status Indicators

- `✓ 20251213_082930 - Already processed` → Skipped (already in MongoDB)
- `○ 20251213_081830 - Not yet processed` → Will be processed

## What Gets Processed

For each unprocessed session, the system:

1. **Reads** metadata.json with capture info
2. **Loads** all 3 angle images (angle_1.jpg, angle_2.jpg, angle_3.jpg)
3. **Sends** to GPT-4o Vision for analysis
4. **Extracts** product features:
   - Product type
   - Colors, materials, shape
   - Text/brand identification
   - Size, condition, notable features
5. **Runs** Multi-View Verification
6. **Saves** ProductRecord to MongoDB
7. **Creates** embeddings for vector search

**Time:** ~15-30 seconds per session (depends on OpenAI API response time)

## After Processing

Once all sessions are processed:

```
[SUCCESS] Vector store initialized with 6 documents

============================================================
STARTING RAG CHATBOT
============================================================
Product Context: Product X - Multi-angle captured products
Model: gpt-4o-mini

Type your questions below. Type 'quit' or 'exit' to end the session.
============================================================

You:
```

Now you can ask questions about **ANY** of the captured products:

```
You: show me all the products you have

You: what are the red products?

You: which product had the highest detection confidence?

You: describe the product from session 20251213_082930
```

## Incremental Processing

The system remembers what's already processed:

**First run:**
```
[SUMMARY] Processed: 0, Unprocessed: 6
Process all 6 unprocessed sessions? [Y/n]: Y
→ Processes all 6 sessions
```

**Second run (after capturing 2 more products):**
```
[SUMMARY] Processed: 6, Unprocessed: 2
Process all 2 unprocessed sessions? [Y/n]: Y
→ Only processes the 2 new sessions
```

**Third run (no new captures):**
```
[SUMMARY] Processed: 8, Unprocessed: 0

[INFO] All sessions already processed!
→ Skips directly to chatbot
```

## Reprocessing

To force reprocessing of a specific session:

```bash
# 1. Delete from MongoDB first
mongosh product_capture_db --eval 'db.captures.deleteOne({session_id: "20251213_082930"})'

# 2. Run chatbot - it will detect as unprocessed
uv run python phase_2/run_chatbot.py
```

## Vector Store Management

### Automatic Initialization

Vector store is automatically initialized when:
- New sessions are processed
- You use `--reinitialize-vector-store` flag

### Manual Reinitialization

If vector store seems out of sync:

```bash
uv run python phase_2/run_chatbot.py --reinitialize-vector-store
```

This rebuilds the vector store from **all** ProductRecords in MongoDB.

## Command Reference

```bash
# Process all unprocessed sessions (interactive)
uv run python phase_2/run_chatbot.py

# Process all automatically (no prompt)
uv run python phase_2/run_chatbot.py --process-all

# Process specific session only
uv run python phase_2/run_chatbot.py --process-metadata path/to/metadata.json

# Rebuild vector store from MongoDB
uv run python phase_2/run_chatbot.py --reinitialize-vector-store

# Skip chatbot, just process and exit
# (not implemented yet - chatbot always starts after processing)
```

## Cost Considerations

**OpenAI API Costs:**
- GPT-4o Vision: ~$0.01-0.02 per session (3 images)
- text-embedding-3-small: ~$0.0001 per session
- GPT-4o-mini (chatbot): ~$0.001 per query

**Processing 10 sessions:**
- Total: ~$0.10-0.20

**Recommendation:** Start with a few test captures, verify quality, then batch process all.

## Troubleshooting

### "All sessions already processed" but chatbot has no data

**Cause:** Sessions are in MongoDB but vector store not initialized.

**Solution:**
```bash
uv run python phase_2/run_chatbot.py --reinitialize-vector-store
```

### Processing fails midway through batch

**What happens:** Partially processed sessions are already saved to MongoDB.

**Resume processing:**
```bash
# Just run again - it will skip completed sessions
uv run python phase_2/run_chatbot.py
```

### Want to see raw MongoDB data

```bash
mongosh product_capture_db --eval 'db.captures.find().pretty()'
```

### Check which sessions are processed

```bash
uv run python test_vectorstore.py
# Shows processed vs unprocessed sessions
```

## Examples

### Scenario 1: First Time Setup

```bash
# You have 10 captured sessions
uv run python phase_2/run_chatbot.py --process-all

# Processes all 10, then starts chatbot
You: what products do I have?
```

### Scenario 2: Daily Usage

```bash
# Day 1: Capture 5 products
uv run python phase_1/capture_system.py
# (capture 5 sessions)

# Process them
uv run python phase_2/run_chatbot.py --process-all

# Day 2: Capture 3 more products
uv run python phase_1/capture_system.py
# (capture 3 sessions)

# Process only the new ones
uv run python phase_2/run_chatbot.py
# Shows: Processed: 5, Unprocessed: 3
```

### Scenario 3: Quality Check Before Batch

```bash
# Process just one session to test
uv run python phase_2/run_chatbot.py --process-metadata captured_images/20251213_082930/metadata.json

# Ask questions to verify quality
You: what is this product?
You: is the description accurate?

# If good, process the rest
uv run python phase_2/run_chatbot.py --process-all
```

---

**See also:**
- [QUICK_START.md](QUICK_START.md) - Basic usage
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Technical details

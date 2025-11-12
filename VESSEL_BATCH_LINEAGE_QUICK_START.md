# Vessel-Batch Lineage Analysis Quick Reference

## What is this?

A tool to track which vessel-batches contributed gallons to any final batch. When you select a lot in Power BI or other reporting tools, you can see all transactions and batches that were involved in creating that final product.

## Quick Start

### 1. Prepare Your Data

Ensure you have these files (these are created by other fetch scripts):
```
Main/data/GET--transaction-search/Transaction_to_analysise.csv
Main/data/GET--vessels/vessels.json
Main/data/GET--shipments/shipments_thin.json
```

### 2. Run the Analysis

```bash
# Standalone
python tools/vessel_batch_lineage_analysis.py

# With Docker
docker-compose exec api bash
export PYTHONPATH=/app
python tools/vessel_batch_lineage_analysis.py
```

### 3. View Results

Output files are created in `Main/data/vessel-batch-lineage/`:
- `batch_lineage_transactions.csv` - Power BI ready transaction details
- `batch_lineage_summary.csv` - Power BI ready batch summary
- `batch_lineage_complete.json` - Complete lineage data
- `batch_lineage_final.json` - Final batches only
- `analysis_summary.json` - Statistics

## Key Concept: 4 Batches Per Transaction

Each transaction has 4 batches that create lineage:
```
Source Vessel Pre Batch  →  Source Vessel Post Batch
       ↓
Destination Vessel Post Batch  ←  Destination Vessel Pre Batch
```

Example:
```
From Pre:  PCAS00250001  →  From Post: PCAS00250002
    ↓
To Post:   PCAS00250003
```

This creates the lineage: `PCAS00250001 → PCAS00250002 → PCAS00250003`

## Power BI Usage

1. Import `batch_lineage_transactions.csv` and `batch_lineage_summary.csv`
2. Link to your existing batch/lot tables using the `Batch` field
3. Create visualizations:
   - **Lineage Tree**: Show ancestor/descendant relationships
   - **Volume Flow**: Track volume changes across batches
   - **Loss Analysis**: Analyze loss/gain reasons

Example DAX:
```dax
Total Ancestors = SUM('batch_lineage_summary'[Ancestor_Count])
Total Volume Transferred = SUM('batch_lineage_transactions'[Dest_Vol_Change])
```

## Need More Help?

- **Full Documentation**: `tools/VESSEL_BATCH_LINEAGE_README.md`
- **Examples**: `tools/examples/vessel_batch_lineage_examples.py`
- **Tool Organization**: `tools/README_TOOLS_ORGANIZATION.md`

## Common Questions

**Q: Why are some batches not showing lineage?**  
A: The batch may not have any transactions in the CSV, or it may be a starting batch with no ancestors.

**Q: Can I filter by date range?**  
A: Yes! See examples in `tools/examples/vessel_batch_lineage_examples.py` (Example 4)

**Q: How do I find which batches contributed to lot XYZ?**  
A: Filter `batch_lineage_summary.csv` by `Batch = "XYZ"` and view the `Ancestor_Batches` column.

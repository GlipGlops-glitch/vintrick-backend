# Vessel-Batch Lineage Analysis Tool

## Overview

This tool analyzes vessel-batch transaction history to determine which vessel-batches contributed gallons to any final vessel-batch. It creates a complete lineage map showing all transactions that affected a particular batch, making it easy to trace the origin of gallons in any given batch.

## Purpose

When you have a final batch (either currently on-hand in a vessel or already bottled/shipped), this tool allows you to:

1. **Trace all contributing batches**: See every batch that contributed gallons to the final state
2. **View transaction details**: Get detailed information about every transaction involved
3. **Analyze lineage relationships**: Understand the flow of gallons through the production process
4. **Report in Power BI**: Export data in formats ready for Power BI visualization

## How It Works

### Understanding Batch Lineage

Each transaction in the system has **4 batches**:
- **Src Batch Pre**: The source vessel's batch before the transaction
- **Src Batch Post**: The source vessel's batch after the transaction
- **Dest Batch Pre**: The destination vessel's batch before the transaction
- **Dest Batch Post**: The destination vessel's batch after the transaction

These 4 batches create lineage relationships:

1. **Batch Evolution in Source**: `Src Batch Pre → Src Batch Post`
   - The batch number may change in the source vessel after gallons are removed

2. **Transfer**: `Src Batch Pre → Dest Batch Post`
   - Gallons from the source batch go into the destination batch

3. **Batch Evolution in Destination**: `Dest Batch Pre → Dest Batch Post`
   - The batch number may change in the destination vessel after receiving gallons

### Example

Given a transaction with these batches:
```
From vessel Pre Batch:  PCAS00250001
From vessel Post Batch: PCAS00250002
To Vessel Pre Batch:    PCAS00250003
To Vessel Post Batch:   PCAS00250003
```

The lineage created is:
- `PCAS00250001 → PCAS00250002` (batch evolved in source vessel)
- `PCAS00250001 → PCAS00250003` (gallons transferred)

If another transaction then moves `PCAS00250002` into `PCAS00250003`, the complete lineage becomes:
- `PCAS00250001 → PCAS00250002 → PCAS00250003`

This means that batch `PCAS00250003` contains gallons that originated from both versions of batch `PCAS00250001`.

## Input Files

The tool requires three data files:

### 1. Transaction History CSV
**Path**: `Main/data/GET--transaction-search/Transaction_to_analysise.csv`

This CSV contains all vessel transactions with the following tracked fields:
- `Op Date`: Operation date
- `Tx Id`: Transaction ID
- `Op Id`: Operation ID
- `Op Type`: Type of operation (Transfer, Blend, Adjustment, etc.)
- `Txn Type`: Transaction type
- `Src Batch Pre`: Source vessel batch before transaction
- `Src Batch Post`: Source vessel batch after transaction
- `Dest Batch Pre`: Destination vessel batch before transaction
- `Dest Batch Post`: Destination vessel batch after transaction
- `Src Vol Change`: Volume change in source vessel
- `Dest Vol Change`: Volume change in destination vessel
- `Loss/Gain Amount (gal)`: Loss or gain amount in gallons
- `Loss/Gain Reason`: Reason for loss/gain
- `Src Vessel`: Source vessel ID
- `Dest Vessel`: Destination vessel ID
- `Work Order`: Work order number
- `Operator`: Operator name

### 2. Current Vessels JSON
**Path**: `Main/data/GET--vessels/vessels.json`

Contains current on-hand vessel inventory with batch information.

### 3. Shipments JSON
**Path**: `Main/data/GET--shipments/shipments_thin.json`

Contains information about batches that have been bottled or shipped out.

## Usage

### Basic Usage

```bash
# From the repository root
python tools/vessel_batch_lineage_analysis.py
```

### Using with Docker

```bash
docker-compose up
docker-compose exec api bash
export PYTHONPATH=/app
python tools/vessel_batch_lineage_analysis.py
```

## Output Files

The tool generates several output files in `Main/data/vessel-batch-lineage/`:

### 1. `batch_lineage_complete.json`
Complete lineage information for ALL batches found in the transaction history.

Structure:
```json
{
  "PCAS00250001": {
    "batch": "PCAS00250001",
    "ancestor_batches": ["PCAS00240005", "PCAS00240006"],
    "descendant_batches": ["PCAS00250002", "PCAS00250003"],
    "ancestor_count": 2,
    "descendant_count": 2,
    "transaction_count": 5,
    "transactions": [
      {
        "tx_id": "238915",
        "op_id": "224808",
        "op_date": "9/1/2025 1:24",
        "op_type": "Measurement",
        "txn_type": "ADJUSTMENT",
        "src_vol_change": -601,
        "dest_vol_change": -601,
        "loss_gain_amount": -601,
        "loss_gain_reason": "Dump Lees",
        "relationship": "parent",
        "related_batch": "PCAS00250002"
      }
    ]
  }
}
```

### 2. `batch_lineage_final.json`
Lineage information for ONLY batches that are currently on-hand or have been shipped.

Same structure as `batch_lineage_complete.json`, but filtered to final batches.

### 3. `batch_lineage_transactions.csv`
Power BI ready CSV with one row per transaction per batch.

Columns:
- `Batch`: The batch being tracked
- `Related_Batch`: The batch related through this transaction
- `Relationship`: Either "parent" (contributed to this batch) or "child" (this batch contributed to)
- `Tx_Id`: Transaction ID
- `Op_Id`: Operation ID
- `Op_Date`: Operation date
- `Op_Type`: Operation type
- `Txn_Type`: Transaction type
- `Src_Vessel`: Source vessel
- `Dest_Vessel`: Destination vessel
- `Src_Vol_Change`: Source volume change
- `Dest_Vol_Change`: Destination volume change
- `Loss_Gain_Amount_Gal`: Loss/gain in gallons
- `Loss_Gain_Reason`: Reason for loss/gain
- `Work_Order`: Work order number
- `Operator`: Operator name
- `Ancestor_Count`: Total number of ancestor batches
- `Descendant_Count`: Total number of descendant batches

### 4. `batch_lineage_summary.csv`
Summary CSV with one row per batch showing all ancestors and descendants.

Columns:
- `Batch`: The batch ID
- `Ancestor_Batches`: Comma-separated list of all ancestor batch IDs
- `Ancestor_Count`: Number of ancestor batches
- `Descendant_Batches`: Comma-separated list of all descendant batch IDs
- `Descendant_Count`: Number of descendant batches
- `Transaction_Count`: Number of transactions involving this batch

### 5. `analysis_summary.json`
Summary statistics about the analysis.

```json
{
  "analysis_timestamp": "2025-11-12T19:32:00.000000",
  "total_batches_analyzed": 1500,
  "final_batches_tracked": 350,
  "total_transactions": 5000,
  "lineage_statistics": {
    "batches_with_ancestors": 1200,
    "batches_with_descendants": 1100,
    "max_ancestors": 15,
    "max_descendants": 20,
    "avg_ancestors": 3.5,
    "avg_descendants": 4.2
  }
}
```

## Power BI Integration

### Recommended Approach

1. **Import the CSV files** into Power BI:
   - `batch_lineage_transactions.csv` - For detailed transaction analysis
   - `batch_lineage_summary.csv` - For high-level batch relationships

2. **Create relationships** between tables:
   - Link `Batch` field to your existing batch/lot tables
   - Link `Tx_Id` to transaction tables if available

3. **Build visualizations**:
   - **Lineage Tree**: Use the summary CSV to show ancestor/descendant relationships
   - **Transaction Timeline**: Use the transactions CSV to show when and how batches were created
   - **Volume Flow**: Track `Src_Vol_Change` and `Dest_Vol_Change` to see gallon movements
   - **Loss Analysis**: Analyze `Loss_Gain_Amount_Gal` and `Loss_Gain_Reason`

### Example DAX Measures

```dax
// Total Ancestor Batches
Total Ancestors = SUM('batch_lineage_summary'[Ancestor_Count])

// Total Descendant Batches
Total Descendants = SUM('batch_lineage_summary'[Descendant_Count])

// Total Volume Transferred
Total Volume Transferred = SUM('batch_lineage_transactions'[Dest_Vol_Change])

// Total Loss/Gain
Total Loss Gain = SUM('batch_lineage_transactions'[Loss_Gain_Amount_Gal])
```

### Sample Power BI Questions Answered

1. **"For lot XYZ, what are all the batches that contributed to it?"**
   - Filter `batch_lineage_summary` by `Batch = "XYZ"`
   - Display `Ancestor_Batches` field

2. **"Show me all transactions involved in creating lot XYZ"**
   - Filter `batch_lineage_transactions` by `Batch = "XYZ"` and `Relationship = "child"`
   - Display all transaction fields

3. **"What was the total volume transferred into lot XYZ?"**
   - Filter `batch_lineage_transactions` by `Batch = "XYZ"` and `Relationship = "child"`
   - Sum `Dest_Vol_Change`

4. **"Which lots did batch ABC contribute to?"**
   - Filter `batch_lineage_summary` by `Batch = "ABC"`
   - Display `Descendant_Batches` field

## Technical Details

### Algorithm

The tool uses a **Breadth-First Search (BFS)** algorithm to trace lineage:

1. **Build Graph**: Creates a directed graph where edges represent batch lineage
2. **Trace Ancestors**: For each batch, traverse backwards to find all contributing batches
3. **Trace Descendants**: For each batch, traverse forwards to find all resulting batches
4. **Store Transactions**: Associates each lineage relationship with transaction details

### Performance

- Handles thousands of batches and transactions efficiently
- Uses defaultdict and sets for O(1) lookups
- BFS with depth limit prevents infinite loops in circular references

### Data Integrity

- Handles missing/null batch values gracefully
- Filters out placeholder values like "--"
- Preserves all transaction metadata for traceability

## Troubleshooting

### Common Issues

**1. File Not Found Error**
```
ERROR: Transaction CSV not found: Main/data/...
```
**Solution**: Ensure the input files exist in the correct directories. You may need to run the fetch scripts first to generate these files.

**2. Empty Output**
```
Found 0 final batches
```
**Solution**: Check that your vessels.json and shipments_thin.json files contain batch information. The tool looks for fields named `batch`, `batchNumber`, or `batchNo`.

**3. No Lineage Found**
```
Total batches analyzed: 0
```
**Solution**: Verify that your Transaction_to_analysise.csv has the correct column names: `Src Batch Pre`, `Src Batch Post`, `Dest Batch Pre`, `Dest Batch Post`.

## Extending the Tool

### Adding Custom Fields

To track additional fields from the transaction CSV:

1. Edit the `build_lineage_graph()` method
2. Add fields to the `txn_info` dictionary
3. Add corresponding columns to `_generate_powerbi_csv()` method

### Changing Output Format

Modify the `_generate_powerbi_csv()` method to customize the CSV structure.

### Advanced Filtering

Add filters in the `main()` function to analyze specific date ranges, vessels, or batch types.

## Support

For issues or questions:
1. Check the log output for error messages
2. Verify input file formats match the expected structure
3. Review the `analysis_summary.json` for insights into what was processed

## Version History

- **v1.0** (2025-11-12): Initial release
  - Complete batch lineage tracking
  - Power BI ready outputs
  - Transaction detail preservation
  - Summary statistics

#!/usr/bin/env python3
"""
Example: Using the Vessel-Batch Lineage Analyzer

This script demonstrates how to use the VesselBatchLineageAnalyzer class
with custom parameters and how to query specific batches.
"""

import sys
import os

# Add parent directory to path to import vessel_batch_lineage_analysis
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vessel_batch_lineage_analysis import VesselBatchLineageAnalyzer


def example_basic_usage():
    """Example 1: Basic usage with default file paths"""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    analyzer = VesselBatchLineageAnalyzer()
    
    # Load data
    analyzer.load_transactions_csv("Main/data/GET--transaction-search/Transaction_to_analysise.csv")
    analyzer.load_vessels_json("Main/data/GET--vessels/vessels.json")
    analyzer.load_shipments_json("Main/data/GET--shipments/shipments_thin.json")
    
    # Build lineage
    analyzer.extract_final_batches()
    analyzer.build_lineage_graph()
    
    # Generate reports
    analyzer.generate_lineage_report("Main/data/vessel-batch-lineage")
    
    print("\n✅ Reports generated successfully!")


def example_query_specific_batch():
    """Example 2: Query lineage for a specific batch"""
    print("\n" + "=" * 60)
    print("Example 2: Query Specific Batch")
    print("=" * 60)
    
    analyzer = VesselBatchLineageAnalyzer()
    
    # Load data
    analyzer.load_transactions_csv("Main/data/GET--transaction-search/Transaction_to_analysise.csv")
    analyzer.load_vessels_json("Main/data/GET--vessels/vessels.json")
    analyzer.load_shipments_json("Main/data/GET--shipments/shipments_thin.json")
    
    # Build lineage
    analyzer.extract_final_batches()
    analyzer.build_lineage_graph()
    
    # Query a specific batch
    batch_to_query = "PCAS00260001"
    
    if batch_to_query in analyzer.batch_to_children or batch_to_query in analyzer.batch_to_parents:
        lineage = analyzer.get_batch_lineage(batch_to_query)
        
        print(f"\nLineage for batch: {batch_to_query}")
        print(f"  Ancestor batches: {lineage['ancestor_batches']}")
        print(f"  Descendant batches: {lineage['descendant_batches']}")
        print(f"  Total transactions: {lineage['transaction_count']}")
        
        # Show contributing batches
        contributors = analyzer.get_all_contributing_batches(batch_to_query)
        print(f"\n  All batches that contributed to {batch_to_query}:")
        for contributor in contributors:
            print(f"    - {contributor}")
    else:
        print(f"\n⚠️  Batch {batch_to_query} not found in transaction history")


def example_find_batches_with_most_ancestors():
    """Example 3: Find batches with the most complex lineage"""
    print("\n" + "=" * 60)
    print("Example 3: Find Batches with Most Ancestors")
    print("=" * 60)
    
    analyzer = VesselBatchLineageAnalyzer()
    
    # Load data
    analyzer.load_transactions_csv("Main/data/GET--transaction-search/Transaction_to_analysise.csv")
    analyzer.load_vessels_json("Main/data/GET--vessels/vessels.json")
    analyzer.load_shipments_json("Main/data/GET--shipments/shipments_thin.json")
    
    # Build lineage
    analyzer.extract_final_batches()
    analyzer.build_lineage_graph()
    
    # Find batches with most ancestors
    all_batches = set(analyzer.batch_to_children.keys()) | set(analyzer.batch_to_parents.keys())
    batch_lineages = []
    
    for batch in all_batches:
        lineage = analyzer.get_batch_lineage(batch)
        batch_lineages.append((batch, lineage['ancestor_count'], lineage['descendant_count']))
    
    # Sort by ancestor count
    batch_lineages.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop 5 batches with most ancestors:")
    for i, (batch, ancestor_count, descendant_count) in enumerate(batch_lineages[:5], 1):
        print(f"  {i}. {batch}: {ancestor_count} ancestors, {descendant_count} descendants")


def example_filter_by_date_range():
    """Example 4: Filter transactions by date range (conceptual)"""
    print("\n" + "=" * 60)
    print("Example 4: Working with Transaction Dates")
    print("=" * 60)
    
    analyzer = VesselBatchLineageAnalyzer()
    
    # Load data
    analyzer.load_transactions_csv("Main/data/GET--transaction-search/Transaction_to_analysise.csv")
    analyzer.load_vessels_json("Main/data/GET--vessels/vessels.json")
    analyzer.load_shipments_json("Main/data/GET--shipments/shipments_thin.json")
    
    # You can filter transactions before building the graph
    # For example, keep only transactions from September 2025
    original_count = len(analyzer.transactions)
    
    analyzer.transactions = [
        txn for txn in analyzer.transactions
        if '9/' in str(txn.get('Op Date', ''))
    ]
    
    print(f"\nFiltered transactions: {len(analyzer.transactions)} (from {original_count})")
    
    # Build lineage with filtered data
    analyzer.extract_final_batches()
    analyzer.build_lineage_graph()
    
    print(f"Unique batches after filtering: {len(set(analyzer.batch_to_children.keys()) | set(analyzer.batch_to_parents.keys()))}")


def example_get_transaction_details():
    """Example 5: Get all transaction details for a specific batch"""
    print("\n" + "=" * 60)
    print("Example 5: Get Transaction Details for a Batch")
    print("=" * 60)
    
    analyzer = VesselBatchLineageAnalyzer()
    
    # Load data
    analyzer.load_transactions_csv("Main/data/GET--transaction-search/Transaction_to_analysise.csv")
    analyzer.load_vessels_json("Main/data/GET--vessels/vessels.json")
    analyzer.load_shipments_json("Main/data/GET--shipments/shipments_thin.json")
    
    # Build lineage
    analyzer.extract_final_batches()
    analyzer.build_lineage_graph()
    
    # Get transaction details
    batch_to_query = "PCAS00250003"
    
    if batch_to_query in analyzer.batch_to_transactions:
        transactions = analyzer.batch_to_transactions[batch_to_query]
        
        print(f"\nAll transactions involving batch: {batch_to_query}")
        print(f"Total: {len(transactions)} transactions\n")
        
        for i, txn in enumerate(transactions[:3], 1):  # Show first 3
            print(f"Transaction {i}:")
            print(f"  Op Date: {txn.get('op_date')}")
            print(f"  Op Type: {txn.get('op_type')}")
            print(f"  Relationship: {txn.get('relationship')}")
            print(f"  Related Batch: {txn.get('related_batch')}")
            print(f"  Volume Change: Src={txn.get('src_vol_change')}, Dest={txn.get('dest_vol_change')}")
            print()
        
        if len(transactions) > 3:
            print(f"  ... and {len(transactions) - 3} more transactions")
    else:
        print(f"\n⚠️  No transactions found for batch {batch_to_query}")


if __name__ == "__main__":
    # Run all examples
    try:
        example_basic_usage()
        example_query_specific_batch()
        example_find_batches_with_most_ancestors()
        example_filter_by_date_range()
        example_get_transaction_details()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: Could not find input file: {e}")
        print("\nMake sure you have the required data files:")
        print("  - Main/data/GET--transaction-search/Transaction_to_analysise.csv")
        print("  - Main/data/GET--vessels/vessels.json")
        print("  - Main/data/GET--shipments/shipments_thin.json")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

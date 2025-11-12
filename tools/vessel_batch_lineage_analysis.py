#!/usr/bin/env python3
"""
Vessel-Batch Lineage Analysis Tool

This script analyzes vessel-batch transaction history to determine which vessel-batches
contributed gallons to a final vessel-batch. It creates a complete lineage map showing
all transactions that affected a particular batch.

Usage:
    python tools/vessel_batch_lineage_analysis.py

Input files:
    - Main/data/GET--vessels/vessels.json (current on-hand gallons)
    - Main/data/GET--shipments/shipments_thin.json (bottled/shipped out)
    - Main/data/GET--transaction-search/Transaction_to_analysise.csv (all transactions)

Output:
    - Main/data/vessel-batch-lineage/batch_lineage.json
    - Main/data/vessel-batch-lineage/batch_lineage_detailed.json
    - Main/data/vessel-batch-lineage/batch_lineage.csv (Power BI ready)

The analysis considers that each transaction has 4 batches:
    - From Vessel Pre Batch
    - From Vessel Post Batch
    - To Vessel Pre Batch
    - To Vessel Post Batch

This creates lineage mappings like:
    PCAS00250001 -> PCAS00250002 -> PCAS00250003
"""

import os
import json
import csv
import logging
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Any, Optional
from datetime import datetime
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class VesselBatchLineageAnalyzer:
    """
    Analyzes vessel-batch transaction lineage to track gallons flow through batches.
    """
    
    def __init__(self):
        self.transactions: List[Dict[str, Any]] = []
        self.vessels: List[Dict[str, Any]] = []
        self.shipments: List[Dict[str, Any]] = []
        
        # Graph structures for lineage tracking
        # batch -> list of batches that came from it
        self.batch_to_children: Dict[str, List[str]] = defaultdict(list)
        # batch -> list of batches that went into it
        self.batch_to_parents: Dict[str, List[str]] = defaultdict(list)
        # batch -> list of transaction details
        self.batch_to_transactions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Final batches (currently on-hand or shipped)
        self.final_batches: Set[str] = set()
        
    def load_transactions_csv(self, csv_path: str) -> None:
        """Load transaction data from CSV file."""
        logger.info(f"Loading transactions from {csv_path}")
        
        if not os.path.exists(csv_path):
            logger.error(f"Transaction CSV not found: {csv_path}")
            return
            
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} transaction records")
        
        # Convert DataFrame to list of dicts
        self.transactions = df.to_dict('records')
        
    def load_vessels_json(self, json_path: str) -> None:
        """Load current vessel data from JSON file."""
        logger.info(f"Loading vessels from {json_path}")
        
        if not os.path.exists(json_path):
            logger.warning(f"Vessels JSON not found: {json_path}")
            return
            
        with open(json_path, 'r', encoding='utf-8') as f:
            self.vessels = json.load(f)
            
        logger.info(f"Loaded {len(self.vessels)} vessel records")
        
    def load_shipments_json(self, json_path: str) -> None:
        """Load shipment data from JSON file."""
        logger.info(f"Loading shipments from {json_path}")
        
        if not os.path.exists(json_path):
            logger.warning(f"Shipments JSON not found: {json_path}")
            return
            
        with open(json_path, 'r', encoding='utf-8') as f:
            self.shipments = json.load(f)
            
        logger.info(f"Loaded {len(self.shipments)} shipment records")
        
    def extract_final_batches(self) -> None:
        """
        Extract final batches from vessels (on-hand) and shipments (shipped out).
        """
        logger.info("Extracting final batches from vessels and shipments")
        
        # Extract from vessels (current on-hand)
        for vessel in self.vessels:
            # Try different possible field names for batch
            batch = vessel.get('batch') or vessel.get('batchNumber') or vessel.get('batchNo')
            if batch and str(batch).strip() and str(batch).strip() != '--':
                self.final_batches.add(str(batch).strip())
        
        # Extract from shipments (bottled/shipped)
        for shipment in self.shipments:
            # Try different possible field names for batch
            batch = (shipment.get('batch') or 
                    shipment.get('batchNumber') or 
                    shipment.get('batchNo') or
                    shipment.get('sourceBatch'))
            if batch and str(batch).strip() and str(batch).strip() != '--':
                self.final_batches.add(str(batch).strip())
                
        logger.info(f"Found {len(self.final_batches)} final batches")
        
    def build_lineage_graph(self) -> None:
        """
        Build the lineage graph from transaction data.
        
        Each transaction has 4 batches that create lineage relationships:
        - Src Batch Pre -> Src Batch Post (batch evolution in source vessel)
        - Src Batch Pre -> Dest Batch Post (gallons transferred)
        - Dest Batch Pre -> Dest Batch Post (batch evolution in destination vessel)
        """
        logger.info("Building lineage graph from transactions")
        
        for idx, txn in enumerate(self.transactions):
            # Extract batch information
            src_pre = self._get_batch(txn, 'Src Batch Pre')
            src_post = self._get_batch(txn, 'Src Batch Post')
            dest_pre = self._get_batch(txn, 'Dest Batch Pre')
            dest_post = self._get_batch(txn, 'Dest Batch Post')
            
            # Extract tracked fields
            txn_info = {
                'tx_id': txn.get('Tx Id', ''),
                'op_id': txn.get('Op Id', ''),
                'op_date': txn.get('Op Date', ''),
                'op_type': txn.get('Op Type', ''),
                'txn_type': txn.get('Txn Type', ''),
                'src_vol_change': txn.get('Src Vol Change', 0),
                'dest_vol_change': txn.get('Dest Vol Change', 0),
                'loss_gain_amount': txn.get('Loss/Gain Amount (gal)', 0),
                'loss_gain_reason': txn.get('Loss/Gain Reason', ''),
                'src_vessel': txn.get('Src Vessel', ''),
                'dest_vessel': txn.get('Dest Vessel', ''),
                'work_order': txn.get('Work Order', ''),
                'operator': txn.get('Operator', ''),
            }
            
            # Create lineage relationships
            # 1. Source vessel batch evolution: Pre -> Post
            if src_pre and src_post and src_pre != src_post:
                self._add_lineage(src_pre, src_post, txn_info)
                
            # 2. Transfer from source to destination: Src Pre -> Dest Post
            if src_pre and dest_post:
                self._add_lineage(src_pre, dest_post, txn_info)
                
            # 3. Destination vessel batch evolution: Pre -> Post
            if dest_pre and dest_post and dest_pre != dest_post:
                self._add_lineage(dest_pre, dest_post, txn_info)
                
        logger.info(f"Built lineage graph with {len(self.batch_to_children)} unique batches")
        
    def _get_batch(self, txn: Dict[str, Any], field: str) -> Optional[str]:
        """Extract and normalize batch ID from transaction."""
        batch = txn.get(field)
        if batch and str(batch).strip() and str(batch).strip() != '--':
            return str(batch).strip()
        return None
        
    def _add_lineage(self, parent_batch: str, child_batch: str, txn_info: Dict[str, Any]) -> None:
        """Add a lineage relationship between two batches."""
        if parent_batch not in self.batch_to_children[parent_batch]:
            self.batch_to_children[parent_batch].append(child_batch)
        if parent_batch not in self.batch_to_parents[child_batch]:
            self.batch_to_parents[child_batch].append(parent_batch)
            
        # Store transaction info for both batches
        self.batch_to_transactions[parent_batch].append({
            **txn_info,
            'relationship': 'parent',
            'related_batch': child_batch,
        })
        self.batch_to_transactions[child_batch].append({
            **txn_info,
            'relationship': 'child',
            'related_batch': parent_batch,
        })
        
    def get_batch_lineage(self, batch: str, max_depth: int = 100) -> Dict[str, Any]:
        """
        Get the complete lineage for a given batch.
        
        Returns all ancestor batches (contributors) and descendant batches.
        Uses BFS to avoid infinite loops.
        """
        ancestors = set()
        descendants = set()
        
        # Find all ancestors (batches that contributed to this batch)
        visited = set()
        queue = deque([batch])
        depth = 0
        
        while queue and depth < max_depth:
            current_batch = queue.popleft()
            if current_batch in visited:
                continue
            visited.add(current_batch)
            
            parents = self.batch_to_parents.get(current_batch, [])
            for parent in parents:
                if parent not in ancestors and parent != batch:
                    ancestors.add(parent)
                    queue.append(parent)
            
            depth += 1
            
        # Find all descendants (batches this batch contributed to)
        visited = set()
        queue = deque([batch])
        depth = 0
        
        while queue and depth < max_depth:
            current_batch = queue.popleft()
            if current_batch in visited:
                continue
            visited.add(current_batch)
            
            children = self.batch_to_children.get(current_batch, [])
            for child in children:
                if child not in descendants and child != batch:
                    descendants.add(child)
                    queue.append(child)
            
            depth += 1
            
        return {
            'batch': batch,
            'ancestor_batches': sorted(list(ancestors)),
            'descendant_batches': sorted(list(descendants)),
            'ancestor_count': len(ancestors),
            'descendant_count': len(descendants),
            'transactions': self.batch_to_transactions.get(batch, []),
            'transaction_count': len(self.batch_to_transactions.get(batch, [])),
        }
        
    def get_all_contributing_batches(self, batch: str, max_depth: int = 100) -> List[str]:
        """
        Get all batches that contributed to the final state of this batch.
        Returns a list of batch IDs in topological order (oldest first).
        """
        ancestors = set()
        visited = set()
        queue = deque([batch])
        depth = 0
        
        while queue and depth < max_depth:
            current_batch = queue.popleft()
            if current_batch in visited:
                continue
            visited.add(current_batch)
            
            parents = self.batch_to_parents.get(current_batch, [])
            for parent in parents:
                if parent not in ancestors and parent != batch:
                    ancestors.add(parent)
                    queue.append(parent)
            
            depth += 1
            
        return sorted(list(ancestors))
        
    def generate_lineage_report(self, output_dir: str) -> None:
        """
        Generate comprehensive lineage reports.
        
        Creates:
        1. Complete lineage map for all batches
        2. Final batch lineage (for batches still on-hand or shipped)
        3. CSV format for Power BI
        """
        logger.info("Generating lineage reports")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Complete lineage map
        all_batches = set(self.batch_to_children.keys()) | set(self.batch_to_parents.keys())
        complete_lineage = {}
        
        for batch in sorted(all_batches):
            complete_lineage[batch] = self.get_batch_lineage(batch)
            
        output_path = os.path.join(output_dir, 'batch_lineage_complete.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(complete_lineage, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved complete lineage to {output_path}")
        
        # 2. Final batch lineage (on-hand or shipped)
        final_lineage = {}
        for batch in sorted(self.final_batches):
            if batch in all_batches:  # Only if we have transaction history
                final_lineage[batch] = self.get_batch_lineage(batch)
                
        output_path = os.path.join(output_dir, 'batch_lineage_final.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_lineage, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved final batch lineage to {output_path}")
        
        # 3. Power BI ready CSV format
        self._generate_powerbi_csv(output_dir, complete_lineage)
        
        # 4. Summary statistics
        self._generate_summary_report(output_dir, complete_lineage, final_lineage)
        
    def _generate_powerbi_csv(self, output_dir: str, lineage_data: Dict[str, Any]) -> None:
        """Generate CSV format suitable for Power BI analysis."""
        csv_rows = []
        
        for batch, lineage in lineage_data.items():
            # Create rows for each transaction
            for txn in lineage.get('transactions', []):
                csv_rows.append({
                    'Batch': batch,
                    'Related_Batch': txn.get('related_batch', ''),
                    'Relationship': txn.get('relationship', ''),
                    'Tx_Id': txn.get('tx_id', ''),
                    'Op_Id': txn.get('op_id', ''),
                    'Op_Date': txn.get('op_date', ''),
                    'Op_Type': txn.get('op_type', ''),
                    'Txn_Type': txn.get('txn_type', ''),
                    'Src_Vessel': txn.get('src_vessel', ''),
                    'Dest_Vessel': txn.get('dest_vessel', ''),
                    'Src_Vol_Change': txn.get('src_vol_change', 0),
                    'Dest_Vol_Change': txn.get('dest_vol_change', 0),
                    'Loss_Gain_Amount_Gal': txn.get('loss_gain_amount', 0),
                    'Loss_Gain_Reason': txn.get('loss_gain_reason', ''),
                    'Work_Order': txn.get('work_order', ''),
                    'Operator': txn.get('operator', ''),
                    'Ancestor_Count': lineage.get('ancestor_count', 0),
                    'Descendant_Count': lineage.get('descendant_count', 0),
                })
                
        # Create ancestry summary CSV
        ancestry_rows = []
        for batch, lineage in lineage_data.items():
            ancestry_rows.append({
                'Batch': batch,
                'Ancestor_Batches': ', '.join(lineage.get('ancestor_batches', [])),
                'Ancestor_Count': lineage.get('ancestor_count', 0),
                'Descendant_Batches': ', '.join(lineage.get('descendant_batches', [])),
                'Descendant_Count': lineage.get('descendant_count', 0),
                'Transaction_Count': lineage.get('transaction_count', 0),
            })
        
        # Write transaction details CSV
        output_path = os.path.join(output_dir, 'batch_lineage_transactions.csv')
        if csv_rows:
            df = pd.DataFrame(csv_rows)
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Saved Power BI transaction CSV to {output_path} ({len(csv_rows)} rows)")
        
        # Write ancestry summary CSV
        output_path = os.path.join(output_dir, 'batch_lineage_summary.csv')
        if ancestry_rows:
            df = pd.DataFrame(ancestry_rows)
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Saved Power BI summary CSV to {output_path} ({len(ancestry_rows)} rows)")
            
    def _generate_summary_report(self, output_dir: str, complete_lineage: Dict[str, Any], 
                                 final_lineage: Dict[str, Any]) -> None:
        """Generate summary statistics report."""
        summary = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_batches_analyzed': len(complete_lineage),
            'final_batches_tracked': len(final_lineage),
            'total_transactions': len(self.transactions),
            'total_vessels': len(self.vessels),
            'total_shipments': len(self.shipments),
            'lineage_statistics': {
                'batches_with_ancestors': sum(1 for l in complete_lineage.values() if l['ancestor_count'] > 0),
                'batches_with_descendants': sum(1 for l in complete_lineage.values() if l['descendant_count'] > 0),
                'max_ancestors': max((l['ancestor_count'] for l in complete_lineage.values()), default=0),
                'max_descendants': max((l['descendant_count'] for l in complete_lineage.values()), default=0),
                'avg_ancestors': sum(l['ancestor_count'] for l in complete_lineage.values()) / len(complete_lineage) if complete_lineage else 0,
                'avg_descendants': sum(l['descendant_count'] for l in complete_lineage.values()) / len(complete_lineage) if complete_lineage else 0,
            }
        }
        
        output_path = os.path.join(output_dir, 'analysis_summary.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved analysis summary to {output_path}")
        
        # Print summary to console
        logger.info("=" * 60)
        logger.info("VESSEL-BATCH LINEAGE ANALYSIS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total batches analyzed: {summary['total_batches_analyzed']}")
        logger.info(f"Final batches tracked: {summary['final_batches_tracked']}")
        logger.info(f"Total transactions: {summary['total_transactions']}")
        logger.info(f"Batches with ancestors: {summary['lineage_statistics']['batches_with_ancestors']}")
        logger.info(f"Batches with descendants: {summary['lineage_statistics']['batches_with_descendants']}")
        logger.info(f"Max ancestors for any batch: {summary['lineage_statistics']['max_ancestors']}")
        logger.info(f"Max descendants for any batch: {summary['lineage_statistics']['max_descendants']}")
        logger.info(f"Average ancestors per batch: {summary['lineage_statistics']['avg_ancestors']:.2f}")
        logger.info(f"Average descendants per batch: {summary['lineage_statistics']['avg_descendants']:.2f}")
        logger.info("=" * 60)


def main():
    """Main execution function."""
    logger.info("Starting Vessel-Batch Lineage Analysis")
    
    # Initialize analyzer
    analyzer = VesselBatchLineageAnalyzer()
    
    # Define file paths
    base_dir = "Main/data"
    transactions_csv = os.path.join(base_dir, "GET--transaction-search", "Transaction_to_analysise.csv")
    vessels_json = os.path.join(base_dir, "GET--vessels", "vessels.json")
    shipments_json = os.path.join(base_dir, "GET--shipments", "shipments_thin.json")
    output_dir = os.path.join(base_dir, "vessel-batch-lineage")
    
    # Load data
    analyzer.load_transactions_csv(transactions_csv)
    analyzer.load_vessels_json(vessels_json)
    analyzer.load_shipments_json(shipments_json)
    
    # Extract final batches
    analyzer.extract_final_batches()
    
    # Build lineage graph
    analyzer.build_lineage_graph()
    
    # Generate reports
    analyzer.generate_lineage_report(output_dir)
    
    logger.info("Vessel-Batch Lineage Analysis completed successfully!")
    logger.info(f"Output files saved to: {output_dir}")


if __name__ == "__main__":
    main()

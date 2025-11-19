#!/usr/bin/env python3
"""
H5 File Structure Inspector

Prints the complete structure of an H5 file including:
- Groups and hierarchy
- Datasets (Tables and Arrays)
- Dataset fields and data types
- Attributes and metadata
- Statistics (row counts, value ranges)
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any

import tables
import h5py
import numpy as np


class H5Inspector:
    """Inspect and display H5 file structure."""

    def __init__(self, h5_path: str, verbose: bool = False, show_stats: bool = False):
        """
        Initialize inspector.

        Args:
            h5_path: Path to H5 file
            verbose: Show detailed information
            show_stats: Calculate and show statistics for each dataset
        """
        self.h5_path = Path(h5_path)
        self.verbose = verbose
        self.show_stats = show_stats
        self.h5_file = None

    def print_file_metadata(self):
        """Print overall file metadata."""
        print("\n" + "=" * 80)
        print("H5 FILE METADATA")
        print("=" * 80)

        print(f"\nFile: {self.h5_path}")
        print(f"File size: {self.h5_path.stat().st_size:,} bytes")

        # Use h5py to get file-level attributes
        with h5py.File(self.h5_path, 'r') as h5:
            print(f"\nFile attributes:")
            if len(h5.attrs) > 0:
                for key, value in h5.attrs.items():
                    print(f"  {key}: {value}")
            else:
                print("  (none)")

        # PyTables specific info
        print(f"\nPyTables format: {self.h5_file.format_version}")
        print(f"Title: {self.h5_file.title}")
        if hasattr(self.h5_file.root, '_v_attrs'):
            root_attrs = self.h5_file.root._v_attrs
            if hasattr(root_attrs, '_v_attrnamesuser') and len(root_attrs._v_attrnamesuser) > 0:
                print(f"\nRoot attributes:")
                for attr_name in root_attrs._v_attrnamesuser:
                    print(f"  {attr_name}: {getattr(root_attrs, attr_name)}")

    def print_tree_structure(self):
        """Print complete hierarchical tree structure."""
        print("\n" + "=" * 80)
        print("HIERARCHICAL TREE STRUCTURE")
        print("=" * 80)

        self._print_node_tree(self.h5_file.root, indent=0)

    def _print_node_tree(self, node, indent: int = 0):
        """Recursively print node tree."""
        prefix = "  " * indent

        # Print node name and type
        node_name = node._v_name if node._v_name else "/"

        if isinstance(node, tables.Group):
            print(f"{prefix}📁 {node_name}/")

            # Print group attributes if verbose
            if self.verbose and hasattr(node, '_v_attrs'):
                attrs = node._v_attrs
                if hasattr(attrs, '_v_attrnamesuser') and len(attrs._v_attrnamesuser) > 0:
                    for attr_name in attrs._v_attrnamesuser:
                        print(f"{prefix}   @{attr_name}: {getattr(attrs, attr_name)}")

            # Print children
            for child in node._f_iter_nodes():
                self._print_node_tree(child, indent + 1)

        elif isinstance(node, tables.Table):
            row_count = node.nrows
            col_count = len(node.colnames)
            print(f"{prefix}📊 {node_name} (Table: {row_count:,} rows, {col_count} columns)")

            if self.verbose:
                print(f"{prefix}   Columns: {', '.join(node.colnames)}")
                print(f"{prefix}   Types: {', '.join(str(node.coltypes[col]) for col in node.colnames)}")

                # Show compression info
                if hasattr(node, 'filters') and node.filters is not None:
                    filters = node.filters
                    if filters.complib:
                        print(f"{prefix}   Compression: {filters.complib} (level {filters.complevel})")

        elif isinstance(node, tables.Array):
            shape = node.shape
            dtype = node.dtype
            print(f"{prefix}📈 {node_name} (Array: shape={shape}, dtype={dtype})")

            if self.verbose and hasattr(node, 'atom'):
                print(f"{prefix}   Atom: {node.atom}")

        else:
            print(f"{prefix}❓ {node_name} ({type(node).__name__})")

    def print_all_datasets(self):
        """Print detailed information about all datasets."""
        print("\n" + "=" * 80)
        print("ALL DATASETS (DETAILED)")
        print("=" * 80)

        datasets = []
        for node in self.h5_file.walk_nodes("/", classname="Leaf"):
            datasets.append(node)

        print(f"\nTotal datasets: {len(datasets)}\n")

        for idx, node in enumerate(datasets, 1):
            print(f"\n[{idx}/{len(datasets)}] {node._v_pathname}")
            print("-" * 80)

            if isinstance(node, tables.Table):
                self._print_table_details(node)
            elif isinstance(node, tables.Array):
                self._print_array_details(node)
            else:
                print(f"  Type: {type(node).__name__}")

    def _print_table_details(self, table: tables.Table):
        """Print detailed information about a Table."""
        print(f"  Type: Table")
        print(f"  Rows: {table.nrows:,}")
        print(f"  Columns: {len(table.colnames)}")

        # Column information
        print(f"\n  Column details:")
        for col_name in table.colnames:
            col_type = table.coltypes[col_name]
            col_shape = table.coldtypes[col_name].shape if hasattr(table.coldtypes[col_name], 'shape') else ()
            print(f"    - {col_name}: {col_type}", end="")
            if col_shape:
                print(f" {col_shape}", end="")
            print()

        # Compression
        if hasattr(table, 'filters') and table.filters is not None:
            filters = table.filters
            if filters.complib:
                print(f"\n  Compression: {filters.complib} (level {filters.complevel})")
            else:
                print(f"\n  Compression: None")

        # Attributes
        if hasattr(table, '_v_attrs'):
            attrs = table._v_attrs
            if hasattr(attrs, '_v_attrnamesuser') and len(attrs._v_attrnamesuser) > 0:
                print(f"\n  Attributes:")
                for attr_name in attrs._v_attrnamesuser:
                    print(f"    {attr_name}: {getattr(attrs, attr_name)}")

        # Statistics if requested
        if self.show_stats and table.nrows > 0:
            print(f"\n  Statistics:")
            for col_name in table.colnames:
                try:
                    col_data = table.col(col_name)
                    self._print_column_stats(col_name, col_data)
                except Exception as e:
                    print(f"    {col_name}: Error - {e}")

    def _print_array_details(self, array: tables.Array):
        """Print detailed information about an Array."""
        print(f"  Type: Array")
        print(f"  Shape: {array.shape}")
        print(f"  Dtype: {array.dtype}")
        print(f"  Size: {array.size:,} elements")

        if hasattr(array, 'atom'):
            print(f"  Atom: {array.atom}")

        # Attributes
        if hasattr(array, '_v_attrs'):
            attrs = array._v_attrs
            if hasattr(attrs, '_v_attrnamesuser') and len(attrs._v_attrnamesuser) > 0:
                print(f"\n  Attributes:")
                for attr_name in attrs._v_attrnamesuser:
                    print(f"    {attr_name}: {getattr(attrs, attr_name)}")

        # Statistics if requested
        if self.show_stats and array.size > 0:
            print(f"\n  Statistics:")
            try:
                data = array.read()
                self._print_column_stats("values", data)
            except Exception as e:
                print(f"    Error reading data: {e}")

    def _print_column_stats(self, col_name: str, data: np.ndarray):
        """Print statistics for a column/array."""
        if np.issubdtype(data.dtype, np.number):
            # Numeric data
            print(f"    {col_name}:")
            print(f"      Min: {np.nanmin(data)}")
            print(f"      Max: {np.nanmax(data)}")
            print(f"      Mean: {np.nanmean(data):.6f}")
            print(f"      Std: {np.nanstd(data):.6f}")

            # Check for NaN/Inf
            nan_count = np.sum(np.isnan(data))
            inf_count = np.sum(np.isinf(data))
            if nan_count > 0:
                print(f"      NaN values: {nan_count} ({nan_count/len(data)*100:.2f}%)")
            if inf_count > 0:
                print(f"      Inf values: {inf_count} ({inf_count/len(data)*100:.2f}%)")

            # Unique values (for small sets)
            unique_vals = np.unique(data)
            if len(unique_vals) <= 10:
                print(f"      Unique values ({len(unique_vals)}): {unique_vals.tolist()}")
            else:
                print(f"      Unique values: {len(unique_vals)}")
        else:
            # Non-numeric data
            unique_vals = np.unique(data)
            print(f"    {col_name}:")
            print(f"      Unique values: {len(unique_vals)}")
            if len(unique_vals) <= 20:
                print(f"      Values: {unique_vals.tolist()}")

    def print_summary(self):
        """Print a quick summary."""
        print("\n" + "=" * 80)
        print("QUICK SUMMARY")
        print("=" * 80)

        # Count groups and datasets
        groups = []
        tables = []
        arrays = []
        others = []

        for node in self.h5_file.walk_nodes("/"):
            if isinstance(node, tables.Group):
                groups.append(node)
            elif isinstance(node, tables.Table):
                tables.append(node)
            elif isinstance(node, tables.Array):
                arrays.append(node)
            else:
                others.append(node)

        print(f"\nGroups: {len(groups)}")
        print(f"Tables: {len(tables)}")
        print(f"Arrays: {len(arrays)}")
        if others:
            print(f"Other nodes: {len(others)}")

        # Group datasets by path prefix
        if tables or arrays:
            print(f"\nDatasets by group:")
            dataset_groups = {}
            for node in tables + arrays:
                path_parts = node._v_pathname.split('/')[1:-1]  # Exclude root and dataset name
                group_path = '/' + '/'.join(path_parts) if path_parts else '/'
                dataset_groups[group_path] = dataset_groups.get(group_path, 0) + 1

            for group_path, count in sorted(dataset_groups.items()):
                print(f"  {group_path}: {count} datasets")

        # Total rows in tables
        if tables:
            total_rows = sum(t.nrows for t in tables)
            print(f"\nTotal rows across all tables: {total_rows:,}")

            # Show largest tables
            print(f"\nLargest tables:")
            sorted_tables = sorted(tables, key=lambda t: t.nrows, reverse=True)[:10]
            for table in sorted_tables:
                print(f"  {table._v_pathname}: {table.nrows:,} rows")

    def inspect(self, mode: str = "full"):
        """
        Run inspection.

        Args:
            mode: Inspection mode - "summary", "tree", "datasets", or "full"
        """
        print(f"\nInspecting H5 file: {self.h5_path}")

        if not self.h5_path.exists():
            print(f"✗ Error: File not found: {self.h5_path}", file=sys.stderr)
            sys.exit(1)

        # Open H5 file
        print("Opening H5 file...")
        self.h5_file = tables.open_file(str(self.h5_path), mode='r')

        try:
            if mode == "summary":
                self.print_file_metadata()
                self.print_summary()

            elif mode == "tree":
                self.print_file_metadata()
                self.print_tree_structure()

            elif mode == "datasets":
                self.print_all_datasets()

            elif mode == "full":
                self.print_file_metadata()
                self.print_tree_structure()
                if self.verbose:
                    self.print_all_datasets()
                else:
                    print("\n💡 Use --verbose to see detailed dataset information")
                self.print_summary()

            else:
                print(f"✗ Unknown mode: {mode}", file=sys.stderr)
                sys.exit(1)

        finally:
            # Close file
            if self.h5_file:
                self.h5_file.close()

        print("\n" + "=" * 80)
        print("✓ Inspection complete")
        print("=" * 80 + "\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Inspect H5 file structure and contents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  summary  - Quick overview of file structure and statistics
  tree     - Hierarchical tree view of groups and datasets
  datasets - Detailed information about all datasets
  full     - Complete inspection (default)

Examples:
  # Quick summary
  python3 h5_inspector.py output.h5 --mode summary

  # Tree view with verbose output
  python3 h5_inspector.py output.h5 --mode tree --verbose

  # All datasets with statistics
  python3 h5_inspector.py output.h5 --mode datasets --stats

  # Full inspection
  python3 h5_inspector.py output.h5 --verbose --stats
        """
    )

    parser.add_argument(
        'h5_file',
        help='Path to H5 file to inspect'
    )

    parser.add_argument(
        '--mode',
        choices=['summary', 'tree', 'datasets', 'full'],
        default='full',
        help='Inspection mode (default: full)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )

    parser.add_argument(
        '-s', '--stats',
        action='store_true',
        help='Calculate and show statistics for each dataset'
    )

    args = parser.parse_args()

    # Create inspector
    inspector = H5Inspector(
        h5_path=args.h5_file,
        verbose=args.verbose,
        show_stats=args.stats,
    )

    try:
        # Run inspection
        inspector.inspect(mode=args.mode)
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {type(e).__name__}: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()

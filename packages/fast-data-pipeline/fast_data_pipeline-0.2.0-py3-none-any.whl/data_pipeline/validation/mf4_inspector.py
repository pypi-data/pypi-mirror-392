#!/usr/bin/env python3
"""
MF4 File Structure Inspector

Prints the complete structure of an MF4 file including:
- Channel groups and channels
- Channel metadata (units, data type, description)
- File metadata and attributes
- Statistics (sample counts, time range)
"""

import argparse
import sys
from pathlib import Path
from typing import Dict

from asammdf import MDF
import numpy as np


class MF4Inspector:
    """Inspect and display MF4 file structure."""

    def __init__(self, mf4_path: str, verbose: bool = False, show_stats: bool = False):
        """
        Initialize inspector.

        Args:
            mf4_path: Path to MF4 file
            verbose: Show detailed information
            show_stats: Calculate and show statistics for each channel
        """
        self.mf4_path = Path(mf4_path)
        self.verbose = verbose
        self.show_stats = show_stats
        self.mdf = None

    def print_file_metadata(self):
        """Print overall file metadata."""
        print("\n" + "=" * 80)
        print("MF4 FILE METADATA")
        print("=" * 80)

        print(f"\nFile: {self.mf4_path}")
        print(f"File size: {self.mf4_path.stat().st_size:,} bytes")
        print(f"MDF version: {self.mdf.version}")

        # File header information
        header = self.mdf.header
        print("\nHeader Information:")
        print(f"  Author: {header.author if hasattr(header, 'author') else 'N/A'}")
        print(f"  Department: {header.department if hasattr(header, 'department') else 'N/A'}")
        print(f"  Project: {header.project if hasattr(header, 'project') else 'N/A'}")
        print(f"  Subject: {header.subject if hasattr(header, 'subject') else 'N/A'}")

        # Time information
        if hasattr(header, 'start_time'):
            print(f"  Start time: {header.start_time}")

        # Channel groups
        print(f"\nChannel Groups: {len(self.mdf.groups)}")
        print(f"Total Channels: {len(self.mdf.channels_db)}")

    def print_channel_groups(self):
        """Print channel group structure."""
        print("\n" + "=" * 80)
        print("CHANNEL GROUPS")
        print("=" * 80)

        for idx, group in enumerate(self.mdf.groups):
            print(f"\nGroup {idx}:")

            # Group metadata
            if hasattr(group, 'channel_group'):
                cg = group.channel_group
                print(f"  Acquisition name: {cg.acq_name if hasattr(cg, 'acq_name') else 'N/A'}")
                print(f"  Comment: {cg.comment if hasattr(cg, 'comment') else 'N/A'}")
                print(f"  Cycles: {cg.cycles_nr if hasattr(cg, 'cycles_nr') else 'N/A'}")

            # Channels in this group
            channel_count = len(group.channels)
            print(f"  Channels in group: {channel_count}")

            if self.verbose and channel_count > 0:
                print(f"  Channel list:")
                for ch_idx, channel in enumerate(group.channels):
                    ch_name = channel.name if hasattr(channel, 'name') else f"Channel_{ch_idx}"
                    print(f"    [{ch_idx}] {ch_name}")

    def print_all_channels(self):
        """Print detailed information about all channels."""
        print("\n" + "=" * 80)
        print("ALL CHANNELS (DETAILED)")
        print("=" * 80)

        # Get all channel names
        all_channels = sorted(self.mdf.channels_db.keys())

        print(f"\nTotal channels: {len(all_channels)}\n")

        for idx, channel_name in enumerate(all_channels, 1):
            print(f"\n[{idx}/{len(all_channels)}] {channel_name}")
            print("-" * 80)

            try:
                # Get signal information
                signal = self.mdf.get(channel_name)

                # Get channel metadata from the MDF structure
                channel_metadata = None
                for group_idx, group in enumerate(self.mdf.groups):
                    for ch_idx, channel in enumerate(group.channels):
                        if hasattr(channel, 'name') and channel.name == channel_name:
                            channel_metadata = channel
                            break
                    if channel_metadata:
                        break

                # Basic info
                print(f"  Numpy dtype: {signal.samples.dtype}")
                print(f"  Unit: {signal.unit if signal.unit else 'N/A'}")
                print(f"  Comment: {signal.comment if signal.comment else 'N/A'}")
                print(f"  Samples: {len(signal.samples):,}")

                # Detailed channel type information from MDF metadata
                if channel_metadata:
                    print("\n  MF4 Channel Metadata:")

                    # Data type
                    if hasattr(channel_metadata, 'data_type'):
                        dtype_map = {
                            0: 'unsigned integer',
                            1: 'signed integer',
                            2: 'IEEE 754 floating-point',
                            3: 'string (UTF-8)',
                            4: 'string (UTF-16 LE)',
                            5: 'string (UTF-16 BE)',
                            6: 'byte array',
                            7: 'MIME sample',
                            8: 'MIME stream',
                            9: 'CANopen date',
                            10: 'CANopen time',
                        }
                        dtype_val = channel_metadata.data_type
                        dtype_str = dtype_map.get(dtype_val, f'unknown ({dtype_val})')
                        print(f"    Data type: {dtype_str}")

                    # Bit count
                    if hasattr(channel_metadata, 'bit_count'):
                        print(f"    Bit count: {channel_metadata.bit_count}")

                    # Byte order
                    if hasattr(channel_metadata, 'byte_order'):
                        byte_order = 'little-endian' if channel_metadata.byte_order == 0 else 'big-endian'
                        print(f"    Byte order: {byte_order}")

                    # Channel type
                    if hasattr(channel_metadata, 'channel_type'):
                        ch_type_map = {
                            0: 'fixed length data',
                            1: 'variable length data',
                            2: 'master channel',
                            3: 'virtual master',
                            4: 'sync',
                            5: 'maximum length data',
                            6: 'virtual data',
                        }
                        ch_type_val = channel_metadata.channel_type
                        ch_type_str = ch_type_map.get(ch_type_val, f'unknown ({ch_type_val})')
                        print(f"    Channel type: {ch_type_str}")

                    # Sync type (for some channels)
                    if hasattr(channel_metadata, 'sync_type'):
                        print(f"    Sync type: {channel_metadata.sync_type}")

                    # Min/Max from metadata
                    if hasattr(channel_metadata, 'min_raw_value') and hasattr(channel_metadata, 'max_raw_value'):
                        print(f"    Raw range: [{channel_metadata.min_raw_value}, {channel_metadata.max_raw_value}]")

                # Timestamp info
                if len(signal.timestamps) > 0:
                    print("\n  Timing:")
                    print(f"    Time range: {signal.timestamps[0]:.6f} - {signal.timestamps[-1]:.6f} seconds")
                    print(f"    Duration: {signal.timestamps[-1] - signal.timestamps[0]:.6f} seconds")

                    # Sample rate calculation
                    if len(signal.timestamps) > 1:
                        time_diffs = np.diff(signal.timestamps)
                        avg_sample_period = np.mean(time_diffs)
                        sample_rate = 1.0 / avg_sample_period if avg_sample_period > 0 else 0
                        print(f"    Avg sample rate: {sample_rate:.2f} Hz")

                        # Check if constant sample rate
                        if np.std(time_diffs) < 1e-9:
                            print("    Sampling: constant rate")
                        else:
                            print(f"    Sampling: variable rate (std: {np.std(time_diffs):.6f}s)")

                # Display name
                if hasattr(signal, 'display_name') and signal.display_name:
                    print(f"\n  Display name: {signal.display_name}")

                # Conversion info
                if hasattr(signal, 'conversion') and signal.conversion:
                    print("\n  Conversion:")
                    print(f"    Type: {type(signal.conversion).__name__}")
                    if hasattr(signal.conversion, 'unit'):
                        print(f"    Unit: {signal.conversion.unit}")
                    # Show conversion formula if available
                    if hasattr(signal.conversion, 'name'):
                        print(f"    Name: {signal.conversion.name}")

                # Value statistics (if enabled)
                if self.show_stats and len(signal.samples) > 0:
                    self._print_channel_statistics(signal)

            except Exception as e:
                print(f"  ⚠ Error reading channel: {type(e).__name__}: {e}")

    def _print_channel_statistics(self, signal):
        """Print statistical information for a signal."""
        samples = signal.samples

        # Handle different data types
        if np.issubdtype(samples.dtype, np.number):
            # Numeric data
            print("\n  Statistics:")
            print(f"    Min: {np.nanmin(samples)}")
            print(f"    Max: {np.nanmax(samples)}")
            print(f"    Mean: {np.nanmean(samples):.6f}")
            print(f"    Std: {np.nanstd(samples):.6f}")

            # Check for NaN/Inf
            nan_count = np.sum(np.isnan(samples))
            inf_count = np.sum(np.isinf(samples))
            if nan_count > 0:
                print(f"    NaN values: {nan_count} ({nan_count/len(samples)*100:.2f}%)")
            if inf_count > 0:
                print(f"    Inf values: {inf_count} ({inf_count/len(samples)*100:.2f}%)")

            # Unique values (for small sets)
            unique_vals = np.unique(samples)
            if len(unique_vals) <= 10:
                print(f"    Unique values ({len(unique_vals)}): {unique_vals.tolist()}")
            else:
                print(f"    Unique values: {len(unique_vals)}")
        else:
            # Non-numeric data
            unique_vals = np.unique(samples)
            print("\n  Statistics:")
            print(f"    Unique values: {len(unique_vals)}")
            if len(unique_vals) <= 20:
                print(f"    Values: {unique_vals.tolist()}")

    def print_channel_tree(self):
        """Print channels organized in a tree structure based on naming."""
        print("\n" + "=" * 80)
        print("CHANNEL TREE (Hierarchical View)")
        print("=" * 80)

        all_channels = sorted(self.mdf.channels_db.keys())

        # Build tree structure
        tree = {}
        for channel in all_channels:
            parts = channel.split('/')
            current = tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            # Store the full channel name as a leaf
            current[parts[-1]] = channel

        # Print tree
        self._print_tree_recursive(tree, indent=0)

    def _print_tree_recursive(self, node: Dict, indent: int = 0):
        """Recursively print tree structure."""
        for key, value in sorted(node.items()):
            if isinstance(value, dict):
                # It's a group/folder
                print("  " * indent + f"📁 {key}/")
                self._print_tree_recursive(value, indent + 1)
            else:
                # It's a channel (leaf)
                print("  " * indent + f"📊 {key}")
                if self.verbose:
                    try:
                        signal = self.mdf.get(value)
                        print("  " * indent + f"   Type: {signal.samples.dtype}, Samples: {len(signal.samples):,}, Unit: {signal.unit or 'N/A'}")
                    except Exception:
                        pass

    def print_summary(self):
        """Print a quick summary."""
        print("\n" + "=" * 80)
        print("QUICK SUMMARY")
        print("=" * 80)

        all_channels = list(self.mdf.channels_db.keys())

        print(f"\nTotal channels: {len(all_channels)}")
        print(f"Channel groups: {len(self.mdf.groups)}")

        # Group channels by prefix
        prefixes = {}
        for channel in all_channels:
            prefix = channel.split('/')[0] if '/' in channel else 'root'
            prefixes[prefix] = prefixes.get(prefix, 0) + 1

        print("\nChannels by prefix:")
        for prefix, count in sorted(prefixes.items(), key=lambda x: -x[1]):
            print(f"  {prefix}: {count}")

        # Data type distribution
        dtypes = {}
        for channel in all_channels:
            try:
                signal = self.mdf.get(channel)
                dtype_str = str(signal.samples.dtype)
                dtypes[dtype_str] = dtypes.get(dtype_str, 0) + 1
            except Exception:
                pass

        if dtypes:
            print("\nData types:")
            for dtype, count in sorted(dtypes.items(), key=lambda x: -x[1]):
                print(f"  {dtype}: {count}")

    def inspect(self, mode: str = "full"):
        """
        Run inspection.

        Args:
            mode: Inspection mode - "summary", "tree", "full", or "channels"
        """
        print(f"\nInspecting MF4 file: {self.mf4_path}")

        if not self.mf4_path.exists():
            print(f"✗ Error: File not found: {self.mf4_path}", file=sys.stderr)
            sys.exit(1)

        # Open MF4 file
        print("Opening MF4 file...")
        self.mdf = MDF(str(self.mf4_path), memory="low")

        try:
            if mode == "summary":
                self.print_file_metadata()
                self.print_summary()

            elif mode == "tree":
                self.print_file_metadata()
                self.print_channel_tree()

            elif mode == "channels":
                self.print_all_channels()

            elif mode == "full":
                self.print_file_metadata()
                self.print_channel_groups()
                self.print_channel_tree()
                if self.verbose:
                    self.print_all_channels()
                else:
                    print("\n💡 Use --verbose to see detailed channel information")

            else:
                print(f"✗ Unknown mode: {mode}", file=sys.stderr)
                sys.exit(1)

        finally:
            # Close file
            if self.mdf:
                self.mdf.close()

        print("\n" + "=" * 80)
        print("✓ Inspection complete")
        print("=" * 80 + "\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Inspect MF4 file structure and contents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  summary  - Quick overview of file structure and statistics
  tree     - Hierarchical tree view of channels
  channels - Detailed information about all channels
  full     - Complete inspection (default)

Examples:
  # Quick summary
  python3 mf4_inspector.py input.mf4 --mode summary

  # Tree view with verbose output
  python3 mf4_inspector.py input.mf4 --mode tree --verbose

  # All channels with statistics
  python3 mf4_inspector.py input.mf4 --mode channels --stats

  # Full inspection
  python3 mf4_inspector.py input.mf4 --verbose --stats
        """
    )

    parser.add_argument(
        'mf4_file',
        help='Path to MF4 file to inspect'
    )

    parser.add_argument(
        '--mode',
        choices=['summary', 'tree', 'channels', 'full'],
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
        help='Calculate and show statistics for each channel'
    )

    args = parser.parse_args()

    # Create inspector
    inspector = MF4Inspector(
        mf4_path=args.mf4_file,
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

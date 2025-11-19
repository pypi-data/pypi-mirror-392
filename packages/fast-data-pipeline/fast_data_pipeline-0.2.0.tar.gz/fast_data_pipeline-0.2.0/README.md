# Fast Data Pipeline

A Python package for processing MF4 (Measurement Data Format) and ROS2 bag files, converting them to HDF5 format, and merging synchronized data streams.

## Features

- **MF4 Ingestion**: Convert MF4 files to HDF5 format based on YAML layout specifications
- **ROS2 Bag Ingestion**: Extract and convert ROS2 bag data to HDF5 format
- **Data Merging**: Synchronize and merge multiple HDF5 data sources based on timestamps
- **Flexible Configuration**: YAML-based layout specifications for customizable data mapping
- **State Management**: Track processed files to avoid reprocessing
- **Validation**: Built-in data validation and completeness checks

## Installation

```bash
pip install fast_data_pipeline
```

## Quick Start

### MF4 to HDF5 Conversion

```python
from data_pipeline.ingestion.mf4_ingestor import MF4Ingester
from data_pipeline.common.state_manager import StateManager

# Initialize state manager
state_manager = StateManager(
    output_folder="/path/to/output",
    state_filename="mf4_processing_state.pkl"
)

# Create MF4 ingester
ingester = MF4Ingester(
    input_folder="/path/to/mf4/files",
    output_folder="/path/to/output",
    state_manager=state_manager,
    file_pattern="*.mf4",
    layout_yaml_path="path/to/layout_spec.yaml"
)

# Process files
ingester.run()
```

### ROS2 Bag to HDF5 Conversion

```python
from data_pipeline.ingestion.rosbag_ingestor import RosbagIngester
from data_pipeline.common.state_manager import StateManager

# Initialize state manager
state_manager = StateManager(
    output_folder="/path/to/output",
    state_filename="rosbag_processing_state.pkl"
)

# Create Rosbag ingester
ingester = RosbagIngester(
    input_folder="/path/to/rosbag/files",
    output_folder="/path/to/output",
    state_manager=state_manager,
    file_pattern="*.db3",
    layout_yaml_path="path/to/layout_spec.yaml"
)

# Process files
ingester.run()
```

### Merging HDF5 Files

```python
from data_pipeline.processing.h5_merger import run as h5_merger_run

# Define metadata function (optional)
def add_metadata(h5file, rec_file, rosbag_file):
    h5file.attrs['source_rec'] = rec_file
    h5file.attrs['source_rosbag'] = rosbag_file
    return h5file

# Run merger
h5_merger_run(
    rec_folder="/path/to/mf4-h5",
    rosbag_folder="/path/to/rosbag-h5",
    output_folder="/path/to/merged",
    rec_timestamp_spec="hi5/vehicle_data/timestamp_s::value",
    rosbag_timestamp_spec="hi5/perception/camera/timestamp_s|hi5/perception/camera/timestamp_ns",
    rec_global_pattern="rec*.h5",
    rosbag_global_pattern="rosbag*.h5",
    logging_file_name="sync_log.pkl",
    metadata_func=add_metadata
)
```

## Layout Specification

The package uses YAML files to define how data should be extracted and structured in HDF5 format.

### Example Layout YAML

```yaml
mapping:
  # MF4 source
  - source: mf4
    original_name: "Model Root/recorder/hi5/velocity_x_mps"
    target_name: /hi5/vehicle_data/velocity_x_mps
    units: "m/s"

  # ROS2 bag source
  - source: ros2bag
    original_name: /camera/image
    target_name: /hi5/perception/camera/image
    units: "-"
```

## Use with Apache Airflow

This package is designed to work seamlessly with Apache Airflow for automated data processing pipelines.

### Example with PythonVirtualenvOperator

```python
from airflow.operators.python import PythonVirtualenvOperator

def process_mf4_data(input_dir, output_dir, layout_path):
    from data_pipeline.ingestion.mf4_ingestor import MF4Ingester
    from data_pipeline.common.state_manager import StateManager

    import os
    os.makedirs(output_dir, exist_ok=True)

    state_manager = StateManager(
        output_folder=output_dir,
        state_filename="mf4_state.pkl"
    )

    ingester = MF4Ingester(
        input_folder=input_dir,
        output_folder=output_dir,
        state_manager=state_manager,
        file_pattern="*.mf4",
        layout_yaml_path=layout_path
    )

    ingester.run()

task = PythonVirtualenvOperator(
    task_id='process_mf4',
    python_callable=process_mf4_data,
    requirements=["fast_data_pipeline==0.1.2"],
    op_kwargs={
        'input_dir': '/data/mf4',
        'output_dir': '/data/mf4-h5',
        'layout_path': 'layout.yaml'
    }
)
```

## Requirements

- Python >= 3.8
- asammdf >= 8.6.0 (for MF4 processing)
- rosbags >= 0.10.0 (for ROS2 bag processing)
- tables >= 3.10.0 (for HDF5 operations)
- pandas >= 2.3.0
- numpy >= 2.0.0
- PyYAML >= 6.0.0

See `pyproject.toml` for complete dependency list.

## Project Structure

```
data_pipeline/
├── ingestion/          # Data ingestion modules
│   ├── mf4_ingestor.py
│   ├── rosbag_ingestor.py
│   └── base_ingestor.py
├── processing/         # Data processing modules
│   ├── h5_merger.py
│   └── metadata_functions.py
├── common/             # Common utilities
│   └── state_manager.py
└── validation/         # Data validation
```

## Development

### Installing for Development

```bash
git clone <repository-url>
cd data-pipeline
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Building the Package

```bash
python -m build
```

## License

MIT License - see LICENSE file for details

## Author

Bora Pilav (bbpilav@gmail.com)

## Changelog

### 0.1.2 (2025-01-18)
- Added support for multi-dimensional array data in MF4 files
- Improved HDF5 structure for array channels
- Enhanced logging and error handling
- Added comprehensive dependencies in pyproject.toml

### 0.1.0
- Initial release
- MF4 to HDF5 conversion
- ROS2 bag to HDF5 conversion
- HDF5 merging functionality

"""
LEAF Example Adapter - Example Template for New Adapter Development

This package demonstrates the basic structure of a LEAF adapter. New developers
should use this as a reference when creating their own equipment adapters.

Package Structure:
    adapter.py - Main Adapter class that coordinates the data collection lifecycle
                 - Inherits from DiscreteExperimentAdapter
                 - Sets up the Watcher (WHEN to collect data)
                 - Sets up the Interpreter (HOW to collect and format data)
                 - Connects to the Output plugin (WHERE to send data)

    interpreter.py - Interpreter class that handles data collection and formatting
                     - retrieval() - Connect to equipment and get raw data
                     - measurement() - Format data into InfluxDB InfluxPoint objects
                     - metadata() - Handle equipment metadata updates

    device.json - Equipment metadata file defining:
                  - adapter_id (unique identifier for this adapter type)
                  - equipment_data (manufacturer, device type, version)
                  - adapter_requirements (required configuration parameters)

    example.yaml - Sample configuration file showing how to:
                   - Configure adapter instance (institute, instance_id)
                   - Set adapter-specific parameters (e.g., polling interval)
                   - Configure MQTT output plugin

Entry Point:
    The Adapter class is registered as a plugin in pyproject.toml:
    [tool.poetry.plugins."leaf.adapters"]
    leaf_example = "leaf_example.adapter:Adapter"

Quick Start for New Developers:
    1. Copy this template and rename the package
    2. Update device.json with your equipment information
    3. Modify interpreter.py to connect to your specific equipment
    4. Adjust the watcher type in adapter.py if needed (SimpleWatcher, EventWatcher, etc.)
    5. Update pyproject.toml with your adapter name and dependencies
    6. Test with the provided test examples in tests/

For complete documentation, visit: https://leaf.systemsbiology.nl
"""
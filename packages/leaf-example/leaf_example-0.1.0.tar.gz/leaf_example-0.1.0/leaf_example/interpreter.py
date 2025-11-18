import os
import random
from datetime import datetime, timezone
from typing import Any

from influxobject import InfluxPoint
from leaf.adapters.equipment_adapter import AbstractInterpreter

from leaf.utility.logger.logger_utils import get_logger
logger = get_logger(__name__, log_file="interpreter.log")

current_dir = os.path.dirname(os.path.abspath(__file__))
metadata_fn = os.path.join(current_dir, "device.json")


class Interpreter(AbstractInterpreter):
    """
    Interpreter class responsible for data collection and formatting.

    The Interpreter is called by the Framework phases:
    - measurement(data) - REQUIRED: Fetch equipment data and format into InfluxDB InfluxPoint objects
    - metadata(data) - OPTIONAL: Handle equipment metadata (default implementation records timestamp)

    How the flow works:
    - Watcher polls and triggers callbacks when events occur
    - Callbacks invoke Framework Phases (StartPhase, MeasurePhase, StopPhase)
    - Phases call interpreter methods (metadata() for start, measurement() for measurements)
    - Interpreter fetches REAL data from equipment (ignoring watcher's dummy input)

    MQTT Topic Structure: '<institute>/<equipment_id>/<instance_id>/details'
    Example: 'VUMC/Example/bioreactor-1/details'
    """
    def __init__(self, metadata_manager: Any) -> None:
        """
        Initialize the Interpreter.

        Args:
            metadata_manager: Provides access to device.json and YAML configuration
        """
        super().__init__()
        # Internal data storage (can be used to cache equipment state between polls)
        self.data = {}
        self.metadata_manager = metadata_manager
        logger.info("Initializing DEMO Interpreter")

    def measurement(self, data) -> set[InfluxPoint]:
        """
        Fetch equipment data and format into InfluxDB InfluxPoint objects.

        This method is called by MeasurePhase whenever the watcher triggers a measurement event.
        The input 'data' parameter contains dummy data from the watcher and should typically
        be ignored - this method should fetch fresh data from the equipment itself.

        For real adapters, this is where you:
        1. Connect to equipment (API, gRPC, serial port, etc.)
        2. Fetch current readings
        3. Transform into InfluxPoint objects
        4. Handle errors (return False or empty set on failure)

        Args:
            data: Dummy data from watcher (typically ignored due to the interval process - fetch real data instead!)

        Returns:
            set[InfluxPoint]: Set of InfluxPoint objects, each representing one metric
            Can also return False or empty set if equipment is unavailable or no data was fetched

        InfluxPoint Structure:
            - measurement: Database table name (e.g., "bioreactor_example")
            - time: UTC timestamp for when the reading was taken
            - tags: Metadata about the equipment instance (e.g., entity tag, device_id, ...)
            - metric: What is being measured (e.g., "temperature", "pH")
            - unit: Unit of measurement (e.g., "celsius", "rpm")
            - fields: The actual data values (dict with at least "value" key)

        Note: Create ONE InfluxPoint per metric. If your equipment returns 10 different
        measurements (temp, pH, pressure, etc.), create 10 separate InfluxPoint objects.
        This allows the backend to efficiently store and query individual metrics.
        """
        logger.debug(f"Measurement triggered by watcher with data: {data}")
        logger.debug(f"Fetching fresh equipment data (ignoring watcher input)...")

        # OPTIONAL: Add instance metadata as tags to InfluxPoint objects
        # This commented example shows how to attach YAML configuration data as tags
        # Uncomment and modify for your real adapter if you need equipment metadata in InfluxDB
        # for key, value in self.metadata_manager.get_instance_data().items():
        #     key = key.lower().split("(")[0].strip().replace(" ", "_")
        #     if isinstance(value, (str, int, float)):
        #         influx_object.add_tag(key, value)

        # Get current UTC timestamp - all measurements in this poll share the same timestamp
        now = datetime.now(timezone.utc)

        # Create a set to hold all InfluxPoint objects (one per metric)
        influx_objects = set()

        # EXAMPLE 1: Temperature measurement
        # Generate random temperature data (in real adapter, this would come from equipment)
        temperature = round(random.uniform(25.0, 30.0), 2)

        # Create a new InfluxPoint for temperature
        influx_object = InfluxPoint()
        influx_object.measurement = self.metadata_manager._equipment_data['adapter_id']  # Table/measurement name
        influx_object.time = now                          # When this reading was taken
        influx_object.set_entity_tag("bioreactor 1")      # Which equipment instance
        influx_object.set_metric("temperature")           # What we're measuring
        influx_object.set_unit("celsius")                 # Unit of measurement
        influx_object.add_field("value", temperature)     # The actual reading value
        influx_objects.add(influx_object)                 # Add to our set

        # EXAMPLE 2: pH measurement
        # Same structure as temperature, but for pH (note: no unit specified for pH)
        ph = round(random.uniform(6.5, 7.5), 1)
        influx_object = InfluxPoint()
        influx_object.measurement = "bioreactor_example"
        influx_object.time = now
        influx_object.set_entity_tag("bioreactor 1")
        influx_object.set_metric("pH")
        influx_object.add_field("value", ph)
        influx_objects.add(influx_object)

        # EXAMPLE 3: Agitation speed measurement
        # Shows how to specify units (rpm) for mechanical measurements
        agitation_speed = round(random.uniform(100, 200), 0)
        influx_object = InfluxPoint()
        influx_object.measurement = "bioreactor_example"
        influx_object.time = now
        influx_object.set_entity_tag("bioreactor 1")
        influx_object.set_metric("agitation_speed")
        influx_object.set_unit("rpm")
        influx_object.add_field("value", agitation_speed)
        influx_objects.add(influx_object)

        for influx_object in influx_objects:
            logger.debug(f"InfluxPoint: {influx_object}")

        # Return all InfluxPoint objects - the framework will handle publishing to MQTT/InfluxDB
        return influx_objects

    # metadata() method is optional - using default from AbstractInterpreter
    # If you need custom metadata processing, uncomment and implement:
    #
    # def metadata(self, data: Any) -> dict[str, Any]:
    #     """Handle equipment metadata when experiment starts."""
    #     logger.info(f"START EVENT - Metadata called with: {data}")
    #     base_metadata = super().metadata(data)  # Records start timestamp
    #     # Add your custom metadata processing here
    #     return base_metadata

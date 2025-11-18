import os
from typing import Optional

from leaf.adapters.core_adapters.discrete_experiment_adapter import DiscreteExperimentAdapter
from leaf.error_handler import error_holder
from leaf.error_handler.error_holder import ErrorHolder
from leaf.modules.input_modules.external_event_watcher import ExternalEventWatcher
from leaf.modules.input_modules.polling_watcher import PollingWatcher
from leaf.modules.input_modules.simple_watcher import SimpleWatcher
from leaf.utility.logger.logger_utils import get_logger
from leaf_register.metadata import MetadataManager

# Interpreter used by this adapter
from leaf_example.interpreter import Interpreter

# Creating a logger using the LEAF framework environment
logger = get_logger(__name__, log_file="app.log")

# Read metadata file from current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
metadata_fn = os.path.join(current_dir, 'device.json')

# The adapter class
class Adapter(DiscreteExperimentAdapter):
    """
    Adapter class for managing discrete experiment connections and simulation.

    This class is designed to connect to discrete experiments, manage their metadata,
    and provide capabilities for interpreting data and running simulations. It handles
    polling operations, manages metadata, and facilitates external interactions through
    its watcher mechanisms.

    Attributes:
        instance_data: The data related to the discrete experiment instance.
        output: Output mechanism for the experiment process.
        maximum_message_size (Optional[int]): Maximum size of messages to be handled, in bytes.
        error_holder (Optional[ErrorHolder]): Instance to hold and manage any error details.
        experiment_timeout (Optional[int]): Experiment timeout duration in seconds.
        external_watcher (ExternalEventWatcher): External watcher for events and updates.
        # Additional variables such as
        interval (int): Time interval in seconds between polling operations.
        # Are obtained from the yaml configuration file
        # More variables can be added as needed and if no default value is provided,
        # they will be mandatory in the yaml configuration file.

    Raises:
        ValueError: If instance_data is None or is an empty dict.
    """
    def __init__(
        self,
        instance_data,
        output,
        interval: int = 100,
        maximum_message_size: Optional[int] = 1,
        error_holder: Optional[ErrorHolder] = None,
        experiment_timeout: int|None=None,
        external_watcher: ExternalEventWatcher = None
        ) -> None:

        # Validate that instance_data is provided (required for adapter initialization)
        if instance_data is None or instance_data == {}:
            raise ValueError("Instance data cannot be empty")

        # This variable is used to control the polling interval and is set by the configuration file
        logger.info(f"Interval: {interval}")

        metadata_manager = MetadataManager()

        # Creating a SimpleWatcher - a simple polling-based watcher
        # The watcher polls every 'interval' seconds and triggers the interpreter's measurement() method
        # There are other adapters availabe such as the HTTPWatcher, ExternalApiWatcher, or other custom watchers
        # for lifecycle management
        watcher: PollingWatcher = SimpleWatcher(
            metadata_manager=metadata_manager,
            interval=interval
        )

        # The Interpreter is responsible for HOW to collect and format data
        # It will be called by the watcher whenever it's time to take a measurement
        # The interpreter handles data retrieval, formatting to InfluxDB format, and metadata processing
        self.interpreter = Interpreter(metadata_manager=metadata_manager)

        # Initialize the base DiscreteExperimentAdapter class
        # This parent class provides the core adapter lifecycle: start, stop, data flow management
        # It connects the watcher (WHEN), interpreter (HOW), and output (WHERE) components
        super().__init__(instance_data=instance_data,
                         watcher=watcher,
                         output=output,
                         interpreter=self.interpreter,
                         maximum_message_size=maximum_message_size,
                         error_holder=error_holder,
                         metadata_manager=metadata_manager,
                         experiment_timeout=experiment_timeout,
                         external_watcher=external_watcher)

        # Load equipment metadata from device.json into the metadata manager
        # This makes equipment information (adapter_id, manufacturer, etc.) accessible throughout the adapter
        self._metadata_manager.add_equipment_data(metadata_fn)
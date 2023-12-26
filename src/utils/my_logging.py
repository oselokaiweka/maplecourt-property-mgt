import os
import logging

from src.utils.file_paths import dir_path, read_config

def mc_logger(log_name, log_level, log_file=None, logger_instance=None):
    """
    Summary:
        Configure a logger_instance with specified parameters. Allows for passing existing logger_instance instances 
        with custom configuration which permits for testing, seamless integration and flexibility.
    Args:
        log_name (str): use abbreviated script file name and '_logger' suffix as log name
        log_level (str): sets the logging level to WARNING, INFO, DEBUG
        log_file (str, optional): Specifies file path where log is saved. Defaults to None.
        logger_instance (str, optional): Existing logger_instance. Defaults to None.
    Raises:
        ValueError: Checks for invalid log level specified.
        ValueError: Checks for invalid existing logger_instance specified.
    Returns:
        logger_instance: Configured logger_instance object
    """  
    # Validate log level specified
    if not hasattr(logging, log_level):
        raise ValueError(f"Invalid log level specified: {log_level}")
    
    # Validate existing logger_instance if provided
    if logger_instance is not None and not isinstance(logger_instance, logging.Logger):
        raise ValueError(f"Invalid logger_instance instance specified: {logger_instance}")

    # Configure root logger_instance only if not already configured
    if logger_instance is None or not hasattr(logging, logger_instance):
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger_instance = logging.getLogger(log_name)

        if log_file is not None:
            config = read_config()
            log_file_path = os.path.join(config.get('AppLogs', 'app_logs_directory'), log_file)
            
            file_handler = logging.FileHandler(log_file_path , mode='w')
            logger_instance.addHandler(file_handler)
        else:
            # If log_file is not specified, log to console.
            console_handler = logging.StreamHandler()
            logger_instance.addHandler(console_handler)
    

    return logger_instance


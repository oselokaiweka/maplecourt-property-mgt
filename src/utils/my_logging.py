import os
import logging

from src.utils.file_paths import dir_path, read_config

def mc_logger(log_name, log_level, log_file=None, logger=None):
    """
    Summary:
        Configure a logger with specified parameters. Allows for passing existing logger instances 
        with custom configuration which permits for testing, seamless integration and flexibility.
    Args:
        log_name (str): use abbreviated script file name and '_logger' suffix as log name
        log_level (str): sets the logging level to WARNING, INFO, DEBUG
        log_file (str, optional): Specifies file path where log is saved. Defaults to None.
        logger (str, optional): Existing logger instance. Defaults to None.
    Raises:
        ValueError: Checks for invalid log level specified.
        ValueError: Checks for invalid existing logger instance specified.
    Returns:
        logger: Configured logger object
    """  
    # Validate log level specified
    if not hasattr(logging, log_level):
        raise ValueError(f"Invalid log level specified: {log_level}")
    
    # Validate existing logger if provided
    if logger is not None and not isinstance(logger, logging.Logger):
        raise ValueError(f"Invalid logger instance specified: {logger}")

    # Configure root logger only if not already configured
    if logger is None or not hasattr(logging, logger):
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(log_name)

        if log_file is not None:
            config = read_config()
            log_file_path = os.path.join(config.get('AppLogs', 'app_logs_directory'), log_file)
            
            file_handler = logging.FileHandler(log_file_path , mode='w')
            file_handler.flush = True
            logger.addHandler(file_handler)
        else:
            # If log_file is not specified, log to console.
            console_handler = logging.StreamHandler()
            logger.addHandler(console_handler)
    

    return logger


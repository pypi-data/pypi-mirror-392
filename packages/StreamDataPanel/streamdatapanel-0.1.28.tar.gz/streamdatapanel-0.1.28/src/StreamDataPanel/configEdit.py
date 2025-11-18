import os
import json
from typing import Union

# Get the absolute path to the directory containing this script
path_current = os.path.dirname(os.path.abspath(__file__))

# Define the path for the primary configuration file
path_config = os.path.join(path_current, 'config.json' )

# Define the path for the default configuration file (used for reset)
path_config_default = os.path.join(path_current, 'configDefault.json' )

def config_load_from(path: str):
    """
    Loads configuration content from a specified JSON file path.

    Parameters
    ----------
    path : str
        The full path to the JSON configuration file.

    Returns
    -------
    Dict[str, Any]
        The loaded configuration dictionary.
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    return content

def config_save_to(content: dict, path: str):
    """
    Saves configuration content to a specified JSON file path.

    Parameters
    ----------
    content : dict
        The configuration dictionary to save.
    path : str
        The full path to the JSON configuration file.
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

def config_load():
    """
    Loads the primary configuration from 'config.json'.

    Returns
    -------
    Dict[str, Any]
        The loaded configuration dictionary.
    """
    return config_load_from(path_config)

def config_save(content: dict):
    """
    Saves the given content back to the primary configuration file 'config.json'.

    Parameters
    ----------
    content : dict
        The configuration dictionary to save.
    """
    config_save_to(content, path_config)

def config_reset():
    """
    Resets the primary configuration file 'config.json' 
    by copying the content from 'configDefault.json'.
    """
    default = config_load_from(path_config_default)
    config_save(default)

def config_update_by(content: dict, config_type: str, config_item: str, config_value: Union[str, int]):
    """
    Updates a specific configuration item within a given configuration dictionary.

    Parameters
    ----------
    content : dict
        The configuration dictionary to modify.
    config_type : str
        The top-level key (e.g., 'API_CONFIG') under which the item resides.
    config_item : str
        The specific item key to update (e.g., 'port').
    config_value : Union[str, int]
        The new value for the configuration item.

    Returns
    -------
    Dict[str, Any]
        The updated configuration dictionary.
    """
    content[config_type][config_item] = config_value
    return content

def config_update(config_type: str, config_item: str, config_value: Union[str, int]):
    """
    Loads the primary configuration, updates a specific item, and saves it back 
    to 'config.json'.

    Parameters
    ----------
    config_type : str
        The top-level key (e.g., 'API_CONFIG').
    config_item : str
        The specific item key to update (e.g., 'port').
    config_value : Union[str, int]
        The new value for the configuration item.
    """
    content = config_load()
    content = config_update_by(content, config_type, config_item, config_value)
    config_save(content)





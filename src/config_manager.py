from configparser import ConfigParser

class ConfigManager:
    """
    provides methods to load, save, and access config values
    stored in the INI file. uses ConfigParser to handle the file I/O
    and data storage.
    
    attributes:
        config (ConfigParser): the ConfigParser object used to manage the configuration.
    """
    def __init__(self):
        """
        init the ConfigManager.
        
        creates a new ConfigParser object and loads the existing config.
        """
        self.config = ConfigParser()
        self.load_config()

    def load_config(self):
        """
        load the config from 'timer.ini'
        
        if the INI file doesn't exist or is empty, this method ensures that a 'section'
        exists in the config and saves it to create the INI file with default values.
        """
        self.config.read('timer.ini')
        
        if not self.config.has_section('section'):
            self.config.add_section('section')
        
        self.save_config()

    def save_config(self):
        """
        save current config to 'timer.ini'
        
        this method writes current state of the config to the INI file,
        overwriting any existing content.
        """
        with open('timer.ini', 'w') as configfile:
            self.config.write(configfile)

    def get_value(self, key, default_value):
        """
        retrieve a value from the config.

        this method returns the value associated with given key. if key
        doesn't exist, it returns the default value. method automatically
        converts return value to appropriate type based on default value.

        args:
            key (str): key of the config item to retrieve.
            default_value (Any): default value to return if key doesn't exist.

        returns:
            value associated with the key, or default value if key doesn't exist.
            return type matches type of default_value.
        """
        if isinstance(default_value, bool):
            return self.config.getboolean('section', key, fallback=default_value)
        elif isinstance(default_value, int):
            return self.config.getint('section', key, fallback=default_value)
        else:
            return self.config.get('section', key, fallback=default_value)

    def set_value(self, key, value):
        """
        set a value in the config.
        
        this method sets value for the given key in the 'section' of the config.
        value is converted to a string before storing.

        args:
            key (str): key of the config item to set.
            value (Any): value to set for the given key.
        """
        self.config.set('section', key, str(value))

    def get_all_programs(self):
        """
        retrieves all configured programs (Program 1, Program2, Program3).
        if a program is not set, an empty string is returned instead.

        returns:
            list: a list containing the values of Program1, Program2, Program3.
        """
        return [
            self.get_value('Program1', ''),
            self.get_value('Program2', ''),
            self.get_value('Program3', '')
        ]
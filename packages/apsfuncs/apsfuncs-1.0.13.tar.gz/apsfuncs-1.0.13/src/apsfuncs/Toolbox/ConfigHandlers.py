import os, sys, json, tempfile

# Function to return the resource path
def get_resource_path(single_file_exe=False):
    # Check if the program is running as an exe or in the IDE and return the appropriate path for each
    if getattr(sys, 'frozen', False):
        # If the program has been flagged as a single_file_exe then return the temp location, otherwise return the _internal folder location
        if single_file_exe:
            return os.path.join(tempfile.mkdtemp(), 'resources')
        else:
            return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '_internal', 'resources')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'resources')

# Function to return the crash log path
def get_crash_log_path(single_file_exe=False):
    # Check if the program is running as an exe or in the IDE and return the appropriate path for each
    if getattr(sys, 'frozen', False):
        # If the program has been flagged as a single_file_exe then return the temp location, otherwise return the _internal folder location
        if single_file_exe:
            return os.path.join(tempfile.mkdtemp(), 'held_crash_logs')
        else:
            return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '_internal', 'held_crash_logs')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'held_crash_logs')
    
# Function to return the held feedback path
def get_held_feedback_path(single_file_exe=False):
    # Check if the program is running as an exe or in the IDE and return the appropriate path for each
    if getattr(sys, 'frozen', False):
        # If the program has been flagged as a single_file_exe then return the temp location, otherwise return the _internal folder location
        if single_file_exe:
            return os.path.join(tempfile.mkdtemp(), 'held_feedback')
        else:
            return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '_internal', 'held_feedback')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'held_feedback')

# Function to return the logs folder
def get_logs_path(single_file_exe=False):
    if getattr(sys, 'frozen', False):
        # If the program has been flagged as a single_file_exe then return the temp location, otherwise return the _internal folder location
        if single_file_exe:
            return os.path.join(tempfile.mkdtemp(), 'logs')
        else:
            return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '_internal', 'logs')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'logs')

# Function to read in the program config json
def load_config(single_file_exe=False):
    # Set the config file path and read in the json
    config_file_loc = os.path.join(get_resource_path(single_file_exe=single_file_exe), "config.json")
    with open(config_file_loc) as config_file:
        config_dict = json.load(config_file)
    # Return the config dictionary
    return config_dict

# Method to overwrite the config dictionary with the passed dictionary
def update_saved_config_dict(new_config_dict, single_file_exe=False):
    # Set the config file path and dump the config dict into it
    config_file_loc = os.path.join(get_resource_path(single_file_exe=single_file_exe), "config.json")
    with open(config_file_loc, 'w') as config_file:
        json.dump(new_config_dict, config_file, indent=4)
    

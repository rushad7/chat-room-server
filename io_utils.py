import os
import json
import yaml


def jsonify_env_var(env_var: str, filename: str) -> None:
    
    if filename.split(".")[1] != "json":
        raise NameError 

    env_var_content = os.environ.get(env_var)
    file_data = json.loads(env_var_content)
    
    with open(filename, 'w') as file:
            json.dump(file_data, file)


def yamlify_env_var(env_var: str, filename: str) -> None:

    if filename.split(".")[1] not in ["yaml", "yml"]:
        raise NameError

    env_var_content = os.environ.get(env_var)
    loader = yaml.SafeLoader(env_var_content)

    try:
        file_data = loader.get_single_data()
    finally:
        loader.dispose()
        
    with open(filename, 'w') as file:
        yaml.dump(file_data, file, default_flow_style=False)

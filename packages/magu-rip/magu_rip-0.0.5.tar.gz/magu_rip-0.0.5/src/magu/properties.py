import os
import importlib.util

def load_properties():
    project_root = os.getcwd()
    
    prop_path = os.path.join(project_root, "properties.py")

    if not os.path.exists(prop_path):
        raise FileNotFoundError(
            f"[Magu] properties.py not found at {prop_path}"
        )

    spec = importlib.util.spec_from_file_location("user_properties", prop_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

props = load_properties()

DATABASE_HOST = props.DATABASE_HOST
DATABASE_USER = props.DATABASE_USER
DATABASE_PASSWORD = props.DATABASE_PASSWORD
DATABASE_PORT=props.DATABASE_PORT
DATABASE_NAME = props.DATABASE_NAME

SERVER_HOST=props.SERVER_HOST
SERVER_PORT=props.SERVER_PORT
SERVER_ADDRESS=props.SERVER_ADDRESS

SECRET_KEY=props.SECRET_KEY

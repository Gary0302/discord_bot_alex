from dotenv import load_dotenv, set_key, find_dotenv
load_dotenv()
import os
os.environ["abc"] = "123q"
set_key(find_dotenv(), "EXISTING_VARIABLE", "modified_value")
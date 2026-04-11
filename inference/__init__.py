import os

os.environ["HF_HOME"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".huggingface", "models") # set huggingface cache to this project's root

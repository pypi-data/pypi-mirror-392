# jupyter_ai_wekeo

`jupyter_ai_wekeo` is a Jupyter AI module, a package
that registers additional model providers and slash commands for the Jupyter AI
extension.

## Requirements

- Python 3.8 - 3.12
- JupyterLab 4

## Install

To install the extension, execute:

```bash
pip install jupyter-ai-wekeo
```

## Config

1. Locate or create the Jupyter AI configuration file `jupyter_jupyter_ai_config.py`. You can copy it into the Jupyter config folder, which can be discovered with:

```bash
jupyter --paths
```

2. Edit `jupyter_jupyter_ai_config.py` to add the server endpoint:

```python
c = get_config()

c.AiExtension.default_language_model = "wekeo-provider:server"
c.AiExtension.allowed_providers = ["wekeo-provider", "openai", "openai-chat"]
c.AiExtension.default_max_chat_history = None

c.AiExtension.model_parameters = {
    "wekeo-provider:server": {
        "endpoint": "<http://wekeo-llm-server-endpoint>/rag"
    }
}
```

3. Save the file in the Jupyter config folder so it will be automatically discovered by Jupyter.

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyter-ai-wekeo
```

## Contributing

### Development install

```bash
cd jupyter-ai-wekeo
pip install -e "."
```

### Development uninstall

```bash
pip uninstall jupyter-ai-wekeo
```

#### Backend tests

This package uses [Pytest](https://docs.pytest.org/) for Python testing.

Install test dependencies (needed only once):

```sh
cd jupyter-ai-wekeo
pip install -e ".[test]"
```

To execute them, run:

```sh
pytest -vv -r ap --cov jupyter-ai-wekeo
```

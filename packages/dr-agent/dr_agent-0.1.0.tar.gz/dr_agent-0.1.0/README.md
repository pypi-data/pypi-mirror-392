# `dr-agent-lib`

## Overview

`dr-agent-lib` is an agent library for training and developing deep research agents. It supports:
- **MCP-Based Tool Backend**: Unified interface for web search and browsing tools
- **High Concurrency**: Global caching and async request management for RL training at scale
- **Flexible Prompting Interface**: Easy composition of search workflows with fine-grained control

## Setup 

```bash
conda create -n dr_agent python=3.10 -y && conda activate dr_agent

uv pip install -e .     # Install dev version
uv pip install dr_agent # Install from pypi 
```

## Getting started 

1. Launch MCP Server 

    ```bash
    MCP_CACHE_DIR=".cache-$(hostname)" python -m mcp_agents.mcp_backend.main --port 8000
    ```

2. Start the VLLM Server 

    ```bash 
    CUDA_VISIBLE_DEVICES=0 vllm serve rl-research/DR-Tulu-8B --dtype auto --port 30002 --max-model-len 40960
    
    CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-8B --dtype auto --port 30002 --max-model-len 40960
    ```

3. Run generation script 

    ```bash
    bash scripts/auto_search.sh
    ```

## Publishing to PyPI

To publish the package to PyPI, first install the dev dependencies:

```bash
pip install -e ".[dev]"
```

Then run the publish script:

```bash
# Test on TestPyPI first (recommended)
bash scripts/publish_to_pypi.sh test

# Publish to PyPI
bash scripts/publish_to_pypi.sh
```

You'll need to have PyPI credentials configured. Set up your `~/.pypirc` file or use environment variables for authentication.

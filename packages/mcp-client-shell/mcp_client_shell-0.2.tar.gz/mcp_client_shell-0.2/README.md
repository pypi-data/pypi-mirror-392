# MCP Client Shell
[![Upload Python Package](https://github.com/cafalchio/mcp-client-shell/actions/workflows/python-publish.yml/badge.svg)](https://github.com/cafalchio/mcp-client-shell/actions/workflows/python-publish.yml)
`mcp-client-shell` is a lightweight Python client to interact with FastMCP servers locally.  
It allows you to list available tools, call them with required parameters, and view results directly in your terminal.

## Features

- Connect to a FastMCP server running on your machine.
- List available tools dynamically.
- Call any tool by name or number.
- Async CLI interaction with input prompts.
- Displays results cleanly for easy testing.

## Requirements

- Python 3.10+
- FastMCP >= 2.13.1

## Install

Install via pip:
    pip install mcp-client-shell

Or from source:
    git clone https://github.com/cafalchio/mcp-client-shell.git
    cd mcp-client-shell
    pip install -e .

## Run

    mcp-client-shell
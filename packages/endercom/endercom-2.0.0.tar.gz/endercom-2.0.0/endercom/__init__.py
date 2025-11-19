"""
Endercom Python SDK

A simple Python library for connecting agents to the Endercom communication platform.

This SDK provides two models:
1. Agent (webhook-based) - for webhook-based agent communication
2. AgentFunction (function-based) - for function-based agent implementations
"""

from .agent import Agent, Message, AgentOptions, MessageHandler
from .agent import create_agent
from .function import AgentFunction, create_function

__version__ = "2.0.0"
__all__ = [
    # Agent model (webhook-based)
    "Agent", "Message", "AgentOptions", "MessageHandler", "create_agent",
    # Function-based model
    "AgentFunction", "create_function"
]


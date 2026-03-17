"""
module2/agent.py
================
Core Repository Analysis Agent for Module 2.

This module implements the LangChain-based agent that analyzes git repositories
to identify applications, technology stacks, and AWS infrastructure requirements.

FRAMEWORK COMPARISON
--------------------
Module 1 uses AWS Strands:
    from strands import Agent
    agent = Agent(model=model, tools=tools, system_prompt=prompt)

Module 2 uses LangChain + LangGraph:
    from langchain.agents import create_tool_calling_agent
    from langgraph.prebuilt import create_react_agent
    agent = create_react_agent(model, tools)

Both implement the same think-act-observe loop, but LangGraph provides
explicit state management and better observability through its graph structure.
"""

from __future__ import annotations

import os
from typing import Any

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable

from module2.config.models import get_chat_bedrock_model
from module2.prompts.system_prompts import SYSTEM_PROMPT
from module2.tools.repo_tools import ALL_TOOLS


# ---------------------------------------------------------------------------
# Agent Factory (Simple AgentExecutor approach)
# ---------------------------------------------------------------------------

def create_agent(
    *,
    verbose: bool = True,
    max_iterations: int = 15,
    region: str | None = None,
    streaming: bool = False,
) -> AgentExecutor:
    """
    Create a Module 2 Repository Analysis Agent using LangChain.

    This is the simple approach using AgentExecutor. For the full LangGraph
    state machine workflow, use create_graph_agent() instead.

    The agent uses:
    - ChatBedrock (LangChain) for model access
    - Tool calling agent pattern
    - AgentExecutor for the execution loop
    - Five repository analysis tools

    Parameters
    ----------
    verbose : bool
        Print agent steps and tool calls. Default True for demos.
    max_iterations : int
        Maximum number of agent loop iterations. Default 15.
    region : str, optional
        AWS region override. Falls back to AWS_REGION env var.
    streaming : bool
        Enable streaming responses from the model.

    Returns
    -------
    AgentExecutor
        Configured LangChain agent ready to analyze repositories.

    Example
    -------
    >>> from module2.agent import create_agent
    >>> agent = create_agent()
    >>> result = agent.invoke({"input": "Analyze repository at /path/to/repo"})
    >>> print(result["output"])
    """
    aws_region = region or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"

    # ── REASONING LAYER ──────────────────────────────────────────────────────
    model = get_chat_bedrock_model(region=aws_region, streaming=streaming)
    
    if verbose:
        print(f"  [Module 2 Agent] Using ChatBedrock (LangChain)")
        print(f"  [Model] Claude Sonnet 4 via Amazon Bedrock")
        print(f"  [Region] {aws_region}")
        print(f"  [Tools] {len(ALL_TOOLS)} repository analysis tools")
        print()

    # ── PROMPT TEMPLATE ──────────────────────────────────────────────────────
    # LangChain uses ChatPromptTemplate for structured prompts
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # ── AGENT CONSTRUCTION ───────────────────────────────────────────────────
    # Create tool-calling agent (supports Claude's tool use format)
    agent = create_tool_calling_agent(model, ALL_TOOLS, prompt)

    # ── EXECUTION LOOP ───────────────────────────────────────────────────────
    # AgentExecutor handles the think-act-observe loop
    agent_executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=verbose,
        max_iterations=max_iterations,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )

    return agent_executor


# ---------------------------------------------------------------------------
# Graph-Based Agent Factory (LangGraph approach)
# ---------------------------------------------------------------------------

def create_graph_agent(
    *,
    verbose: bool = True,
    region: str | None = None,
) -> Runnable:
    """
    Create a Module 2 Repository Analysis Agent using LangGraph state machine.

    This approach uses the explicit workflow defined in analysis_graph.py
    with five stages: scan → detect → analyze → map → synthesize.

    The LangGraph approach provides:
    - Better observability (see each stage transition)
    - Conditional branching (skip stages if needed)
    - Parallel execution (analyze multiple apps simultaneously)
    - State persistence (save/resume analysis)

    Parameters
    ----------
    verbose : bool
        Print workflow stage transitions. Default True.
    region : str, optional
        AWS region override.

    Returns
    -------
    Runnable
        Compiled LangGraph workflow ready to invoke.

    Example
    -------
    >>> from module2.agent import create_graph_agent
    >>> agent = create_graph_agent()
    >>> result = agent.invoke({
    ...     "repo_path": "/path/to/repo",
    ...     "messages": [],
    ...     "current_stage": "init",
    ... })
    >>> print(result["analysis_report"])
    """
    from langgraph.prebuilt import create_react_agent
    
    from module2.config.models import get_chat_bedrock_model
    from module2.tools.repo_tools import ALL_TOOLS
    
    aws_region = region or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    
    # Get model
    model = get_chat_bedrock_model(region=aws_region)
    
    if verbose:
        print(f"  [Module 2 Graph Agent] Using LangGraph state machine")
        print(f"  [Model] ChatBedrock - Claude Sonnet 4")
        print(f"  [Workflow] scan → detect → analyze → map → synthesize")
        print()
    
    # Create ReAct agent with LangGraph
    # This provides the basic agent loop that we'll enhance with our workflow
    agent = create_react_agent(
        model,
        ALL_TOOLS,
        state_modifier=SYSTEM_PROMPT,
    )
    
    return agent


# ---------------------------------------------------------------------------
# Convenience Functions
# ---------------------------------------------------------------------------

def analyze_repository(repo_path: str, verbose: bool = True) -> dict[str, Any]:
    """
    Analyze a repository and return structured results.

    This is a convenience function that creates an agent, runs the analysis,
    and returns the results in a structured format.

    Parameters
    ----------
    repo_path : str
        Absolute path to the git repository to analyze.
    verbose : bool
        Print agent steps during analysis.

    Returns
    -------
    dict
        Analysis results with applications, stacks, and AWS requirements.

    Example
    -------
    >>> from module2.agent import analyze_repository
    >>> results = analyze_repository("/path/to/my-repo")
    >>> print(f"Found {len(results['applications'])} applications")
    """
    agent = create_agent(verbose=verbose)
    
    query = f"""Analyze the git repository at: {repo_path}

Please:
1. Scan the repository structure
2. Detect all applications/services
3. Analyze the technology stack for each application
4. Map dependencies to AWS infrastructure requirements
5. Provide a comprehensive analysis report

Return the results as structured JSON."""

    result = agent.invoke({"input": query})
    
    return {
        "repo_path": repo_path,
        "output": result.get("output", ""),
        "intermediate_steps": result.get("intermediate_steps", []),
    }

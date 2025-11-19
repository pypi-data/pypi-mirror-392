"""
Function calling integration for Cite-Agent.

Handles the function calling workflow:
1. Send user query to LLM with available tools
2. Parse LLM response for tool calls
3. Execute requested tools
4. Send results back to LLM for final response
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .function_tools import TOOLS, validate_tool_call


@dataclass
class ToolCall:
    """Represents a tool call from the LLM"""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class FunctionCallingResponse:
    """Response from function calling workflow"""
    response: str  # Final text response
    tool_calls: List[ToolCall]  # Tools that were called
    tool_results: Dict[str, Any]  # Results from tool executions
    tokens_used: int = 0
    model: str = ""
    assistant_message: Optional[Any] = None  # Original assistant message with tool_calls


def format_tool_result(tool_name: str, result: Dict[str, Any]) -> str:
    """
    Format tool results into concise, structured summaries for synthesis.
    Reduces token usage and improves LLM understanding.
    """
    if "error" in result:
        return f"Error: {result['error']}"

    # Format based on tool type
    if tool_name == "search_papers":
        papers = result.get("papers", [])
        count = len(papers)
        if count == 0:
            return "No papers found"

        # Concise paper list with key info (optimized for synthesis)
        paper_summaries = []
        for i, p in enumerate(papers[:5], 1):  # Max 5 papers in summary
            title = p.get("title", "Unknown")[:100]  # Slightly longer titles
            year = p.get("year", "N/A")
            citations = p.get("citations_count", 0)
            authors = p.get("authors", [])
            first_author = authors[0].get("name", "Unknown") if authors else "Unknown"
            doi = p.get("doi", "")

            # Compact format: Title (FirstAuthor, Year) - citations cites [DOI]
            summary = f"{i}. {title} ({first_author}, {year})"
            if citations > 0:
                summary += f" - {citations:,} citations"
            if doi:
                summary += f" [DOI: {doi}]"
            paper_summaries.append(summary)

        return f"Found {count} papers:\n" + "\n".join(paper_summaries)

    elif tool_name == "get_financial_data":
        ticker = result.get("ticker", "Unknown")
        data = result.get("data", {})

        # Extract key metrics
        summaries = []
        for metric, info in data.items():
            if isinstance(info, dict):
                value = info.get("value", "N/A")
                period = info.get("period", "")
                summaries.append(f"{metric}: ${value:,.0f}" if isinstance(value, (int, float)) else f"{metric}: {value}")

        return f"{ticker} - " + ", ".join(summaries) if summaries else json.dumps(result)[:200]

    elif tool_name == "list_directory":
        listing = result.get("listing", "")
        lines = listing.split("\n")[:10]  # Max 10 lines
        return "\n".join(lines) + ("...[more files]" if len(listing.split("\n")) > 10 else "")

    elif tool_name == "export_to_zotero":
        if result.get("success"):
            filename = result.get("filename", "")
            count = result.get("papers_count", 0)
            format_type = result.get("format", "")
            return f"✅ Exported {count} papers to {filename} ({format_type.upper()} format). Import via File → Import in Zotero."
        return result.get("message", json.dumps(result)[:200])

    elif tool_name == "find_related_papers":
        count = result.get("count", 0)
        method = result.get("method", "")
        if count == 0:
            return "No related papers found"

        papers = result.get("related_papers", [])
        paper_summaries = []
        for p in papers[:5]:  # Max 5 in summary
            title = p.get("title", "Unknown")[:80]
            year = p.get("year", "N/A")
            citations = p.get("citations_count", 0)
            paper_summaries.append(f"- {title} ({year}, {citations} cites)")

        base_paper = result.get("base_paper", {})
        base_title = base_paper.get("title", "")[:60] if base_paper else "query"

        return f"Found {count} papers related to '{base_title}' via {method}:\n" + "\n".join(paper_summaries)

    elif tool_name == "chat":
        return result.get("message", "")

    elif tool_name == "load_dataset":
        # CRITICAL: Format dataset loading to show statistics prominently
        rows = result.get("rows", 0)
        columns = result.get("columns", 0)
        col_names = result.get("column_names", [])

        output = f"Dataset loaded: {rows} rows × {columns} columns\n"
        output += f"Columns: {', '.join(col_names)}\n"

        # CRITICAL: Show computed statistics if available
        if "column_statistics" in result:
            output += "\n=== COMPUTED STATISTICS (USE THESE VALUES) ===\n"
            for col, stats in result["column_statistics"].items():
                output += f"{col}:\n"
                output += f"  mean = {stats['mean']:.6f}\n"
                output += f"  std = {stats['std']:.6f}\n"
                output += f"  min = {stats['min']:.6f}\n"
                output += f"  max = {stats['max']:.6f}\n"
                output += f"  median = {stats['median']:.6f}\n"
            output += "=== END STATISTICS ===\n"
            output += "\nIMPORTANT: These statistics are already computed. Report them directly to user.\n"

        return output

    elif tool_name == "analyze_data":
        # Format analysis results concisely
        if "column" in result:
            # Single column stats
            col = result["column"]
            output = f"Statistics for {col}:\n"
            output += f"  mean = {result.get('mean', 'N/A')}\n"
            output += f"  std = {result.get('std', 'N/A')}\n"
            output += f"  min = {result.get('min', 'N/A')}\n"
            output += f"  max = {result.get('max', 'N/A')}\n"
            output += f"  median = {result.get('median', 'N/A')}\n"
            return output
        elif "stats" in result:
            # All columns stats
            output = "Statistics for all numeric columns:\n"
            for col, stats in result["stats"].items():
                output += f"{col}: mean={stats['mean']:.4f}, std={stats['std']:.4f}\n"
            return output
        return json.dumps(result)[:400]

    elif tool_name == "run_python_code":
        # Format Python execution results
        if result.get("success"):
            code = result.get("code", "")
            res = result.get("result", "")
            result_type = result.get("result_type", "")
            return f"Code executed: {code[:100]}...\nResult ({result_type}):\n{res[:1000]}"
        return result.get("error", json.dumps(result)[:400])

    # Default: truncated JSON
    return json.dumps(result)[:400]


class FunctionCallingAgent:
    """
    Handles function calling workflow with Cerebras/OpenAI compatible APIs.
    """

    def __init__(self, client, model: str = "gpt-oss-120b", provider: str = "cerebras"):
        """
        Initialize function calling agent.

        Args:
            client: OpenAI-compatible client (Cerebras or OpenAI)
            model: Model name to use
            provider: Provider name ('cerebras' or 'openai')
        """
        self.client = client
        self.model = model
        self.provider = provider
        self.debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"

    async def process_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> FunctionCallingResponse:
        """
        Process a query using function calling.

        Workflow:
        1. Call LLM with query + tools
        2. If LLM wants to call tools:
           a. Execute tools
           b. Send results back to LLM
           c. Get final response
        3. Return final response

        Args:
            query: User query
            conversation_history: Previous messages
            system_prompt: Optional system prompt override

        Returns:
            FunctionCallingResponse with final answer and metadata
        """
        if conversation_history is None:
            conversation_history = []

        # Build messages
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            # Default system prompt (compressed for token efficiency)
            messages.append({
                "role": "system",
                "content": (
                    "Route queries to tools: papers/research→search_papers, "
                    "financials/stocks→get_financial_data, files/folders→list_directory, "
                    "shell commands→execute_shell_command, news/current events→web_search. "
                    "Use chat only for greetings/thanks. Prefer action tools."
                )
            })

        # Add conversation history
        messages.extend(conversation_history)

        # Add current query
        messages.append({"role": "user", "content": query})

        if self.debug_mode:
            print(f"🔍 [Function Calling] Sending query to {self.provider}: {query[:100]}...")

        # Step 1: Initial LLM call with tools
        try:
            if self.debug_mode:
                print(f"🔍 [Function Calling] Calling {self.provider} with model {self.model}")

            # Add timeout to prevent hanging
            import httpx
            timeout = httpx.Timeout(30.0, connect=10.0)  # 30s total, 10s connect

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",  # Let LLM decide
                temperature=0.2,  # Low temperature for more consistent tool selection
                timeout=timeout
            )

            if self.debug_mode:
                print(f"🔍 [Function Calling] Got response from {self.provider}")

        except Exception as e:
            error_str = str(e)

            # Check if it's a rate limit error (429)
            if "429" in error_str or "rate" in error_str.lower() or "queue" in error_str.lower():
                if self.debug_mode:
                    print(f"⚠️ [Function Calling] {self.provider} rate limited (429)")
                # Return user-friendly rate limit message
                return FunctionCallingResponse(
                    response="The AI service is experiencing high traffic right now. Please try again in a moment.",
                    tool_calls=[],
                    tool_results={},
                    tokens_used=0
                )

            if self.debug_mode:
                print(f"❌ [Function Calling] LLM call failed: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()

            # Fallback: return error as chat response
            return FunctionCallingResponse(
                response=f"I encountered an error calling the LLM: {str(e)}",
                tool_calls=[],
                tool_results={},
                tokens_used=0
            )

        message = response.choices[0].message
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0

        # Check if LLM wants to call tools
        if not message.tool_calls:
            # Direct response (chat tool or no tools needed)
            if self.debug_mode:
                print(f"🔍 [Function Calling] No tool calls, direct response")

            return FunctionCallingResponse(
                response=message.content or "I'm not sure how to help with that.",
                tool_calls=[],
                tool_results={},
                tokens_used=tokens_used,
                model=self.model
            )

        # Step 2: Execute tool calls
        if self.debug_mode:
            print(f"🔍 [Function Calling] {len(message.tool_calls)} tool(s) requested")

        tool_calls_list = []
        tool_results = {}
        tool_messages = []  # For sending back to LLM

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                if self.debug_mode:
                    print(f"❌ [Function Calling] Invalid JSON in arguments: {e}")
                tool_args = {}

            if self.debug_mode:
                print(f"🔍 [Function Calling] Tool: {tool_name}, Args: {tool_args}")

            # Validate tool call
            is_valid, error_msg = validate_tool_call(tool_name, tool_args)
            if not is_valid:
                if self.debug_mode:
                    print(f"❌ [Function Calling] Validation failed: {error_msg}")
                tool_results[tool_call.id] = {"error": error_msg}
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": error_msg})
                })
                continue

            # Store tool call
            tool_calls_list.append(ToolCall(
                id=tool_call.id,
                name=tool_name,
                arguments=tool_args
            ))

            # Tool execution happens in the main agent
            # For now, we just mark it as pending
            tool_results[tool_call.id] = {
                "tool": tool_name,
                "args": tool_args,
                "status": "pending"
            }

        # Return tool calls for execution by main agent
        # The main agent will execute tools and call finalize_response()
        return FunctionCallingResponse(
            response="",  # No final response yet
            tool_calls=tool_calls_list,
            tool_results=tool_results,
            tokens_used=tokens_used,
            model=self.model,
            assistant_message=message  # Include original assistant message for finalize
        )

    async def finalize_response(
        self,
        original_query: str,
        conversation_history: List[Dict[str, str]],
        tool_calls: List[ToolCall],
        tool_execution_results: Dict[str, Any],
        assistant_message: Optional[Any] = None
    ) -> FunctionCallingResponse:
        """
        Get final response from LLM after tools have been executed.

        Args:
            original_query: Original user query
            conversation_history: Conversation history
            tool_calls: Tool calls that were made
            tool_execution_results: Results from executing tools
            assistant_message: Original assistant message with tool_calls (optional)

        Returns:
            Final response from LLM
        """
        # OPTIMIZATION: Skip synthesis for simple/obvious responses (saves 500-1500 tokens each)
        if len(tool_calls) == 1:
            tool_name = tool_calls[0].name
            result = tool_execution_results.get(tool_calls[0].id, {})

            # Case 1: Simple chat (hi, thanks, etc.)
            if (tool_name == "chat" and len(original_query.split()) <= 3):
                if "message" in result:
                    if self.debug_mode:
                        print(f"🔍 [Function Calling] Skipping synthesis for simple chat (token optimization)")
                    return FunctionCallingResponse(
                        response=result["message"],
                        tool_calls=tool_calls,
                        tool_results=tool_execution_results,
                        tokens_used=0,  # No second LLM call
                        model=self.model
                    )

            # Case 2: Single directory listing (just show the output)
            elif tool_name == "list_directory" and "listing" in result:
                if self.debug_mode:
                    print(f"🔍 [Function Calling] Skipping synthesis for directory listing (token optimization)")
                path = result.get("path", ".")
                listing = result.get("listing", "")
                return FunctionCallingResponse(
                    response=f"Contents of {path}:\n\n{listing}",
                    tool_calls=tool_calls,
                    tool_results=tool_execution_results,
                    tokens_used=0,
                    model=self.model
                )

            # Case 3: Single file read (just show the content)
            elif tool_name == "read_file" and "content" in result:
                if self.debug_mode:
                    print(f"🔍 [Function Calling] Skipping synthesis for file read (token optimization)")
                file_path = result.get("file_path", "unknown")
                content = result.get("content", "")
                return FunctionCallingResponse(
                    response=f"Contents of {file_path}:\n\n{content}",
                    tool_calls=tool_calls,
                    tool_results=tool_execution_results,
                    tokens_used=0,
                    model=self.model
                )

            # Case 4: Shell command execution - show actual output, not analysis
            elif tool_name == "execute_shell_command" and "output" in result:
                if self.debug_mode:
                    print(f"🔍 [Function Calling] Direct shell output (no synthesis needed)")

                command = result.get("command", "unknown")
                output = result.get("output", "")
                cwd = result.get("working_directory", ".")

                # Detect command type for appropriate formatting
                if command.strip().startswith("cd "):
                    # Directory change - brief confirmation
                    new_dir = result.get("working_directory", output.strip())
                    return FunctionCallingResponse(
                        response=f"Changed to {new_dir}",
                        tool_calls=tool_calls,
                        tool_results=tool_execution_results,
                        tokens_used=0,
                        model=self.model
                    )
                elif any(command.strip().startswith(cmd) for cmd in ["ls", "find", "grep", "cat", "head", "tail", "pwd"]):
                    # File operations - show raw output
                    return FunctionCallingResponse(
                        response=output if output else "(no output)",
                        tool_calls=tool_calls,
                        tool_results=tool_execution_results,
                        tokens_used=0,
                        model=self.model
                    )
                else:
                    # Other commands - show command and output
                    return FunctionCallingResponse(
                        response=f"$ {command}\n{output}" if output else f"$ {command}\n(completed)",
                        tool_calls=tool_calls,
                        tool_results=tool_execution_results,
                        tokens_used=0,
                        model=self.model
                    )

        # Build messages for second LLM call
        messages = conversation_history.copy()

        # If tool_calls is empty, conversation_history already has everything
        # (multi-step execution case)
        if tool_calls:
            # Single-step case: Add assistant message and tool results

            # Add assistant message with tool_calls if provided
            # This is REQUIRED by OpenAI's chat completion API
            if assistant_message and hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

            # Add tool responses (formatted for efficiency and clarity)
            for tool_call in tool_calls:
                result = tool_execution_results.get(tool_call.id, {})

                # Format result into structured summary (reduces tokens, improves synthesis)
                result_str = format_tool_result(tool_call.name, result)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.name,
                    "content": result_str
                })

        if self.debug_mode:
            print(f"🔍 [Function Calling] Sending tool results back to LLM for synthesis")

        # Detect query type for context-aware synthesis
        is_file_operation = any(tc.name in ["list_directory", "read_file", "write_file", "execute_shell_command"] for tc in tool_calls)
        is_research_query = any(tc.name in ["search_papers", "find_related_papers", "export_to_zotero"] for tc in tool_calls)
        is_financial_query = any(tc.name in ["get_financial_data"] for tc in tool_calls)
        is_data_analysis = any(tc.name in ["load_dataset", "analyze_data", "run_regression", "plot_data"] for tc in tool_calls)

        # Context-aware synthesis prompt
        if is_data_analysis:
            # Data analysis: CONCISE, show actual numbers
            synthesis_instruction = {
                "role": "system",
                "content": (
                    "You are a data analysis assistant. Report results concisely.\n\n"
                    "CRITICAL RULES:\n"
                    "- Extract and report the ACTUAL NUMBERS from the tool results\n"
                    "- If user asks for 'mean spread', find the mean value for Spread column and report it\n"
                    "- Format: 'Mean Spread = -0.678' or 'Spread: mean=-0.678, std=0.123'\n"
                    "- Be EXTREMELY BRIEF - just the numbers requested\n"
                    "- NO essays, NO lengthy explanations, NO academic vocabulary\n"
                    "- If data has column_statistics, use those values directly\n"
                    "- Maximum 1-2 sentences for simple stats queries\n"
                    "- NO JSON output"
                )
            }
        elif is_file_operation:
            # File operations: BE CONCISE, show results
            synthesis_instruction = {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Synthesize the tool results concisely.\n\n"
                    "RULES:\n"
                    "- Be BRIEF and DIRECT\n"
                    "- Show actual file contents/listings when relevant\n"
                    "- Don't add unnecessary analysis or recommendations\n"
                    "- If user asked 'ls', just describe what files are there\n"
                    "- If user asked 'find', show what was found\n"
                    "- Maximum 2-3 sentences unless more detail is needed\n"
                    "- NO academic vocabulary unless specifically asked\n"
                    "- NO JSON in output"
                )
            }
        elif is_research_query:
            # Research queries: USE academic vocabulary
            synthesis_instruction = {
                "role": "system",
                "content": (
                    "Synthesize research findings professionally.\n\n"
                    "Use terms: 'paper', 'approach', 'method', 'metric', 'analysis', "
                    "'significant', 'gap', 'limitation', 'recommend', 'suggest'.\n\n"
                    "Cite papers properly with title, authors, year.\n"
                    "NO JSON output - only natural language."
                )
            }
        elif is_financial_query:
            # Financial queries: Factual, numbers-focused
            synthesis_instruction = {
                "role": "system",
                "content": (
                    "Present financial data clearly and accurately.\n\n"
                    "- Report actual numbers from the data\n"
                    "- Include units (millions, billions, percentages)\n"
                    "- Be factual, not speculative\n"
                    "- NO JSON output"
                )
            }
        else:
            # Default: Balanced response
            synthesis_instruction = {
                "role": "system",
                "content": (
                    "Synthesize the tool results into a helpful response.\n"
                    "Be concise and direct. NO JSON output."
                )
            }

        # Insert system message at beginning if not already present
        if not messages or messages[0].get("role") != "system":
            messages.insert(0, synthesis_instruction)

        # Call LLM again with tool results
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )

            final_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0

            if self.debug_mode:
                print(f"🔍 [Function Calling] Final response generated ({tokens_used} tokens)")

            return FunctionCallingResponse(
                response=final_response,
                tool_calls=tool_calls,
                tool_results=tool_execution_results,
                tokens_used=tokens_used,
                model=self.model
            )

        except Exception as e:
            if self.debug_mode:
                print(f"❌ [Function Calling] Finalize call failed: {e}")

            # Fallback: synthesize response from tool results
            results_summary = []
            for tool_call in tool_calls:
                result = tool_execution_results.get(tool_call.id, {})
                if "error" not in result:
                    results_summary.append(f"{tool_call.name}: {json.dumps(result)[:200]}")

            return FunctionCallingResponse(
                response=f"I found:\n" + "\n".join(results_summary) if results_summary else "I completed the requested actions.",
                tool_calls=tool_calls,
                tool_results=tool_execution_results,
                tokens_used=0,
                model=self.model
            )


def detect_simple_chat_query(query: str) -> bool:
    """
    Fast check if query is a simple chat that doesn't need tools.
    Used to bypass function calling for obvious cases.
    """
    query_lower = query.lower().strip()

    # Single word greetings/acknowledgments
    simple_words = {
        'hi', 'hello', 'hey', 'chat', 'test', 'testing', 'thanks', 'thank',
        'bye', 'ok', 'okay', 'yes', 'no', 'maybe'
    }

    if query_lower in simple_words:
        return True

    # Short conversational phrases
    simple_phrases = [
        'how are you', 'whats up', 'thank you', 'thanks a lot',
        'got it', 'i see', 'sounds good', 'makes sense',
        'just testing', 'this is a test'
    ]

    query_normalized = ''.join(c for c in query_lower if c.isalnum() or c.isspace()).strip()
    if query_normalized in simple_phrases:
        return True

    return False

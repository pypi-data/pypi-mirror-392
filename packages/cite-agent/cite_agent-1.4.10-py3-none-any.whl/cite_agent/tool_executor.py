"""
Tool executor for Cite-Agent function calling.

Executes tools requested by the LLM and returns structured results.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from .research_assistant import DataAnalyzer, ASCIIPlotter, RExecutor, ProjectDetector
from .r_workspace_bridge import RWorkspaceBridge
from .qualitative_coding import QualitativeCodingAssistant
from .data_cleaning_magic import DataCleaningWizard
from .advanced_statistics import AdvancedStatistics
from .power_analysis import PowerAnalyzer
from .literature_synthesis import LiteratureSynthesizer


class ToolExecutor:
    """
    Executes tools requested via function calling.

    This class bridges between the function calling layer and the existing
    agent capabilities (Archive API, FinSight API, shell, etc.)
    """

    def __init__(self, agent):
        """
        Initialize tool executor.

        Args:
            agent: EnhancedNocturnalAgent instance (for accessing APIs, shell, etc.)
        """
        self.agent = agent
        self.debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool and return results.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments from LLM

        Returns:
            Dict with tool results or error
        """
        if self.debug_mode:
            print(f"🔧 [Tool Executor] Executing: {tool_name}({json.dumps(arguments)[:100]}...)")

        try:
            if tool_name == "search_papers":
                return await self._execute_search_papers(arguments)
            elif tool_name == "get_financial_data":
                return await self._execute_get_financial_data(arguments)
            elif tool_name == "web_search":
                return await self._execute_web_search(arguments)
            elif tool_name == "list_directory":
                return self._execute_list_directory(arguments)
            elif tool_name == "read_file":
                return self._execute_read_file(arguments)
            elif tool_name == "write_file":
                return self._execute_write_file(arguments)
            elif tool_name == "execute_shell_command":
                return self._execute_shell_command(arguments)
            elif tool_name == "export_to_zotero":
                return self._execute_export_to_zotero(arguments)
            elif tool_name == "find_related_papers":
                return await self._execute_find_related_papers(arguments)
            elif tool_name == "chat":
                return self._execute_chat(arguments)
            # Research Assistant Tools
            elif tool_name == "load_dataset":
                return self._execute_load_dataset(arguments)
            elif tool_name == "analyze_data":
                return self._execute_analyze_data(arguments)
            elif tool_name == "run_regression":
                return self._execute_run_regression(arguments)
            elif tool_name == "plot_data":
                return self._execute_plot_data(arguments)
            elif tool_name == "run_python_code":
                return self._execute_run_python_code(arguments)
            elif tool_name == "run_r_code":
                return self._execute_run_r_code(arguments)
            elif tool_name == "detect_project":
                return self._execute_detect_project(arguments)
            elif tool_name == "check_assumptions":
                return self._execute_check_assumptions(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            if self.debug_mode:
                print(f"❌ [Tool Executor] Error executing {tool_name}: {e}")
            return {"error": str(e)}

    # =========================================================================
    # TOOL IMPLEMENTATIONS
    # =========================================================================

    async def _execute_search_papers(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search_papers tool"""
        query = args.get("query", "")
        limit = args.get("limit", 5)
        sources = args.get("sources", ["semantic_scholar", "openalex"])  # For logging only

        if not query:
            return {"error": "Missing required parameter: query"}

        if self.debug_mode:
            print(f"📚 [Archive API] Searching: {query} (limit={limit}, sources={sources})")

        # Call Archive API via agent
        # Note: search_academic_papers has built-in source fallback, doesn't accept sources param
        try:
            results = await self.agent.search_academic_papers(
                query=query,
                limit=limit
            )

            if self.debug_mode:
                papers = results.get("results", [])
                print(f"📚 [Archive API] Found {len(papers)} papers")

            return {
                "papers": results.get("results", []),
                "count": len(results.get("results", [])),
                "query": query,
                "sources_tried": results.get("sources_tried", [])
            }

        except Exception as e:
            return {"error": f"Archive API error: {str(e)}"}

    async def _execute_get_financial_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get_financial_data tool"""
        ticker = args.get("ticker", "").upper()
        metrics = args.get("metrics", ["revenue", "profit", "market_cap"])

        if not ticker:
            return {"error": "Missing required parameter: ticker"}

        if self.debug_mode:
            print(f"💰 [FinSight API] Getting data for {ticker}: {metrics}")

        # Call FinSight API via agent
        try:
            results = await self.agent.get_financial_metrics(
                ticker=ticker,
                metrics=metrics
            )

            if self.debug_mode:
                print(f"💰 [FinSight API] Retrieved {len(results)} metrics")

            return {
                "ticker": ticker,
                "data": results,
                "company_name": ticker  # get_financial_metrics doesn't return company name
            }

        except Exception as e:
            return {"error": f"FinSight API error: {str(e)}"}

    async def _execute_web_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web_search tool"""
        query = args.get("query", "")
        num_results = args.get("num_results", 5)

        if not query:
            return {"error": "Missing required parameter: query"}

        if self.debug_mode:
            print(f"🌐 [Web Search] Searching: {query} (num_results={num_results})")

        # Call web search via agent
        try:
            results = await self.agent.web_search.search_web(
                query=query,
                num_results=num_results
            )

            if self.debug_mode:
                print(f"🌐 [Web Search] Found {len(results.get('results', []))} results")

            return {
                "results": results.get("results", []),
                "count": len(results.get("results", [])),
                "query": query
            }

        except Exception as e:
            return {"error": f"Web search error: {str(e)}"}

    def _execute_list_directory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute list_directory tool with PERSISTENT working directory context"""
        path = args.get("path", ".")
        show_hidden = args.get("show_hidden", False)

        # Get current working directory from agent context
        current_cwd = self.agent.file_context.get('current_cwd', os.getcwd())

        # If path is "." or default, use current working directory
        if path == "." or path == "":
            path = current_cwd

        if self.debug_mode:
            print(f"📁 [List Directory] Path: {path}, show_hidden: {show_hidden}")
            print(f"📁 [List Directory] Current CWD: {current_cwd}")

        # Use shell command to list directory
        try:
            if self.agent.shell_session:
                if show_hidden:
                    command = f"ls -lah {path}"
                else:
                    command = f"ls -lh {path}"

                # Execute in context of current working directory
                if path != current_cwd and not path.startswith('/') and not path.startswith('~'):
                    # Relative path - prepend current directory
                    full_path = os.path.join(current_cwd, path)
                    if show_hidden:
                        command = f"ls -lah {full_path}"
                    else:
                        command = f"ls -lh {full_path}"

                output = self.agent.execute_command(command)

                if self.debug_mode:
                    print(f"📁 [List Directory] Got {len(output)} chars of output")

                return {
                    "path": path,
                    "listing": output,
                    "command": command
                }
            else:
                # Fallback to Python's pathlib
                path_obj = Path(path).expanduser()
                if not path_obj.exists():
                    return {"error": f"Path does not exist: {path}"}

                if not path_obj.is_dir():
                    return {"error": f"Not a directory: {path}"}

                entries = []
                for entry in path_obj.iterdir():
                    if not show_hidden and entry.name.startswith('.'):
                        continue
                    entries.append({
                        "name": entry.name,
                        "is_dir": entry.is_dir(),
                        "is_file": entry.is_file()
                    })

                listing = "\n".join([
                    f"{'[DIR]' if e['is_dir'] else '[FILE]'} {e['name']}"
                    for e in entries
                ])

                return {
                    "path": str(path_obj),
                    "listing": listing,
                    "entries": entries
                }

        except Exception as e:
            return {"error": f"Failed to list directory: {str(e)}"}

    def _execute_read_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute read_file tool with PERSISTENT working directory context"""
        file_path = args.get("file_path", "")
        lines = args.get("lines", -1)

        if not file_path:
            return {"error": "Missing required parameter: file_path"}

        # Get current working directory from agent context
        current_cwd = self.agent.file_context.get('current_cwd', os.getcwd())

        if self.debug_mode:
            print(f"📄 [Read File] Path: {file_path}, lines: {lines}")
            print(f"📄 [Read File] Current CWD: {current_cwd}")

        try:
            # Resolve path relative to current working directory
            if not file_path.startswith('/') and not file_path.startswith('~'):
                # Relative path - resolve from current working directory
                file_path = os.path.join(current_cwd, file_path)

            path_obj = Path(file_path).expanduser()
            if not path_obj.exists():
                return {"error": f"File does not exist: {file_path}"}

            if not path_obj.is_file():
                return {"error": f"Not a file: {file_path}"}

            with open(path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                if lines > 0:
                    content = ''.join(f.readlines()[:lines])
                else:
                    content = f.read()

            if self.debug_mode:
                print(f"📄 [Read File] Read {len(content)} characters")

            return {
                "file_path": str(path_obj),
                "content": content,
                "lines_read": len(content.split('\n'))
            }

        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    def _execute_write_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute write_file tool with PERSISTENT working directory context"""
        file_path = args.get("file_path", "")
        content = args.get("content", "")

        # Get current working directory from agent context
        current_cwd = self.agent.file_context.get('current_cwd', os.getcwd())

        # Resolve path relative to current working directory
        if file_path and not file_path.startswith('/') and not file_path.startswith('~'):
            # Relative path - resolve from current working directory
            file_path = os.path.join(current_cwd, file_path)
        overwrite = args.get("overwrite", False)

        if not file_path:
            return {"error": "Missing required parameter: file_path"}

        if self.debug_mode:
            print(f"✏️  [Write File] Path: {file_path}, overwrite: {overwrite}, content_len: {len(content)}")

        try:
            path_obj = Path(file_path).expanduser()

            if path_obj.exists() and not overwrite:
                return {"error": f"File already exists (use overwrite=true): {file_path}"}

            # Create parent directories if needed
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            with open(path_obj, 'w', encoding='utf-8') as f:
                f.write(content)

            if self.debug_mode:
                print(f"✏️  [Write File] Wrote {len(content)} characters")

            return {
                "file_path": str(path_obj),
                "bytes_written": len(content.encode('utf-8')),
                "success": True
            }

        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}

    def _execute_shell_command(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute execute_shell_command tool with PERSISTENT working directory"""
        command = args.get("command", "")
        working_directory = args.get("working_directory", ".")

        if not command:
            return {"error": "Missing required parameter: command"}

        # Safety check
        if not self.agent.shell_session:
            return {"error": "Shell session not available"}

        # Get current working directory from agent context
        current_cwd = self.agent.file_context.get('current_cwd', os.getcwd())

        if self.debug_mode:
            print(f"⚙️  [Shell Command] Executing: {command}")
            print(f"⚙️  [Shell Command] Current CWD: {current_cwd}")

        # Classify command safety
        safety_level = self.agent._classify_command_safety(command)
        if safety_level in ('BLOCKED', 'DANGEROUS'):
            return {
                "error": f"Command blocked for safety: {command}",
                "safety_level": safety_level
            }

        try:
            # PERSISTENT WORKING DIRECTORY: Handle cd commands specially
            command_stripped = command.strip()

            # Detect cd commands (including cd &&, cd;, cd alone)
            is_cd_command = (
                command_stripped.startswith('cd ') or
                command_stripped == 'cd' or
                command_stripped.startswith('cd\t')
            )

            if is_cd_command:
                # Extract target directory
                # Handle: "cd ~/Downloads", "cd /path", "cd ..", "cd"
                parts = command_stripped.split(maxsplit=1)
                if len(parts) > 1:
                    target_dir = parts[1].split('&&')[0].split(';')[0].strip()
                else:
                    target_dir = os.path.expanduser("~")  # cd alone goes home

                # Expand ~ and resolve path
                if target_dir.startswith('~'):
                    target_dir = os.path.expanduser(target_dir)
                elif not target_dir.startswith('/'):
                    # Relative path - resolve from current_cwd
                    target_dir = os.path.join(current_cwd, target_dir)

                # SEMANTIC/FUZZY DIRECTORY MATCHING
                # If exact path doesn't exist, try to find a close match
                if not os.path.exists(target_dir):
                    parent_dir = os.path.dirname(target_dir)
                    target_name = os.path.basename(target_dir)

                    if os.path.exists(parent_dir):
                        # Look for similar directories in parent
                        try:
                            subdirs = [d for d in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, d))]

                            # Normalize target for matching (remove spaces, lowercase)
                            target_normalized = target_name.lower().replace(" ", "").replace("-", "").replace("_", "")

                            best_match = None
                            best_score = 0

                            for subdir in subdirs:
                                # Normalize subdir name
                                subdir_normalized = subdir.lower().replace(" ", "").replace("-", "").replace("_", "")

                                # Check various matching strategies
                                score = 0

                                # Exact normalized match
                                if target_normalized == subdir_normalized:
                                    score = 100
                                # Target is substring of subdir (e.g., "cm522" in "cm522-main")
                                elif target_normalized in subdir_normalized:
                                    score = 80
                                # Subdir is substring of target
                                elif subdir_normalized in target_normalized:
                                    score = 70
                                # Check if all parts of target appear in subdir
                                # e.g., "cm 522" -> ["cm", "522"] both in "cm522-main"
                                else:
                                    target_parts = target_name.lower().split()
                                    if all(part.replace("-", "").replace("_", "") in subdir_normalized for part in target_parts):
                                        score = 60

                                if score > best_score:
                                    best_score = score
                                    best_match = subdir

                            if best_match and best_score >= 60:
                                old_target = target_dir
                                target_dir = os.path.join(parent_dir, best_match)
                                if self.debug_mode:
                                    print(f"⚙️  [Shell Command] Fuzzy match: '{os.path.basename(old_target)}' → '{best_match}' (score: {best_score})")
                        except Exception as e:
                            if self.debug_mode:
                                print(f"⚙️  [Shell Command] Fuzzy matching failed: {e}")

                # Execute cd and get new pwd
                cd_cmd = f"cd {target_dir} && pwd"
                output = self.agent.execute_command(cd_cmd)

                if "ERROR" not in output and output.strip():
                    # Update persistent working directory
                    new_cwd = output.strip().split('\n')[-1]
                    self.agent.file_context['current_cwd'] = new_cwd
                    self.agent.file_context['last_directory'] = new_cwd

                    if self.debug_mode:
                        print(f"⚙️  [Shell Command] Directory changed: {current_cwd} → {new_cwd}")

                    return {
                        "command": command,
                        "output": f"Changed directory to {new_cwd}",
                        "working_directory": new_cwd,
                        "previous_directory": current_cwd,
                        "success": True
                    }
                else:
                    return {
                        "command": command,
                        "output": output,
                        "error": f"Failed to change directory to {target_dir}",
                        "working_directory": current_cwd,
                        "success": False
                    }

            # Non-cd commands: Execute in current working directory
            # Prepend cd to ensure we're in the right directory
            if current_cwd and current_cwd != ".":
                full_command = f"cd {current_cwd} && {command}"
            else:
                full_command = command

            if working_directory and working_directory != "." and working_directory != current_cwd:
                # User specified a different directory - use that instead
                full_command = f"cd {working_directory} && {command}"

            # Execute command
            output = self.agent.execute_command(full_command)

            if self.debug_mode:
                print(f"⚙️  [Shell Command] Output: {len(output)} characters")

            return {
                "command": command,
                "output": output,
                "working_directory": current_cwd,
                "success": "ERROR" not in output
            }

        except Exception as e:
            return {"error": f"Failed to execute command: {str(e)}"}

    def _execute_export_to_zotero(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute export_to_zotero tool"""
        papers = args.get("papers", [])
        format_type = args.get("format", "bibtex").lower()
        filename = args.get("filename")

        if not papers:
            return {"error": "No papers provided to export"}

        if self.debug_mode:
            print(f"📚 [Zotero Export] Exporting {len(papers)} papers to {format_type}")

        try:
            from datetime import datetime

            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cite_agent_export_{timestamp}.{format_type}"

            # Ensure correct extension
            if not filename.endswith(f".{format_type}"):
                filename = f"{filename}.{format_type}"

            output_path = Path(filename).expanduser()

            if format_type == "bibtex":
                content = self._generate_bibtex(papers)
            elif format_type == "ris":
                content = self._generate_ris(papers)
            else:
                return {"error": f"Unsupported format: {format_type}"}

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            if self.debug_mode:
                print(f"📚 [Zotero Export] Exported to {output_path}")

            return {
                "success": True,
                "filename": str(output_path),
                "format": format_type,
                "papers_count": len(papers),
                "message": f"Exported {len(papers)} papers to {output_path}. Import this file in Zotero via File → Import."
            }

        except Exception as e:
            return {"error": f"Export failed: {str(e)}"}

    def _generate_bibtex(self, papers: list) -> str:
        """Generate BibTeX content from papers"""
        from datetime import datetime

        content = f"% Generated by Cite-Agent\n"
        content += f"% Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for paper in papers:
            # Generate citation key
            title = paper.get('title', 'Unknown')
            authors_raw = paper.get('authors', [])
            year = paper.get('year', 'YEAR')

            # Normalize authors - handle both string list and dict list formats
            authors = []
            for author in authors_raw:
                if isinstance(author, dict):
                    authors.append(author.get('name', ''))
                elif isinstance(author, str):
                    authors.append(author)

            first_author = authors[0].split()[-1] if authors else "Unknown"
            title_word = title.split()[0] if title else "Paper"
            citation_key = f"{first_author}{year}{title_word}".replace(" ", "").replace(",", "").replace(":", "")

            # Build BibTeX entry
            content += f"@article{{{citation_key},\n"
            content += f"  title = {{{title}}},\n"

            if authors:
                authors_str = " and ".join(authors)
                content += f"  author = {{{authors_str}}},\n"

            content += f"  year = {{{year}}},\n"

            if 'venue' in paper and paper['venue']:
                content += f"  journal = {{{paper['venue']}}},\n"

            if 'doi' in paper and paper['doi']:
                content += f"  doi = {{{paper['doi']}}},\n"

            if 'url' in paper and paper['url']:
                content += f"  url = {{{paper['url']}}},\n"

            if 'abstract' in paper and paper['abstract']:
                abstract = paper['abstract'].replace("\n", " ").replace("{", "").replace("}", "")[:500]
                content += f"  abstract = {{{abstract}...}},\n"

            content += "}\n\n"

        return content

    def _generate_ris(self, papers: list) -> str:
        """Generate RIS content from papers (Zotero also supports this)"""
        content = ""

        for paper in papers:
            content += "TY  - JOUR\n"  # Journal article type

            title = paper.get('title', '')
            if title:
                content += f"TI  - {title}\n"

            authors_raw = paper.get('authors', [])
            # Normalize authors - handle both string list and dict list formats
            for author in authors_raw:
                if isinstance(author, dict):
                    author_name = author.get('name', '')
                elif isinstance(author, str):
                    author_name = author
                else:
                    continue
                if author_name:
                    content += f"AU  - {author_name}\n"

            year = paper.get('year', '')
            if year:
                content += f"PY  - {year}\n"

            venue = paper.get('venue', '')
            if venue:
                content += f"JO  - {venue}\n"

            doi = paper.get('doi', '')
            if doi:
                content += f"DO  - {doi}\n"

            url = paper.get('url', '')
            if url:
                content += f"UR  - {url}\n"

            abstract = paper.get('abstract', '')
            if abstract:
                content += f"AB  - {abstract}\n"

            content += "ER  - \n\n"

        return content

    async def _execute_find_related_papers(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute find_related_papers tool"""
        paper_id = args.get("paper_id", "")
        method = args.get("method", "similar")
        limit = args.get("limit", 10)

        if not paper_id:
            return {"error": "Missing required parameter: paper_id"}

        if self.debug_mode:
            print(f"🔗 [Related Papers] Finding related papers for: {paper_id} (method: {method})")

        try:
            # Use Archive API to find related papers
            # This typically works by searching for the paper first, then getting related papers
            result = await self.agent.search_academic_papers(
                query=paper_id,
                limit=1,
                sources=['semantic_scholar', 'openalex']
            )

            if 'error' in result or result.get('papers_count', 0) == 0:
                # If we can't find the exact paper, search for similar ones
                related_result = await self.agent.search_academic_papers(
                    query=f"related to {paper_id}",
                    limit=limit,
                    sources=['semantic_scholar', 'openalex']
                )

                return {
                    "method": "similar_search",
                    "query": paper_id,
                    "related_papers": related_result.get('papers', []),
                    "count": len(related_result.get('papers', [])),
                    "note": "Found papers related to the query (exact paper match not found)"
                }

            # Got the paper, now find related ones based on method
            base_paper = result['papers'][0]

            if method == "citations":
                # Papers that cite this paper
                query = f"cites:{base_paper.get('title', paper_id)}"
            elif method == "references":
                # Papers referenced by this paper
                query = f"references:{base_paper.get('title', paper_id)}"
            else:  # similar
                # Papers with similar topics/keywords
                query = f"{base_paper.get('title', paper_id)} similar research"

            related_result = await self.agent.search_academic_papers(
                query=query,
                limit=limit,
                sources=['semantic_scholar', 'openalex']
            )

            if self.debug_mode:
                print(f"🔗 [Related Papers] Found {len(related_result.get('papers', []))} related papers")

            return {
                "method": method,
                "base_paper": {
                    "title": base_paper.get('title'),
                    "authors": base_paper.get('authors', []),
                    "year": base_paper.get('year'),
                    "citations": base_paper.get('citations_count', 0)
                },
                "related_papers": related_result.get('papers', []),
                "count": len(related_result.get('papers', [])),
                "message": f"Found {len(related_result.get('papers', []))} papers {method} '{base_paper.get('title', paper_id)}'"
            }

        except Exception as e:
            return {"error": f"Failed to find related papers: {str(e)}"}

    def _execute_chat(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute chat tool (pure conversational response)"""
        message = args.get("message", "")

        if self.debug_mode:
            print(f"💬 [Chat] Conversational response: {message[:100]}...")

        # Chat tool just returns the message directly
        # The LLM has already generated the response in the 'message' parameter
        return {
            "message": message,
            "type": "conversational"
        }

    # =========================================================================
    # RESEARCH ASSISTANT TOOLS
    # =========================================================================

    def _execute_load_dataset(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute load_dataset tool - Load CSV/Excel dataset with PERSISTENT cwd support"""
        filepath = args.get("filepath", "")

        if not filepath:
            return {"error": "Missing required parameter: filepath"}

        # Get current working directory from agent context
        current_cwd = self.agent.file_context.get('current_cwd', os.getcwd())

        # Resolve relative paths from current working directory
        if not filepath.startswith('/') and not filepath.startswith('~'):
            filepath = os.path.join(current_cwd, filepath)
        elif filepath.startswith('~'):
            filepath = os.path.expanduser(filepath)

        if self.debug_mode:
            print(f"📊 [Data Analyzer] Loading dataset: {filepath}")
            print(f"📊 [Data Analyzer] Current CWD: {current_cwd}")

        try:
            # Initialize data analyzer if needed
            if not hasattr(self, '_data_analyzer'):
                self._data_analyzer = DataAnalyzer()

            result = self._data_analyzer.load_dataset(filepath)

            if self.debug_mode:
                print(f"📊 [Data Analyzer] Loaded {result.get('rows', 0)} rows, {result.get('columns', 0)} columns")

            # ENHANCEMENT: Auto-compute descriptive stats for all numeric columns
            # This allows single-call data analysis (no need to chain load + analyze)
            if "error" not in result and hasattr(self._data_analyzer, 'current_dataset'):
                df = self._data_analyzer.current_dataset
                if df is not None:
                    # Add basic stats for each numeric column
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if numeric_cols:
                        column_stats = {}
                        for col in numeric_cols:
                            series = df[col]
                            column_stats[col] = {
                                "mean": float(series.mean()),
                                "std": float(series.std()),
                                "min": float(series.min()),
                                "max": float(series.max()),
                                "median": float(series.median())
                            }
                        result["column_statistics"] = column_stats

                        if self.debug_mode:
                            print(f"📊 [Data Analyzer] Auto-computed stats for {len(numeric_cols)} numeric columns")

            return result

        except Exception as e:
            return {"error": f"Failed to load dataset: {str(e)}"}

    def _execute_analyze_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analyze_data tool - Descriptive statistics and correlation"""
        analysis_type = args.get("analysis_type", "descriptive")  # descriptive or correlation
        column = args.get("column")  # For descriptive stats
        var1 = args.get("var1")  # For correlation
        var2 = args.get("var2")  # For correlation
        method = args.get("method", "pearson")  # pearson or spearman

        if self.debug_mode:
            print(f"📊 [Data Analyzer] Running {analysis_type} analysis")

        try:
            if not hasattr(self, '_data_analyzer'):
                return {"error": "No dataset loaded. Use load_dataset first."}

            if analysis_type == "descriptive":
                result = self._data_analyzer.descriptive_stats(column)
            elif analysis_type == "correlation":
                if not var1 or not var2:
                    return {"error": "Missing var1 or var2 for correlation analysis"}
                result = self._data_analyzer.run_correlation(var1, var2, method)
            else:
                return {"error": f"Unknown analysis type: {analysis_type}"}

            if self.debug_mode:
                print(f"📊 [Data Analyzer] Analysis complete")

            return result

        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    def _execute_run_regression(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute run_regression tool - Linear/multiple regression"""
        y_variable = args.get("y_variable", "")
        x_variables = args.get("x_variables", [])
        model_type = args.get("model_type", "linear")

        if not y_variable:
            return {"error": "Missing required parameter: y_variable"}

        if not x_variables:
            return {"error": "Missing required parameter: x_variables"}

        # Ensure x_variables is a list
        if isinstance(x_variables, str):
            x_variables = [x_variables]

        if self.debug_mode:
            print(f"📊 [Data Analyzer] Running {model_type} regression: {y_variable} ~ {' + '.join(x_variables)}")

        try:
            if not hasattr(self, '_data_analyzer'):
                return {"error": "No dataset loaded. Use load_dataset first."}

            result = self._data_analyzer.run_regression(y_variable, x_variables, model_type)

            if self.debug_mode:
                print(f"📊 [Data Analyzer] Regression complete - R²: {result.get('r_squared', 'N/A')}")

            return result

        except Exception as e:
            return {"error": f"Regression failed: {str(e)}"}

    def _execute_plot_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plot_data tool - ASCII plotting"""
        plot_type = args.get("plot_type", "scatter")  # scatter, bar, histogram
        x_data = args.get("x_data")  # Column name or list of values
        y_data = args.get("y_data")  # Column name or list of values (for scatter)
        title = args.get("title", "Data Plot")
        categories = args.get("categories")  # For bar charts
        values = args.get("values")  # For bar charts
        bins = args.get("bins", 10)  # For histograms

        if self.debug_mode:
            print(f"📈 [ASCII Plotter] Creating {plot_type} plot: {title}")

        try:
            # Initialize plotter
            if not hasattr(self, '_ascii_plotter'):
                self._ascii_plotter = ASCIIPlotter()

            # Get actual data from dataset if column names provided
            if hasattr(self, '_data_analyzer') and self._data_analyzer.df is not None:
                df = self._data_analyzer.df

                if isinstance(x_data, str) and x_data in df.columns:
                    x_data = df[x_data].tolist()
                if isinstance(y_data, str) and y_data in df.columns:
                    y_data = df[y_data].tolist()
                if isinstance(values, str) and values in df.columns:
                    values = df[values].tolist()

            # Create plot based on type
            if plot_type == "scatter":
                if x_data is None or y_data is None:
                    return {"error": "Missing x_data or y_data for scatter plot"}
                plot = self._ascii_plotter.plot_scatter(x_data, y_data, title)

            elif plot_type == "bar":
                if categories is None or values is None:
                    return {"error": "Missing categories or values for bar chart"}
                plot = self._ascii_plotter.plot_bar(categories, values, title)

            elif plot_type == "histogram":
                if x_data is None:
                    return {"error": "Missing x_data for histogram"}
                plot = self._ascii_plotter.plot_histogram(x_data, bins, title)

            else:
                return {"error": f"Unknown plot type: {plot_type}"}

            if self.debug_mode:
                print(f"📈 [ASCII Plotter] Plot created ({len(plot)} characters)")

            return {
                "plot": plot,
                "plot_type": plot_type,
                "title": title
            }

        except Exception as e:
            return {"error": f"Plotting failed: {str(e)}"}

    def _execute_run_python_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code for data analysis with pandas/numpy/scipy"""
        python_code = args.get("python_code", "")
        filepath = args.get("filepath", "")

        if not python_code:
            return {"error": "Missing required parameter: python_code"}

        if self.debug_mode:
            print(f"🐍 [Python Code] Executing: {python_code[:100]}...")

        try:
            import pandas as pd
            import numpy as np
            from pathlib import Path

            # Load dataset if filepath provided
            df = None
            if filepath:
                # Resolve relative paths from current working directory
                current_cwd = self.agent.file_context.get('current_cwd', os.getcwd())
                if not filepath.startswith('/') and not filepath.startswith('~'):
                    filepath = os.path.join(current_cwd, filepath)
                elif filepath.startswith('~'):
                    filepath = os.path.expanduser(filepath)

                # Load the file
                path_obj = Path(filepath)
                if path_obj.suffix.lower() == '.csv':
                    df = pd.read_csv(filepath)
                elif path_obj.suffix.lower() in ['.xlsx', '.xls']:
                    df = pd.read_excel(filepath)
                elif path_obj.suffix.lower() == '.tsv':
                    df = pd.read_csv(filepath, sep='\t')
                else:
                    return {"error": f"Unsupported file type: {path_obj.suffix}"}

                if self.debug_mode:
                    print(f"🐍 [Python Code] Loaded dataset: {filepath} ({len(df)} rows)")

            # If no filepath provided, use the already loaded dataset
            elif hasattr(self, '_data_analyzer') and self._data_analyzer.current_dataset is not None:
                df = self._data_analyzer.current_dataset
                if self.debug_mode:
                    print(f"🐍 [Python Code] Using pre-loaded dataset ({len(df)} rows)")
            else:
                return {"error": "No dataset loaded. Provide 'filepath' parameter or load dataset first."}

            # Create execution environment
            exec_globals = {
                'pd': pd,
                'np': np,
                'df': df,
                '__builtins__': __builtins__,
            }

            # Try to import scipy if available
            try:
                import scipy.stats
                exec_globals['scipy'] = __import__('scipy')
                exec_globals['stats'] = scipy.stats
            except ImportError:
                pass

            # Execute the code
            # If it's an expression, evaluate and return
            try:
                result = eval(python_code, exec_globals)
            except SyntaxError:
                # If eval fails, it might be a statement - execute it
                exec(python_code, exec_globals)
                result = exec_globals.get('result', 'Code executed successfully (no return value)')

            # Convert result to string representation
            if isinstance(result, pd.DataFrame):
                result_str = result.to_string()
            elif isinstance(result, pd.Series):
                result_str = result.to_string()
            elif isinstance(result, np.ndarray):
                result_str = str(result)
            else:
                result_str = str(result)

            if self.debug_mode:
                print(f"🐍 [Python Code] Result: {result_str[:200]}...")

            return {
                "code": python_code,
                "result": result_str,
                "result_type": type(result).__name__,
                "success": True
            }

        except Exception as e:
            return {"error": f"Python execution failed: {str(e)}"}

    def _execute_run_r_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute run_r_code tool - Safe R code execution"""
        r_code = args.get("r_code", "")
        allow_writes = args.get("allow_writes", False)

        if not r_code:
            return {"error": "Missing required parameter: r_code"}

        if self.debug_mode:
            print(f"🔬 [R Executor] Executing R code ({len(r_code)} chars)")

        try:
            # Initialize R executor if needed
            if not hasattr(self, '_r_executor'):
                self._r_executor = RExecutor()

            result = self._r_executor.execute_r_code(r_code, allow_writes)

            if self.debug_mode:
                if result.get("success"):
                    print(f"🔬 [R Executor] Execution successful")
                else:
                    print(f"🔬 [R Executor] Execution failed: {result.get('error', 'Unknown error')}")

            return result

        except Exception as e:
            return {"error": f"R execution failed: {str(e)}"}

    def _execute_detect_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute detect_project tool - Detect project type (R, Jupyter, Python)"""
        path = args.get("path", ".")

        if self.debug_mode:
            print(f"🔍 [Project Detector] Detecting project type in: {path}")

        try:
            # Initialize detector if needed
            if not hasattr(self, '_project_detector'):
                self._project_detector = ProjectDetector(path)

            project_info = self._project_detector.detect_project()

            if project_info:
                if self.debug_mode:
                    print(f"🔍 [Project Detector] Found {project_info.get('type')} project")

                # Add R packages if R project
                if project_info.get('type') == 'r_project':
                    project_info['r_packages'] = self._project_detector.get_r_packages()

                return project_info
            else:
                return {
                    "type": "unknown",
                    "message": "No specific project type detected"
                }

        except Exception as e:
            return {"error": f"Project detection failed: {str(e)}"}

    def _execute_check_assumptions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute check_assumptions tool - Check statistical test assumptions"""
        test_type = args.get("test_type", "")

        if not test_type:
            return {"error": "Missing required parameter: test_type"}

        if self.debug_mode:
            print(f"📊 [Data Analyzer] Checking assumptions for: {test_type}")

        try:
            if not hasattr(self, '_data_analyzer'):
                return {"error": "No dataset loaded. Use load_dataset first."}

            result = self._data_analyzer.check_assumptions(test_type)

            if self.debug_mode:
                print(f"📊 [Data Analyzer] Assumption checks complete")

            return result

        except Exception as e:
            return {"error": f"Assumption check failed: {str(e)}"}
    # =====================================================================
    # MAGICAL RESEARCH MODULES - Advanced Research Assistant Features
    # =====================================================================

    # ---------------------------------------------------------------------
    # R Workspace Bridge - Access R console objects
    # ---------------------------------------------------------------------

    def _execute_list_r_objects(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all objects in R workspace"""
        workspace_path = args.get("workspace_path")

        if self.debug_mode:
            print(f"🔬 [R Bridge] Listing R workspace objects")

        try:
            if not hasattr(self, '_r_bridge'):
                self._r_bridge = RWorkspaceBridge()

            result = self._r_bridge.list_objects(workspace_path)
            return result

        except Exception as e:
            return {"error": f"Failed to list R objects: {str(e)}"}

    def _execute_get_r_dataframe(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a dataframe from R workspace"""
        object_name = args.get("object_name", "")
        workspace_path = args.get("workspace_path")

        if not object_name:
            return {"error": "Missing required parameter: object_name"}

        if self.debug_mode:
            print(f"🔬 [R Bridge] Retrieving R object: {object_name}")

        try:
            if not hasattr(self, '_r_bridge'):
                self._r_bridge = RWorkspaceBridge()

            result = self._r_bridge.get_dataframe(object_name, workspace_path)
            return result

        except Exception as e:
            return {"error": f"Failed to retrieve R dataframe: {str(e)}"}

    def _execute_execute_r_and_capture(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute R code and capture specific objects"""
        r_code = args.get("r_code", "")
        capture_objects = args.get("capture_objects", [])

        if not r_code:
            return {"error": "Missing required parameter: r_code"}

        if self.debug_mode:
            print(f"🔬 [R Bridge] Executing R code and capturing {len(capture_objects)} objects")

        try:
            if not hasattr(self, '_r_bridge'):
                self._r_bridge = RWorkspaceBridge()

            result = self._r_bridge.execute_and_capture(r_code, capture_objects)
            return result

        except Exception as e:
            return {"error": f"Failed to execute R code: {str(e)}"}

    # ---------------------------------------------------------------------
    # Qualitative Coding Suite - Qualitative research automation
    # ---------------------------------------------------------------------

    def _execute_create_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new qualitative code"""
        code_name = args.get("code_name", "")
        description = args.get("description", "")
        parent_code = args.get("parent_code")

        if not code_name:
            return {"error": "Missing required parameter: code_name"}

        if self.debug_mode:
            print(f"📝 [Qual Coding] Creating code: {code_name}")

        try:
            if not hasattr(self, '_qual_coder'):
                self._qual_coder = QualitativeCodingAssistant()

            result = self._qual_coder.create_code(code_name, description, parent_code)
            return result

        except Exception as e:
            return {"error": f"Failed to create code: {str(e)}"}

    def _execute_load_transcript(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Load a transcript for qualitative coding"""
        doc_id = args.get("doc_id", "")
        content = args.get("content", "")
        format_type = args.get("format_type", "plain")

        if not doc_id or not content:
            return {"error": "Missing required parameters: doc_id, content"}

        if self.debug_mode:
            print(f"📝 [Qual Coding] Loading transcript: {doc_id}")

        try:
            if not hasattr(self, '_qual_coder'):
                self._qual_coder = QualitativeCodingAssistant()

            result = self._qual_coder.load_transcript(doc_id, content, format_type)
            return result

        except Exception as e:
            return {"error": f"Failed to load transcript: {str(e)}"}

    def _execute_code_segment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Code a segment of text"""
        doc_id = args.get("doc_id", "")
        line_start = args.get("line_start")
        line_end = args.get("line_end")
        codes = args.get("codes", [])

        if not doc_id or line_start is None or line_end is None or not codes:
            return {"error": "Missing required parameters: doc_id, line_start, line_end, codes"}

        if self.debug_mode:
            print(f"📝 [Qual Coding] Coding lines {line_start}-{line_end} in {doc_id}")

        try:
            if not hasattr(self, '_qual_coder'):
                self._qual_coder = QualitativeCodingAssistant()

            result = self._qual_coder.code_segment(doc_id, line_start, line_end, codes)
            return result

        except Exception as e:
            return {"error": f"Failed to code segment: {str(e)}"}

    def _execute_get_coded_excerpts(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get all excerpts coded with a specific code"""
        code_name = args.get("code_name", "")

        if not code_name:
            return {"error": "Missing required parameter: code_name"}

        if self.debug_mode:
            print(f"📝 [Qual Coding] Getting excerpts for code: {code_name}")

        try:
            if not hasattr(self, '_qual_coder'):
                self._qual_coder = QualitativeCodingAssistant()

            result = self._qual_coder.get_coded_excerpts(code_name)
            return result

        except Exception as e:
            return {"error": f"Failed to get excerpts: {str(e)}"}

    def _execute_auto_extract_themes(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically extract themes from coded documents"""
        doc_ids = args.get("doc_ids")
        min_frequency = args.get("min_frequency", 3)

        if self.debug_mode:
            print(f"📝 [Qual Coding] Auto-extracting themes (min_freq={min_frequency})")

        try:
            if not hasattr(self, '_qual_coder'):
                self._qual_coder = QualitativeCodingAssistant()

            result = self._qual_coder.auto_extract_themes(doc_ids, min_frequency)
            return result

        except Exception as e:
            return {"error": f"Failed to extract themes: {str(e)}"}

    def _execute_calculate_kappa(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate inter-rater reliability (Cohen's Kappa)"""
        coder1_codes = args.get("coder1_codes", [])
        coder2_codes = args.get("coder2_codes", [])
        method = args.get("method", "cohen_kappa")

        if not coder1_codes or not coder2_codes:
            return {"error": "Missing required parameters: coder1_codes, coder2_codes"}

        if self.debug_mode:
            print(f"📝 [Qual Coding] Calculating {method}")

        try:
            if not hasattr(self, '_qual_coder'):
                self._qual_coder = QualitativeCodingAssistant()

            # Convert to CodedSegment objects (simplified for this interface)
            from .qualitative_coding import CodedSegment
            segments1 = [CodedSegment(doc_id="", line_start=i, line_end=i, codes=[c], text="") for i, c in enumerate(coder1_codes)]
            segments2 = [CodedSegment(doc_id="", line_start=i, line_end=i, codes=[c], text="") for i, c in enumerate(coder2_codes)]

            result = self._qual_coder.calculate_inter_rater_reliability(segments1, segments2, method)
            return result

        except Exception as e:
            return {"error": f"Failed to calculate kappa: {str(e)}"}

    # ---------------------------------------------------------------------
    # Data Cleaning Magic - Automated data quality
    # ---------------------------------------------------------------------

    def _execute_scan_data_quality(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Scan dataset for quality issues"""
        if self.debug_mode:
            print(f"🧹 [Data Cleaning] Scanning data quality issues")

        try:
            if not hasattr(self, '_data_analyzer'):
                return {"error": "No dataset loaded. Use load_dataset first."}

            # Create wizard from existing dataframe
            wizard = DataCleaningWizard(self._data_analyzer.df)
            result = wizard.scan_all_issues()

            # Store wizard for auto-fix
            self._data_wizard = wizard

            return result

        except Exception as e:
            return {"error": f"Failed to scan data quality: {str(e)}"}

    def _execute_auto_clean_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-fix data quality issues"""
        fix_types = args.get("fix_types")

        if self.debug_mode:
            print(f"🧹 [Data Cleaning] Auto-fixing data issues")

        try:
            if not hasattr(self, '_data_wizard'):
                return {"error": "Run scan_data_quality first"}

            result = self._data_wizard.auto_fix_issues(fix_types)

            # Update the main dataframe
            self._data_analyzer.df = self._data_wizard.df

            return result

        except Exception as e:
            return {"error": f"Failed to auto-clean data: {str(e)}"}

    def _execute_handle_missing_values(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle missing values with specific strategy"""
        column = args.get("column", "")
        method = args.get("method", "median")

        if not column:
            return {"error": "Missing required parameter: column"}

        if self.debug_mode:
            print(f"🧹 [Data Cleaning] Handling missing values in {column} using {method}")

        try:
            if not hasattr(self, '_data_wizard'):
                # Create wizard if doesn't exist
                if not hasattr(self, '_data_analyzer'):
                    return {"error": "No dataset loaded. Use load_dataset first."}
                self._data_wizard = DataCleaningWizard(self._data_analyzer.df)

            result = self._data_wizard.handle_missing_values(column, method)

            # Update the main dataframe
            self._data_analyzer.df = self._data_wizard.df

            return result

        except Exception as e:
            return {"error": f"Failed to handle missing values: {str(e)}"}

    # ---------------------------------------------------------------------
    # Advanced Statistics - PCA, Factor Analysis, Mediation, Moderation
    # ---------------------------------------------------------------------

    def _execute_run_pca(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run Principal Component Analysis"""
        variables = args.get("variables")
        n_components = args.get("n_components")
        standardize = args.get("standardize", True)

        if self.debug_mode:
            print(f"📊 [Advanced Stats] Running PCA")

        try:
            if not hasattr(self, '_data_analyzer'):
                return {"error": "No dataset loaded. Use load_dataset first."}

            stats = AdvancedStatistics(self._data_analyzer.df)
            result = stats.principal_component_analysis(variables, n_components, standardize)

            return result

        except Exception as e:
            return {"error": f"PCA failed: {str(e)}"}

    def _execute_run_factor_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run Exploratory Factor Analysis"""
        variables = args.get("variables")
        n_factors = args.get("n_factors", 3)
        rotation = args.get("rotation", "varimax")

        if self.debug_mode:
            print(f"📊 [Advanced Stats] Running Factor Analysis ({n_factors} factors)")

        try:
            if not hasattr(self, '_data_analyzer'):
                return {"error": "No dataset loaded. Use load_dataset first."}

            stats = AdvancedStatistics(self._data_analyzer.df)
            result = stats.exploratory_factor_analysis(variables, n_factors, rotation)

            return result

        except Exception as e:
            return {"error": f"Factor analysis failed: {str(e)}"}

    def _execute_run_mediation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run mediation analysis (X → M → Y)"""
        X = args.get("X", "")
        M = args.get("M", "")
        Y = args.get("Y", "")
        bootstrap_samples = args.get("bootstrap_samples", 5000)

        if not X or not M or not Y:
            return {"error": "Missing required parameters: X, M, Y"}

        if self.debug_mode:
            print(f"📊 [Advanced Stats] Running mediation: {X} → {M} → {Y}")

        try:
            if not hasattr(self, '_data_analyzer'):
                return {"error": "No dataset loaded. Use load_dataset first."}

            stats = AdvancedStatistics(self._data_analyzer.df)
            result = stats.mediation_analysis(X, M, Y, bootstrap_samples)

            return result

        except Exception as e:
            return {"error": f"Mediation analysis failed: {str(e)}"}

    def _execute_run_moderation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run moderation analysis (X*W → Y)"""
        X = args.get("X", "")
        W = args.get("W", "")
        Y = args.get("Y", "")
        center_variables = args.get("center_variables", True)

        if not X or not W or not Y:
            return {"error": "Missing required parameters: X, W, Y"}

        if self.debug_mode:
            print(f"📊 [Advanced Stats] Running moderation: {X}*{W} → {Y}")

        try:
            if not hasattr(self, '_data_analyzer'):
                return {"error": "No dataset loaded. Use load_dataset first."}

            stats = AdvancedStatistics(self._data_analyzer.df)
            result = stats.moderation_analysis(X, W, Y, center_variables)

            return result

        except Exception as e:
            return {"error": f"Moderation analysis failed: {str(e)}"}

    # ---------------------------------------------------------------------
    # Power Analysis - Sample size and power calculations
    # ---------------------------------------------------------------------

    def _execute_calculate_sample_size(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required sample size"""
        test_type = args.get("test_type", "")
        effect_size = args.get("effect_size")
        alpha = args.get("alpha", 0.05)
        power = args.get("power", 0.80)
        n_groups = args.get("n_groups")
        n_predictors = args.get("n_predictors")

        if not test_type or effect_size is None:
            return {"error": "Missing required parameters: test_type, effect_size"}

        if self.debug_mode:
            print(f"🔬 [Power Analysis] Calculating sample size for {test_type}")

        try:
            analyzer = PowerAnalyzer()

            if test_type == "ttest":
                result = analyzer.sample_size_ttest(effect_size, alpha, power)
            elif test_type == "correlation":
                result = analyzer.sample_size_correlation(effect_size, alpha, power)
            elif test_type == "anova":
                if n_groups is None:
                    return {"error": "Missing required parameter: n_groups for ANOVA"}
                result = analyzer.sample_size_anova(effect_size, n_groups, alpha, power)
            elif test_type == "regression":
                if n_predictors is None:
                    return {"error": "Missing required parameter: n_predictors for regression"}
                result = analyzer.sample_size_regression(effect_size, n_predictors, alpha, power)
            else:
                return {"error": f"Unknown test type: {test_type}"}

            return result

        except Exception as e:
            return {"error": f"Sample size calculation failed: {str(e)}"}

    def _execute_calculate_power(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate achieved statistical power"""
        test_type = args.get("test_type", "")
        effect_size = args.get("effect_size")
        n = args.get("n")
        alpha = args.get("alpha", 0.05)
        n_groups = args.get("n_groups")
        n_predictors = args.get("n_predictors")

        if not test_type or effect_size is None or n is None:
            return {"error": "Missing required parameters: test_type, effect_size, n"}

        if self.debug_mode:
            print(f"🔬 [Power Analysis] Calculating achieved power for {test_type}")

        try:
            analyzer = PowerAnalyzer()

            kwargs = {}
            if n_groups is not None:
                kwargs['n_groups'] = n_groups
            if n_predictors is not None:
                kwargs['n_predictors'] = n_predictors

            result = analyzer.calculate_achieved_power(test_type, effect_size, n, alpha, **kwargs)

            return result

        except Exception as e:
            return {"error": f"Power calculation failed: {str(e)}"}

    def _execute_calculate_mde(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate minimum detectable effect"""
        test_type = args.get("test_type", "")
        n = args.get("n")
        alpha = args.get("alpha", 0.05)
        power = args.get("power", 0.80)
        n_groups = args.get("n_groups")

        if not test_type or n is None:
            return {"error": "Missing required parameters: test_type, n"}

        if self.debug_mode:
            print(f"🔬 [Power Analysis] Calculating minimum detectable effect for {test_type}")

        try:
            analyzer = PowerAnalyzer()

            kwargs = {}
            if n_groups is not None:
                kwargs['n_groups'] = n_groups

            result = analyzer.minimum_detectable_effect(test_type, n, alpha, power, **kwargs)

            return result

        except Exception as e:
            return {"error": f"MDE calculation failed: {str(e)}"}

    # ---------------------------------------------------------------------
    # Literature Synthesis AI - Systematic review automation
    # ---------------------------------------------------------------------

    def _execute_add_paper(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Add a paper to literature synthesis"""
        paper_id = args.get("paper_id", "")
        title = args.get("title", "")
        abstract = args.get("abstract", "")
        year = args.get("year")
        authors = args.get("authors")
        keywords = args.get("keywords")
        findings = args.get("findings")

        if not paper_id or not title or not abstract:
            return {"error": "Missing required parameters: paper_id, title, abstract"}

        if self.debug_mode:
            print(f"📚 [Lit Synthesis] Adding paper: {paper_id}")

        try:
            if not hasattr(self, '_lit_synth'):
                self._lit_synth = LiteratureSynthesizer()

            result = self._lit_synth.add_paper(paper_id, title, abstract, year, authors, keywords, findings)

            return result

        except Exception as e:
            return {"error": f"Failed to add paper: {str(e)}"}

    def _execute_extract_lit_themes(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract common themes across papers"""
        min_papers = args.get("min_papers", 3)
        theme_length = args.get("theme_length", 2)

        if self.debug_mode:
            print(f"📚 [Lit Synthesis] Extracting themes (min_papers={min_papers})")

        try:
            if not hasattr(self, '_lit_synth'):
                return {"error": "No papers loaded. Use add_paper first."}

            result = self._lit_synth.extract_common_themes(min_papers, theme_length)

            return result

        except Exception as e:
            return {"error": f"Failed to extract themes: {str(e)}"}

    def _execute_find_research_gaps(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Identify research gaps in literature"""
        if self.debug_mode:
            print(f"📚 [Lit Synthesis] Identifying research gaps")

        try:
            if not hasattr(self, '_lit_synth'):
                return {"error": "No papers loaded. Use add_paper first."}

            result = self._lit_synth.identify_research_gaps()

            return result

        except Exception as e:
            return {"error": f"Failed to find research gaps: {str(e)}"}

    def _execute_create_synthesis_matrix(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create synthesis matrix comparing papers"""
        dimensions = args.get("dimensions", ["method", "findings"])

        if self.debug_mode:
            print(f"📚 [Lit Synthesis] Creating synthesis matrix")

        try:
            if not hasattr(self, '_lit_synth'):
                return {"error": "No papers loaded. Use add_paper first."}

            result = self._lit_synth.create_synthesis_matrix(dimensions)

            # Remove dataframe from result (not JSON serializable)
            if "dataframe" in result:
                del result["dataframe"]

            return result

        except Exception as e:
            return {"error": f"Failed to create synthesis matrix: {str(e)}"}

    def _execute_find_contradictions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Find contradictory findings in literature"""
        if self.debug_mode:
            print(f"📚 [Lit Synthesis] Finding contradictory findings")

        try:
            if not hasattr(self, '_lit_synth'):
                return {"error": "No papers loaded. Use add_paper first."}

            result = self._lit_synth.find_contradictory_findings()

            return result

        except Exception as e:
            return {"error": f"Failed to find contradictions: {str(e)}"}

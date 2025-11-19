"""
Function calling tool definitions for Cite-Agent.

This module defines all available tools that the LLM can call using
OpenAI-compatible function calling API (works with Cerebras, OpenAI, etc.)

Each tool has:
- name: Unique identifier
- description: When to use this tool (guides LLM decision)
- parameters: JSON schema for validation
"""

from typing import Dict, List, Any

# Tool definitions in OpenAI function calling format
TOOLS: List[Dict[str, Any]] = [
    # =========================================================================
    # ACADEMIC RESEARCH TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": (
                "Search 200M+ academic papers from Semantic Scholar, OpenAlex, and PubMed. "
                "Use when user asks about: research studies, academic papers, scientific findings, "
                "literature review, citations, peer-reviewed research, methodology, authors. "
                "Examples: 'find papers on machine learning', 'what does research say about X', "
                "'papers by Smith on climate change'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for papers (e.g., 'neural networks', 'climate change impacts')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of papers to return (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "sources": {
                        "type": "array",
                        "description": "Which databases to search (default: all)",
                        "items": {
                            "type": "string",
                            "enum": ["semantic_scholar", "openalex", "pubmed"]
                        },
                        "default": ["semantic_scholar", "openalex"]
                    }
                },
                "required": ["query"]
            }
        }
    },

    # =========================================================================
    # FINANCIAL DATA TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "get_financial_data",
            "description": (
                "Get company financial data from SEC filings and Yahoo Finance. "
                "Use when user asks about: revenue, profit, earnings, market cap, stock price, "
                "financial statements, 10-K/10-Q filings, company metrics, valuation. "
                "Examples: 'Tesla revenue', 'Apple market cap', 'Microsoft P/E ratio'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'TSLA', 'AAPL', 'MSFT')"
                    },
                    "metrics": {
                        "type": "array",
                        "description": "Which metrics to retrieve (default: all available)",
                        "items": {
                            "type": "string",
                            "enum": [
                                "revenue", "profit", "earnings", "market_cap",
                                "stock_price", "pe_ratio", "debt", "cash_flow"
                            ]
                        },
                        "default": ["revenue", "profit", "market_cap"]
                    }
                },
                "required": ["ticker"]
            }
        }
    },

    # =========================================================================
    # WEB SEARCH TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web using DuckDuckGo for current information. "
                "Use when user asks about: current events, recent news, general facts, "
                "products, companies (non-financial), how-to guides, definitions. "
                "Examples: 'latest news on AI', 'what is X', 'how to do Y'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Web search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        }
    },

    # =========================================================================
    # FILE SYSTEM TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": (
                "List files and folders in a directory. "
                "Use when user asks: 'what folders are here', 'list files', 'show directory contents', "
                "'what's in this folder', 'ls'. "
                "DO NOT use for conversational questions about the agent itself."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list (default: current directory)",
                        "default": "."
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "description": "Include hidden files (default: false)",
                        "default": False
                    }
                },
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read contents of a file. "
                "Use when user asks to: read, show, display, or view a specific file. "
                "Examples: 'read config.json', 'show me app.py', 'what's in README.md'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of lines to read (default: all)",
                        "default": -1
                    }
                },
                "required": ["file_path"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "execute_shell_command",
            "description": (
                "Execute a shell command (bash/powershell). "
                "Use for: searching files (grep, find), git operations, running scripts, "
                "system operations. "
                "Examples: 'find Python files', 'git status', 'search for TODO in code'. "
                "IMPORTANT: Only for actual system commands, not for listing directories "
                "(use list_directory for that)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute (e.g., 'git status', 'find . -name \"*.py\"')"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Directory to run command in (default: current)",
                        "default": "."
                    }
                },
                "required": ["command"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write or create a file with content. "
                "Use when user asks to: create, write, save a file. "
                "Examples: 'create test.py with hello world', 'write config.json'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path where file should be created"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite if file exists (default: false)",
                        "default": False
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },

    # =========================================================================
    # CITATION MANAGEMENT TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "export_to_zotero",
            "description": (
                "Export papers to Zotero-compatible formats (BibTeX or RIS). "
                "Use when user wants to: export citations, save to Zotero, generate BibTeX, "
                "create bibliography, export references for LaTeX/Word. "
                "Examples: 'export to BibTeX', 'save these papers to Zotero', "
                "'generate bibliography for these papers'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "papers": {
                        "type": "array",
                        "description": "List of papers to export (paper objects from previous search)",
                        "items": {"type": "object"}
                    },
                    "format": {
                        "type": "string",
                        "description": "Export format (bibtex or ris)",
                        "enum": ["bibtex", "ris"],
                        "default": "bibtex"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (optional)",
                        "default": None
                    }
                },
                "required": ["papers"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "find_related_papers",
            "description": (
                "Find papers related to a given paper via citation networks. "
                "Discovers papers that cite the same references (co-citations) or "
                "are cited by similar papers. Great for literature review expansion. "
                "Use when user wants: related papers, similar research, citation network, "
                "papers building on this work, what cites this paper. "
                "Examples: 'find related papers to BERT', 'what papers cite this', "
                "'expand my literature review'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "Paper ID, DOI, or title to find related papers for"
                    },
                    "method": {
                        "type": "string",
                        "description": "How to find related papers",
                        "enum": ["citations", "references", "similar"],
                        "default": "similar"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of related papers to return",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["paper_id"]
            }
        }
    },

    # =========================================================================
    # DATA ANALYSIS & STATISTICS TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "load_dataset",
            "description": (
                "Load a dataset from CSV or Excel file and AUTOMATICALLY compute statistics (mean, std, min, max, median). "
                "ALWAYS use this tool (not read_file) when user asks for: mean, average, standard deviation, min, max, median, statistics, "
                "calculate, compute, analyze data, load CSV/Excel, work with datasets. "
                "This tool returns pre-computed statistics so you can answer statistical questions immediately. "
                "Examples: 'load data.csv and calculate mean', 'analyze this Excel file', "
                "'what is the average in my dataset', 'compute standard deviation'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to CSV or Excel file (.csv, .xlsx, .xls, .tsv)"
                    }
                },
                "required": ["filepath"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "analyze_data",
            "description": (
                "Compute descriptive statistics or correlation analysis on loaded dataset. "
                "Use for: descriptive stats (mean, median, std, quartiles), correlation tests, "
                "data summary, exploring relationships between variables. "
                "Examples: 'show me descriptive stats', 'correlate hours and scores', "
                "'is there a relationship between X and Y'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of analysis to perform",
                        "enum": ["descriptive", "correlation"],
                        "default": "descriptive"
                    },
                    "column": {
                        "type": "string",
                        "description": "Column name for descriptive stats (optional, all columns if not specified)"
                    },
                    "var1": {
                        "type": "string",
                        "description": "First variable for correlation (required for correlation)"
                    },
                    "var2": {
                        "type": "string",
                        "description": "Second variable for correlation (required for correlation)"
                    },
                    "method": {
                        "type": "string",
                        "description": "Correlation method",
                        "enum": ["pearson", "spearman"],
                        "default": "pearson"
                    }
                },
                "required": ["analysis_type"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "run_regression",
            "description": (
                "Run linear or multiple regression analysis on loaded dataset. "
                "Use when user wants: regression analysis, predict Y from X, model relationships, "
                "test predictors, find R-squared, regression coefficients. "
                "Examples: 'regress score on hours', 'predict Y from X1 and X2', "
                "'run regression: sales ~ advertising + price'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "y_variable": {
                        "type": "string",
                        "description": "Dependent variable (outcome) to predict"
                    },
                    "x_variables": {
                        "type": "array",
                        "description": "Independent variables (predictors)",
                        "items": {"type": "string"},
                        "minItems": 1
                    },
                    "model_type": {
                        "type": "string",
                        "description": "Type of regression model",
                        "enum": ["linear"],
                        "default": "linear"
                    }
                },
                "required": ["y_variable", "x_variables"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_assumptions",
            "description": (
                "Check statistical assumptions for tests (normality, homoscedasticity, etc.). "
                "Use when user asks: check assumptions, validate test requirements, "
                "normality test, homoscedasticity, assumption violations. "
                "Examples: 'check regression assumptions', 'is my data normal', "
                "'can I use ANOVA with this data'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "test_type": {
                        "type": "string",
                        "description": "Type of statistical test to check assumptions for",
                        "enum": ["regression", "anova", "ttest"]
                    }
                },
                "required": ["test_type"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "plot_data",
            "description": (
                "Create ASCII plots (scatter, bar, histogram) for data visualization in terminal. "
                "Use when user wants: plot data, visualize relationship, show distribution, "
                "create chart, graph variables. "
                "Examples: 'plot hours vs scores', 'show histogram of ages', "
                "'create bar chart of categories'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "plot_type": {
                        "type": "string",
                        "description": "Type of plot to create",
                        "enum": ["scatter", "bar", "histogram"],
                        "default": "scatter"
                    },
                    "x_data": {
                        "description": "X-axis data (column name from dataset or list of values)"
                    },
                    "y_data": {
                        "description": "Y-axis data for scatter plots (column name or list of values)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Plot title",
                        "default": "Data Plot"
                    },
                    "categories": {
                        "type": "array",
                        "description": "Category names for bar chart",
                        "items": {"type": "string"}
                    },
                    "values": {
                        "description": "Values for bar chart or histogram (column name or list)"
                    },
                    "bins": {
                        "type": "integer",
                        "description": "Number of bins for histogram",
                        "default": 10,
                        "minimum": 5,
                        "maximum": 50
                    }
                },
                "required": ["plot_type"]
            }
        }
    },

    # =========================================================================
    # PYTHON CODE EXECUTION TOOL
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "run_python_code",
            "description": (
                "Execute Python code for data analysis with pandas, numpy, scipy. "
                "Use for COMPLEX calculations: correlations, regressions, custom aggregations, "
                "filtering, groupby operations, statistical tests, data transformations. "
                "The code has access to 'df' (loaded dataset) and returns the result. "
                "Examples: 'df.groupby(\"Method\").mean()', 'df[\"Spread\"].corr(df[\"Low_Ivol_Return\"])', "
                "'scipy.stats.ttest_ind(group1, group2)', 'df.describe()'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "python_code": {
                        "type": "string",
                        "description": "Python code to execute. Has access to: df (pandas DataFrame), pd (pandas), np (numpy), scipy.stats"
                    },
                    "filepath": {
                        "type": "string",
                        "description": "Optional: Path to CSV/Excel file to load as 'df' (if not already loaded)"
                    }
                },
                "required": ["python_code"]
            }
        }
    },

    # =========================================================================
    # R INTEGRATION TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "run_r_code",
            "description": (
                "Execute R code safely with validation and timeout. "
                "Use when user wants: run R script, execute R code, R analysis, "
                "use R packages, statistical analysis in R. "
                "Examples: 'run this R code: lm(y~x)', 'execute R script', "
                "'install.packages in R'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "r_code": {
                        "type": "string",
                        "description": "R code to execute"
                    },
                    "allow_writes": {
                        "type": "boolean",
                        "description": "Allow file write operations (default: false for safety)",
                        "default": False
                    }
                },
                "required": ["r_code"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "detect_project",
            "description": (
                "Detect project type (R project, Jupyter notebook, Python project) in directory. "
                "Use when user asks: what type of project, detect environment, "
                "check if R project, find project files, what packages installed. "
                "Examples: 'what type of project is this', 'am I in an R project', "
                "'what R packages do I have'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to check for project (default: current directory)",
                        "default": "."
                    }
                },
                "required": []
            }
        }
    },

    # =========================================================================
    # CONVERSATIONAL TOOL
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "chat",
            "description": (
                "Respond to conversational queries without using any tools. "
                "Use for: greetings ('hi', 'hello'), acknowledgments ('thanks', 'ok'), "
                "meta questions about the agent ('what can you do', 'who made you', 'are you AI'), "
                "simple tests ('test', 'testing'), casual conversation. "
                "Examples: 'test', 'thanks', 'how are you', 'what are your capabilities', "
                "'did you hardcode this', 'who built you'. "
                "IMPORTANT: Use this for questions ABOUT the agent itself, not questions "
                "that need external data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Conversational response to user"
                    }
                },
                "required": ["message"]
            }
        }
    },
    # =========================================================================
    # MAGICAL RESEARCH MODULES - Advanced Research Assistant
    # =========================================================================
    
    # ---------------------------------------------------------------------
    # R Workspace Bridge
    # ---------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "list_r_objects",
            "description": "List all objects in R workspace/environment. Use when user wants to see what datasets or variables are available in their R session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_path": {
                        "type": "string",
                        "description": "Path to .RData file (optional, uses active R session if not specified)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_r_dataframe",
            "description": "Retrieve a dataframe from R workspace without saving to disk first. Use when user has data in R console and wants to analyze it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Name of R object to retrieve (e.g., 'my_data', 'df')"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Path to .RData file (optional)"
                    }
                },
                "required": ["object_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_r_and_capture",
            "description": "Execute R code and capture specific objects from the result. Use for complex R operations where you need the output objects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "r_code": {
                        "type": "string",
                        "description": "R code to execute"
                    },
                    "capture_objects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Names of R objects to capture after execution"
                    }
                },
                "required": ["r_code", "capture_objects"]
            }
        }
    },
    
    # ---------------------------------------------------------------------
    # Qualitative Coding Suite
    # ---------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "create_code",
            "description": "Create a qualitative code for interview/focus group analysis. Use when user wants to code qualitative data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code_name": {
                        "type": "string",
                        "description": "Name of the code (e.g., 'hope', 'barrier', 'motivation')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what this code represents"
                    },
                    "parent_code": {
                        "type": "string",
                        "description": "Parent code for hierarchical coding (optional)"
                    }
                },
                "required": ["code_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_transcript",
            "description": "Load interview or focus group transcript for coding. Use when user has qualitative text data to analyze.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Unique document identifier (e.g., 'interview_01')"
                    },
                    "content": {
                        "type": "string",
                        "description": "Full transcript text"
                    },
                    "format_type": {
                        "type": "string",
                        "enum": ["plain", "interview", "focus_group"],
                        "description": "Format of transcript (default: plain)"
                    }
                },
                "required": ["doc_id", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "code_segment",
            "description": "Apply codes to a segment of transcript. Use when coding specific text excerpts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document identifier"
                    },
                    "line_start": {
                        "type": "integer",
                        "description": "Starting line number (1-indexed)"
                    },
                    "line_end": {
                        "type": "integer",
                        "description": "Ending line number"
                    },
                    "codes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of code names to apply"
                    }
                },
                "required": ["doc_id", "line_start", "line_end", "codes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_coded_excerpts",
            "description": "Get all text excerpts coded with a specific code. Use to retrieve all instances of a theme.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code_name": {
                        "type": "string",
                        "description": "Code name to retrieve excerpts for"
                    }
                },
                "required": ["code_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "auto_extract_themes",
            "description": "Automatically extract themes from transcripts using n-gram analysis. Use when user wants to find common themes across multiple documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Document IDs to analyze (null = all documents)"
                    },
                    "min_frequency": {
                        "type": "integer",
                        "description": "Minimum times a theme must appear (default: 3)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_kappa",
            "description": "Calculate Cohen's Kappa inter-rater reliability between two coders. Use to assess coding agreement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "coder1_codes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Codes from coder 1"
                    },
                    "coder2_codes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Codes from coder 2 (same length as coder1)"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["cohen_kappa"],
                        "description": "Reliability method (default: cohen_kappa)"
                    }
                },
                "required": ["coder1_codes", "coder2_codes"]
            }
        }
    },
    
    # ---------------------------------------------------------------------
    # Data Cleaning Magic
    # ---------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "scan_data_quality",
            "description": "Automatically scan dataset for quality issues: missing values, outliers, duplicates, type mismatches, distribution problems. Use before data analysis.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "auto_clean_data",
            "description": "Automatically fix data quality issues found by scan_data_quality. One-click cleaning for common problems.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fix_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Types to fix: ['missing_values', 'duplicates', 'outliers'] (null = all fixable)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "handle_missing_values",
            "description": "Handle missing values in specific column with chosen strategy (median, mean, mode, forward_fill, knn).",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "Column name to handle missing values"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["median", "mean", "mode", "forward_fill", "knn"],
                        "description": "Imputation method"
                    }
                },
                "required": ["column", "method"]
            }
        }
    },
    
    # ---------------------------------------------------------------------
    # Advanced Statistics
    # ---------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "run_pca",
            "description": "Run Principal Component Analysis for dimensionality reduction. Use when user has many correlated variables and wants to reduce them.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Variables to include (null = all numeric)"
                    },
                    "n_components": {
                        "type": "integer",
                        "description": "Number of components to extract (null = all)"
                    },
                    "standardize": {
                        "type": "boolean",
                        "description": "Whether to standardize variables first (default: true)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_factor_analysis",
            "description": "Run Exploratory Factor Analysis to identify latent factors. Use when user wants to find underlying constructs in survey/scale data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Variables to analyze"
                    },
                    "n_factors": {
                        "type": "integer",
                        "description": "Number of factors to extract (default: 3)"
                    },
                    "rotation": {
                        "type": "string",
                        "enum": ["varimax", "promax"],
                        "description": "Rotation method (default: varimax)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_mediation",
            "description": "Run mediation analysis to test if M mediates X → Y relationship (Baron & Kenny approach with bootstrap CI). Use for testing indirect effects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "X": {
                        "type": "string",
                        "description": "Independent variable (predictor)"
                    },
                    "M": {
                        "type": "string",
                        "description": "Mediator variable"
                    },
                    "Y": {
                        "type": "string",
                        "description": "Dependent variable (outcome)"
                    },
                    "bootstrap_samples": {
                        "type": "integer",
                        "description": "Number of bootstrap samples for CI (default: 5000)"
                    }
                },
                "required": ["X", "M", "Y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_moderation",
            "description": "Run moderation analysis to test if W moderates X → Y relationship (interaction effect). Use to test conditional effects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "X": {
                        "type": "string",
                        "description": "Independent variable (predictor)"
                    },
                    "W": {
                        "type": "string",
                        "description": "Moderator variable"
                    },
                    "Y": {
                        "type": "string",
                        "description": "Dependent variable (outcome)"
                    },
                    "center_variables": {
                        "type": "boolean",
                        "description": "Whether to mean-center X and W (default: true)"
                    }
                },
                "required": ["X", "W", "Y"]
            }
        }
    },
    
    # ---------------------------------------------------------------------
    # Power Analysis
    # ---------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "calculate_sample_size",
            "description": "Calculate required sample size for a statistical test given effect size and desired power. Use for grant proposals and study planning.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_type": {
                        "type": "string",
                        "enum": ["ttest", "correlation", "anova", "regression"],
                        "description": "Type of statistical test"
                    },
                    "effect_size": {
                        "type": "number",
                        "description": "Expected effect size (Cohen's d for t-test, r for correlation, f for ANOVA, f² for regression)"
                    },
                    "alpha": {
                        "type": "number",
                        "description": "Significance level (default: 0.05)"
                    },
                    "power": {
                        "type": "number",
                        "description": "Desired statistical power (default: 0.80)"
                    },
                    "n_groups": {
                        "type": "integer",
                        "description": "Number of groups (required for ANOVA)"
                    },
                    "n_predictors": {
                        "type": "integer",
                        "description": "Number of predictors (required for regression)"
                    }
                },
                "required": ["test_type", "effect_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_power",
            "description": "Calculate achieved statistical power given sample size and effect size. Use to assess whether existing study is adequately powered.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_type": {
                        "type": "string",
                        "enum": ["ttest", "correlation", "anova", "regression"],
                        "description": "Type of statistical test"
                    },
                    "effect_size": {
                        "type": "number",
                        "description": "Effect size"
                    },
                    "n": {
                        "type": "integer",
                        "description": "Sample size (per group for t-test/ANOVA, total for correlation/regression)"
                    },
                    "alpha": {
                        "type": "number",
                        "description": "Significance level (default: 0.05)"
                    },
                    "n_groups": {
                        "type": "integer",
                        "description": "Number of groups (for ANOVA)"
                    },
                    "n_predictors": {
                        "type": "integer",
                        "description": "Number of predictors (for regression)"
                    }
                },
                "required": ["test_type", "effect_size", "n"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_mde",
            "description": "Calculate minimum detectable effect size given sample size and power. Use to understand what effects can be reliably detected.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_type": {
                        "type": "string",
                        "enum": ["ttest", "anova"],
                        "description": "Type of statistical test"
                    },
                    "n": {
                        "type": "integer",
                        "description": "Sample size"
                    },
                    "alpha": {
                        "type": "number",
                        "description": "Significance level (default: 0.05)"
                    },
                    "power": {
                        "type": "number",
                        "description": "Desired power (default: 0.80)"
                    },
                    "n_groups": {
                        "type": "integer",
                        "description": "Number of groups (for ANOVA)"
                    }
                },
                "required": ["test_type", "n"]
            }
        }
    },
    
    # ---------------------------------------------------------------------
    # Literature Synthesis AI
    # ---------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "add_paper",
            "description": "Add a paper to literature synthesis for systematic review. Use when building a literature review across multiple papers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "Unique paper identifier"
                    },
                    "title": {
                        "type": "string",
                        "description": "Paper title"
                    },
                    "abstract": {
                        "type": "string",
                        "description": "Paper abstract"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Publication year"
                    },
                    "authors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of author names"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paper keywords"
                    },
                    "findings": {
                        "type": "string",
                        "description": "Key findings/conclusion"
                    }
                },
                "required": ["paper_id", "title", "abstract"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_lit_themes",
            "description": "Extract common themes across all papers in literature synthesis using n-gram analysis. Use to find recurring topics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_papers": {
                        "type": "integer",
                        "description": "Minimum papers mentioning theme (default: 3)"
                    },
                    "theme_length": {
                        "type": "integer",
                        "description": "Length of n-grams for themes (default: 2)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_research_gaps",
            "description": "Identify research gaps: understudied time periods, underused methods, emerging themes, underrepresented contexts. Use to find dissertation topics.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_synthesis_matrix",
            "description": "Create synthesis matrix comparing papers across dimensions (method, sample_size, findings, population). Use for systematic review tables.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dimensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Dimensions to compare (default: ['method', 'findings'])"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_contradictions",
            "description": "Find papers with contradictory findings on the same topics. Use to identify debates in literature.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
]


def get_tool_by_name(name: str) -> Dict[str, Any]:
    """Get tool definition by name"""
    for tool in TOOLS:
        if tool["function"]["name"] == name:
            return tool
    return None


def get_tool_names() -> List[str]:
    """Get list of all tool names"""
    return [tool["function"]["name"] for tool in TOOLS]


def validate_tool_call(tool_name: str, arguments: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a tool call against its schema.

    Returns:
        (is_valid, error_message)
    """
    tool = get_tool_by_name(tool_name)
    if not tool:
        return False, f"Unknown tool: {tool_name}"

    schema = tool["function"]["parameters"]
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    # Check required parameters
    for param in required:
        if param not in arguments:
            return False, f"Missing required parameter: {param}"

    # Check parameter types (basic validation)
    for param, value in arguments.items():
        if param not in properties:
            return False, f"Unknown parameter: {param}"

        expected_type = properties[param].get("type")
        if expected_type == "string" and not isinstance(value, str):
            return False, f"Parameter {param} must be a string"
        elif expected_type == "integer" and not isinstance(value, int):
            return False, f"Parameter {param} must be an integer"
        elif expected_type == "boolean" and not isinstance(value, bool):
            return False, f"Parameter {param} must be a boolean"
        elif expected_type == "array" and not isinstance(value, list):
            return False, f"Parameter {param} must be an array"

    return True, ""

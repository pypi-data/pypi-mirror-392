#!/usr/bin/env python3
"""
Research Assistant Module
Comprehensive data analysis, visualization, and R integration
Integrates: adaptive_providers, ascii_plotting, execution_safety, project_detector
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import subprocess
import tempfile
import os
import re
from enum import Enum


# ============================================================================
# DATA ANALYSIS
# ============================================================================

@dataclass
class DatasetInfo:
    """Information about a loaded dataset"""
    filepath: str
    rows: int
    columns: int
    column_names: List[str]
    column_types: Dict[str, str]
    missing_values: Dict[str, int]
    numeric_columns: List[str]
    categorical_columns: List[str]


@dataclass
class StatisticalResult:
    """Result from statistical analysis"""
    test_name: str
    statistic: float
    p_value: float
    interpretation: str
    details: Dict[str, Any]


class DataAnalyzer:
    """Statistical data analysis and hypothesis testing"""

    def __init__(self):
        self.current_dataset: Optional[pd.DataFrame] = None
        self.dataset_info: Optional[DatasetInfo] = None

    @property
    def df(self) -> Optional[pd.DataFrame]:
        """Alias for current_dataset for compatibility with tool_executor"""
        return self.current_dataset

    def load_dataset(self, filepath: str) -> Dict[str, Any]:
        """Load CSV or Excel file and return dataset info"""
        try:
            path = Path(filepath).expanduser()

            # Detect file type and load
            if path.suffix.lower() == '.csv':
                df = pd.read_csv(path)
            elif path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(path)
            elif path.suffix.lower() == '.tsv':
                df = pd.read_csv(path, sep='\t')
            else:
                return {"error": f"Unsupported file type: {path.suffix}"}

            self.current_dataset = df

            # Analyze dataset
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

            missing = {col: int(df[col].isna().sum()) for col in df.columns}

            self.dataset_info = DatasetInfo(
                filepath=str(path),
                rows=len(df),
                columns=len(df.columns),
                column_names=df.columns.tolist(),
                column_types={col: str(df[col].dtype) for col in df.columns},
                missing_values=missing,
                numeric_columns=numeric_cols,
                categorical_columns=categorical_cols
            )

            return {
                "success": True,
                "filepath": str(path),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "numeric_columns": numeric_cols,
                "categorical_columns": categorical_cols,
                "missing_values": missing,
                "preview": df.head(5).to_dict('records')
            }

        except Exception as e:
            return {"error": f"Failed to load dataset: {str(e)}"}

    def descriptive_stats(self, column: Optional[str] = None) -> Dict[str, Any]:
        """Compute descriptive statistics"""
        if self.current_dataset is None:
            return {"error": "No dataset loaded"}

        try:
            if column:
                # Stats for specific column
                if column not in self.current_dataset.columns:
                    return {"error": f"Column '{column}' not found"}

                series = self.current_dataset[column]

                if pd.api.types.is_numeric_dtype(series):
                    return {
                        "column": column,
                        "count": int(series.count()),
                        "mean": float(series.mean()),
                        "std": float(series.std()),
                        "min": float(series.min()),
                        "q25": float(series.quantile(0.25)),
                        "median": float(series.median()),
                        "q75": float(series.quantile(0.75)),
                        "max": float(series.max()),
                        "missing": int(series.isna().sum())
                    }
                else:
                    value_counts = series.value_counts().head(10).to_dict()
                    return {
                        "column": column,
                        "type": "categorical",
                        "unique_values": int(series.nunique()),
                        "top_values": {str(k): int(v) for k, v in value_counts.items()},
                        "missing": int(series.isna().sum())
                    }
            else:
                # Stats for all numeric columns
                numeric_cols = self.dataset_info.numeric_columns if self.dataset_info else self.current_dataset.select_dtypes(include=[np.number]).columns.tolist()

                # Compute stats for each column
                stats_dict = {}
                for col in numeric_cols:
                    series = self.current_dataset[col]
                    stats_dict[col] = {
                        "count": int(series.count()),
                        "mean": float(series.mean()),
                        "std": float(series.std()),
                        "min": float(series.min()),
                        "q25": float(series.quantile(0.25)),
                        "median": float(series.median()),
                        "q75": float(series.quantile(0.75)),
                        "max": float(series.max()),
                        "missing": int(series.isna().sum())
                    }

                return {
                    "stats": stats_dict,
                    "correlation_matrix": self.current_dataset[numeric_cols].corr().to_dict() if numeric_cols else {}
                }

        except Exception as e:
            return {"error": f"Failed to compute stats: {str(e)}"}

    def run_correlation(self, var1: str, var2: str, method: str = "pearson") -> Dict[str, Any]:
        """Compute correlation between two variables"""
        if self.current_dataset is None:
            return {"error": "No dataset loaded"}

        try:
            from scipy.stats import pearsonr, spearmanr

            if var1 not in self.current_dataset.columns or var2 not in self.current_dataset.columns:
                return {"error": "One or both variables not found"}

            # Drop missing values
            data = self.current_dataset[[var1, var2]].dropna()

            if len(data) < 3:
                return {"error": "Not enough data points (need at least 3)"}

            x = data[var1]
            y = data[var2]

            if method == "pearson":
                r, p = pearsonr(x, y)
                method_name = "Pearson"
            else:
                r, p = spearmanr(x, y)
                method_name = "Spearman"

            # Interpret strength
            if abs(r) < 0.3:
                strength = "weak"
            elif abs(r) < 0.7:
                strength = "moderate"
            else:
                strength = "strong"

            direction = "positive" if r > 0 else "negative"

            return {
                "correlation_coefficient": float(r),
                "p_value": float(p),
                "method": method_name,
                "n_observations": len(data),
                "interpretation": f"{strength} {direction} correlation",
                "significant": p < 0.05
            }

        except Exception as e:
            return {"error": f"Correlation analysis failed: {str(e)}"}

    def run_regression(self, y_var: str, x_vars: List[str], model_type: str = "linear") -> Dict[str, Any]:
        """Run regression analysis"""
        if self.current_dataset is None:
            return {"error": "No dataset loaded"}

        try:
            from scipy.stats import linregress
            import statsmodels.api as sm

            # Prepare data
            y = self.current_dataset[y_var].dropna()
            X = self.current_dataset[x_vars].dropna()

            # Align indices
            common_idx = y.index.intersection(X.index)
            y = y.loc[common_idx]
            X = X.loc[common_idx]

            if len(y) < len(x_vars) + 2:
                return {"error": f"Need at least {len(x_vars) + 2} observations"}

            if model_type == "linear":
                # Simple linear regression (one predictor)
                if len(x_vars) == 1:
                    x = X.iloc[:, 0]
                    slope, intercept, r_value, p_value, std_err = linregress(x, y)

                    return {
                        "model_type": "Simple Linear Regression",
                        "dependent_variable": y_var,
                        "independent_variable": x_vars[0],
                        "n_observations": len(y),
                        "coefficients": {
                            "intercept": float(intercept),
                            x_vars[0]: float(slope)
                        },
                        "r_squared": float(r_value ** 2),
                        "p_value": float(p_value),
                        "std_error": float(std_err),
                        "equation": f"{y_var} = {intercept:.3f} + {slope:.3f}*{x_vars[0]}"
                    }
                else:
                    # Multiple regression
                    X_with_const = sm.add_constant(X)
                    model = sm.OLS(y, X_with_const).fit()

                    return {
                        "model_type": "Multiple Linear Regression",
                        "dependent_variable": y_var,
                        "independent_variables": x_vars,
                        "n_observations": int(model.nobs),
                        "r_squared": float(model.rsquared),
                        "adj_r_squared": float(model.rsquared_adj),
                        "f_statistic": float(model.fvalue),
                        "f_pvalue": float(model.f_pvalue),
                        "coefficients": {
                            k: float(v) for k, v in model.params.items()
                        },
                        "p_values": {
                            k: float(v) for k, v in model.pvalues.items()
                        },
                        "summary": str(model.summary())
                    }

        except Exception as e:
            return {"error": f"Regression failed: {str(e)}"}

    def check_assumptions(self, test_type: str) -> Dict[str, Any]:
        """Check statistical assumptions for a given test"""
        if self.current_dataset is None:
            return {"error": "No dataset loaded"}

        try:
            from scipy.stats import shapiro, levene

            if test_type.lower() in ["anova", "t-test", "regression"]:
                # Check normality for numeric columns
                normality_results = {}

                for col in self.dataset_info.numeric_columns[:5]:  # Check first 5
                    data = self.current_dataset[col].dropna()
                    if len(data) >= 3:
                        stat, p = shapiro(data)
                        normality_results[col] = {
                            "statistic": float(stat),
                            "p_value": float(p),
                            "normal": p > 0.05
                        }

                return {
                    "test_type": test_type,
                    "assumptions_checked": ["normality"],
                    "normality_tests": normality_results,
                    "guidance": "p > 0.05 suggests data is normally distributed"
                }

            return {"error": f"Assumption checking not implemented for {test_type}"}

        except Exception as e:
            return {"error": f"Assumption check failed: {str(e)}"}


# ============================================================================
# ASCII PLOTTING (from ascii_plotting.py)
# ============================================================================

class ASCIIPlotter:
    """Generate ASCII plots in terminal"""

    def __init__(self, width: int = 70, height: int = 20):
        self.width = width
        self.height = height

    def plot_scatter(self, x: List[float], y: List[float], title: str = "Scatter Plot") -> str:
        """Create ASCII scatter plot"""
        if len(x) != len(y) or len(x) == 0:
            return "Error: x and y must have same length and not be empty"

        # Normalize to plot dimensions
        x_min, x_max = min(x), max(x)
        y_min, y_max = min(y), max(y)

        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1

        # Create plot grid
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Plot points
        for xi, yi in zip(x, y):
            plot_x = int((xi - x_min) / x_range * (self.width - 1))
            plot_y = int((1 - (yi - y_min) / y_range) * (self.height - 1))
            if 0 <= plot_x < self.width and 0 <= plot_y < self.height:
                grid[plot_y][plot_x] = '●'

        # Build output
        output = [f"\n{title}"]
        output.append("┌" + "─" * self.width + "┐")

        for row in grid:
            output.append("│" + "".join(row) + "│")

        output.append("└" + "─" * self.width + "┘")
        output.append(f"  {x_min:.2f}" + " " * (self.width - 20) + f"{x_max:.2f}")

        return "\n".join(output)

    def plot_bar(self, categories: List[str], values: List[float], title: str = "Bar Chart") -> str:
        """Create ASCII bar chart"""
        if len(categories) != len(values) or len(categories) == 0:
            return "Error: categories and values must have same length"

        max_val = max(values) if values else 1
        max_label_len = max(len(c) for c in categories)

        output = [f"\n{title}", ""]

        for cat, val in zip(categories, values):
            bar_len = int((val / max_val) * (self.width - max_label_len - 10))
            bar = "█" * bar_len
            output.append(f"{cat:>{max_label_len}} │{bar} {val:.2f}")

        return "\n".join(output)

    def plot_histogram(self, data: List[float], bins: int = 10, title: str = "Histogram") -> str:
        """Create ASCII histogram"""
        if not data:
            return "Error: no data provided"

        # Create bins
        min_val, max_val = min(data), max(data)
        bin_width = (max_val - min_val) / bins

        hist_bins = [0] * bins
        for val in data:
            bin_idx = min(int((val - min_val) / bin_width), bins - 1)
            hist_bins[bin_idx] += 1

        max_count = max(hist_bins) if hist_bins else 1

        output = [f"\n{title}", ""]

        for i, count in enumerate(hist_bins):
            bin_start = min_val + i * bin_width
            bin_end = bin_start + bin_width
            bar_len = int((count / max_count) * (self.width - 20))
            bar = "█" * bar_len
            output.append(f"{bin_start:7.2f}-{bin_end:7.2f} │{bar} ({count})")

        return "\n".join(output)


# ============================================================================
# EXECUTION SAFETY (from execution_safety.py)
# ============================================================================

class CommandClassification(Enum):
    """Safety classification for commands"""
    SAFE = "safe"                  # File reads, non-destructive queries
    WRITE = "write"                # File writes, modifications
    DANGEROUS = "dangerous"         # rm -rf, format disk, etc.
    BLOCKED = "blocked"            # Never execute


class ExecutionSafetyValidator:
    """Validates commands before execution"""

    # Patterns for dangerous commands
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf\s+/',
        r'format\s+[A-Z]:',
        r'dd\s+if=',
        r'mkfs\.',
        r'fdisk',
        r':(){ :|:& };:',  # Fork bomb
        r'shutdown',
        r'reboot',
        r'init\s+0',
    ]

    # Patterns for write operations
    WRITE_PATTERNS = [
        r'>\s*\S+',  # Redirection
        r'>>\s*\S+',
        r'\brm\b',
        r'\bmv\b',
        r'\bcp\b.*\S+',
        r'install\.packages',
        r'save\(',
        r'write\.',
    ]

    @classmethod
    def classify_command(cls, command: str) -> CommandClassification:
        """Classify command safety level"""
        cmd_lower = command.lower()

        # Check dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_lower, re.IGNORECASE):
                return CommandClassification.DANGEROUS

        # Check write patterns
        for pattern in cls.WRITE_PATTERNS:
            if re.search(pattern, command):
                return CommandClassification.WRITE

        # Default to safe for reads
        return CommandClassification.SAFE

    @classmethod
    def validate_r_code(cls, r_code: str) -> Tuple[bool, str, CommandClassification]:
        """
        Validate R code before execution
        Returns: (is_safe, message, classification)
        """
        classification = cls.classify_command(r_code)

        if classification == CommandClassification.DANGEROUS:
            return False, "Code contains dangerous operations", classification

        if classification == CommandClassification.WRITE:
            return True, "Code will modify files - proceed with caution", classification

        return True, "Code appears safe", classification


# ============================================================================
# R CODE EXECUTOR
# ============================================================================

class RExecutor:
    """Execute R code safely"""

    def __init__(self):
        self.safety_validator = ExecutionSafetyValidator()

    def execute_r_code(self, r_code: str, allow_writes: bool = False) -> Dict[str, Any]:
        """Execute R code and return results"""
        # Validate safety
        is_safe, message, classification = self.safety_validator.validate_r_code(r_code)

        if not is_safe:
            return {
                "error": f"Code rejected: {message}",
                "classification": classification.value
            }

        if classification == CommandClassification.WRITE and not allow_writes:
            return {
                "error": "Code requires write permissions. Set allow_writes=True to execute.",
                "classification": classification.value,
                "preview": r_code[:200]
            }

        # Check if R is available
        try:
            subprocess.run(['R', '--version'], capture_output=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {"error": "R is not installed or not in PATH"}

        # Execute R code
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
                f.write(r_code)
                script_path = f.name

            try:
                result = subprocess.run(
                    ['Rscript', script_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "classification": classification.value
                }
            finally:
                os.unlink(script_path)

        except subprocess.TimeoutExpired:
            return {"error": "R code execution timed out (30s limit)"}
        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}


# ============================================================================
# PROJECT DETECTOR (from project_detector.py)
# ============================================================================

class ProjectDetector:
    """Detects project type and provides context"""

    def __init__(self, working_dir: Optional[str] = None):
        self.working_dir = Path(working_dir or os.getcwd())

    def detect_project(self) -> Optional[Dict[str, Any]]:
        """Detect project type"""
        # Check for R project
        rproj_files = list(self.working_dir.glob('*.Rproj'))
        if rproj_files:
            return {
                "type": "r_project",
                "name": rproj_files[0].stem,
                "path": str(self.working_dir),
                "project_file": str(rproj_files[0]),
                "r_files": len(list(self.working_dir.glob('*.R'))),
                "rmd_files": len(list(self.working_dir.glob('*.Rmd')))
            }

        # Check for Jupyter notebooks
        ipynb_files = list(self.working_dir.glob('*.ipynb'))
        if ipynb_files:
            return {
                "type": "jupyter_project",
                "path": str(self.working_dir),
                "notebooks": [f.name for f in ipynb_files]
            }

        # Check for Python project
        if (self.working_dir / 'setup.py').exists() or (self.working_dir / 'pyproject.toml').exists():
            return {
                "type": "python_project",
                "path": str(self.working_dir),
                "py_files": len(list(self.working_dir.glob('*.py')))
            }

        return None

    def get_r_packages(self) -> List[str]:
        """Get installed R packages"""
        try:
            result = subprocess.run(
                ['Rscript', '-e', 'cat(installed.packages()[,1], sep="\n")'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
        except:
            pass
        return []

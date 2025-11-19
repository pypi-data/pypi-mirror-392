"""
Data Cleaning Magic - Auto-detect and Fix Data Quality Issues
=============================================================

Automatically detect:
- Outliers (IQR, Z-score, isolation forest)
- Missing values (with smart imputation)
- Duplicates
- Data type issues
- Distribution problems

The "magical" part: Smart suggestions for fixing issues.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from scipy import stats
from dataclasses import dataclass


@dataclass
class DataQualityIssue:
    """Represents a data quality problem"""
    issue_type: str  # "outlier", "missing", "duplicate", etc.
    severity: str  # "low", "medium", "high"
    column: Optional[str]
    row_indices: Optional[List[int]]
    description: str
    suggestion: str
    auto_fixable: bool


class DataCleaningWizard:
    """Automatically detect and fix data quality issues"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.original_df = df.copy()
        self.issues: List[DataQualityIssue] = []

    def scan_all_issues(self) -> Dict[str, Any]:
        """
        Comprehensive scan for all data quality issues

        Returns:
            Report of all issues found
        """
        self.issues = []

        # Check each type of issue
        self._detect_missing_values()
        self._detect_duplicates()
        self._detect_outliers()
        self._detect_type_issues()
        self._detect_distribution_issues()

        # Categorize by severity
        high = [i for i in self.issues if i.severity == "high"]
        medium = [i for i in self.issues if i.severity == "medium"]
        low = [i for i in self.issues if i.severity == "low"]

        return {
            "success": True,
            "total_issues": len(self.issues),
            "high_severity": len(high),
            "medium_severity": len(medium),
            "low_severity": len(low),
            "auto_fixable": sum(1 for i in self.issues if i.auto_fixable),
            "issues": [
                {
                    "type": issue.issue_type,
                    "severity": issue.severity,
                    "column": issue.column,
                    "affected_rows": len(issue.row_indices) if issue.row_indices else None,
                    "description": issue.description,
                    "suggestion": issue.suggestion,
                    "auto_fixable": issue.auto_fixable
                }
                for issue in self.issues
            ]
        }

    def _detect_missing_values(self):
        """Detect missing values and suggest fixes"""
        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(self.df)) * 100
                missing_idx = self.df[self.df[col].isna()].index.tolist()

                # Determine severity
                if missing_pct > 50:
                    severity = "high"
                    suggestion = f"Consider dropping column '{col}' (>{missing_pct:.1f}% missing)"
                elif missing_pct > 20:
                    severity = "medium"
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        suggestion = f"Impute with median or mean, or use predictive imputation"
                    else:
                        suggestion = f"Impute with mode or create 'Missing' category"
                else:
                    severity = "low"
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        suggestion = f"Impute with median (recommended for <20% missing)"
                    else:
                        suggestion = f"Impute with mode or most frequent value"

                self.issues.append(DataQualityIssue(
                    issue_type="missing_values",
                    severity=severity,
                    column=col,
                    row_indices=missing_idx,
                    description=f"{missing_count} missing values ({missing_pct:.1f}%) in column '{col}'",
                    suggestion=suggestion,
                    auto_fixable=missing_pct < 50
                ))

    def _detect_duplicates(self):
        """Detect duplicate rows"""
        duplicates = self.df[self.df.duplicated(keep=False)]
        if len(duplicates) > 0:
            dup_idx = duplicates.index.tolist()
            unique_dups = self.df[self.df.duplicated(keep='first')].index.tolist()

            self.issues.append(DataQualityIssue(
                issue_type="duplicates",
                severity="medium",
                column=None,
                row_indices=dup_idx,
                description=f"{len(unique_dups)} duplicate rows found ({len(dup_idx)} total including originals)",
                suggestion="Remove duplicates using drop_duplicates(). Keep first occurrence.",
                auto_fixable=True
            ))

    def _detect_outliers(self):
        """Detect outliers using IQR and Z-score methods"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            data = self.df[col].dropna()

            if len(data) < 10:
                continue  # Skip if too few values

            # IQR method
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers_iqr = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)].index.tolist()

            # Z-score method (>3 std devs from mean)
            z_scores = np.abs(stats.zscore(data))
            outliers_zscore = data[z_scores > 3].index.tolist()

            # Combine both methods
            outliers = list(set(outliers_iqr + outliers_zscore))

            if outliers:
                outlier_pct = (len(outliers) / len(self.df)) * 100

                severity = "high" if outlier_pct > 10 else "medium" if outlier_pct > 5 else "low"

                self.issues.append(DataQualityIssue(
                    issue_type="outliers",
                    severity=severity,
                    column=col,
                    row_indices=outliers,
                    description=f"{len(outliers)} outliers detected in '{col}' ({outlier_pct:.1f}%) using IQR and Z-score",
                    suggestion=f"Options: (1) Winsorize (cap at 5th/95th percentile), (2) Log transform, (3) Remove if truly erroneous, (4) Keep if legitimate extreme values",
                    auto_fixable=False  # Requires judgment
                ))

    def _detect_type_issues(self):
        """Detect columns with wrong data types"""
        for col in self.df.columns:
            # Check if numeric column stored as string
            if self.df[col].dtype == 'object':
                # Try converting to numeric
                try:
                    pd.to_numeric(self.df[col], errors='raise')
                    # If successful, it's a type issue
                    self.issues.append(DataQualityIssue(
                        issue_type="type_mismatch",
                        severity="medium",
                        column=col,
                        row_indices=None,
                        description=f"Column '{col}' contains numeric data but stored as text/object",
                        suggestion=f"Convert to numeric: df['{col}'] = pd.to_numeric(df['{col}'])",
                        auto_fixable=True
                    ))
                except (ValueError, TypeError):
                    # Mixed types - check if mostly numeric
                    numeric_count = pd.to_numeric(self.df[col], errors='coerce').notna().sum()
                    total_count = self.df[col].notna().sum()

                    if numeric_count / total_count > 0.8:
                        non_numeric_idx = pd.to_numeric(self.df[col], errors='coerce').isna() & self.df[col].notna()
                        problem_rows = self.df[non_numeric_idx].index.tolist()

                        self.issues.append(DataQualityIssue(
                            issue_type="mixed_types",
                            severity="high",
                            column=col,
                            row_indices=problem_rows,
                            description=f"Column '{col}' is mostly numeric but has {len(problem_rows)} non-numeric values",
                            suggestion=f"Clean non-numeric values, then convert to numeric",
                            auto_fixable=False
                        ))

    def _detect_distribution_issues(self):
        """Detect skewed distributions that might need transformation"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            data = self.df[col].dropna()

            if len(data) < 30:
                continue  # Need sufficient sample size

            # Calculate skewness
            skewness = stats.skew(data)

            if abs(skewness) > 1.0:
                direction = "right" if skewness > 0 else "left"

                self.issues.append(DataQualityIssue(
                    issue_type="skewed_distribution",
                    severity="low",
                    column=col,
                    row_indices=None,
                    description=f"Column '{col}' is highly {direction}-skewed (skewness={skewness:.2f})",
                    suggestion=f"Consider log transformation" if direction == "right" else "Consider reflection + log transform",
                    auto_fixable=True
                ))

    def auto_fix_issues(self, fix_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Automatically fix fixable issues

        Args:
            fix_types: Which types to fix (None = all auto-fixable)

        Returns:
            Report of fixes applied
        """
        if fix_types is None:
            fix_types = ["missing_values", "duplicates", "type_mismatch", "skewed_distribution"]

        fixes_applied = []

        # Fix duplicates
        if "duplicates" in fix_types:
            before = len(self.df)
            self.df = self.df.drop_duplicates()
            after = len(self.df)
            if before != after:
                fixes_applied.append({
                    "type": "duplicates",
                    "description": f"Removed {before - after} duplicate rows"
                })

        # Fix missing values (simple imputation)
        if "missing_values" in fix_types:
            for issue in self.issues:
                if issue.issue_type == "missing_values" and issue.auto_fixable:
                    col = issue.column
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        median_val = self.df[col].median()
                        self.df[col] = self.df[col].fillna(median_val)
                        fixes_applied.append({
                            "type": "missing_values",
                            "column": col,
                            "description": f"Imputed {len(issue.row_indices)} missing values with median ({median_val:.2f})"
                        })
                    else:
                        mode_val = self.df[col].mode()[0] if len(self.df[col].mode()) > 0 else "Unknown"
                        self.df[col] = self.df[col].fillna(mode_val)
                        fixes_applied.append({
                            "type": "missing_values",
                            "column": col,
                            "description": f"Imputed {len(issue.row_indices)} missing values with mode ('{mode_val}')"
                        })

        # Fix type mismatches
        if "type_mismatch" in fix_types:
            for issue in self.issues:
                if issue.issue_type == "type_mismatch" and issue.auto_fixable:
                    col = issue.column
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    fixes_applied.append({
                        "type": "type_mismatch",
                        "column": col,
                        "description": f"Converted column to numeric type"
                    })

        # Fix skewed distributions
        if "skewed_distribution" in fix_types:
            for issue in self.issues:
                if issue.issue_type == "skewed_distribution" and issue.auto_fixable:
                    col = issue.column
                    # Log transformation for right-skewed data
                    if self.df[col].min() > 0:  # Can only log-transform positive values
                        self.df[f"{col}_log"] = np.log(self.df[col])
                        fixes_applied.append({
                            "type": "skewed_distribution",
                            "column": col,
                            "description": f"Created log-transformed column '{col}_log'"
                        })

        return {
            "success": True,
            "fixes_applied": len(fixes_applied),
            "details": fixes_applied,
            "cleaned_dataframe": self.df
        }

    def impute_missing_advanced(
        self,
        column: str,
        method: str = "knn",
        n_neighbors: int = 5
    ) -> Dict[str, Any]:
        """
        Advanced missing value imputation using KNN or predictive methods

        Args:
            column: Column to impute
            method: "knn", "mean", "median", "mode", or "forward_fill"
            n_neighbors: Number of neighbors for KNN imputation

        Returns:
            Imputation results
        """
        from sklearn.impute import KNNImputer

        if column not in self.df.columns:
            return {"error": f"Column '{column}' not found"}

        missing_before = self.df[column].isna().sum()

        if missing_before == 0:
            return {"error": f"No missing values in column '{column}'"}

        if method == "knn":
            # Use KNN imputer on numeric columns only
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()

            if column not in numeric_cols:
                return {"error": "KNN imputation only works for numeric columns"}

            imputer = KNNImputer(n_neighbors=n_neighbors)
            self.df[numeric_cols] = imputer.fit_transform(self.df[numeric_cols])

            return {
                "success": True,
                "method": "KNN",
                "column": column,
                "values_imputed": missing_before,
                "n_neighbors": n_neighbors
            }

        elif method in ["mean", "median", "mode"]:
            if method == "mean":
                fill_value = self.df[column].mean()
            elif method == "median":
                fill_value = self.df[column].median()
            else:  # mode
                fill_value = self.df[column].mode()[0]

            self.df[column] = self.df[column].fillna(fill_value)

            return {
                "success": True,
                "method": method,
                "column": column,
                "fill_value": fill_value,
                "values_imputed": missing_before
            }

        elif method == "forward_fill":
            self.df[column] = self.df[column].fillna(method='ffill')

            return {
                "success": True,
                "method": "forward_fill",
                "column": column,
                "values_imputed": missing_before
            }

        else:
            return {"error": f"Unknown imputation method: {method}"}

    def detect_and_remove_outliers(
        self,
        column: str,
        method: str = "iqr",
        threshold: float = 1.5
    ) -> Dict[str, Any]:
        """
        Detect and remove outliers from a column

        Args:
            column: Column to clean
            method: "iqr", "zscore", or "winsorize"
            threshold: IQR multiplier (1.5) or Z-score threshold (3.0)

        Returns:
            Outlier removal report
        """
        if column not in self.df.columns:
            return {"error": f"Column '{column}' not found"}

        if not pd.api.types.is_numeric_dtype(self.df[column]):
            return {"error": f"Column '{column}' must be numeric"}

        data = self.df[column].dropna()
        before_count = len(self.df)

        if method == "iqr":
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR

            self.df = self.df[(self.df[column] >= lower_bound) & (self.df[column] <= upper_bound)]

        elif method == "zscore":
            z_scores = np.abs(stats.zscore(data))
            self.df = self.df[np.abs(stats.zscore(self.df[column])) <= threshold]

        elif method == "winsorize":
            # Cap at percentiles instead of removing
            lower = self.df[column].quantile(0.05)
            upper = self.df[column].quantile(0.95)
            self.df[column] = self.df[column].clip(lower, upper)

        else:
            return {"error": f"Unknown method: {method}"}

        after_count = len(self.df)
        removed = before_count - after_count

        return {
            "success": True,
            "method": method,
            "column": column,
            "rows_removed": removed,
            "outliers_pct": (removed / before_count) * 100,
            "remaining_rows": after_count
        }

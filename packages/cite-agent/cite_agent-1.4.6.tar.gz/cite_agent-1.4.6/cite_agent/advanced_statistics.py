"""
Advanced Statistics - PCA, Factor Analysis, Time Series, Mediation/Moderation
==============================================================================

Beyond basic stats - the advanced analyses researchers need for publications.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from scipy import stats
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.preprocessing import StandardScaler


class AdvancedStatistics:
    """Advanced statistical analyses for research"""

    def __init__(self, df: Optional[pd.DataFrame] = None):
        self.df = df
        self.scaler = StandardScaler()

    def principal_component_analysis(
        self,
        variables: Optional[List[str]] = None,
        n_components: Optional[int] = None,
        standardize: bool = True
    ) -> Dict[str, Any]:
        """
        Principal Component Analysis (PCA) - Dimensionality reduction

        Args:
            variables: Which columns to include (None = all numeric)
            n_components: Number of components to extract (None = all)
            standardize: Whether to standardize variables first

        Returns:
            PCA results with loadings, explained variance, scores
        """
        if self.df is None:
            return {"error": "No dataframe loaded"}

        # Select variables
        if variables is None:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        else:
            numeric_cols = variables

        if len(numeric_cols) < 2:
            return {"error": "Need at least 2 numeric variables for PCA"}

        X = self.df[numeric_cols].dropna()

        if len(X) < 10:
            return {"error": "Need at least 10 observations for reliable PCA"}

        # Standardize if requested
        if standardize:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X.values

        # Fit PCA
        pca = PCA(n_components=n_components)
        scores = pca.fit_transform(X_scaled)

        # Create loadings dataframe
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=[f"PC{i+1}" for i in range(pca.n_components_)],
            index=numeric_cols
        )

        # Explained variance
        explained_var = pca.explained_variance_ratio_ * 100

        # Cumulative variance
        cumulative_var = np.cumsum(explained_var)

        return {
            "success": True,
            "n_components": pca.n_components_,
            "explained_variance_pct": explained_var.tolist(),
            "cumulative_variance_pct": cumulative_var.tolist(),
            "loadings": loadings.to_dict(),
            "principal_components": scores.tolist(),
            "interpretation": {
                f"PC{i+1}": f"Explains {explained_var[i]:.1f}% of variance"
                for i in range(len(explained_var))
            },
            "recommendation": self._interpret_pca_results(explained_var, cumulative_var)
        }

    def _interpret_pca_results(self, explained_var, cumulative_var):
        """Helper to interpret PCA results"""
        # Kaiser criterion: eigenvalue > 1 (roughly >1/n_vars variance explained)
        avg_variance = 100 / len(explained_var)
        n_above_avg = sum(1 for var in explained_var if var > avg_variance)

        # Find components explaining 80% variance
        n_for_80pct = sum(1 for cum in cumulative_var if cum < 80) + 1

        return {
            "kaiser_criterion": f"Retain {n_above_avg} components (eigenvalue > 1)",
            "scree_plot_suggestion": f"First {min(5, len(explained_var))} components capture most variance",
            "variance_criterion": f"Retain {n_for_80pct} components to explain 80% variance",
            "recommended": min(n_above_avg, n_for_80pct)
        }

    def exploratory_factor_analysis(
        self,
        variables: Optional[List[str]] = None,
        n_factors: int = 3,
        rotation: str = "varimax"
    ) -> Dict[str, Any]:
        """
        Exploratory Factor Analysis - Identify latent factors

        Args:
            variables: Which columns to include
            n_factors: Number of factors to extract
            rotation: "varimax" (orthogonal) or "promax" (oblique)

        Returns:
            Factor loadings, communalities, variance explained
        """
        if self.df is None:
            return {"error": "No dataframe loaded"}

        # Select variables
        if variables is None:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        else:
            numeric_cols = variables

        if len(numeric_cols) < n_factors * 3:
            return {"error": f"Need at least {n_factors * 3} variables for {n_factors} factors (rule of thumb: 3 items per factor)"}

        X = self.df[numeric_cols].dropna()
        X_scaled = self.scaler.fit_transform(X)

        # Fit factor analysis
        fa = FactorAnalysis(n_components=n_factors, rotation=rotation, random_state=42)
        fa.fit(X_scaled)

        # Factor loadings
        loadings = pd.DataFrame(
            fa.components_.T,
            columns=[f"Factor{i+1}" for i in range(n_factors)],
            index=numeric_cols
        )

        # Communalities (proportion of variance explained by factors)
        communalities = 1 - fa.noise_variance_

        # Find dominant loading for each variable
        dominant_factors = {}
        for var in numeric_cols:
            factor_loadings = loadings.loc[var]
            dominant_factor = factor_loadings.abs().idxmax()
            dominant_factors[var] = {
                "factor": dominant_factor,
                "loading": float(factor_loadings[dominant_factor])
            }

        return {
            "success": True,
            "n_factors": n_factors,
            "rotation": rotation,
            "loadings": loadings.to_dict(),
            "communalities": {var: float(comm) for var, comm in zip(numeric_cols, communalities)},
            "dominant_factors": dominant_factors,
            "factor_interpretation": self._suggest_factor_labels(loadings, numeric_cols),
            "quality_metrics": {
                "avg_communality": float(np.mean(communalities)),
                "low_communality_vars": [
                    var for var, comm in zip(numeric_cols, communalities) if comm < 0.3
                ]
            }
        }

    def _suggest_factor_labels(self, loadings, variable_names):
        """Suggest interpretive labels for factors based on high-loading variables"""
        n_factors = loadings.shape[1]
        suggestions = {}

        for i in range(n_factors):
            factor_name = f"Factor{i+1}"
            factor_loadings = loadings[factor_name]

            # Get variables with high loadings (>0.5)
            high_loading_vars = [
                var for var in variable_names
                if abs(factor_loadings[var]) > 0.5
            ]

            suggestions[factor_name] = {
                "high_loading_variables": high_loading_vars,
                "suggestion": f"Review these {len(high_loading_vars)} variables to identify common theme"
            }

        return suggestions

    def mediation_analysis(
        self,
        X: str,  # Independent variable
        M: str,  # Mediator
        Y: str,  # Dependent variable
        bootstrap_samples: int = 5000
    ) -> Dict[str, Any]:
        """
        Mediation analysis - Test if M mediates X → Y relationship

        Classic Baron & Kenny approach with bootstrapped confidence intervals

        Args:
            X: Independent variable (predictor)
            M: Mediator variable
            Y: Dependent variable (outcome)
            bootstrap_samples: Number of bootstrap samples for CI

        Returns:
            Direct, indirect, and total effects with significance
        """
        if self.df is None:
            return {"error": "No dataframe loaded"}

        for var in [X, M, Y]:
            if var not in self.df.columns:
                return {"error": f"Variable '{var}' not found"}

        # Drop missing values
        data = self.df[[X, M, Y]].dropna()

        if len(data) < 30:
            return {"error": "Need at least 30 observations for reliable mediation analysis"}

        # Path coefficients
        # c: Total effect (X → Y)
        from scipy.stats import linregress
        slope_c, intercept_c, r_c, p_c, se_c = linregress(data[X], data[Y])

        # a: X → M
        slope_a, intercept_a, r_a, p_a, se_a = linregress(data[X], data[M])

        # b: M → Y (controlling for X)
        # Use multiple regression: Y ~ X + M
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        X_multi = data[[X, M]].values
        y_vals = data[Y].values
        model.fit(X_multi, y_vals)

        c_prime = model.coef_[0]  # Direct effect (X → Y controlling for M)
        b = model.coef_[1]  # M → Y controlling for X

        # Indirect effect (mediation)
        indirect_effect = slope_a * b

        # Bootstrap confidence intervals for indirect effect
        indirect_effects = []
        np.random.seed(42)

        for _ in range(bootstrap_samples):
            # Resample with replacement
            boot_sample = data.sample(n=len(data), replace=True)

            # Recalculate paths
            slope_a_boot, _, _, _, _ = linregress(boot_sample[X], boot_sample[M])

            model_boot = LinearRegression()
            X_boot = boot_sample[[X, M]].values
            y_boot = boot_sample[Y].values
            model_boot.fit(X_boot, y_boot)
            b_boot = model_boot.coef_[1]

            indirect_effects.append(slope_a_boot * b_boot)

        # 95% CI
        ci_lower = np.percentile(indirect_effects, 2.5)
        ci_upper = np.percentile(indirect_effects, 97.5)

        # Mediation is significant if CI doesn't include 0
        significant_mediation = not (ci_lower <= 0 <= ci_upper)

        # Proportion mediated
        if abs(slope_c) > 0.001:
            proportion_mediated = abs(indirect_effect / slope_c)
        else:
            proportion_mediated = np.nan

        return {
            "success": True,
            "variables": {"X": X, "M": M, "Y": Y},
            "total_effect": {
                "coefficient": float(slope_c),
                "p_value": float(p_c),
                "significant": p_c < 0.05
            },
            "direct_effect": {
                "coefficient": float(c_prime),
                "description": f"Effect of {X} on {Y} controlling for {M}"
            },
            "indirect_effect": {
                "coefficient": float(indirect_effect),
                "ci_95": [float(ci_lower), float(ci_upper)],
                "significant": significant_mediation,
                "description": f"Effect of {X} on {Y} through {M}"
            },
            "path_a": {
                "coefficient": float(slope_a),
                "p_value": float(p_a),
                "description": f"{X} → {M}"
            },
            "path_b": {
                "coefficient": float(b),
                "description": f"{M} → {Y} (controlling for {X})"
            },
            "proportion_mediated": float(proportion_mediated) if not np.isnan(proportion_mediated) else None,
            "interpretation": self._interpret_mediation(significant_mediation, proportion_mediated, p_c, slope_c, c_prime)
        }

    def _interpret_mediation(self, sig_mediation, prop_mediated, p_total, total_effect, direct_effect):
        """Interpret mediation results"""
        if not sig_mediation:
            return "No significant mediation detected (95% CI includes zero)"

        if np.isnan(prop_mediated):
            return "Cannot calculate proportion mediated (total effect near zero)"

        if prop_mediated > 1:
            return f"Full mediation with suppression effect ({prop_mediated*100:.1f}% mediated)"
        elif prop_mediated > 0.8:
            return f"Strong/full mediation ({prop_mediated*100:.1f}% of effect is mediated)"
        elif prop_mediated > 0.5:
            return f"Partial mediation ({prop_mediated*100:.1f}% of effect is mediated)"
        elif prop_mediated > 0.2:
            return f"Weak partial mediation ({prop_mediated*100:.1f}% of effect is mediated)"
        else:
            return f"Minimal mediation detected ({prop_mediated*100:.1f}% of effect is mediated)"

    def moderation_analysis(
        self,
        X: str,  # Independent variable
        W: str,  # Moderator
        Y: str,  # Dependent variable
        center_variables: bool = True
    ) -> Dict[str, Any]:
        """
        Moderation analysis - Test if W moderates X → Y relationship

        Tests for interaction effect (X * W)

        Args:
            X: Independent variable (predictor)
            W: Moderator variable
            Y: Dependent variable (outcome)
            center_variables: Whether to mean-center X and W (reduces multicollinearity)

        Returns:
            Main effects, interaction effect, simple slopes
        """
        if self.df is None:
            return {"error": "No dataframe loaded"}

        for var in [X, W, Y]:
            if var not in self.df.columns:
                return {"error": f"Variable '{var}' not found"}

        # Drop missing values
        data = self.df[[X, W, Y]].dropna().copy()

        if len(data) < 30:
            return {"error": "Need at least 30 observations for reliable moderation analysis"}

        # Center variables if requested
        if center_variables:
            data[f"{X}_c"] = data[X] - data[X].mean()
            data[f"{W}_c"] = data[W] - data[W].mean()
            X_var = f"{X}_c"
            W_var = f"{W}_c"
        else:
            X_var = X
            W_var = W

        # Create interaction term
        data["interaction"] = data[X_var] * data[W_var]

        # Multiple regression: Y ~ X + W + X*W
        from sklearn.linear_model import LinearRegression
        import statsmodels.api as sm

        X_model = data[[X_var, W_var, "interaction"]].values
        X_model = sm.add_constant(X_model)
        y_vals = data[Y].values

        model = sm.OLS(y_vals, X_model).fit()

        # Extract coefficients
        coef_intercept = model.params[0]
        coef_X = model.params[1]
        coef_W = model.params[2]
        coef_interaction = model.params[3]

        # p-values
        p_X = model.pvalues[1]
        p_W = model.pvalues[2]
        p_interaction = model.pvalues[3]

        # Simple slopes analysis (effect of X at low/mean/high W)
        W_values = {
            "low": data[W_var].mean() - data[W_var].std(),
            "mean": data[W_var].mean(),
            "high": data[W_var].mean() + data[W_var].std()
        }

        simple_slopes = {}
        for level, w_value in W_values.items():
            slope = coef_X + coef_interaction * w_value
            simple_slopes[level] = {
                "W_value": float(w_value),
                "slope": float(slope),
                "interpretation": f"When {W}={w_value:.2f}, effect of {X} on {Y} is {slope:.3f}"
            }

        return {
            "success": True,
            "variables": {"X": X, "W": W, "Y": Y},
            "r_squared": float(model.rsquared),
            "adj_r_squared": float(model.rsquared_adj),
            "main_effect_X": {
                "coefficient": float(coef_X),
                "p_value": float(p_X),
                "significant": p_X < 0.05
            },
            "main_effect_W": {
                "coefficient": float(coef_W),
                "p_value": float(p_W),
                "significant": p_W < 0.05
            },
            "interaction_effect": {
                "coefficient": float(coef_interaction),
                "p_value": float(p_interaction),
                "significant": p_interaction < 0.05,
                "description": f"Interaction between {X} and {W}"
            },
            "simple_slopes": simple_slopes,
            "interpretation": self._interpret_moderation(p_interaction, coef_interaction, simple_slopes)
        }

    def _interpret_moderation(self, p_interaction, coef, simple_slopes):
        """Interpret moderation results"""
        if p_interaction >= 0.05:
            return "No significant moderation effect detected (interaction p >= 0.05)"

        # Check if slopes differ substantially
        slopes = [s["slope"] for s in simple_slopes.values()]
        slope_range = max(slopes) - min(slopes)

        if slope_range < 0.1:
            return "Significant interaction but effect size is small (slopes barely differ)"
        else:
            direction = "strengthens" if coef > 0 else "weakens"
            return f"Significant moderation: W {direction} the X → Y relationship (slope range: {slope_range:.3f})"

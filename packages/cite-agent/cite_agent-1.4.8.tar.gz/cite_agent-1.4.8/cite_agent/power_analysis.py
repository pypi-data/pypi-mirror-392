"""
Power Analysis - Sample Size Calculations for Study Design
==========================================================

Calculate required sample sizes, statistical power, effect sizes.
Essential for grant proposals and study planning.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, Optional


class PowerAnalyzer:
    """Statistical power analysis for research planning"""

    def sample_size_ttest(
        self,
        effect_size: float,
        alpha: float = 0.05,
        power: float = 0.80,
        alternative: str = "two-sided"
    ) -> Dict[str, Any]:
        """
        Calculate required sample size for t-test

        Args:
            effect_size: Cohen's d (small=0.2, medium=0.5, large=0.8)
            alpha: Significance level (Type I error rate)
            power: Desired statistical power (1 - Type II error)
            alternative: "two-sided" or "one-sided"

        Returns:
            Required sample size per group
        """
        from statsmodels.stats.power import TTestIndPower

        analysis = TTestIndPower()
        nobs1 = analysis.solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            ratio=1.0,
            alternative=alternative
        )

        # Round up
        n_per_group = int(np.ceil(nobs1))
        total_n = n_per_group * 2

        return {
            "success": True,
            "test_type": "Independent samples t-test",
            "effect_size_d": effect_size,
            "alpha": alpha,
            "power": power,
            "n_per_group": n_per_group,
            "total_n": total_n,
            "interpretation": self._interpret_sample_size("ttest", effect_size, n_per_group, power)
        }

    def sample_size_correlation(
        self,
        effect_size: float,
        alpha: float = 0.05,
        power: float = 0.80,
        alternative: str = "two-sided"
    ) -> Dict[str, Any]:
        """
        Calculate required sample size for correlation

        Args:
            effect_size: Expected correlation coefficient r
            alpha: Significance level
            power: Desired power
            alternative: "two-sided" or "one-sided"

        Returns:
            Required sample size
        """
        # Fisher's Z transformation
        z_effect = 0.5 * np.log((1 + effect_size) / (1 - effect_size))

        # Critical values
        if alternative == "two-sided":
            z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            z_alpha = stats.norm.ppf(1 - alpha)

        z_beta = stats.norm.ppf(power)

        # Sample size formula for correlation
        n = ((z_alpha + z_beta) / z_effect) ** 2 + 3

        n_required = int(np.ceil(n))

        return {
            "success": True,
            "test_type": "Pearson correlation",
            "effect_size_r": effect_size,
            "alpha": alpha,
            "power": power,
            "n_required": n_required,
            "interpretation": self._interpret_sample_size("correlation", effect_size, n_required, power)
        }

    def sample_size_anova(
        self,
        effect_size: float,
        n_groups: int,
        alpha: float = 0.05,
        power: float = 0.80
    ) -> Dict[str, Any]:
        """
        Calculate required sample size for one-way ANOVA

        Args:
            effect_size: Cohen's f (small=0.1, medium=0.25, large=0.4)
            n_groups: Number of groups to compare
            alpha: Significance level
            power: Desired power

        Returns:
            Required sample size per group
        """
        from statsmodels.stats.power import FTestAnovaPower

        analysis = FTestAnovaPower()
        n_per_group = analysis.solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            k_groups=n_groups
        )

        n_per_group = int(np.ceil(n_per_group))
        total_n = n_per_group * n_groups

        return {
            "success": True,
            "test_type": f"One-way ANOVA ({n_groups} groups)",
            "effect_size_f": effect_size,
            "alpha": alpha,
            "power": power,
            "n_per_group": n_per_group,
            "total_n": total_n,
            "interpretation": self._interpret_sample_size("anova", effect_size, total_n, power)
        }

    def sample_size_regression(
        self,
        effect_size: float,
        n_predictors: int,
        alpha: float = 0.05,
        power: float = 0.80
    ) -> Dict[str, Any]:
        """
        Calculate required sample size for multiple regression

        Args:
            effect_size: Cohen's f² (small=0.02, medium=0.15, large=0.35)
            n_predictors: Number of predictor variables
            alpha: Significance level
            power: Desired power

        Returns:
            Required total sample size
        """
        from statsmodels.stats.power import FTestPower

        # Convert f² to f
        effect_size_f = np.sqrt(effect_size)

        analysis = FTestPower()

        # Degrees of freedom
        df_num = n_predictors

        # Solve for sample size
        # For regression: df_den = n - k - 1, so n = df_den + k + 1
        # We need to iterate to find n

        for n_total in range(n_predictors + 10, 1000):
            df_den = n_total - n_predictors - 1
            if df_den <= 0:
                continue

            achieved_power = analysis.power(
                effect_size=effect_size_f,
                df_num=df_num,
                df_denom=df_den,
                alpha=alpha
            )

            if achieved_power >= power:
                break

        return {
            "success": True,
            "test_type": f"Multiple regression ({n_predictors} predictors)",
            "effect_size_f2": effect_size,
            "alpha": alpha,
            "power": power,
            "n_required": n_total,
            "interpretation": self._interpret_sample_size("regression", effect_size, n_total, power)
        }

    def calculate_achieved_power(
        self,
        test_type: str,
        effect_size: float,
        n: int,
        alpha: float = 0.05,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate achieved power given sample size

        Args:
            test_type: "ttest", "correlation", "anova", or "regression"
            effect_size: Expected effect size
            n: Sample size (per group for ttest/anova, total for correlation/regression)
            alpha: Significance level
            **kwargs: Additional parameters (n_groups for ANOVA, n_predictors for regression)

        Returns:
            Achieved statistical power
        """
        if test_type == "ttest":
            from statsmodels.stats.power import TTestIndPower
            analysis = TTestIndPower()
            power = analysis.power(
                effect_size=effect_size,
                nobs1=n,
                alpha=alpha,
                alternative="two-sided"
            )

        elif test_type == "correlation":
            # Fisher's Z
            z_effect = 0.5 * np.log((1 + effect_size) / (1 - effect_size))
            z_alpha = stats.norm.ppf(1 - alpha/2)

            # Standard error
            se = 1 / np.sqrt(n - 3)

            # Power calculation
            z_beta = z_effect / se - z_alpha
            power = stats.norm.cdf(z_beta)

        elif test_type == "anova":
            from statsmodels.stats.power import FTestAnovaPower
            n_groups = kwargs.get("n_groups", 3)
            analysis = FTestAnovaPower()
            power = analysis.power(
                effect_size=effect_size,
                nobs=n,
                alpha=alpha,
                k_groups=n_groups
            )

        elif test_type == "regression":
            from statsmodels.stats.power import FTestPower
            n_predictors = kwargs.get("n_predictors", 1)
            effect_size_f = np.sqrt(effect_size)  # Convert f² to f
            analysis = FTestPower()
            df_den = n - n_predictors - 1
            power = analysis.power(
                effect_size=effect_size_f,
                df_num=n_predictors,
                df_denom=df_den,
                alpha=alpha
            )

        else:
            return {"error": f"Unknown test type: {test_type}"}

        return {
            "success": True,
            "test_type": test_type,
            "effect_size": effect_size,
            "sample_size": n,
            "alpha": alpha,
            "achieved_power": float(power),
            "interpretation": self._interpret_power(power)
        }

    def minimum_detectable_effect(
        self,
        test_type: str,
        n: int,
        alpha: float = 0.05,
        power: float = 0.80,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate minimum detectable effect size given sample size and power

        Args:
            test_type: "ttest", "correlation", "anova", or "regression"
            n: Sample size
            alpha: Significance level
            power: Desired power
            **kwargs: Additional parameters

        Returns:
            Minimum detectable effect size
        """
        if test_type == "ttest":
            from statsmodels.stats.power import TTestIndPower
            analysis = TTestIndPower()
            effect = analysis.solve_power(
                nobs1=n,
                alpha=alpha,
                power=power,
                alternative="two-sided"
            )

        elif test_type == "anova":
            from statsmodels.stats.power import FTestAnovaPower
            n_groups = kwargs.get("n_groups", 3)
            analysis = FTestAnovaPower()
            effect = analysis.solve_power(
                nobs=n,
                alpha=alpha,
                power=power,
                k_groups=n_groups
            )

        else:
            return {"error": f"MDE calculation not implemented for {test_type}"}

        return {
            "success": True,
            "test_type": test_type,
            "sample_size": n,
            "alpha": alpha,
            "power": power,
            "minimum_detectable_effect": float(effect),
            "interpretation": f"With n={n} and power={power}, can detect effects ≥ {effect:.3f}"
        }

    def _interpret_sample_size(self, test_type, effect_size, n, power):
        """Interpret sample size results"""
        interpretations = []

        # Effect size interpretation
        if test_type == "ttest":
            if effect_size < 0.3:
                interpretations.append(f"Small effect (d={effect_size}): Requires larger sample")
            elif effect_size < 0.6:
                interpretations.append(f"Medium effect (d={effect_size}): Moderate sample needed")
            else:
                interpretations.append(f"Large effect (d={effect_size}): Smaller sample sufficient")

        # Power interpretation
        if power < 0.70:
            interpretations.append("⚠️ Low power: High risk of missing true effects")
        elif power < 0.80:
            interpretations.append("Acceptable power but below conventional 0.80")
        elif power < 0.90:
            interpretations.append("Good power: Conventional threshold met")
        else:
            interpretations.append("Excellent power: Low risk of Type II error")

        # Sample size practical considerations
        if n < 30:
            interpretations.append("Small sample: Consider increasing for robustness")
        elif n > 200:
            interpretations.append("Large sample required: Consider focusing research question")

        return " | ".join(interpretations)

    def _interpret_power(self, power):
        """Interpret achieved power"""
        if power < 0.50:
            return "Very low power: Less than 50% chance of detecting true effect"
        elif power < 0.70:
            return "Low power: Substantial risk of Type II error"
        elif power < 0.80:
            return "Acceptable power but below conventional threshold"
        elif power < 0.90:
            return "Good power: Meets conventional 0.80 threshold"
        else:
            return "Excellent power: Very high probability of detecting true effect"

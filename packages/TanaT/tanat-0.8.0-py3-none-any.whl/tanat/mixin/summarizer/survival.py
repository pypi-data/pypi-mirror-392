#!/usr/bin/env python3
"""Survival analysis summarizer."""

from .base import BaseSummarizerMixin


class SurvivalSummarizerMixin(BaseSummarizerMixin):
    """Summarization mixin for survival analysis."""

    @property
    def statistics(self):
        """
        Compute survival statistics.

        Returns:
            dict: Survival metrics.
        """
        if not hasattr(self, "_last_result") or self._last_result is None:
            return {
                "status": "No analysis performed",
                "model_type": self.model_type,
                "total_sequences": 0,
                "observed_events": 0,
                "censored_events": 0,
                "censoring_rate": 0.0,
                "mean_duration": 0.0,
                "median_duration": 0.0,
                "duration_std": 0.0,
            }

        result = self._last_result
        n_observed = result.observation_data["observed"].sum()
        n_total = len(result.observation_data)
        n_censored = n_total - n_observed

        return {
            "status": "Analysis performed",
            "model_type": self.model_type,
            "total_sequences": n_total,
            "observed_events": int(n_observed),
            "censored_events": int(n_censored),
            "censoring_rate": float((n_censored / n_total) * 100),
            "mean_duration": float(result.durations.mean()),
            "median_duration": float(result.durations.median()),
            "duration_std": float(result.durations.std()),
        }

    def _get_title(self):
        """Get the summary title."""
        return f"Survival Analysis ({self.model_type}) Summary"

    def _format_statistics(self):
        """Generate survival statistics section."""
        stats = self.statistics

        if stats["status"] == "No analysis performed":
            lines = [
                self._format_stat_line("Status", stats["status"]),
                self._format_stat_line("Model type", stats["model_type"]),
            ]
        else:
            lines = [
                self._format_stat_line("Model type", stats["model_type"]),
                self._format_stat_line("Total sequences", stats["total_sequences"]),
                self._format_stat_line("Observed events", stats["observed_events"]),
                self._format_stat_line("Censored events", stats["censored_events"]),
                self._format_stat_line(
                    "Censoring rate", f"{stats['censoring_rate']:.1f}%"
                ),
                self._format_stat_line(
                    "Mean duration", f"{stats['mean_duration']:.2f}"
                ),
                self._format_stat_line(
                    "Median duration", f"{stats['median_duration']:.2f}"
                ),
            ]

        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_data_preview(self):
        """Generate survival data preview."""
        sections = []

        # Model settings
        sections.append(f"{self.INDENT}Model Settings:")
        settings_dict = (
            self.settings.__dict__ if hasattr(self.settings, "__dict__") else {}
        )
        for key, value in settings_dict.items():
            if not key.startswith("_"):
                sections.append(f"{self.INDENT * 2}{key:<20}{value}")

        if hasattr(self, "_last_result") and self._last_result is not None:
            sections.extend(
                [
                    "",
                    f"{self.INDENT}Duration Statistics:",
                    f"{self.INDENT * 2}Min: {self._last_result.durations.min():.2f}",
                    f"{self.INDENT * 2}25%: {self._last_result.durations.quantile(0.25):.2f}",
                    f"{self.INDENT * 2}75%: {self._last_result.durations.quantile(0.75):.2f}",
                    f"{self.INDENT * 2}Max: {self._last_result.durations.max():.2f}",
                ]
            )

        return self._format_section("MODEL & DATA DETAILS", "\n".join(sections))

    def get_compact_summary(self):
        """Generate compact summary for embedding in other summaries."""
        stats = self.statistics

        if stats["status"] == "No analysis performed":
            return [f"Model: {stats['model_type']}", "Status: No analysis performed"]

        return [
            f"Model: {stats['model_type']}",
            f"Sequences: {stats['total_sequences']}",
            f"Observed: {stats['observed_events']}",
            f"Censoring: {stats['censoring_rate']:.1f}%",
            f"Mean duration: {stats['mean_duration']:.2f}",
        ]

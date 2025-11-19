#! /usr/bin/env python3
"""
Sequence summarizer.
"""

from .base import BaseSummarizerMixin


class SequenceSummarizerMixin(BaseSummarizerMixin):
    """Sequence summarizer mixin."""

    @property
    def statistics(self):
        """
        Compute sequence statistics.

        Returns:
            dict: Sequence metrics (flat structure).
        """
        if self._is_pool:
            # Pool: aggregate describe() and flatten to dict
            desc = self.describe(aggregate=True, dropna=True)
            return {
                "total_sequences": len(self.unique_ids),
                "avg_length": float(desc["length"]["mean"]),
                "min_length": int(desc["length"]["min"]),
                "max_length": int(desc["length"]["max"]),
                "vocab_size": len(self.vocabulary),  # Pool vocabulary (union)
            }
        else:
            # Single: convert describe() row to dict
            desc_df = self.describe(aggregate=False, dropna=True)
            desc = desc_df.iloc[0].to_dict()
            # Add vocabulary size (not in describe)
            desc["vocab_size"] = len(self.vocabulary)
            return desc

    def _format_statistics(self):
        """Generate sequence statistics section."""
        if self._is_pool:
            return self._format_pool_statistics()
        return self._format_single_statistics()

    def _format_pool_statistics(self):
        """Generate pool statistics."""
        stats = self.statistics

        lines = [
            self._format_stat_line("Total sequences", stats["total_sequences"]),
            self._format_stat_line("Average length", f"{stats['avg_length']:.1f}"),
            self._format_stat_line("Minimum length", stats["min_length"]),
            self._format_stat_line("Maximum length", stats["max_length"]),
            self._format_stat_line("Vocabulary size", stats["vocab_size"]),
        ]
        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_single_statistics(self):
        """Generate single sequence statistics."""
        stats = self.statistics

        lines = [
            self._format_stat_line("Sequence ID", str(self.id_value)),
            self._format_stat_line("Length", int(stats["length"])),
            self._format_stat_line("Vocabulary size", stats["vocab_size"]),
            self._format_stat_line("Entropy", f"{stats['entropy']:.3f}"),
        ]
        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_data_preview(self):
        """Generate data preview section."""
        sections = []

        # Sequence data preview
        sequence_sample = (
            self.sequence_data.head(3)
            .reset_index(drop=False, inplace=False)
            .to_string(index=False)
        )
        sections.append(f"{self.INDENT}Sequence Data:")
        sections.append(self._indent_text(sequence_sample, level=2))

        # Static data preview
        if self.static_data is not None:
            static_sample = (
                self.static_data.head(3)
                .reset_index(drop=False, inplace=False)
                .to_string(index=False)
            )
            sections.extend(
                [
                    "",
                    f"{self.INDENT}Static Data:",
                    self._indent_text(static_sample, level=2),
                ]
            )
        else:
            sections.extend(
                ["", f"{self.INDENT}Static Data:", f"{self.INDENT * 2}None"]
            )

        # Metadata preview
        metadata_preview = self.metadata.describe(verbose=False)
        sections.extend(
            [
                "",
                f"{self.INDENT}Metadata:",
                self._indent_text(metadata_preview, level=2),
            ]
        )

        return self._format_section("DATA PREVIEW", "\n".join(sections))

    def get_compact_summary(self):
        """Generate compact summary for embedding in other summaries."""
        stats = self.statistics

        if self._is_pool:
            return [
                f"Total sequences: {stats['total_sequences']}",
                f"Avg length: {stats['avg_length']:.1f}",
                f"Length range: {stats['min_length']}-{stats['max_length']}",
                f"Vocab size: {stats['vocab_size']}",
            ]

        return [
            f"Length: {int(stats['length'])}",
            f"Vocab size: {stats['vocab_size']}",
            f"Entropy: {stats['entropy']:.3f}",
        ]

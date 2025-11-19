#! /usr/bin/env python3
"""
Trajectory summarizer.
"""

from .base import BaseSummarizerMixin


class TrajectorySummarizerMixin(BaseSummarizerMixin):
    """Trajectory summarizer mixin."""

    @property
    def statistics(self):
        """
        Compute trajectory statistics.

        Returns:
            dict: Trajectory metrics (flat structure).
        """
        # Determine if we're working with single trajectory or pool
        if hasattr(self, "sequences"):
            # Single trajectory: use sequences property (dict of Sequence)
            sequence_objects = self.sequences
            is_pool = False
        else:
            # Pool: use sequence_pools (dict of SequencePool)
            sequence_objects = self.sequence_pools
            is_pool = True

        # Build trajectory-level stats
        if is_pool:
            stats = {
                "total_trajectories": len(self.unique_ids),
                "sequence_types": len(sequence_objects),
                "sequence_names": list(sequence_objects.keys()),
                "intersection_mode": str(self.settings.intersection),
            }
        else:
            stats = {
                "trajectory_id": self.id_value,
                "sequence_count": len(sequence_objects),
                "sequence_names": list(sequence_objects.keys()),
            }

        # Add prefixed stats from each sequence object
        for seq_name, seq_obj in sequence_objects.items():
            seq_stats = seq_obj.statistics
            prefix = f"{seq_name}_"
            for key, value in seq_stats.items():
                stats[f"{prefix}{key}"] = value

        return stats

    def _format_statistics(self):
        """Generate trajectory statistics section."""
        if self._is_pool:
            return self._format_pool_statistics()
        return self._format_single_statistics()

    def _format_pool_statistics(self):
        """Generate pool statistics."""
        stats = self.statistics
        display_names = self._format_names(stats["sequence_names"])

        lines = [
            self._format_stat_line("Total trajectories", stats["total_trajectories"]),
            self._format_stat_line("Sequence types", stats["sequence_types"]),
            self._format_stat_line("Sequence names", display_names),
            self._format_stat_line("Intersection mode", stats["intersection_mode"]),
        ]

        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_single_statistics(self):
        """Generate single trajectory statistics."""
        stats = self.statistics
        display_names = self._format_names(stats["sequence_names"])

        lines = [
            self._format_stat_line("Trajectory ID", str(stats["trajectory_id"])),
            self._format_stat_line("Sequence count", stats["sequence_count"]),
            self._format_stat_line("Sequence names", display_names),
        ]

        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_data_preview(self):
        """Generate trajectory data preview."""
        sections = []

        # Static data
        if self.static_data is not None:
            static_sample = (
                self.static_data.head(3)
                .reset_index(drop=False, inplace=False)
                .to_string(index=False)
            )
            sections.extend(
                [
                    f"{self.INDENT}Static Data:",
                    self._indent_text(static_sample, level=2),
                    "",
                ]
            )

        # Sequence data
        sequences = self.sequence_pools if self._is_pool else self.sequences
        sections.append(f"{self.INDENT}Sequence Data:")

        for name, seq_obj in sequences.items():
            sections.append(f"{self.INDENT * 2}> {name}")
            compact_info = seq_obj.get_compact_summary()
            for info in compact_info:
                sections.append(f"{self.INDENT * 3}{info}")
            sections.append("")  # Spacing between sequences

        # Metadata preview
        metadata_preview = self.metadata.describe(verbose=False)
        sections.extend(
            [
                "",
                f"{self.INDENT}Metadata:",
                self._indent_text(metadata_preview, level=2),
            ]
        )

        # Remove last empty line
        if sections and sections[-1] == "":
            sections.pop()

        return self._format_section("DATA PREVIEW", "\n".join(sections))

    def _format_names(self, names, max_display=3):
        """Format sequence names with truncation if needed."""
        if len(names) <= max_display:
            return ", ".join(names)
        return ", ".join(names[:max_display]) + f" (+{len(names) - max_display} more)"

    def get_compact_summary(self):
        """Generate compact summary for embedding in other summaries."""
        stats = self.statistics

        if self._is_pool:
            lines = [
                f"Total trajectories: {stats['total_trajectories']}",
                f"Sequence types: {stats['sequence_types']}",
            ]
            # Add first sequence type stats as example
            if stats["sequence_names"]:
                seq_name = stats["sequence_names"][0]
                prefix = f"{seq_name}_"
                if f"{prefix}total_sequences" in stats:
                    lines.append(
                        f"{seq_name}: {stats[f'{prefix}total_sequences']} sequences, avg length {stats[f'{prefix}avg_length']:.1f}"
                    )
            return lines

        lines = [
            f"Trajectory ID: {stats['trajectory_id']}",
            f"Sequence count: {stats['sequence_count']}",
        ]
        # Add first sequence stats as example
        if stats["sequence_names"]:
            seq_name = stats["sequence_names"][0]
            prefix = f"{seq_name}_"
            if f"{prefix}length" in stats:
                lines.append(
                    f"{seq_name}: length {int(stats[f'{prefix}length'])}, vocab {stats[f'{prefix}vocab_size']}"
                )
        return lines

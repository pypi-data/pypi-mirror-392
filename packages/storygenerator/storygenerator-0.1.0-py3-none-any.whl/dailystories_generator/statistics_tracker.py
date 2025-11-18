"""Statistics tracking for prompt optimization iterations."""

import csv
from pathlib import Path
from datetime import datetime
from typing import Dict

from dailystories_generator.evaluation import EvaluationResult


class StatisticsTracker:
    """Track evaluation scores across optimization iterations."""
    
    # Category names in order for CSV headers
    CATEGORIES = [
        "creativity",
        "age_appropriateness",
        "coherence",
        "engagement",
        "language_quality",
        "plot_structure",
        "character_development",
        "character_introduction",
        "emotional_resonance",
        "pacing",
        "tone_consistency",
    ]
    
    def __init__(self, csv_path: Path):
        """
        Initialize the statistics tracker.
        
        Args:
            csv_path: Path to the statistics CSV file
        """
        self.csv_path = csv_path
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self) -> None:
        """Create the CSV file with headers if it doesn't exist."""
        if not self.csv_path.exists():
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = ['timestamp', 'mode', 'iteration', 'prompt_version'] + self.CATEGORIES + ['average_score']
                writer.writerow(headers)
    
    def log_iteration(
        self,
        mode: str,
        iteration: int,
        prompt_version: int,
        evaluation: EvaluationResult,
    ) -> None:
        """
        Log an iteration's evaluation scores to the CSV.
        
        Args:
            mode: The mode being optimized ('outline' or 'pages')
            iteration: The iteration number (1-based)
            prompt_version: The version number of the prompt
            evaluation: The evaluation results
        """
        timestamp = datetime.now().isoformat()
        scores = evaluation.get_scores_dict()
        average_score = evaluation.get_average_score()
        
        # Build row data
        row = [timestamp, mode, iteration, prompt_version]
        
        # Add scores in category order
        for category in self.CATEGORIES:
            row.append(scores[category])
        
        # Add average score
        row.append(f"{average_score:.2f}")
        
        # Write to CSV
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    
    def get_latest_scores(self) -> Dict[str, float] | None:
        """
        Get the latest scores from the CSV.
        
        Returns:
            Dictionary of category scores, or None if no data exists
        """
        if not self.csv_path.exists():
            return None
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                return None
            
            # Get the last row
            last_row = rows[-1]
            
            # Extract scores
            scores = {}
            for category in self.CATEGORIES:
                scores[category] = float(last_row[category])
            
            return scores


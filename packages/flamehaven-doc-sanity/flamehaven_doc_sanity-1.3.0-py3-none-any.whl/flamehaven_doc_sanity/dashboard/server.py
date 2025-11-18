"""Dashboard server for drift monitoring and visualization."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

from flamehaven_doc_sanity.config import load_golden_baseline
from flamehaven_doc_sanity.governance.driftlock_guard import (
    JSD_TOLERANCE_MINOR,
    JSD_TOLERANCE_MODERATE,
    JSD_TOLERANCE_NONE,
    JSD_TOLERANCE_SEVERE,
    DriftLockGuard,
)


class DashboardServer:
    """Flask-based dashboard server for drift monitoring."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        """Initialize dashboard server.

        Args:
            host: Server host address
            port: Server port number
        """
        self.host = host
        self.port = port
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).parent / "templates"),
            static_folder=str(Path(__file__).parent / "static"),
        )

        # Load baseline configuration
        self.baseline = load_golden_baseline()
        self.drift_guard = DriftLockGuard(self.baseline)

        # In-memory drift history (in production, use a database)
        self.drift_history: List[Dict[str, Any]] = []

        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes for dashboard."""

        @self.app.route("/")
        def index():
            """Render main dashboard page."""
            return render_template("dashboard.html")

        @self.app.route("/api/baseline")
        def get_baseline():
            """Get golden baseline configuration."""
            return jsonify(
                {
                    "baseline": self.baseline.get("golden_baseline", {}),
                    "thresholds": {
                        "none": JSD_TOLERANCE_NONE,
                        "minor": JSD_TOLERANCE_MINOR,
                        "moderate": JSD_TOLERANCE_MODERATE,
                        "severe": JSD_TOLERANCE_SEVERE,
                    },
                }
            )

        @self.app.route("/api/check", methods=["POST"])
        def check_drift():
            """Check configuration for drift."""
            try:
                current_config = request.json
                verdict = self.drift_guard.check(current_config)

                # Record in history
                history_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "jsd_score": verdict.jsd_score,
                    "severity": verdict.severity,
                    "affected_dimensions": verdict.affected_dimensions,
                    "drift_detected": verdict.drift_detected,
                }
                self.drift_history.append(history_entry)

                # Keep only last 100 entries
                if len(self.drift_history) > 100:
                    self.drift_history = self.drift_history[-100:]

                return jsonify(
                    {
                        "verdict": {
                            "severity": verdict.severity,
                            "jsd_score": verdict.jsd_score,
                            "drift_detected": verdict.drift_detected,
                            "affected_dimensions": verdict.affected_dimensions,
                            "recommendation": verdict.recommendation,
                        },
                        "timestamp": history_entry["timestamp"],
                    }
                )
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        @self.app.route("/api/history")
        def get_history():
            """Get drift history."""
            return jsonify(
                {
                    "history": self.drift_history,
                    "count": len(self.drift_history),
                }
            )

        @self.app.route("/api/clear-history", methods=["POST"])
        def clear_history():
            """Clear drift history."""
            self.drift_history.clear()
            return jsonify({"status": "cleared"})

    def run(self, debug: bool = False):
        """Run the dashboard server.

        Args:
            debug: Enable Flask debug mode
        """
        print(f"🎯 DriftLock Dashboard starting on http://{self.host}:{self.port}")
        print(
            f"📊 Baseline version: {self.baseline.get('golden_baseline', {}).get('version', 'unknown')}"
        )
        print(f"✨ JSD tolerance: {self.drift_guard.jsd_tolerance}")
        self.app.run(host=self.host, port=self.port, debug=debug)


def create_dashboard(host: str = "127.0.0.1", port: int = 5000) -> DashboardServer:
    """Create and return a dashboard server instance.

    Args:
        host: Server host address
        port: Server port number

    Returns:
        DashboardServer instance
    """
    return DashboardServer(host=host, port=port)

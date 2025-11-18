"""Dashboard module for Flamehaven-Doc-Sanity drift monitoring.

Provides real-time visualization of:
- JSD scores and drift severity
- Historical drift trends
- Affected dimensions analysis
- Alert threshold configuration
"""

from flamehaven_doc_sanity.dashboard.server import DashboardServer

__all__ = ["DashboardServer"]

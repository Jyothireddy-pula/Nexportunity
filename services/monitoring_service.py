import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ScraperStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ScraperMetric:
    """Individual scraper execution metric"""
    source: str
    status: ScraperStatus
    items_scraped: int
    duration_seconds: float
    timestamp: datetime
    error_message: Optional[str] = None


class MonitoringService:
    """Service for monitoring scraper reliability and performance"""
    
    _metrics: List[ScraperMetric] = field(default_factory=list)
    _max_metrics = 1000  # Keep last 1000 metrics
    
    @classmethod
    def record_execution(cls, source: str, status: ScraperStatus, 
                        items_scraped: int, duration_seconds: float,
                        error_message: Optional[str] = None) -> None:
        """Record a scraper execution metric"""
        metric = ScraperMetric(
            source=source,
            status=status,
            items_scraped=items_scraped,
            duration_seconds=duration_seconds,
            timestamp=datetime.utcnow(),
            error_message=error_message
        )
        cls._metrics.append(metric)
        
        # Keep only recent metrics
        if len(cls._metrics) > cls._max_metrics:
            cls._metrics = cls._metrics[-cls._max_metrics:]
        
        logger.info(f"Recorded metric: {source} - {status.value} - {items_scraped} items - {duration_seconds:.2f}s")
    
    @classmethod
    def get_source_stats(cls, source: str, hours: int = 24) -> Dict:
        """Get statistics for a specific source"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        source_metrics = [m for m in cls._metrics if m.source == source and m.timestamp >= cutoff]
        
        if not source_metrics:
            return {
                "source": source,
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_items": 0,
                "avg_duration": 0.0,
                "last_execution": None
            }
        
        successful = [m for m in source_metrics if m.status == ScraperStatus.SUCCESS]
        total_items = sum(m.items_scraped for m in source_metrics)
        total_duration = sum(m.duration_seconds for m in source_metrics)
        
        return {
            "source": source,
            "total_executions": len(source_metrics),
            "success_rate": len(successful) / len(source_metrics) * 100,
            "avg_items": total_items / len(source_metrics),
            "avg_duration": total_duration / len(source_metrics),
            "last_execution": source_metrics[-1].timestamp.isoformat(),
            "last_status": source_metrics[-1].status.value
        }
    
    @classmethod
    def get_all_stats(cls, hours: int = 24) -> Dict[str, Dict]:
        """Get statistics for all sources"""
        sources = set(m.source for m in cls._metrics)
        return {source: cls.get_source_stats(source, hours) for source in sources}
    
    @classmethod
    def get_recent_failures(cls, hours: int = 24) -> List[Dict]:
        """Get recent failures across all sources"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        failures = [m for m in cls._metrics if m.status != ScraperStatus.SUCCESS and m.timestamp >= cutoff]
        
        return [
            {
                "source": m.source,
                "status": m.status.value,
                "error": m.error_message,
                "timestamp": m.timestamp.isoformat()
            }
            for m in failures[-20:]  # Last 20 failures
        ]
    
    @classmethod
    def is_healthy(cls, source: str, min_success_rate: float = 50.0, hours: int = 24) -> bool:
        """Check if a source is healthy based on success rate"""
        stats = cls.get_source_stats(source, hours)
        if stats["total_executions"] == 0:
            return True  # No data yet, assume healthy
        return stats["success_rate"] >= min_success_rate
    
    @classmethod
    def clear_metrics(cls) -> None:
        """Clear all metrics"""
        cls._metrics.clear()
        logger.info("Monitoring metrics cleared")

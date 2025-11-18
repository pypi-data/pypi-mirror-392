"""
Helper functions for UnifiedSigilPipeline.

Extracted from unified_pipeline.py to reduce file size and improve maintainability.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


async def gather_documentation(
    scraper: Any,
    crate_name: str,
    repository_url: Optional[str],
    logger: logging.Logger,
) -> Dict[str, Any]:
    """
    Gather documentation from various sources.
    
    Extracted from UnifiedSigilPipeline._gather_documentation for better organization.
    """
    docs = {
        "readme": None,
        "repository_url": repository_url,
        "docs_rs_url": f"https://docs.rs/{crate_name}",
    }
    
    # Try to scrape README from repository
    if repository_url:
        try:
            if scraper:
                result = await scraper.scrape(repository_url)
                if result and result.content:
                    # Extract README content
                    content = result.content
                    # Limit README size
                    if len(content) > 50000:  # ~50KB limit
                        content = content[:50000] + "... [truncated]"
                    docs["readme"] = content
                    logger.info(f"Scraped README for {crate_name} ({len(content)} chars)")
        except Exception as e:
            logger.warning(f"Failed to scrape README for {crate_name}: {e}")
    
    return docs


async def add_ml_predictions(
    ml_predictor: Any,
    crate_name: str,
    crate_metadata: Any,
    logger: logging.Logger,
) -> Dict[str, Any]:
    """
    Add ML quality predictions to analysis.
    
    Extracted from UnifiedSigilPipeline._add_ml_predictions for better organization.
    """
    if not ml_predictor:
        return {}
    
    try:
        # Convert metadata to dict format expected by predictor
        crate_data = crate_metadata.to_dict() if hasattr(crate_metadata, "to_dict") else {}
        
        # Get predictions
        prediction = ml_predictor.predict_quality(crate_data)
        
        return {
            "quality_score": prediction.quality_score,
            "security_risk": prediction.security_risk,
            "maintenance_score": prediction.maintenance_score,
            "popularity_trend": prediction.popularity_trend,
            "dependency_health": prediction.dependency_health,
            "confidence": prediction.confidence,
            "model_version": prediction.model_version,
        }
    except Exception as e:
        logger.warning(f"ML prediction failed for {crate_name}: {e}")
        return {}


async def generate_analysis_report(
    crate_name: str,
    trace: Any,
    output_dir: str,
    logger: logging.Logger,
) -> None:
    """
    Generate analysis report for a crate.
    
    Extracted from UnifiedSigilPipeline._generate_analysis_report for better organization.
    """
    try:
        from pathlib import Path
        from .utils.serialization_utils import to_serializable
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save sacred chain trace
        trace_file = output_path / f"{crate_name}_sacred_chain.json"
        report_data = to_serializable(trace.to_dict())
        
        import json
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis report saved to {trace_file}")
    except Exception as e:
        logger.warning(f"Failed to generate analysis report for {crate_name}: {e}")


import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from ..config import APP_HOME_DIR

@dataclass
class LlamaParseConfig:
    """Configuration for the LlamaParse client."""

    api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("LLAMA_CLOUD_API_KEY")
    )
    num_ongoing_requests: int = 10
    base_url: str = "https://api.cloud.llamaindex.ai"
    parse_kwargs: Dict[str, str] = field(
        default_factory=lambda: {
            "parse_mode": "parse_page_with_agent",
            "model": "openai-gpt-4-1-mini",
            "high_res_ocr": "true",
            "adaptive_long_table": "true",
            "outlined_table_extraction": "true",
            "output_tables_as_HTML": "true",
        }
    )
    cache_dir: Path = field(
        default_factory=lambda: APP_HOME_DIR / "cache" / "parse"
    )
    skippable_extensions: List[str] = field(
        default_factory=lambda: [".md", ".markdown", ".txt"]
    )
    upload_endpoint: str = "/api/parsing/upload"
    job_endpoint_template: str = "/api/parsing/job/{job_id}"
    result_endpoint_suffix: str = "/result/markdown"
    check_interval: float = 5.0  # in seconds
    max_timeout: int = 3600  # in seconds
    max_retries: int = 3
    retry_delay_ms: int = 1000
    backoff_multiplier: float = 2.0

    @classmethod
    def from_config_file(cls, path: Path) -> "LlamaParseConfig":
        """Loads configuration from a JSON file, falling back to defaults."""
        if not path.exists():
            return cls()

        with open(path, "r") as f:
            config_data = json.load(f)
        return cls(**config_data)

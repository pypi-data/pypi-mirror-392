import logging
import sys
import os
import httpx
import threading
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, field
from centra_sdk.models.connector.v1.operations.config import ConfigOpts


@dataclass
class IntegrationContext:
    """Context holding integration resources and configuration."""
    httpx_client: Optional[httpx.AsyncClient] = None
    logger: Optional[logging.Logger] = None
    component_id: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    schema: Optional[List[ConfigOpts]] = None
    _is_closed: bool = field(default=False, init=False)
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.httpx_client is None:
            self.httpx_client = httpx.AsyncClient()
        if self.logger is None:
            self.logger = logging.getLogger('centra_sdk')
    
    async def close(self):
        """Properly close resources."""
        if not self._is_closed and self.httpx_client:
            await self.httpx_client.aclose()
            self._is_closed = True
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class IntegrationContextApi:
    """Thread-safe singleton API for managing integration context."""
    CONTEXT: Optional[IntegrationContext] = None
    _lock = threading.RLock()

    @classmethod
    async def clean(cls) -> None:
        """Clean up resources and reset context."""
        with cls._lock:
            if cls.CONTEXT:
                await cls.CONTEXT.close()
                cls.CONTEXT = None

    @classmethod
    def context(cls) -> IntegrationContext:
        """Get or create the singleton context instance."""
        with cls._lock:
            if cls.CONTEXT is None:
                cls.CONTEXT = cls._build_context(cls._get_log_level())
            return cls.CONTEXT

    @classmethod
    def _build_context(cls, log_level: int) -> IntegrationContext:
        """Build a new context instance with proper configuration."""
        ctx = IntegrationContext()
        
        # Configure logger
        ctx.logger.setLevel(log_level)
        if not ctx.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s %(name)s: %(message)s'
            )
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            ctx.logger.addHandler(handler)

        return ctx

    @classmethod
    def client(cls) -> httpx.AsyncClient:
        """Get the HTTP client instance.
        
        Raises:
            RuntimeError: If context has been closed
        """
        ctx = cls.context()
        if ctx._is_closed:
            raise RuntimeError("Cannot access client: context has been closed")
        return ctx.httpx_client

    @classmethod
    def log(cls) -> logging.Logger:
        """Get the logger instance."""
        return cls.context().logger

    @classmethod
    def schema(cls) -> Optional[List[ConfigOpts]]:
        """Get the integration schema."""
        return cls.context().schema

    @classmethod
    def configuration(cls) -> Optional[Dict[str, Any]]:
        """Get the integration configuration."""
        return cls.context().configuration

    @classmethod
    def component_id(cls) -> Optional[str]:
        """Get the component ID."""
        return cls.context().component_id

    @classmethod
    def set_schema(cls, schema: List[ConfigOpts]) -> None:
        """Register schema of integration configuration.
        
        Args:
            schema: List of ConfigOpts defining the integration schema
            
        Example:
            set_schema([
                ConfigOpts(
                    name="api_url",
                    opt_type=OptType.OPT_STRING,
                    default_value="default",
                    description="Inventory API URL"
                ),
                # ...
            ])
        """
        cls.context().schema = schema

    @classmethod
    def set_component_id(cls, component_id: str) -> None:
        """Set component_id that is used to identify integration on Centra side.
        
        Args:
            component_id: Unique identifier for this integration component
        """
        if not component_id:
            raise ValueError("component_id cannot be empty")
        cls.context().component_id = component_id

    @classmethod
    def set_configuration(cls, configuration: Dict[str, Any]) -> None:
        """Set configuration as dict of Key: Value.
        
        Args:
            configuration: Configuration dictionary
            
        Example:
            set_configuration({
                'api_url': 'http://www.integration.com',
                'api_key': '<secret_key>'
            })
        """
        if not isinstance(configuration, dict):
            raise TypeError("configuration must be a dictionary")
        cls.context().configuration = configuration

    @classmethod
    def set_log_level(cls, level: Union[int, str]) -> None:
        """Set the log level for the SDK logger.
        
        Args:
            level: Log level (int or string like 'DEBUG', 'INFO', etc.)
        """
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        cls.context().logger.setLevel(level)

    @classmethod
    def _get_log_level(cls) -> int:
        """Get log level from environment variable or default to INFO.
        
        Returns:
            int: The logging level
            
        Raises:
            ValueError: If environment variable contains invalid log level
        """
        level_name = os.getenv('CENTRA_SDK_LOG_LEVEL', 'INFO').upper()
        level = getattr(logging, level_name, None)
        if level is None:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            raise ValueError(
                f"Invalid log level '{level_name}'. Valid levels are: {valid_levels}"
            )
        return level

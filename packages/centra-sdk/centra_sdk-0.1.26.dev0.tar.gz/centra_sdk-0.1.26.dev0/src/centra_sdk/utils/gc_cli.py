#!/usr/bin/env python3
"""
CLI interface for Claroty integration.

This module provides command-line tools for testing and managing
the Claroty integration outside of the FastAPI server context.

TODO: 
- Move into SDK package
- Add missing dependencies to pyproject.toml: click>=8.0.0, rich>=13.0.0
- Add comprehensive unit tests
- Add logging support
- Add configuration validation
- Consider using click.Context.ensure_object() pattern
"""

import json
import sys
import click
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Union, Literal, Optional
from rich.console import Console

from rich import print as rprint
from click import pass_context
from rich.table import Table

from centra_sdk.models.connector.v1.operations.config import ConfigOpts

# Constants
OUTPUT_FORMAT_TABLE = 'table'
OUTPUT_FORMAT_JSON = 'json'
STATUS_OK = 'okay'
STATUS_ERROR = 'error'

# Type aliases
OutputFormat = Literal['table', 'json']

console = Console()


@dataclass
class CliResponse(ABC):
    """Base class for CLI response data."""
    status: str
    message: str

    @property
    @abstractmethod
    def value(self) -> Union[Dict[str, Any], List]:
        """Convert to dictionary for JSON serialization."""
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        """Convert to dictionary for JSON serialization."""
        pass

    def print(self, format: str = 'json'):
        response_fmt = self.format(format)
        if isinstance(response_fmt, Table):
            rprint(response_fmt)
        else:
            print(response_fmt)

    def format(self, output_format: OutputFormat) -> Union[Table, str]:
        """Format the schema fields based on the requested output format."""

        if output_format == OUTPUT_FORMAT_JSON:
            return json.dumps(self.value)

        # table format
        if output_format == OUTPUT_FORMAT_TABLE:
            table = Table(title=self.title)
            if isinstance(self.value, list):
                for i, raw in enumerate(self.value):
                    if not i:
                        # build schema from first entry
                        for field in raw:
                            table.add_column(field.capitalize(), style="cyan")
                    table.add_row(*[str(raw[field]) for field in raw])
            return table

        return self.value


@dataclass
class DiscoverSchemaResponse(CliResponse):
    """Response wrapper for schema discovery operations.

    Encapsulates the result of discovering configuration schema fields,
    including the list of ConfigOpts objects that define the available
    configuration parameters.

    Attributes:
        schema_fields: List of configuration option definitions
    """
    schema_fields: List[ConfigOpts]

    @property
    def title(self) -> str:
        """Get the title for table display.

        Returns:
            Title string for schema table output
        """
        return "Configuration Schema"

    @classmethod
    def success(cls, schema_fields: List[ConfigOpts]) -> 'DiscoverSchemaResponse':
        """Create a successful schema discovery response.

        Args:
            schema_fields: List of discovered configuration options

        Returns:
            DiscoverSchemaResponse instance with success status
        """
        return cls(
            status=STATUS_OK,
            message="Schema discovery successful",
            schema_fields=schema_fields
        )

    @classmethod
    def error(cls, error_message: str, schema_fields: List[ConfigOpts] = None) -> 'DiscoverSchemaResponse':
        """Create an error schema discovery response.

        Args:
            error_message: Description of the error that occurred
            schema_fields: Optional partial schema fields (defaults to empty list)

        Returns:
            DiscoverSchemaResponse instance with error status
        """
        return cls(
            status=STATUS_ERROR,
            message=error_message,
            schema_fields=schema_fields or []
        )

    @property
    def value(self) -> List[Dict[str, Any]]:
        """Get the schema fields as serializable data.

        Returns:
            List of dictionaries containing schema field information
        """
        return [field.model_dump(mode='json') for field in self.schema_fields]


@dataclass
class HealthCheckResponse(CliResponse):
    """Response wrapper for health check operations.

    Encapsulates the result of performing a health check on the integration,
    including validation results, connectivity status, and diagnostic details.

    Attributes:
        details: Additional diagnostic information and context
    """
    details: Dict[str, Any]

    @property
    def title(self) -> str:
        """Get the title for table display.

        Returns:
            Title string for health check table output
        """
        return "Health check"

    @classmethod
    def success(cls, input_config: Dict[str, Any]) -> 'HealthCheckResponse':
        """Create a successful health check response.

        Args:
            input_config: The configuration that was validated successfully

        Returns:
            HealthCheckResponse instance with success status
        """
        return cls(
            status=STATUS_OK,
            message="Health check successful", 
            details={'input_config': input_config}
        )

    @classmethod
    def error(cls, error_message: str, details: Dict[str, Any] = None) -> 'HealthCheckResponse':
        """Create an error health check response.

        Args:
            error_message: Description of the health check failure
            details: Optional additional error context and diagnostic info

        Returns:
            HealthCheckResponse instance with error status
        """
        return cls(
            status=STATUS_ERROR,
            message=error_message,
            details=details or {}
        )

    @property
    def value(self) -> Dict[str, Any]:
        """Get the complete health check result as serializable data.
        
        Returns:
            Dictionary containing status, message, and diagnostic details
        """
        return {
            "status": self.status,
            "message": self.message,
            "details": self.details
        }


class CliHandler(ABC):
    """Abstract base class for CLI command handlers.
    
    This class defines the interface that all concrete CLI handlers must implement.
    It provides the contract for schema discovery and health check operations,
    ensuring consistent behavior across different integration implementations.
    
    Concrete implementations should inherit from this class and provide
    specific logic for their integration type (e.g., Claroty, ServiceNow, etc.).
    """

    @abstractmethod
    def discover_schema_handler(self) -> DiscoverSchemaResponse:
        """Handle schema discovery command.
        
        Discovers and returns the configuration schema for the integration,
        including all available configuration parameters, their types,
        default values, and descriptions.
        
        Returns:
            DiscoverSchemaResponse containing the discovered schema information
            
        Raises:
            Exception: If schema discovery fails due to configuration or system errors
        """
        pass

    @abstractmethod
    def health_check_handler(self, input_config: dict) -> HealthCheckResponse:
        """Handle health check command.

        Validates the provided configuration and tests connectivity to the
        target integration. This may include API authentication, endpoint
        availability, and permission validation.

        Args:
            input_config: Dictionary containing the configuration to validate

        Returns:
            HealthCheckResponse containing the validation results and diagnostic info

        Raises:
            Exception: If health check fails due to invalid configuration or system errors
        """
        pass

    @classmethod
    def from_context(cls, ctx) -> 'CliHandler':
        """Extract the CLI handler from the Click context.

        Args:
            ctx: Click context object containing the handler in ctx.obj['handler']

        Returns:
            The CLI handler instance from the context
        """
        return ctx.obj['handler']


def _discover_schema_command():
    """Create the discover-schema command function."""
    @click.command()
    @click.option('--format', 'output_format', type=click.Choice([OUTPUT_FORMAT_TABLE, OUTPUT_FORMAT_JSON]), 
                 default=OUTPUT_FORMAT_TABLE, help='Output format')
    @pass_context
    def discover_schema(ctx, output_format: OutputFormat):
        """Discover and display the configuration schema for the integration.

        This command queries the integration to discover all available configuration
        parameters, including their types, default values, and descriptions. The output
        can be formatted as either a human-readable table or machine-parseable JSON.

        Args:
            output_format: The desired output format ('table' for console display, 'json' for programmatic use)

        Examples:
            # Display schema as a table
            cli discover-schema

            # Get schema as JSON for automation
            cli discover-schema --format json
        """
        try:
            ret = CliHandler.from_context(ctx).discover_schema_handler()
            ret.print(output_format)
        except Exception as e:
            ret = DiscoverSchemaResponse.error(f"Error while discovering schema: {e}")
            ret.print(OUTPUT_FORMAT_JSON)
            sys.exit(1)
    return discover_schema


def _health_check_command():
    """Create the health-check command function."""
    @click.command()
    @click.option('--config', 'input_config', required=True, help='Config credentials (JSON)')
    @pass_context
    def health_check(ctx, input_config: str):
        """Perform a health check on the integration configuration.

        This command validates the provided configuration and tests connectivity
        to the target integration. It verifies authentication, endpoint availability,
        and basic functionality to ensure the integration is properly configured.

        Args:
            input_config: JSON string containing the configuration to validate

        Examples:
            # Check configuration from command line
            cli health-check --config '{"platform_url": "https://...", "platform_key": "..."}'
        """
        try:
            config = json.loads(input_config)
            ret = CliHandler.from_context(ctx).health_check_handler(config)
            ret.print(OUTPUT_FORMAT_JSON)
        except json.JSONDecodeError as e:
            ret = HealthCheckResponse.error(f"Invalid JSON input: {e}")
            ret.print(OUTPUT_FORMAT_JSON)
            sys.exit(1)
        except Exception as e:
            ret = HealthCheckResponse.error(f"Error while verifying health check: {e}")
            ret.print(OUTPUT_FORMAT_JSON)
            sys.exit(1)
    return health_check


def get_default_commands() -> List[click.Command]:
    """Get the default CLI commands.
    
    Returns:
        List of default commands (discover-schema and health-check)
        
    Example:
        # Get default commands for customization
        commands = get_default_commands()
        commands.append(my_custom_command())
        app = create_cli(handler, "my-cli", commands=commands)
    """
    return [_discover_schema_command(), _health_check_command()]


def create_cli(handler: 'CliHandler', prog_name: str = "cli", commands: Optional[List[click.Command]] = None):
    """Factory function to create a CLI with a specific handler and program name.
    
    Args:
        handler: The CLI handler instance that implements the abstract methods
        prog_name: The program name to display in help and version info
        commands: Optional list of custom commands to add (defaults to standard commands)
        
    Returns:
        Configured Click group ready to run
        
    Example:
        handler = MyCliHandler()
        app = create_cli(handler, "my-cli")
        app()
        
        # Or with custom commands
        custom_commands = [_discover_schema_command(), my_custom_command()]
        app = create_cli(handler, "my-cli", commands=custom_commands)
    """
    @click.group(name="cli")
    @click.version_option(version="1.0.0", prog_name=prog_name)
    @pass_context
    def cli_group(ctx):
        ctx.ensure_object(dict)
        ctx.obj['handler'] = handler

    # Add commands to the group (use defaults if none provided)
    if commands is None:
        commands = get_default_commands()
    
    for command in commands:
        cli_group.add_command(command)

    return cli_group

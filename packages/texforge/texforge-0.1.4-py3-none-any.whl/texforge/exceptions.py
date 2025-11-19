"""
Custom exceptions for TexForge agents
"""


class TexForgeError(Exception):
    """Base exception for all TexForge errors"""
    pass


class AgentError(TexForgeError):
    """Base exception for agent errors"""
    pass


class APIError(AgentError):
    """Error calling external API (Anthropic, etc.)"""
    pass


class CodeGenerationError(AgentError):
    """Error generating code"""
    pass


class ParseError(AgentError):
    """Error parsing LaTeX or other structured content"""
    pass


class VerificationError(AgentError):
    """Error during proof/simulation verification"""
    pass


class ConfigurationError(TexForgeError):
    """Error in configuration"""
    pass


class FileNotFoundError(TexForgeError):
    """Required file not found"""
    pass


class TimeoutError(AgentError):
    """Operation timed out"""
    pass

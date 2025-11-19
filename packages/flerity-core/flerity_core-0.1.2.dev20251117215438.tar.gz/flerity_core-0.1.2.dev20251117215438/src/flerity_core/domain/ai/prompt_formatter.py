"""Robust prompt template formatting with variable replacement."""

import re
from typing import Dict, Any, Optional
from string import Formatter


class SafeFormatter(Formatter):
    """Custom formatter that handles missing variables gracefully."""
    
    def __init__(self, default_value: str = ""):
        self.default_value = default_value
    
    def get_value(self, key: Any, args: tuple, kwargs: Dict[str, Any]) -> Any:
        """Get value for a key, return default if missing."""
        if isinstance(key, str):
            try:
                return kwargs[key]
            except KeyError:
                return self.default_value
        else:
            return super().get_value(key, args, kwargs)


class PromptFormatter:
    """Handles AI prompt template formatting with variable replacement."""
    
    # Define all supported variables and their defaults
    SUPPORTED_VARIABLES = {
        # Suggestion prompt variables
        'messages_context': '',
        'max_suggestions': '3',
        'tone_description': 'amigável',
        'hint_section': '',
        'rag_examples': '',
        
        # Icebreaker prompt variables  
        'context_section': '',
        
        # Topic filtering variables
        'preferred_topics': '',
        'avoid_topics': '',
        'topic_guidance': '',
        
        # Common variables
        'platform': 'instagram',
        'age_range': '25-45'  # Default age range
    }
    
    def __init__(self):
        self.formatter = SafeFormatter(default_value="")
    
    def format_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Format template with variables, handling missing ones gracefully.
        
        Args:
            template: Template string with {variable} placeholders
            variables: Dictionary of variable values
            
        Returns:
            Formatted template string
        """
        # Merge provided variables with defaults
        all_variables = {**self.SUPPORTED_VARIABLES, **variables}
        
        try:
            # Use safe formatter to handle missing variables
            return self.formatter.format(template, **all_variables)
        except Exception as e:
            # Ultimate fallback - return template as-is
            return template
    
    def extract_variables(self, template: str) -> list[str]:
        """
        Extract all variable names from a template.
        
        Args:
            template: Template string with {variable} placeholders
            
        Returns:
            List of variable names found in template
        """
        # Find all {variable} patterns
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, template)
        return list(set(matches))  # Remove duplicates
    
    def validate_template(self, template: str) -> Dict[str, Any]:
        """
        Validate template and return analysis.
        
        Args:
            template: Template string to validate
            
        Returns:
            Dictionary with validation results
        """
        variables_found = self.extract_variables(template)
        unsupported_vars = [var for var in variables_found if var not in self.SUPPORTED_VARIABLES]
        
        return {
            'is_valid': len(unsupported_vars) == 0,
            'variables_found': variables_found,
            'unsupported_variables': unsupported_vars,
            'supported_variables': list(self.SUPPORTED_VARIABLES.keys())
        }
    
    def calculate_age_range(self, birth_year: int | None) -> str:
        """
        Calculate age range (±5 years) from birth year.
        
        Args:
            birth_year: User's birth year
            
        Returns:
            Age range string like "25-35" or default "25-45"
        """
        if not birth_year:
            return self.SUPPORTED_VARIABLES['age_range']  # Default: "25-45"
        
        from datetime import datetime
        current_year = datetime.now().year
        current_age = current_year - birth_year
        
        # Calculate range (±5 years)
        min_age = max(18, current_age - 5)  # Minimum age 18
        max_age = min(65, current_age + 5)  # Maximum age 65
        
        return f"{min_age}-{max_age}"

    def build_suggestion_variables(
        self,
        messages_context: str,
        max_suggestions: int,
        tone_description: str,
        hint_section: str = "",
        rag_examples: str = "",
        age_range: str = "",
        topic_guidance: str = "",
        **extra_vars
    ) -> Dict[str, Any]:
        """Build variables dictionary for suggestion prompts."""
        return {
            'messages_context': messages_context,
            'max_suggestions': str(max_suggestions),
            'tone_description': tone_description,
            'hint_section': hint_section,
            'rag_examples': rag_examples,
            'age_range': age_range or self.SUPPORTED_VARIABLES['age_range'],
            'topic_guidance': topic_guidance,
            **extra_vars
        }
    
    def build_icebreaker_variables(
        self,
        max_suggestions: int,
        tone_description: str,
        context_section: str = "",
        age_range: str = "",
        topic_guidance: str = "",
        **extra_vars
    ) -> Dict[str, Any]:
        """Build variables dictionary for icebreaker prompts."""
        return {
            'max_suggestions': str(max_suggestions),
            'tone_description': tone_description,
            'context_section': context_section,
            'age_range': age_range or self.SUPPORTED_VARIABLES['age_range'],
            'topic_guidance': topic_guidance,
            **extra_vars
        }


# Global instance
prompt_formatter = PromptFormatter()


def format_prompt_template(template: str, **variables) -> str:
    """
    Convenience function to format a prompt template.
    
    Args:
        template: Template string with {variable} placeholders
        **variables: Variable values as keyword arguments
        
    Returns:
        Formatted template string
    """
    return prompt_formatter.format_template(template, variables)


def validate_prompt_template(template: str) -> Dict[str, Any]:
    """
    Convenience function to validate a prompt template.
    
    Args:
        template: Template string to validate
        
    Returns:
        Dictionary with validation results
    """
    return prompt_formatter.validate_template(template)

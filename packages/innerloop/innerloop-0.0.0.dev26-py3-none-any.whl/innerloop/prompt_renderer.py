"""Simple prompt rendering function."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from .prompt_context import PromptContext

# Cached Jinja environment (created once)
_env: Environment | None = None


def _get_env() -> Environment:
    """Get or create Jinja environment."""
    global _env
    if _env is None:
        template_dir = Path(__file__).parent / "templates"
        _env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
    return _env


def render_prompt(
    ctx: PromptContext, custom_template: str | None = None
) -> str:
    """Render prompt from context.

    Args:
        ctx: Prompt context (internal object)
        custom_template: Optional custom template string

    Returns:
        Rendered prompt string
    """
    if custom_template:
        # Custom inline template
        tmpl = Template(custom_template, trim_blocks=True, lstrip_blocks=True)
        return tmpl.render(ctx=ctx)

    # Use default template
    env = _get_env()
    template = env.get_template("main.jinja2")
    return template.render(ctx=ctx)

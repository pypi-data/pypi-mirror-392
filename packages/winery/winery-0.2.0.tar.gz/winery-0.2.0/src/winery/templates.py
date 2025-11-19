import jinja2
from pathlib import Path
from jinja2 import nodes


class WineryTemplate:
    def __init__(self, template_name: str, context_vars: list[str] | None = None):
        self.template_name = template_name
        self.context_vars = context_vars or []

    def __eq__(self, other):
        if not isinstance(other, WineryTemplate):
            return False
        return (
            self.template_name == other.template_name
            and self.context_vars == other.context_vars
        )

    def to_dict(self):
        return {"template_name": self.template_name, "context_vars": self.context_vars}


class WineryTemplateBackend:
    def __init__(self, winery, template_path: Path):
        self.winery = winery
        self.template_path = template_path
        self.jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_path), autoescape=True
        )
        self.templates = self._discover_templates()

    def _discover_templates(self) -> list[WineryTemplate]:
        """
        Discovers templates and their context variables in the template path.

        Iterates through all available templates, parses their Abstract Syntax
        Tree (AST), and extracts variable names defined within ``{% set %}``
        blocks.

        This implementation recursively handles tuple unpacking and skips
        templates that contain syntax errors.

        :return: A list of WineryTemplate objects containing the template name
                and a sorted list of defined context variables.
        :rtype: list[WineryTemplate]
        """
        templates = []
        env = self.jinja2_env

        def _extract_names(target):
            """Recursively yields variable names from a node target."""
            if isinstance(target, nodes.Name):
                yield target.name
            elif isinstance(target, nodes.Tuple):
                for item in target.items:
                    yield from _extract_names(item)

        for template_name in env.list_templates():
            try:
                source, _, _ = env.loader.get_source(env, template_name)
                ast = env.parse(source)
            except Exception:
                continue

            context_vars = set()

            for node in ast.find_all(nodes.Assign):
                context_vars.update(_extract_names(node.target))

            templates.append(WineryTemplate(template_name, sorted(context_vars)))

        return templates

    def get_template(self, template_name):
        """Gets a Jinja2 template object."""
        return self.jinja2_env.get_template(template_name)

    def render_template(self, template_name: str, **context) -> str:
        """Renders a template with the given context."""
        template = self.get_template(template_name)
        return template.render(**context)

import pytest
from pathlib import Path
import tempfile
from winery.templates import WineryTemplate, WineryTemplateBackend


@pytest.fixture
def template_dir():
    """Creates a temporary directory with various Jinja2 templates for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        d = Path(temp_dir)
        # Template with a single variable
        (d / "simple.html").write_text("{% set my_var = 'test' %}")
        # Template with tuple unpacking
        (d / "tuple.html").write_text("{% set var1, var2 = ('a', 'b') %}")
        # Template with nested tuple unpacking
        (d / "nested.html").write_text(
            "{% set (var1, (var2, var3)) = ('a', ('b', 'c')) %}"
        )
        # Template with no variables
        (d / "no_vars.html").write_text("Hello, world!")
        # Template with a syntax error
        (d / "syntax_error.html").write_text("{% set my_var = %}")
        # Subdirectory with a template
        (d / "subdir").mkdir()
        (d / "subdir/sub.html").write_text("{% set sub_var = 42 %}")
        yield d


class TestWineryTemplate:
    """Tests for the WineryTemplate data class."""

    def test_init(self):
        """Tests basic initialization."""
        t = WineryTemplate("a.html", context_vars=["var1"])
        assert t.template_name == "a.html"
        assert t.context_vars == ["var1"]

    def test_init_no_vars(self):
        """Tests initialization with no context vars."""
        t = WineryTemplate("b.html")
        assert t.template_name == "b.html"
        assert t.context_vars == []

    def test_to_dict(self):
        """Tests dictionary conversion."""
        t = WineryTemplate("c.html", context_vars=["var1", "var2"])
        assert t.to_dict() == {
            "template_name": "c.html",
            "context_vars": ["var1", "var2"],
        }

    def test_equality(self):
        """Tests the __eq__ method."""
        t1 = WineryTemplate("a.html", ["var1"])
        t2 = WineryTemplate("a.html", ["var1"])
        t3 = WineryTemplate("a.html", ["var2"])
        t4 = WineryTemplate("b.html", ["var1"])
        assert t1 == t2
        assert t1 != t3
        assert t1 != t4
        assert t1 != "not a template"


class TestWineryTemplateBackend:
    """Tests for the WineryTemplateBackend."""

    @pytest.fixture
    def backend(self, template_dir):
        """Initializes WineryTemplateBackend with the test template directory."""
        # The backend requires a 'winery' object, but it's not used in discovery.
        # We can pass None or a mock object.
        return WineryTemplateBackend(winery=None, template_path=template_dir)

    def test_discover_templates(self, backend):
        """Tests that templates and their context variables are discovered correctly."""
        templates = backend.templates
        # Note: Jinja2's list_templates() doesn't guarantee order, so we check contents.

        # There should be 5 valid templates found (syntax_error.html is skipped)
        assert len(templates) == 5

        expected_templates = {
            "simple.html": WineryTemplate("simple.html", ["my_var"]),
            "tuple.html": WineryTemplate("tuple.html", ["var1", "var2"]),
            "nested.html": WineryTemplate("nested.html", ["var1", "var2", "var3"]),
            "no_vars.html": WineryTemplate("no_vars.html", []),
            "subdir/sub.html": WineryTemplate("subdir/sub.html", ["sub_var"]),
        }

        discovered_map = {t.template_name: t for t in templates}

        for name, expected in expected_templates.items():
            assert name in discovered_map
            assert discovered_map[name] == expected

    def test_discover_templates_with_syntax_error(self, template_dir):
        """Ensures templates with syntax errors are skipped without crashing."""
        # This file contains a syntax error
        (template_dir / "bad_template.j2").write_text("{% set a = 'val %}")
        backend = WineryTemplateBackend(winery=None, template_path=template_dir)

        # The discovery should not crash and should find the other valid templates
        assert len(backend.templates) > 0

    def test_render_template(self, backend):
        """Tests rendering a template."""
        (backend.template_path / "render_test.html").write_text("Hello, {{ name }}!")
        # Re-initialize to discover the new template
        backend.templates = backend._discover_templates()
        output = backend.render_template("render_test.html", name="Winery")
        assert output == "Hello, Winery!"

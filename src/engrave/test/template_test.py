import unittest
import tempfile
import os
import shutil
from pathlib import Path

from engrave.template import get_template


class TemplateTests(unittest.TestCase):
    def setUp(self):
        # Create primary temporary directory for test templates
        self.temp_dir = tempfile.mkdtemp()

        # Create a second directory to test multiple template paths
        self.temp_dir2 = tempfile.mkdtemp()

        # Create test template files
        self.template_file = os.path.join(self.temp_dir, "main.html")
        with open(self.template_file, "w") as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <body>
                <h1>{{ title }}</h1>
                <div class="included">{{ markdown('content.md') }}</div>
                <div class="filter">{{ content|markdown }}</div>
                {% include 'partial.html' %}
            </body>
            </html>
            """)

        # Create partial template for inclusion
        self.partial_file = os.path.join(self.temp_dir, "partial.html")
        with open(self.partial_file, "w") as f:
            f.write('<div class="partial">{{ partial_content }}</div>')

        # Create markdown file for inclusion
        self.md_file = os.path.join(self.temp_dir, "content.md")
        with open(self.md_file, "w") as f:
            f.write("# Hello World\n\nThis is **markdown** content.")

        # Create a template in the second directory
        self.template_file2 = os.path.join(self.temp_dir2, "secondary.html")
        with open(self.template_file2, "w") as f:
            f.write('<p>{{ markdown("secondary.md") }}</p>')

        # Create markdown file in the second directory
        self.md_file2 = os.path.join(self.temp_dir2, "secondary.md")
        with open(self.md_file2, "w") as f:
            f.write("## Secondary content\n\nFrom *second* directory.")

    def tearDown(self):
        # Clean up the temporary directories
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.temp_dir2)

    def test_get_template_basic(self):
        """Test that get_template returns a callable template loader"""
        template_loader = get_template(dir_src=self.temp_dir)
        self.assertTrue(callable(template_loader))

        # Check that we can load a template
        template = template_loader("main.html")
        self.assertIsNotNone(template)

    def test_template_environment(self):
        """Test that the Jinja2 environment has the expected functions"""
        template_loader = get_template(dir_src=self.temp_dir)

        # Access the environment through a loaded template
        template = template_loader("main.html")
        env = template.environment

        # Check for markdown function and filter
        self.assertTrue('markdown' in env.globals)
        self.assertTrue('markdown' in env.filters)
        self.assertTrue(callable(env.globals['markdown']))
        self.assertTrue(callable(env.filters['markdown']))

    def test_markdown_function(self):
        """Test that the markdown function correctly renders markdown files"""
        template_loader = get_template(dir_src=self.temp_dir)
        template = template_loader("main.html")
        result = template.render(
            title="Test Title",
            content="**Inline** markdown",
            partial_content="Partial template content"
        )

        # Check if markdown file was included and rendered
        self.assertIn("<h1>Hello World</h1>", result)
        self.assertIn("<strong>markdown</strong> content", result)

        # Check if markdown filter works
        self.assertIn("<strong>Inline</strong> markdown", result)

        # Check if partial template was included
        self.assertIn('<div class="partial">Partial template content</div>', result)

    def test_custom_markdown_parser(self):
        """Test using a custom markdown parser function"""
        def custom_parser(text):
            return f"<custom>{text}</custom>"

        template_loader = get_template(dir_src=self.temp_dir, markdown_to_html=custom_parser)
        template = template_loader("main.html")
        result = template.render(
            title="Test Title",
            content="**Inline** markdown",
            partial_content="Partial content"
        )

        # Check if our custom parser was used for both function and filter
        self.assertIn("<custom># Hello World\n\nThis is **markdown** content.</custom>", result)
        self.assertIn("<custom>**Inline** markdown</custom>", result)

    def test_multiple_template_directories(self):
        """Test that templates can be loaded from multiple directories"""
        template_loader = get_template(dir_src=[self.temp_dir, self.temp_dir2])

        # Check main template from first directory
        main_template = template_loader("main.html")
        self.assertIsNotNone(main_template)

        # Check secondary template from second directory
        secondary_template = template_loader("secondary.html")
        self.assertIsNotNone(secondary_template)

        # Verify content from secondary template
        result = secondary_template.render()
        self.assertIn("Secondary content", result)
        self.assertIn("<em>second</em>", result)

    def test_path_objects(self):
        """Test using Path objects instead of strings"""
        template_loader = get_template(dir_src=Path(self.temp_dir))
        template = template_loader("main.html")
        result = template.render(
            title="Test Title",
            content="**Path** test",
            partial_content="Path test"
        )
        self.assertIn("<h1>Test Title</h1>", result)
        self.assertIn("<strong>Path</strong> test", result)

    def test_markdown_file_not_found(self):
        """Test behavior when markdown file is not found"""
        template_loader = get_template(dir_src=self.temp_dir)

        # Create a template that references a non-existent markdown file
        test_file = os.path.join(self.temp_dir, "not_found_test.html")
        with open(test_file, "w") as f:
            f.write('{{ markdown("nonexistent.md") }}')

        template = template_loader("not_found_test.html")

        with self.assertRaises(FileNotFoundError) as context:
            template.render()

        self.assertIn("Markdown file not found", str(context.exception))

    def test_additional_jinja_args(self):
        """Test passing additional arguments to Jinja environment"""
        template_loader = get_template(
            dir_src=self.temp_dir,
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = template_loader("main.html")
        self.assertTrue(template.environment.trim_blocks)
        self.assertTrue(template.environment.lstrip_blocks)

    def test_markdown_error_handling(self):
        """Test error handling when processing markdown files"""
        # Create a markdown file that will cause an error when processed
        error_dir = tempfile.mkdtemp()
        error_md = ""  # Initialize here to avoid "possibly unbound" error
        try:
            # Create a template that accesses a markdown file
            error_template = os.path.join(error_dir, "error.html")
            with open(error_template, "w") as f:
                f.write('{{ markdown("error.md") }}')

            # Create a "markdown" file that's actually not accessible
            error_md = os.path.join(error_dir, "error.md")
            with open(error_md, "w") as f:
                f.write("# Test content")

            # Make the file non-readable to simulate an error
            os.chmod(error_md, 0)  # Remove all permissions

            template_loader = get_template(dir_src=error_dir)
            template = template_loader("error.html")

            # This should raise an exception
            with self.assertRaises(Exception) as context:
                template.render()

            self.assertIn("Error processing markdown file", str(context.exception))
        finally:
            # Restore permissions so we can clean up
            if os.path.exists(error_md):
                os.chmod(error_md, 0o644)
            shutil.rmtree(error_dir)


if __name__ == "__main__":
    unittest.main()

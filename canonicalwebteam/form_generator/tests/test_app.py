import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from flask import Flask
from canonicalwebteam.form_generator.app import FormGenerator


class TestFormGenerator(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.form_template_path = "form-template.html"

    def test_init(self):
        """
        Test FormGenerator initialization.
        """
        form_generator = FormGenerator(self.app, self.form_template_path)
        self.assertEqual(form_generator.app, self.app)
        self.assertEqual(
            form_generator.form_template_path, self.form_template_path
        )
        self.assertIn("load_form", self.app.jinja_env.globals)

    @patch(
        "canonicalwebteam.form_generator.app.open",
        new_callable=mock_open,
        read_data='{"form": {"test_path": '
        '{"templatePath": "test.html", "fieldsets": [], "formData": {}}}}',
    )
    @patch("canonicalwebteam.form_generator.app.Path.rglob")
    def test_load_forms(self, mock_rglob, mock_open):
        """
        Test loading forms from JSON files.
        """
        mock_path = MagicMock(spec=Path)
        mock_rglob.return_value = [mock_path]

        form_generator = FormGenerator(self.app, self.form_template_path)
        form_generator.load_forms()

        self.assertIn("test_path", form_generator.form_metadata)
        self.assertEqual(
            form_generator.form_metadata["test_path"]["template"], "test"
        )

    @patch("canonicalwebteam.form_generator.app.render_template")
    def test_load_form(self, mock_render_template):
        """
        Test the load_form function.
        """
        form_generator = FormGenerator(self.app, self.form_template_path)

        form_generator._load_form_json = MagicMock(
            return_value={
                "/test": {
                    "fieldsets": [{"fields": []}],
                    "formData": {"title": "Test Form"},
                }
            }
        )

        form_generator.form_metadata = {
            "/test": {
                "file_path": "path/to/form.json",
                "template": "test-template",
            }
        }

        form_generator.load_form("/test")

        mock_render_template.assert_called_once()
        args, kwargs = mock_render_template.call_args
        self.assertEqual(args[0], self.form_template_path)
        self.assertEqual(kwargs["fieldsets"], [{"fields": []}])
        self.assertEqual(kwargs["formData"], {"title": "Test Form"})
        self.assertIsNone(kwargs["path"])

    def test_store_metadata(self):
        """
        Test the _store_metadata function.
        """
        form_generator = FormGenerator(self.app, self.form_template_path)
        file_path = Path("path/to/form-data.json")
        forms_data = {
            "/test": {
                "templatePath": "test.html",
                "childrenPaths": ["/child/index"],
            }
        }

        form_generator._store_metadata(file_path, forms_data)

        self.assertIn("/test", form_generator.form_metadata)
        self.assertEqual(
            form_generator.form_metadata["/test"]["template"], "test"
        )
        self.assertEqual(
            form_generator.form_metadata["/test"]["file_path"], file_path
        )

        self.assertIn("/child", form_generator.form_metadata)
        self.assertTrue(form_generator.form_metadata["/child"]["is_child"])

    def test_process_child_path(self):
        """
        Test the _process_child_path function.
        """
        result = FormGenerator._process_child_path("/parent/child/index")
        self.assertEqual(result, "/parent/child")

        result = FormGenerator._process_child_path("/parent/child")
        self.assertEqual(result, "/parent/child")

    def test_remove_file_extension(self):
        """
        Test the _remove_file_extension function.
        """
        result = FormGenerator._remove_file_extension("test.html")
        self.assertEqual(result, "test")

        result = FormGenerator._remove_file_extension("test")
        self.assertEqual(result, "test")

    @patch(
        "canonicalwebteam.form_generator.app.open",
        new_callable=mock_open,
        read_data='{"form": {"test_path": {"templatePath": "test.html"}}}',
    )
    def test_load_form_json(self, mock_open):
        """
        Test the _load_form_json function.
        """
        form_generator = FormGenerator(self.app, self.form_template_path)
        file_path = Path("path/to/form-data.json")

        result = form_generator._load_form_json(file_path)

        self.assertIn("test_path", result)
        self.assertEqual(result["test_path"]["templatePath"], "test.html")

    @patch(
        "canonicalwebteam.form_generator.app.open",
        side_effect=FileNotFoundError,
    )
    def test_load_form_json_file_not_found(self, mock_open):
        """
        Test _load_form_json with a missing file.
        """
        form_generator = FormGenerator(self.app, self.form_template_path)
        file_path = Path("missing/form-data.json")

        with self.assertRaises(Exception) as context:
            form_generator._load_form_json(file_path)
        self.assertIn("JSON file not found", str(context.exception))

    @patch(
        "canonicalwebteam.form_generator.app.open",
        new_callable=mock_open,
        read_data="invalid json",
    )
    def test_load_form_json_invalid_json(self, mock_open):
        """
        Test _load_form_json with invalid JSON.
        """
        form_generator = FormGenerator(self.app, self.form_template_path)
        file_path = Path("path/to/invalid.json")

        with self.assertRaises(Exception) as context:
            form_generator._load_form_json(file_path)
        self.assertIn("Invalid JSON format", str(context.exception))

    @patch("canonicalwebteam.form_generator.app.Path.rglob")
    @patch(
        "canonicalwebteam.form_generator.app.open",
        new_callable=mock_open,
        read_data='{"invalid_key": {}}',
    )
    @patch("canonicalwebteam.form_generator.app.abort")
    def test_load_forms_missing_form_key(
        self, mock_abort, mock_open, mock_rglob
    ):
        """
        Test load_forms with a JSON file missing the top level 'form' key.
        """
        mock_rglob.return_value = [Path("path/to/bad-form-data.json")]
        form_generator = FormGenerator(self.app, self.form_template_path)

        form_generator.load_forms()

        mock_abort.assert_called_once()
        self.assertEqual(mock_abort.call_args[0][0], 400)
        self.assertIn(
            "The JSON should have a 'form' key",
            mock_abort.call_args[1]["description"],
        )


if __name__ == "__main__":
    unittest.main()

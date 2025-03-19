import json
import flask
from pathlib import Path


class FormGenerator:
    def __init__(self, app, form_template_path):
        """
        Initialize with a Flask app instance.

        :param app: Flask app instance
        :param form_template_path: Path to the form template
        """
        self.app = app
        self.form_template_path = form_template_path
        self.templates_folder = Path(app.root_path).parent / "templates"
        self.form_metadata = {}

        # Register Jinja function globally
        self.app.jinja_env.globals["load_form"] = self.load_form

    def load_forms(self):
        """
        Finds all 'form-data.json' files within the 'templates' dir and
        stores limited metadata.
        """
        for file_path in self.templates_folder.rglob("form-data.json"):
            with open(file_path) as forms_json:
                data = json.load(forms_json)
                self._store_metadata(file_path, data["form"])

    def _store_metadata(self, file_path: Path, forms_data: dict):
        """
        Stores metadata ('file_path' and 'template') about forms under their
        respective paths.
        """
        for path, form in forms_data.items():
            self.form_metadata[path] = {
                "file_path": file_path,
                "template": form["templatePath"].rsplit(".", 1)[
                    0
                ],  # Remove file extension
            }

            for child_path in form.get("childrenPaths", []):
                processed_path = self._process_child_path(child_path)
                self.form_metadata[processed_path] = {
                    "file_path": file_path,
                    "template": form["templatePath"].rsplit(".", 1)[0],
                }

    def load_form(self, form_path: Path) -> str:
        """
        Jinja function that return a html string form.
        
        Usage: {{ load_form('/aws') }}
        """
        form_info = self.form_metadata.get(form_path)
        # ADD ERROR HANDLING

        form_json = self._load_form_json(form_info["file_path"]).get(form_path)
        # ADD ERROR HANDLING

        return flask.render_template(
            self.form_template_path,
            fieldsets=form_json["fieldsets"],
            formData=form_json["formData"],
            isModal=form_json.get("isModal"),
            modalId=form_json.get("modalId"),
            path=form_path,
        )

    def _load_form_json(self, file_path: Path) -> dict:
        """
        Loads form data from a JSON file.
        """
        try:
            with open(file_path) as forms_json:
                return json.load(forms_json).get("form", {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
            # ADD ERROR HANDLING

    @staticmethod
    def _process_child_path(child_path: str) -> str:
        """
        Processes child path, removing 'index' if present.
        """
        path_split = child_path.strip("/").split("/")
        return (
            "/" + "/".join(path_split[:-1])
            if path_split[-1] == "index"
            else child_path
        )

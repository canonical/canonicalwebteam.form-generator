import json
import flask
import jinja2
from functools import wraps
from pathlib import Path


class FormGenerator:
    def __init__(self, app):
        """
        Initialize with a Flask app instance.

        :param app: Flask app instance
        """
        self.app = app
        self.templates_folder = Path(app.root_path).parent / "templates"

    def load_forms(self):
        """
        Finds all 'form-data.json' files within the 'templates' dir and
        registers form routes.
        """
        for file_path in self.templates_folder.rglob("form-data.json"):
            with open(file_path) as forms_json:
                data = json.load(forms_json)
                self._register_forms(data["form"])

    def _register_forms(self, forms_data: dict):
        """
        Registers routes based on form-data.json contents.
        """
        for path, form in forms_data.items():
            self._register_route(path, form)

            # Register child paths if any
            for child_path in form.get("childrenPaths", []):
                processed_path = self._process_child_path(child_path)
                self._register_route(processed_path, form, child=True)

    def _register_route(self, path: str, form: dict, child: bool = False):
        """
        Registers a _render_form func to a specific route and passes
        in the form data.
        """
        template_path = (
            form["templatePath"].split(".")[0] if not child else path
        )
        self.app.add_url_rule(
            path,
            view_func=self._render_form(form, template_path, child),
            endpoint=path,
        )

    def _render_form(
        self, form: dict, template_path: str, child: bool = False
    ):
        """
        Returns a function to render the form template.
        """

        @wraps(self._render_form)
        def wrapper_func():
            try:
                return flask.render_template(
                    f"{template_path}.html",
                    fieldsets=form["fieldsets"],
                    formData=form["formData"],
                    isModal=form.get("isModal"),
                    modalId=form.get("modalId"),
                    path=template_path if child else None,
                )
            except jinja2.exceptions.TemplateNotFound:
                flask.abort(
                    404, description=f"Template {template_path} not found."
                )

        return wrapper_func

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

from json import load as json_load, JSONDecodeError
from flask import abort, render_template
from pathlib import Path
from werkzeug.exceptions import HTTPException


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

        # Register Jinja function so it can be accessed in templates
        self.app.jinja_env.globals["load_form"] = self.load_form

    def load_forms(self):
        """
        Finds all 'form-data.json' files within the 'templates' dir and
        stores limited metadata.
        """
        for file_path in self.templates_folder.rglob("form-data.json"):
            try:
                with open(file_path) as forms_json:
                    data = json_load(forms_json)
                    if "form" not in data:
                        abort(
                            400,
                            description=(
                                "The JSON should have a 'form' key containing"
                                f" the form data: {file_path}"
                            ),
                        )
                    else:
                        self._store_metadata(file_path, data["form"])
            except HTTPException:
                raise
            except (
                JSONDecodeError,
                FileNotFoundError,
            ) as e:
                abort(
                    500,
                    description=(
                        "Error processing form data from "
                        f"{file_path}: {str(e)}"
                    ),
                )
            except Exception as e:
                abort(
                    500,
                    description=(
                        "Error processing form data from "
                        f"{file_path}: {str(e)}"
                    ),
                )

    def _store_metadata(self, file_path: Path, forms_data: dict):
        """
        Stores metadata ('file_path' and 'template') about forms under their
        respective paths.
        """
        for path, form in forms_data.items():
            self.form_metadata[path] = {
                "file_path": file_path,
                "template": self._remove_file_extension(form["templatePath"]),
            }

            for child_path in form.get("childrenPaths", []):
                processed_path = self._process_child_path(child_path)
                self.form_metadata[processed_path] = {
                    "file_path": file_path,
                    "template": self._remove_file_extension(
                        form["templatePath"]
                    ),
                    "is_child": True,
                }

    def load_form(
        self, form_path: Path, formId: int = None, isModal: bool = None
    ) -> str:
        """
        Jinja function that return a html string form.

        :param form_path: The path to the parent form
        :return: HTML form
        :usage: {{ load_form('/aws') }}
        """
        form_info = self.form_metadata.get(form_path)
        if form_info is None:
            abort(
                404,
                description=f"Form metadata not found for path: {form_path}",
            )

        is_child = form_info.get("is_child", False)

        form_json = self._load_form_json(form_info["file_path"]).get(form_path)
        if not form_json:
            abort(
                404, description=f"Form data not found for path: {form_path}"
            )

        try:
            is_modal = form_json.get("isModal") if isModal is None else isModal
            return render_template(
                self.form_template_path,
                fieldsets=form_json["fieldsets"],
                formData=form_json["formData"],
                isModal=is_modal,
                modalId=form_json.get("modalId"),
                path=form_path if is_child else None,
                formId=formId,
            )
        except Exception as e:
            abort(
                500,
                f"Error rendering template for {form_path}: {str(e)}",
            )

    def _load_form_json(self, file_path: Path) -> dict:
        """
        Loads form data from a JSON file.
        """
        try:
            with open(file_path, encoding="utf-8") as form_json:
                return json_load(form_json).get("form", {})
        except FileNotFoundError:
            abort(404, description=f"JSON file not found: {file_path} \n")
        except JSONDecodeError:
            abort(400, description=f"Invalid JSON format: {file_path} \n")
        except Exception as e:
            abort(
                500, description=f"Unexpected error loading JSON: {str(e)} \n"
            )

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

    @staticmethod
    def _remove_file_extension(file_path: Path) -> str:
        """
        Removes file extension from a file path.
        """
        return file_path.rsplit(".", 1)[0]

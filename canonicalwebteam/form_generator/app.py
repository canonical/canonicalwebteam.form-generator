import json

import flask
import jinja2
from functools import wraps
from pathlib import Path


def render_form(form, template_path, child=False):
    @wraps(render_form)
    def wrapper_func():
        try:
            if child:
                return flask.render_template(
                    template_path + ".html",
                    fieldsets=form["fieldsets"],
                    formData=form["formData"],
                    isModal=form.get("isModal"),
                    modalId=form.get("modalId"),
                    path=template_path,
                )
            else:
                return flask.render_template(
                    template_path + ".html",
                    fieldsets=form["fieldsets"],
                    formData=form["formData"],
                    isModal=form.get("isModal"),
                    modalId=form.get("modalId"),
                )
        except jinja2.exceptions.TemplateNotFound:
            flask.abort(
                404, description=f"Template {template_path} not found."
            )

    return wrapper_func


def set_form_rules(app):
    templates_folder = Path(app.root_path).parent / "templates"
    for file_path in templates_folder.rglob("form-data.json"):
        with open(file_path) as forms_json:
            data = json.load(forms_json)
            for path, form in data["form"].items():
                if "childrenPaths" in form:
                    for child_path in form["childrenPaths"]:
                        # If the child path ends with 'index', remove it for
                        # the path
                        path_split = child_path.strip("/").split("/")
                        if path_split[-1] == "index":
                            processed_path = "/" + "/".join(path_split[:-1])
                        else:
                            processed_path = child_path
                        app.add_url_rule(
                            processed_path,
                            view_func=render_form(
                                form, child_path, child=True
                            ),
                            endpoint=processed_path,
                        )
                app.add_url_rule(
                    path,
                    view_func=render_form(
                        form, form["templatePath"].split(".")[0]
                    ),
                    endpoint=path,
                )
# canonicalwebteam.form_generator

Flask extension that generates unique HTML forms based on `json` data and registers them to URLs.

## Installation and usage

Install the project with pip: `pip install canonicalwebteam.form-generator`

You can then initialize it by passing a Flask app instance and path to the form template, and then load the forms:

```
from canonicalwebteam.form_generator import FormGenerator

form_template_path = "path/to/form-template.html"
form_loader = FormGenerator(app, form_template_path)
form_loader.load_forms()
```

You can then call the `load_forms` function from within a Jinja template. Providing a path for the `form-data.json` (required), a formId (optional) and isModal (optional):

```
{{ load_form('/aws', 1234) | safe }}
{{ load_form('/aws', 1234, True) | safe }}
{{ load_form('/aws', isModal=True) | safe }}
```

See the [full guide](https://webteam.canonical.com/practices/automated-form-builder) for more information.

## Local development

### Running the project

This guide assumes you are using [dotrun](https://github.com/canonical/dotrun/).

Include a relative path to the project in your `requirements.txt` (this example assumes both project exist in the same dir):
`-e ../form-generator`

Run dotrun with a mounted additor:
`dotrun -m /path/to/canonicalwebteam.form-generator:../form-generator`

A more detailed guide can be found [here (internal only)](https://discourse.canonical.com/t/how-to-run-our-python-modules-for-local-development/308).

### Linting

To use the standard linting rules of this project you should use [Tox](https://tox.wiki/en/latest/):

```
pip3 install tox  # Install tox
tox -e lint       # Check the format of Python code
tox -e format     # Reformat the Python code
```

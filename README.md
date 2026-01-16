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

You can then call the `load_form` function from within a Jinja template. The function accepts the following parameters:

### Parameters

- `form_path` (required): Path to the form in your `form-data.json`
- `formId` (optional): Marketo ID for the form - overrides the formId from JSON
- `isModal` (optional): Boolean to determine if form is displayed as a modal
- `title` (optional): Title of the form - overrides the title from JSON
- `introText` (optional): Form description - overrides the introText from JSON
- `returnUrl` (optional): Return URL on form submission - overrides the returnUrl from JSON
- `lpUrl` (optional): Landing page URL - overrides the lpUrl from JSON
- `lpId` (optional): Landing page ID - overrides the lpId from JSON
- `product` (optional): Product name - overrides the product from JSON

### Usage Examples

**Basic usage:**
```
{{ load_form('/aws') | safe }}
{{ load_form('/aws', 1234) | safe }}
{{ load_form('/aws', isModal=True) | safe }}
```

**Customizing form data:**
```
{{ load_form('/aws',
    title='Talk to our PostgreSQL experts',
    returnUrl='/data/postgresql#contact-form-success') | safe }}

{{ load_form('/contact',
    formId=1266,
    title='Get in touch with our team',
    introText='We are here to help you with your database needs',
    returnUrl='/contact#contact-form-success',
    lpUrl='https://pages.ubuntu.com/example') | safe }}
```

**Reusing the same form with different content:**
```
{# PostgreSQL page #}
{{ load_form('/data/contact',
    title='PostgreSQL Support',
    product='PostgreSQL',
    returnUrl='/data/postgresql#contact-form-success') | safe }}

{# MySQL page #}
{{ load_form('/data/contact',
    title='MySQL Solutions',
    product='MySQL',
    returnUrl='/data/mysql#contact-form-success') | safe }}
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

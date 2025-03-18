# canonicalwebteam.form_generator

Flask extension that generates unique HTML forms based on `json` data.

## Local development

### Running the project

To use this module locally on a [dotrun](https://github.com/canonical/dotrun/) project:

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
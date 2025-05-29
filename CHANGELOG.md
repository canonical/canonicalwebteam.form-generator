## [2.0.1] - 2025-05-26
### Added
- Testing for app.py

## [2.0.0] - 2025-03-18
### Changed
- No longer registers a function to each route, instead exposes a Jinja function to dynamically build the form, `load_form()`
- Path to the form template must now be passed to the `load_form` function. This eliminates the need to include the form template in each template that uses it

### Added
- Error handling

## [1.0.0] - 2025-03-18
### Added
- Initial project release
- Core functionality:
    - Consumes a Flask app and locates all form-data.json files
    - Processes them into HTML forms and register them to URLs
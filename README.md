# CSP Observer
## Early prototype. Do not install.
CSP Observer is a Django app that monitors incoming Content Security Policy (CSP) reports for your site. It tries to detect security/privacy issues and notifies your visitors.

## Installation

1. Add "csp_observer" to your `INSTALLED_APPS`:
    ```
    INSTALLED_APPS = [
        ...
        'csp_observer',
    ]
    ```
2. Include the url configuration in your `urls.py`:
    ```
    path('csp/', include('csp_observer.urls')),
    ```
3. Run ``python manage.py migrate`` to create the necessary database tables.
4. The basic installation is finished! View the *Configuration* section for more information on how to configure the app.

## Configuration

Overview of all available settings and their default values:

| Setting | Default | Description |
| ------- | ------- | ----------- |
| REPORT_ONLY | ``True`` | Wether to enforce the CSP rules or only report them. |
| ENABLED_PATHS | ``["/"]`` | An array of paths for which the CSP header should be set. |
| CSP_POLICIES | ``["default-src 'self'"]`` | An array of CSP policies that should be applied. |
| ENABLE_NEW_API | ``False`` | Whether to enable the new Reporting API or use the old report-uri directive |

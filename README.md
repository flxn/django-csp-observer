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
| CSP_POLICIES | ``{'default-src': ["'self'"],'script-src': ["'self'", "'unsafe-inline'"],'connect-src': ["'self'"],}`` | A disctionary of CSP policies that should be applied. Key is the name of the directive and value is a list of expressions. |
| ENABLE_NEW_API | ``False`` | Whether to enable the new Reporting API or use the old report-uri directive |
| SESSION_KEEP_DAYS | ``14`` | The number of days sessions should be kept in the database. |
| IS_MASTER_COLLECTOR | ``False`` | Indicates if the instance should function as a central collector of CSP reports for multiple other instances. |
| AUTHORIZED_REPORTERS | ``[]`` | A list of domains that are allowed send their CSP reports to the master. Example: ``['http://127.0.0.1:8000', 'https://example.com']`` |
| REMOTE_SECRET | ``''`` | A shared secret that **must be the same** for the master collector and all reporters. |
| REMOTE_REPORTING | ``False`` | Wether to use a central remote collector or not. |
|REMOTE_CSP_OBSERVER_URL | ``''`` | The URL of the remote collector instance. Must be the path to the *csp_observer* app, as defined in *urls.py*. Example: ``http://example.com/csp`` |
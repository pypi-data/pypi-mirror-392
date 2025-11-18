# AA "Top"

System Utilization and AA Statistics plugin for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth/).

Inspired by <https://zkillboard.com/ztop/> by Squizz Caphinator

## Features

Resource Monitor
Celery Jobs in Queue

Diff of last update

## Planned Features

## Installation

### Step 2 - Install app

```shell
pip install aa-top
```

### Step 3 - Configure Auth settings

Configure your Auth settings (`local.py`) as follows:

- Add `'top'` to `INSTALLED_APPS`
- Add below lines to your settings file:

```python
## Settings for AA-Top
# Update aatop.txt
CELERYBEAT_SCHEDULE['top_update_aa_top_txt'] = {
    'task': 'top.tasks.update_aa_top_txt',
    'schedule': crontab(minute='*'),
}
```

### Step 4 - Maintain Alliance Auth

- Run migrations `python manage.py migrate`
- Gather your staticfiles `python manage.py collectstatic`
- Restart your project `supervisorctl restart myauth:`

- Add file permissions `setfacl -m u:allianceserver:rw /var/www/myauth/static/top/aatop.txt`

## Permissions

| Perm         | Admin Site | Perm                                 | Description |
| ------------ | ---------- | ------------------------------------ | ----------- |
| basic_access | nill       | Can access the web view for this app | -           |

## Settings

| Name | Description | Default |
| ---- | ----------- | ------- |

## Contributing

Make sure you have signed the [License Agreement](https://developers.eveonline.com/resource/license-agreement) by logging in at <https://developers.eveonline.com> before submitting any pull requests. All bug fixes or features must not include extra superfluous formatting changes.

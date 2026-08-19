command = '/home/lms/LMS-Education-system/env/bin/gunicorn'
pythonpath = '/home/lms/LMS-Education-system'
bind = '127.0.0.1:8020'
workers = 17
user = 'lms'
limit_request_fields = 32000
limit_request_field_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE=config.settings'

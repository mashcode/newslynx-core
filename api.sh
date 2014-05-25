workon newslynx-core
gunicorn -w 4 newslynx_core.api:app

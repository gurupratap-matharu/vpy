APP_LIST ?= main users
.PHONY: collectstatic run test ci install install-dev migrations staticfiles

help:
	@echo "Available commands"
	@echo "ci - lints, migrations, tests, coverage"
	@echo "runserver - runs the development server"
	@echo "shellplus - runs the development shell"
	@echo "lint - check style with black, flake8, sort python with isort, and indent html"
	@echo "format - enforce a consistent code style across the codebase and sort python files with isort"

tags:
	ctags --recurse=yes --exclude=.git --exclude=docs --exclude=static --exclude=staticfiles

collectstatic:
	python manage.py collectstatic --noinput

clean:
	rm -rf __pycache__ .pytest_cache

check:
	python manage.py check

check-deploy:
	python manage.py check --deploy

css:
	sass static/assets/scss/softui.scss -s compressed static/assets/css/styles.min.css

shellplus:
	python manage.py shell_plus --print-sql

shell:
	python manage.py shell

showmigrations:
	python manage.py showmigrations

makemigrations:
	python manage.py makemigrations

makemessages:
	django-admin makemessages --all

compilemessages:
	django-admin compilemessages

translations: makemessages compilemessages

migrate:
	python manage.py migrate

migrations-check:
	python manage.py makemigrations --check --dry-run

runserver:
	python manage.py runserver

build: install makemigrations migrate runserver

format:
	ruff check --select I --fix
	ruff format .
	djlint --reformat .

lint:
	ruff check .
	djlint --lint .
	djlint --check .

test: check migrations-check
	coverage run --source='.' manage.py test
	coverage html

ci: format lint test

superuser:
	python manage.py createsuperuser

status:
	@echo "Nginx"
	@sudo systemctl status nginx

	@echo "Gunicorn Socket"
	@sudo systemctl status vpy.socket

	@echo "Gunicorn Service"
	@sudo systemctl status vpy.service


reload:
	@echo "reloading daemon..."
	@sudo systemctl daemon-reload

	@echo "🔌 restarting gunicorn socket..."
	@sudo systemctl restart vpy.socket

	@echo "🦄 restarting gunicorn service..."
	@sudo systemctl restart vpy.service

	@echo "⚙️ reloading nginx..."
	@sudo nginx -s reload

	@echo "All done! 💅💫💖"

logs:
	@sudo journalctl -fu vpy.service

# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/configure.html#configuration-file
# https://docs.gunicorn.org/en/stable/settings.html

# import multiprocessing
import gunicorn

# Replace gunicorn server http header to avoid leaking info to attackers
gunicorn.SERVER = ""

# restart workers every 1200-1250 requests
max_requests = 1200
max_requests_jitter = 50


# Bind to a unix socket (created by systemd)
bind = "unix:/run/vpy.sock"

# Define the number of workers
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1  # <-- Change this later but for testing 1 is enough

# Access log - records incoming HTTP requests
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s "%(r)s" %(s)s'

# Error log - records Gunicorn server errors
errorlog = "-"
error_log_format = '%(h)s %(l)s %(u)s "%(r)s" %(s)s'

log_file = "-"

# Whether to send Django output to the error log
capture_output = True

# How verbose the Gunicorn error logs should be
loglevel = "info"

enable_stdio_inheritance = True

# Load app-prefork to save memory and worker startup time
preload_app = True

# Timeout after 25 secs
timeout = 25

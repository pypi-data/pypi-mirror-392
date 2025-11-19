import os
import argparse
from functools import wraps
from flask import Flask, request, render_template_string, send_from_directory, Response
from werkzeug.utils import secure_filename

app = Flask(__name__)

ROOT_DIR = ''
ALLOWED_DESTINATIONS = {}
AUTH_USERNAME = None
AUTH_PASSWORD = None
ALLOWED_EXTENSIONS = None  # None means all allowed
BLOCKED_EXTENSIONS = set()  # Extensions to block


def require_auth(f):
    """Decorator to require HTTP Basic Authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if AUTH_USERNAME is None or AUTH_PASSWORD is None:
            return f(*args, **kwargs)

        auth = request.authorization

        if not auth or auth.username != AUTH_USERNAME or auth.password != AUTH_PASSWORD:
            return Response(
                'Authentication required. Please provide valid credentials.',
                401,
                {'WWW-Authenticate': 'Basic realm="flexup - Login Required"'}
            )

        return f(*args, **kwargs)
    return decorated


def is_allowed_file(filename):
    """Check if file extension is allowed based on configuration."""
    if not filename or '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()

    if ext in BLOCKED_EXTENSIONS:
        return False

    if ALLOWED_EXTENSIONS is not None:
        return ext in ALLOWED_EXTENSIONS

    return True

@app.route('/upload', methods=['GET', 'POST'])
@require_auth
def upload_page():
    if request.method == 'POST':
        files = request.files.getlist('files')
        default_key = list(ALLOWED_DESTINATIONS.keys())[0] if ALLOWED_DESTINATIONS else None
        dest_key = request.form.get('destination_key', default_key)

        dest_dir = ALLOWED_DESTINATIONS.get(dest_key)

        if not files or not dest_dir:
            return 'Invalid request', 400

        uploaded = []
        errors = []

        for file in files:
            if not file or file.filename == '':
                continue

            if not is_allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'none'
                errors.append(f'{file.filename}: File type not allowed (.{ext})')
                continue

            filename = secure_filename(file.filename)

            if not filename:
                errors.append(f'{file.filename}: Invalid filename after sanitization')
                continue

            final_path = os.path.join(dest_dir, filename)

            try:
                file.save(final_path)
                uploaded.append(filename)
            except Exception as e:
                errors.append(f'{filename}: {str(e)}')

        if not uploaded:
            if errors:
                return '\n'.join(errors), 400
            return 'No valid files to upload', 400

        # Return 204 No Content on success (matches uploadserver behavior)
        return '', 204

    HTML_FORM = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload File</title>
    </head>
    <body>
        <h2>Upload File</h2>
        <form method="POST" enctype="multipart/form-data" action="/upload">
          <div>
            <label for="dest">Destination:</label>
            <select name="destination_key">
              {% for key in destinations %}
              <option value="{{ key }}">{{ key }}</option>
              {% endfor %}
            </select>
          </div>
          <br />
          <div>
            <label for="files">File(s):</label>
            <input type="file" name="files" multiple />
          </div>
          <br />
          <button type="submit">Upload</button>
        </form>
        <hr>
        <p><a href="/">Back to file index</a></p>
    </body>
    </html>
    """
    return render_template_string(HTML_FORM, destinations=ALLOWED_DESTINATIONS.keys())

@app.route('/')
@app.route('/<path:path>')
@require_auth
def serve_files(path=''):
    """Serve files or directory listing."""
    full_path = os.path.join(ROOT_DIR, path)

    # Security: prevent directory traversal
    if not os.path.abspath(full_path).startswith(os.path.abspath(ROOT_DIR)):
        return 'Access denied', 403

    if os.path.isfile(full_path):
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)

    if os.path.isdir(full_path):
        try:
            items = os.listdir(full_path)
            items.sort()

            current_path = '/' + path if path else '/'
            parent_path = '/' + os.path.dirname(path) if path else None

            file_items = []
            for item in items:
                item_path = os.path.join(full_path, item)
                relative_path = os.path.join(path, item) if path else item

                item_data = {
                    'name': item,
                    'url': '/' + relative_path,
                    'is_dir': os.path.isdir(item_path)
                }

                if not item_data['is_dir']:
                    file_size = os.path.getsize(item_path)
                    item_data['size'] = format_size(file_size)

                file_items.append(item_data)

            HTML_LISTING = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Index of {{ current_path }}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }
                    ul { list-style: none; padding: 0; }
                    li { padding: 8px; border-bottom: 1px solid #eee; }
                    li:hover { background-color: #f5f5f5; }
                    a { text-decoration: none; color: #0066cc; }
                    a:hover { text-decoration: underline; }
                    .upload-link { margin-top: 20px; padding: 10px; background-color: #4CAF50; color: white;
                                    display: inline-block; border-radius: 4px; text-decoration: none; }
                    .upload-link:hover { background-color: #45a049; }
                </style>
            </head>
            <body>
                <h1>Index of {{ current_path }}</h1>
                <ul>
                    {% if parent_path is not none %}
                    <li><a href="{{ parent_path }}">..</a></li>
                    {% endif %}
                    {% for item in items %}
                    <li>
                        <a href="{{ item.url }}">{{ item.name }}{% if item.is_dir %}/{% endif %}</a>
                        {% if not item.is_dir %}
                        <span style="color: #666;">({{ item.size }})</span>
                        {% endif %}
                    </li>
                    {% endfor %}
                </ul>
                <a href="/upload" class="upload-link">Upload Files</a>
            </body>
            </html>
            """
            return render_template_string(HTML_LISTING, current_path=current_path, parent_path=parent_path, items=file_items)
        except PermissionError:
            return 'Permission denied', 403

    return 'Not found', 404


def format_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def main():
    parser = argparse.ArgumentParser(description='Simple file server with whitelisted upload destinations.')
    parser.add_argument(
        '-D', '--directory',
        default='.',
        help='Root directory to serve files from and base uploads on. [default: current directory]'
    )
    parser.add_argument(
        '-d', '--dest',
        action='append',
        dest='destinations',
        help='Define an allowed upload destination relative to the root directory. Format: key=rel_path (e.g., -d images=uploads/pics)'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host address to bind to. [default: 0.0.0.0 (all interfaces)]'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run the server on.'
    )
    parser.add_argument(
        '--basic-auth',
        help='Enable HTTP Basic Authentication. Format: username:password (e.g., --basic-auth admin:secret123)'
    )
    parser.add_argument(
        '--allow-exts',
        help='Comma-separated list of allowed file extensions (e.g., --allow-exts txt,pdf,jpg). If not specified, all extensions are allowed except blocked ones.'
    )
    parser.add_argument(
        '--block-exts',
        default='exe,sh,bat,cmd,com,pif,scr,vbs,js,jar,app,deb,rpm',
        help='Comma-separated list of blocked file extensions. Default blocks dangerous executable types.'
    )
    args = parser.parse_args()

    global ROOT_DIR, ALLOWED_DESTINATIONS, AUTH_USERNAME, AUTH_PASSWORD, ALLOWED_EXTENSIONS, BLOCKED_EXTENSIONS, app

    ROOT_DIR = os.path.abspath(args.directory)
    ALLOWED_DESTINATIONS = {}

    if args.basic_auth:
        if ':' in args.basic_auth:
            AUTH_USERNAME, AUTH_PASSWORD = args.basic_auth.split(':', 1)
        else:
            print("! Warning: --basic-auth format should be username:password")
            print("! Authentication disabled due to invalid format")
            AUTH_USERNAME = None
            AUTH_PASSWORD = None
    else:
        AUTH_USERNAME = None
        AUTH_PASSWORD = None

    if args.allow_exts:
        ALLOWED_EXTENSIONS = set(ext.strip().lower() for ext in args.allow_exts.split(','))
    else:
        ALLOWED_EXTENSIONS = None

    if args.block_exts:
        BLOCKED_EXTENSIONS = set(ext.strip().lower() for ext in args.block_exts.split(','))
    else:
        BLOCKED_EXTENSIONS = set()

    dest_list = args.destinations if args.destinations else ['default=.']

    for arg in dest_list:
        parts = arg.split('=', 1)
        if len(parts) == 2:
            key, user_rel_path = parts

            normalized_path = os.path.normpath(user_rel_path)

            if normalized_path.startswith('..') or '/..' in normalized_path or '\\..' in normalized_path:
                print(f"! Skipping invalid upload path (traversal attempt): {arg}")
                continue

            safe_rel_path = normalized_path.lstrip('./\\')
            abs_upload_path = os.path.join(ROOT_DIR, safe_rel_path)

            if not os.path.abspath(abs_upload_path).startswith(os.path.abspath(ROOT_DIR)):
                print(f"! Skipping invalid upload path (outside root): {arg}")
                continue

            ALLOWED_DESTINATIONS[key] = abs_upload_path
        else:
            print(f"! Ignoring malformed destination argument: {arg}")

    for dir_path in ALLOWED_DESTINATIONS.values():
        os.makedirs(dir_path, exist_ok=True)

    print(f"\n* Serving files from: {ROOT_DIR}")
    print(f"* Upload page available at: http://{args.host}:{args.port}/upload")

    if AUTH_USERNAME and AUTH_PASSWORD:
        print(f"* Authentication: ENABLED (user: {AUTH_USERNAME})")
    else:
        print("* Authentication: DISABLED (public access)")

    if ALLOWED_EXTENSIONS:
        print(f"* File type whitelist: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    elif BLOCKED_EXTENSIONS:
        print(f"* File type blacklist: {', '.join(sorted(BLOCKED_EXTENSIONS))}")
    else:
        print("* File type restrictions: NONE (all types allowed)")

    print("* Allowed upload destinations:")
    for key, path in ALLOWED_DESTINATIONS.items():
        print(f"    {key}: {path}")

    app.run(host=args.host, port=args.port)

if __name__ == '__main__':
    main()
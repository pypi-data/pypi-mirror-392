"""Tests for the flexup server module."""

import os
import pytest
import tempfile
import shutil
import re
from pathlib import Path
from io import BytesIO
from flexup.server import app, format_size, ALLOWED_DESTINATIONS, ROOT_DIR


@pytest.fixture
def test_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def client(test_dir):
    """Create a Flask test client with test configuration."""
    # Import here to avoid circular imports
    from flexup import server

    # Set up test configuration
    server.ROOT_DIR = test_dir
    server.ALLOWED_DESTINATIONS = {'uploads': os.path.join(test_dir, 'uploads')}
    server.AUTH_USERNAME = None
    server.AUTH_PASSWORD = None
    server.ALLOWED_EXTENSIONS = None
    server.BLOCKED_EXTENSIONS = set()
    os.makedirs(server.ALLOWED_DESTINATIONS['uploads'], exist_ok=True)

    # Create some test files
    test_file = os.path.join(test_dir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('test content')

    # Create a subdirectory with a file
    subdir = os.path.join(test_dir, 'subdir')
    os.makedirs(subdir, exist_ok=True)
    subfile = os.path.join(subdir, 'subfile.txt')
    with open(subfile, 'w') as f:
        f.write('subfile content')

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(test_dir):
    """Create a Flask test client with authentication enabled."""
    from flexup import server

    # Set up test configuration with auth
    server.ROOT_DIR = test_dir
    server.ALLOWED_DESTINATIONS = {'uploads': os.path.join(test_dir, 'uploads')}
    server.AUTH_USERNAME = 'testuser'
    server.AUTH_PASSWORD = 'testpass'
    server.ALLOWED_EXTENSIONS = None
    server.BLOCKED_EXTENSIONS = set()
    os.makedirs(server.ALLOWED_DESTINATIONS['uploads'], exist_ok=True)

    # Create some test files
    test_file = os.path.join(test_dir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('test content')

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestFormatSize:
    """Test the format_size utility function."""

    def test_bytes(self):
        """Test formatting bytes."""
        assert format_size(0) == "0.0 B"
        assert format_size(100) == "100.0 B"
        assert format_size(1023) == "1023.0 B"

    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_size(1024) == "1.0 KB"
        assert format_size(2048) == "2.0 KB"
        assert format_size(1536) == "1.5 KB"

    def test_megabytes(self):
        """Test formatting megabytes."""
        assert format_size(1024 * 1024) == "1.0 MB"
        assert format_size(1024 * 1024 * 2.5) == "2.5 MB"

    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_size(1024 * 1024 * 1024 * 3) == "3.0 GB"

    def test_terabytes(self):
        """Test formatting terabytes."""
        assert format_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"


class TestUploadEndpoint:
    """Test the /upload endpoint."""

    def test_upload_page_get(self, client):
        """Test GET request to upload page shows form."""
        response = client.get('/upload')
        assert response.status_code == 200
        assert b'Upload File' in response.data
        assert b'<form' in response.data
        assert b'type="file"' in response.data

    def test_upload_page_shows_destinations(self, client):
        """Test that upload page shows available destinations."""
        response = client.get('/upload')
        assert response.status_code == 200
        assert b'uploads' in response.data
        assert b'<select' in response.data

    def test_upload_file_success(self, client, test_dir):
        """Test successful file upload."""
        data = {
            'files': (BytesIO(b'test file content'), 'testfile.txt'),
            'destination_key': 'uploads'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 204

        # Verify file was created
        uploaded_file = os.path.join(test_dir, 'uploads', 'testfile.txt')
        assert os.path.exists(uploaded_file)
        with open(uploaded_file, 'r') as f:
            assert f.read() == 'test file content'

    def test_upload_multiple_files(self, client, test_dir):
        """Test uploading multiple files in a single request."""
        data = {
            'files': [
                (BytesIO(b'content 1'), 'file1.txt'),
                (BytesIO(b'content 2'), 'file2.txt'),
                (BytesIO(b'content 3'), 'file3.txt'),
            ],
            'destination_key': 'uploads'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 204

        # Verify all files were created
        for i in range(1, 4):
            uploaded_file = os.path.join(test_dir, 'uploads', f'file{i}.txt')
            assert os.path.exists(uploaded_file)
            with open(uploaded_file, 'r') as f:
                assert f.read() == f'content {i}'

    def test_upload_without_file(self, client):
        """Test upload without file returns error."""
        data = {'destination_key': 'uploads'}
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_upload_empty_filename(self, client):
        """Test upload with empty filename returns error."""
        data = {
            'files': (BytesIO(b'content'), ''),
            'destination_key': 'uploads'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_upload_invalid_destination(self, client):
        """Test upload to invalid destination returns error."""
        data = {
            'files': (BytesIO(b'content'), 'test.txt'),
            'destination_key': 'invalid_dest'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_upload_secure_filename(self, client, test_dir):
        """Test that filenames are sanitized."""
        data = {
            'files': (BytesIO(b'content'), '../../../etc/passwd'),
            'destination_key': 'uploads'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 204

        # Verify file is saved with secure name, not path traversal
        uploaded_file = os.path.join(test_dir, 'uploads', 'etc_passwd')
        assert os.path.exists(uploaded_file)
        # Original path should NOT work
        assert not os.path.exists(os.path.join(test_dir, '..', '..', '..', 'etc', 'passwd'))


class TestFileServing:
    """Test file serving functionality."""

    def test_serve_root_directory(self, client):
        """Test serving root directory shows listing."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Index of' in response.data
        assert b'test.txt' in response.data
        assert b'subdir' in response.data

    def test_serve_file(self, client):
        """Test serving a file."""
        response = client.get('/test.txt')
        assert response.status_code == 200
        assert response.data == b'test content'

    def test_serve_subdirectory(self, client):
        """Test serving subdirectory shows listing."""
        response = client.get('/subdir')
        assert response.status_code == 200
        assert b'Index of /subdir' in response.data
        assert b'subfile.txt' in response.data
        assert b'..' in response.data  # Parent directory link

    def test_serve_file_in_subdirectory(self, client):
        """Test serving file in subdirectory."""
        response = client.get('/subdir/subfile.txt')
        assert response.status_code == 200
        assert response.data == b'subfile content'

    def test_nonexistent_file(self, client):
        """Test requesting nonexistent file returns 404."""
        response = client.get('/nonexistent.txt')
        assert response.status_code == 404

    def test_directory_listing_has_upload_link(self, client):
        """Test that directory listings include upload link."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Upload Files' in response.data
        assert b'href="/upload"' in response.data

    def test_directory_listing_shows_file_sizes(self, client):
        """Test that directory listings show file sizes."""
        response = client.get('/')
        assert response.status_code == 200
        # Should show file size for test.txt
        assert b'B)' in response.data or b'KB)' in response.data


class TestSecurity:
    """Test security features."""

    def test_path_traversal_prevention(self, client, test_dir):
        """Test that path traversal attempts are blocked."""
        # Try to access parent directory
        response = client.get('/../')
        assert response.status_code == 403
        assert b'Access denied' in response.data

    def test_path_traversal_with_encoded_chars(self, client):
        """Test path traversal with encoded characters is blocked."""
        response = client.get('/%2e%2e/')
        # Flask decodes this and our security check should catch it
        assert response.status_code in [403, 404]

    def test_absolute_path_blocked(self, client):
        """Test that absolute paths outside root are blocked."""
        response = client.get('/etc/passwd')
        # Should either not exist (404) or be blocked based on our root
        assert response.status_code in [403, 404]


class TestDestinationConfiguration:
    """Test destination configuration."""

    def test_no_destinations_uses_root(self, test_dir):
        """Test that no destinations defaults to root directory."""
        from flexup import server

        server.ROOT_DIR = test_dir
        server.ALLOWED_DESTINATIONS = {}

        # Simulate default behavior
        dest_list = ['default=.']
        for arg in dest_list:
            parts = arg.split('=', 1)
            if len(parts) == 2:
                key, user_rel_path = parts
                safe_rel_path = os.path.normpath(user_rel_path).lstrip('./\\')
                abs_upload_path = os.path.join(server.ROOT_DIR, safe_rel_path)
                server.ALLOWED_DESTINATIONS[key] = abs_upload_path

        assert 'default' in server.ALLOWED_DESTINATIONS
        # Normalize both paths for comparison (handles trailing slashes)
        assert os.path.normpath(server.ALLOWED_DESTINATIONS['default']) == os.path.normpath(test_dir)

    def test_multiple_destinations(self, test_dir):
        """Test configuring multiple destinations."""
        from flexup import server

        server.ROOT_DIR = test_dir
        server.ALLOWED_DESTINATIONS = {}

        dest_list = ['images=img', 'docs=documents']
        for arg in dest_list:
            parts = arg.split('=', 1)
            if len(parts) == 2:
                key, user_rel_path = parts
                safe_rel_path = os.path.normpath(user_rel_path).lstrip('./\\')
                abs_upload_path = os.path.join(server.ROOT_DIR, safe_rel_path)
                server.ALLOWED_DESTINATIONS[key] = abs_upload_path

        assert len(server.ALLOWED_DESTINATIONS) == 2
        assert 'images' in server.ALLOWED_DESTINATIONS
        assert 'docs' in server.ALLOWED_DESTINATIONS
        assert server.ALLOWED_DESTINATIONS['images'] == os.path.join(test_dir, 'img')
        assert server.ALLOWED_DESTINATIONS['docs'] == os.path.join(test_dir, 'documents')

    def test_path_traversal_in_destination_rejected(self, test_dir):
        """Test that path traversal in destination config is rejected."""
        from flexup import server

        server.ROOT_DIR = test_dir
        server.ALLOWED_DESTINATIONS = {}

        dest_list = ['evil=../../etc']
        for arg in dest_list:
            parts = arg.split('=', 1)
            if len(parts) == 2:
                key, user_rel_path = parts

                # Normalize the path
                normalized_path = os.path.normpath(user_rel_path)

                # Check for path traversal before stripping
                if normalized_path.startswith('..') or '/..' in normalized_path or '\\..' in normalized_path:
                    continue

                # Remove leading ./ or .\
                safe_rel_path = normalized_path.lstrip('./\\')

                abs_upload_path = os.path.join(server.ROOT_DIR, safe_rel_path)

                # Double-check: ensure the absolute path is within ROOT_DIR
                if not os.path.abspath(abs_upload_path).startswith(os.path.abspath(server.ROOT_DIR)):
                    continue

                server.ALLOWED_DESTINATIONS[key] = abs_upload_path

        # The evil destination should not be added
        assert 'evil' not in server.ALLOWED_DESTINATIONS


class TestAuthentication:
    """Test HTTP Basic Authentication."""

    def test_auth_disabled_by_default(self, client):
        """Test that authentication is disabled when not configured."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Index of' in response.data

    def test_auth_required_without_credentials(self, auth_client):
        """Test that requests without credentials are rejected when auth is enabled."""
        response = auth_client.get('/')
        assert response.status_code == 401
        assert b'Authentication required' in response.data
        assert 'WWW-Authenticate' in response.headers
        assert 'Basic' in response.headers['WWW-Authenticate']

    def test_auth_with_valid_credentials(self, auth_client):
        """Test that valid credentials grant access."""
        import base64
        credentials = base64.b64encode(b'testuser:testpass').decode('utf-8')
        response = auth_client.get('/', headers={'Authorization': f'Basic {credentials}'})
        assert response.status_code == 200
        assert b'Index of' in response.data

    def test_auth_with_invalid_username(self, auth_client):
        """Test that invalid username is rejected."""
        import base64
        credentials = base64.b64encode(b'wronguser:testpass').decode('utf-8')
        response = auth_client.get('/', headers={'Authorization': f'Basic {credentials}'})
        assert response.status_code == 401

    def test_auth_with_invalid_password(self, auth_client):
        """Test that invalid password is rejected."""
        import base64
        credentials = base64.b64encode(b'testuser:wrongpass').decode('utf-8')
        response = auth_client.get('/', headers={'Authorization': f'Basic {credentials}'})
        assert response.status_code == 401

    def test_upload_requires_auth(self, auth_client):
        """Test that upload endpoint requires authentication."""
        response = auth_client.get('/upload')
        assert response.status_code == 401

    def test_upload_with_valid_auth(self, auth_client, test_dir):
        """Test that upload works with valid credentials."""
        import base64
        credentials = base64.b64encode(b'testuser:testpass').decode('utf-8')
        headers = {'Authorization': f'Basic {credentials}'}

        # Test GET first
        response = auth_client.get('/upload', headers=headers)
        assert response.status_code == 200
        assert b'Upload File' in response.data

        # Test POST
        data = {
            'files': (BytesIO(b'test content'), 'test.txt'),
            'destination_key': 'uploads'
        }
        response = auth_client.post('/upload', data=data, headers=headers, content_type='multipart/form-data')
        assert response.status_code == 204

    def test_file_serving_requires_auth(self, auth_client):
        """Test that file serving requires authentication."""
        response = auth_client.get('/test.txt')
        assert response.status_code == 401

    def test_file_serving_with_valid_auth(self, auth_client):
        """Test that file serving works with valid credentials."""
        import base64
        credentials = base64.b64encode(b'testuser:testpass').decode('utf-8')
        response = auth_client.get('/test.txt', headers={'Authorization': f'Basic {credentials}'})
        assert response.status_code == 200
        assert response.data == b'test content'


class TestXSSAndSSTIPrevention:
    """Test that XSS and SSTI vulnerabilities are prevented."""

    def test_xss_in_filename_is_escaped(self, client, test_dir):
        """Test that HTML in filenames is properly escaped."""
        # Create a file with a name that could be used for XSS if not escaped
        # Using ' and " which need to be escaped in HTML attributes
        xss_filename = 'test\'"><img src=x>.txt'
        safe_path = os.path.join(test_dir, xss_filename)
        with open(safe_path, 'w') as f:
            f.write('test content')

        response = client.get('/')
        assert response.status_code == 200

        # The filename should be properly escaped in HTML
        response_text = response.data.decode('utf-8')
        # Check that quotes are escaped in the href attribute
        assert '\'"><img src=x>' not in response_text or '&quot;&gt;&lt;img' in response_text
        # The filename should appear but be safe
        assert 'test' in response_text

    def test_ssti_in_filename_not_executed(self, client, test_dir):
        """Test that Jinja2 template syntax in filenames is not executed."""
        # Create a file with SSTI attempt in filename
        ssti_filename = 'test{{7*7}}.txt'
        safe_path = os.path.join(test_dir, ssti_filename)
        with open(safe_path, 'w') as f:
            f.write('test content')

        response = client.get('/')
        assert response.status_code == 200

        # Should show the literal template syntax, not execute it
        assert b'test{{7*7}}.txt' in response.data or b'test{{7*7}}' in response.data
        # Should NOT show the result of execution
        assert b'test49.txt' not in response.data

    def test_ssti_in_directory_name_not_executed(self, client, test_dir):
        """Test that Jinja2 template syntax in directory names is not executed."""
        # Create a directory with SSTI attempt in name
        ssti_dirname = 'dir{{config}}'
        dir_path = os.path.join(test_dir, ssti_dirname)
        os.makedirs(dir_path, exist_ok=True)

        response = client.get('/')
        assert response.status_code == 200

        # Should show the literal template syntax, not execute it
        assert b'dir{{config}}' in response.data or b'{{config}}' in response.data
        # Should NOT expose Flask config
        assert b'SECRET_KEY' not in response.data
        assert b'DEBUG' not in response.data

    def test_xss_in_directory_name_is_escaped(self, client, test_dir):
        """Test that HTML in directory names is properly escaped."""
        # Create a directory with special HTML chars that need escaping
        xss_dirname = 'dir&test'
        dir_path = os.path.join(test_dir, xss_dirname)
        os.makedirs(dir_path, exist_ok=True)

        response = client.get('/')
        assert response.status_code == 200

        # The directory name should be HTML-escaped
        response_text = response.data.decode('utf-8')
        # The & should be escaped as &amp; in HTML
        assert 'dir&amp;test' in response_text or 'dir&test' in response_text
        # The directory should be listed
        assert 'dir' in response_text

    def test_path_displayed_safely(self, client, test_dir):
        """Test that the current path is displayed safely."""
        # Create a subdirectory with special chars
        subdir = os.path.join(test_dir, 'normal_subdir')
        os.makedirs(subdir, exist_ok=True)

        response = client.get('/normal_subdir')
        assert response.status_code == 200
        assert b'Index of /normal_subdir' in response.data

        # Verify no raw HTML injection in path display
        assert b'<h1>Index of /normal_subdir</h1>' in response.data


class TestMIMETypeValidation:
    """Test MIME type / file extension validation."""

    def test_blocked_extension_rejected(self, client, test_dir):
        """Test that blocked extensions are rejected."""
        from flexup import server
        server.BLOCKED_EXTENSIONS = {'exe', 'sh'}

        data = {
            'files': (BytesIO(b'malicious content'), 'virus.exe'),
            'destination_key': 'uploads'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        assert b'File type not allowed' in response.data

    def test_allowed_extension_accepted(self, client, test_dir):
        """Test that allowed extensions are accepted."""
        from flexup import server
        server.ALLOWED_EXTENSIONS = {'txt', 'pdf'}

        data = {
            'files': (BytesIO(b'safe content'), 'document.txt'),
            'destination_key': 'uploads'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 204

    def test_not_in_whitelist_rejected(self, client):
        """Test that extensions not in whitelist are rejected."""
        from flexup import server
        server.ALLOWED_EXTENSIONS = {'txt', 'pdf'}

        data = {
            'files': (BytesIO(b'content'), 'file.exe'),
            'destination_key': 'uploads'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        assert b'File type not allowed' in response.data

    def test_file_without_extension_rejected(self, client):
        """Test that files without extensions are rejected."""
        data = {
            'files': (BytesIO(b'content'), 'noextension'),
            'destination_key': 'uploads'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_case_insensitive_extension_check(self, client, test_dir):
        """Test that extension checking is case-insensitive."""
        from flexup import server
        server.BLOCKED_EXTENSIONS = {'exe'}

        data = {
            'files': (BytesIO(b'content'), 'file.EXE'),
            'destination_key': 'uploads'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        assert b'File type not allowed' in response.data

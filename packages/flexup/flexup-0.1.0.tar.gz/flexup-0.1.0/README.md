# flexup

A flexible file upload server with Flask that provides predefined upload destinations.

Similar to [uploadserver](https://github.com/Densaugeo/uploadserver), but built with Flask and allows you to configure multiple named upload destinations that clients can choose from.

## Features

- File serving with directory browsing
- Web-based file upload interface
- Multiple predefined upload destinations
- Secure filename handling and path traversal prevention
- HTTP Basic Authentication support
- File type validation (whitelist/blacklist)
- Human-readable file sizes in listings
- Command-line interface

## Installation

```bash
pip install flexup
```

## Usage

### Basic usage (uploads to root directory):

```bash
flexup
```

### Specify a custom directory:

```bash
flexup -D /path/to/serve
```

### Define multiple upload destinations:

```bash
flexup -d images=uploads/images -d docs=uploads/documents -d videos=uploads/videos
```

### Custom port:

```bash
flexup --port 8080
```

### With authentication and security:

```bash
flexup -D /var/www \
  --basic-auth admin:secret123 \
  --allow-exts txt,pdf,jpg,png \
  --host 127.0.0.1 \
  --port 8080
```

This will:
- Serve files from `/var/www`
- Require authentication (username: admin, password: secret123)
- Only allow specific file types
- Bind to localhost only
- Run on port 8080

## Command-Line Options

```
-D, --directory    Root directory to serve files from [default: current directory]
-d, --dest         Define upload destination: key=path (can be used multiple times)
--host             Host address to bind to [default: 0.0.0.0 (all interfaces)]
--port             Port to run the server on [default: 5000]
--basic-auth       Enable HTTP Basic Auth: username:password
--allow-exts       Comma-separated list of allowed file extensions (whitelist)
--block-exts       Comma-separated list of blocked file extensions (blacklist)
                   [default blocks: exe,sh,bat,cmd,com,pif,scr,vbs,js,jar,app,deb,rpm]
```

### Security Options

**Authentication:**
```bash
flexup --basic-auth admin:secret123
```

**Bind to localhost only:**
```bash
flexup --host 127.0.0.1
```

**File type whitelist (most secure):**
```bash
flexup --allow-exts txt,pdf,jpg,png,gif
```

**File type blacklist (block executables):**
```bash
flexup --block-exts exe,sh,bat,js
```

**Disable default blocklist (not recommended):**
```bash
flexup --block-exts ""
```

## Web Interface

Once running, access:
- `http://localhost:5000/` - Browse and download files
- `http://localhost:5000/upload` - Upload files to predefined destinations

## Uploading with curl

### Single File Upload

```bash
curl -X POST http://localhost:5000/upload -F "files=@filename.txt"
```

### Multiple Files Upload

Upload multiple files in a single request:
```bash
curl -X POST http://localhost:5000/upload \
  -F "files=@file1.txt" \
  -F "files=@file2.txt" \
  -F "files=@file3.txt"
```

### With Authentication

```bash
curl -X POST http://localhost:5000/upload \
  -u admin:secret123 \
  -F "files=@document.pdf"
```

### Upload to Specific Destination

If you configured destinations:
```bash
flexup -d images=uploads/img -d docs=uploads/documents
```

Upload to specific destination:
```bash
# Single file to images
curl -X POST http://localhost:5000/upload \
  -F "files=@photo.jpg" \
  -F "destination_key=images"

# Multiple files to docs
curl -X POST http://localhost:5000/upload \
  -F "files=@report.pdf" \
  -F "files=@summary.pdf" \
  -F "destination_key=docs"
```

### Bulk Upload

Upload all files in current directory:
```bash
curl -X POST http://localhost:5000/upload \
  $(for f in *.txt; do echo "-F files=@$f"; done)
```

**Note:** Successful uploads return **204 No Content** (matching uploadserver behavior)

## Development

### Setup

Clone the repository and install development dependencies:

```bash
git clone https://github.com/dyay108/flexup.git
cd flexup
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src tests
```

### Type Checking

```bash
mypy src
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

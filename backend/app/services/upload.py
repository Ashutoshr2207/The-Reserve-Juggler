"""Stream exactly one untrusted multipart CSV into a bounded local temporary file."""
import os
import re
import tempfile
from pathlib import Path

from python_multipart.multipart import MultipartParser, parse_options_header

from app.api.contracts import Problem
from app.domain.intake import MAX_UPLOAD, fail


async def receive_csv(request, temporary_root):
    media, options = parse_options_header(request.headers.get('content-type', ''))
    boundary = options.get(b'boundary')
    if media != b'multipart/form-data' or not boundary or len(boundary) > 200:
        fail('file', 'Expected multipart/form-data with one CSV file.')
    directory = Path(temporary_root)
    directory.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(dir=directory, suffix='.upload', delete=False)
    path = Path(handle.name)
    state = {'parts': 0, 'field': bytearray(), 'value': bytearray(), 'headers': {},
             'header_bytes': 0, 'size': 0, 'ready': False, 'ended': False}

    def begin():
        state['parts'] += 1
        if state['parts'] != 1:
            fail('file', 'Exactly one file part is allowed.')

    def header_field(data, start, end):
        state['header_bytes'] += end-start
        if state['header_bytes'] > 4096:
            fail('file', 'Multipart headers exceed the limit.')
        state['field'].extend(data[start:end])

    def header_value(data, start, end):
        state['header_bytes'] += end-start
        if state['header_bytes'] > 4096:
            fail('file', 'Multipart headers exceed the limit.')
        state['value'].extend(data[start:end])

    def header_end():
        field = bytes(state['field']).lower()
        if field in state['headers']:
            fail('file', 'Duplicate multipart header.')
        state['headers'][field] = bytes(state['value'])
        state['field'].clear()
        state['value'].clear()

    def headers_finished():
        disposition = state['headers'].get(b'content-disposition', b'')
        # The MIME helper strips legacy Windows paths. Reject the raw path first.
        raw_name = re.search(br'filename\s*=\s*"([^"]*)"', disposition, re.I)
        if raw_name and any(c in raw_name[1] for c in (b'/', b'\\', b':', b'\x00')):
            fail('file', 'Unsafe source filename.')
        kind, params = parse_options_header(disposition)
        name = params.get(b'filename', b'')
        if kind != b'form-data' or params.get(b'name') != b'file' or not name.lower().endswith(b'.csv'):
            fail('file', 'Expected the file field with a CSV filename.')
        if len(name) > 255 or any(c in name for c in (b'/', b'\\', b':', b'\x00')) or name.startswith(b'.'):
            fail('file', 'Unsafe source filename.')
        state['ready'] = True

    def part_data(data, start, end):
        if not state['ready']:
            fail('file', 'Missing file headers.')
        state['size'] += end-start
        if state['size'] > MAX_UPLOAD:
            fail('file', 'CSV exceeds 5 MiB.')
        handle.write(data[start:end])

    def finished():
        state['ended'] = True

    try:
        parser = MultipartParser(boundary, {
            'on_part_begin': begin, 'on_header_field': header_field,
            'on_header_value': header_value, 'on_header_end': header_end,
            'on_headers_finished': headers_finished, 'on_part_data': part_data,
            'on_end': finished,
        })
        received = 0
        async for chunk in request.stream():
            received += len(chunk)
            if received > MAX_UPLOAD + 65536:
                fail('file', 'Multipart request exceeds the upload limit.')
            parser.write(chunk)
        parser.finalize()
        if not state['ended'] or state['parts'] != 1 or not state['size']:
            fail('file', 'Incomplete or empty CSV upload.')
        handle.flush()
        os.fsync(handle.fileno())
        handle.close()
        return path
    except BaseException as exc:
        handle.close()
        path.unlink(missing_ok=True)
        if isinstance(exc, Problem) or not isinstance(exc, Exception):
            raise
        fail('file', 'Malformed multipart upload.')

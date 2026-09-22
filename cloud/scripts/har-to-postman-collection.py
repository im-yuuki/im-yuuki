#!/usr/bin/env python3
"""Convert the only HAR in a workspace to a Postman Collection v2.1 file.

The conversion is entirely local. Request URLs, headers, cookies, and bodies may
contain secrets, so the output is written with owner-only permissions.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import uuid
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


POSTMAN_SCHEMA = (
    "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
)


def find_only_har(workspace: Path) -> Path:
    har_files = sorted(path for path in workspace.rglob("*.har") if path.is_file())
    if len(har_files) != 1:
        raise ValueError(
            f"expected exactly one .har file under {workspace}, found {len(har_files)}"
        )
    return har_files[0]


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def convert_headers(request: dict[str, Any]) -> list[dict[str, str]]:
    headers = []
    header_names = set()
    for header in request.get("headers") or []:
        name = as_text(header.get("name"))
        if not name:
            continue
        headers.append({"key": name, "value": as_text(header.get("value")), "type": "text"})
        header_names.add(name.lower())

    cookies = request.get("cookies") or []
    if cookies and "cookie" not in header_names:
        cookie_value = "; ".join(
            f"{as_text(cookie.get('name'))}={as_text(cookie.get('value'))}"
            for cookie in cookies
            if cookie.get("name") is not None
        )
        if cookie_value:
            headers.append({"key": "Cookie", "value": cookie_value, "type": "text"})
    return headers


def convert_form_params(params: list[dict[str, Any]]) -> list[dict[str, str]]:
    converted = []
    for param in params:
        name = as_text(param.get("name"))
        if not name:
            continue
        item = {
            "key": name,
            "value": as_text(param.get("value")),
            "type": "text",
        }
        if param.get("contentType"):
            item["contentType"] = as_text(param["contentType"])
        converted.append(item)
    return converted


def convert_body(request: dict[str, Any]) -> dict[str, Any] | None:
    post_data = request.get("postData")
    if not isinstance(post_data, dict):
        return None

    mime_type = as_text(post_data.get("mimeType")).lower()
    params = post_data.get("params") or []
    text = as_text(post_data.get("text"))

    if "application/x-www-form-urlencoded" in mime_type:
        if params:
            values = convert_form_params(params)
        else:
            values = [
                {"key": key, "value": value, "type": "text"}
                for key, value in parse_qsl(text, keep_blank_values=True)
            ]
        return {"mode": "urlencoded", "urlencoded": values}

    if "multipart/form-data" in mime_type and params:
        return {"mode": "formdata", "formdata": convert_form_params(params)}

    body: dict[str, Any] = {"mode": "raw", "raw": text}
    language = None
    if "json" in mime_type:
        language = "json"
    elif "xml" in mime_type:
        language = "xml"
    elif "html" in mime_type:
        language = "html"
    elif "javascript" in mime_type:
        language = "javascript"
    if language:
        body["options"] = {"raw": {"language": language}}
    return body


def request_url(request: dict[str, Any]) -> str:
    raw_url = as_text(request.get("url"))
    if not raw_url:
        raise ValueError("request is missing its URL")

    parsed = urlsplit(raw_url)
    query_items = request.get("queryString") or []
    if not parsed.query and query_items:
        query = urlencode(
            [
                (as_text(item.get("name")), as_text(item.get("value")))
                for item in query_items
                if item.get("name") is not None
            ]
        )
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))
    return raw_url


def item_name(request: dict[str, Any], counts: Counter[str]) -> str:
    method = as_text(request.get("method") or "GET").upper()
    path = urlsplit(as_text(request.get("url"))).path or "/"
    base_name = f"{method} {path}"
    counts[base_name] += 1
    if counts[base_name] == 1:
        return base_name
    return f"{base_name} ({counts[base_name]})"


def endpoint_key(request: dict[str, Any]) -> tuple[str, str, str, str]:
    parsed = urlsplit(as_text(request.get("url")))
    return (
        as_text(request.get("method") or "GET").upper(),
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path or "/",
    )


def convert_har(har: dict[str, Any], collection_name: str) -> dict[str, Any]:
    log = har.get("log")
    if not isinstance(log, dict) or not isinstance(log.get("entries"), list):
        raise ValueError("input does not contain a valid HAR log.entries array")

    items = []
    names: Counter[str] = Counter()
    seen_endpoints: set[tuple[str, str, str, str]] = set()
    for index, entry in enumerate(log["entries"], start=1):
        request = entry.get("request")
        if not isinstance(request, dict):
            raise ValueError(f"HAR entry {index} does not contain a request object")

        key = endpoint_key(request)
        if key in seen_endpoints:
            continue
        seen_endpoints.add(key)

        converted_request: dict[str, Any] = {
            "method": as_text(request.get("method") or "GET").upper(),
            "header": convert_headers(request),
            "url": request_url(request),
        }
        body = convert_body(request)
        if body is not None:
            converted_request["body"] = body

        items.append(
            {
                "name": item_name(request, names),
                "request": converted_request,
                "response": [],
            }
        )

    return {
        "info": {
            "_postman_id": str(uuid.uuid4()),
            "name": collection_name,
            "schema": POSTMAN_SCHEMA,
        },
        "item": items,
    }


def private_json_dump(data: dict[str, Any], output: Path, overwrite: bool) -> None:
    output = output.resolve()
    if output.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {output}; pass --force to replace it")
    if not output.parent.is_dir():
        raise FileNotFoundError(f"output directory does not exist: {output.parent}")

    descriptor, temporary_name = tempfile.mkstemp(
        dir=output.parent, prefix=f".{output.name}.", suffix=".tmp"
    )
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, output)
        output.chmod(0o600)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a HAR file to an importable Postman Collection v2.1 file."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="HAR file (defaults to the only .har file below the current directory)",
    )
    parser.add_argument("-o", "--output", type=Path, help="output collection path")
    parser.add_argument("--name", help="Postman collection name")
    parser.add_argument("-f", "--force", action="store_true", help="replace an existing output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = (args.input or find_only_har(Path.cwd())).resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"HAR file does not exist: {input_path}")

    output_path = args.output or input_path.with_suffix(".postman_collection.json")
    collection_name = args.name or input_path.stem

    with input_path.open("r", encoding="utf-8-sig") as stream:
        har = json.load(stream)
    collection = convert_har(har, collection_name)
    private_json_dump(collection, output_path, args.force)

    print(f"Converted {len(collection['item'])} requests to {output_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

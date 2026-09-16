from flask import request

def get_pagination_params():
    try:
        limit = int(request.args.get('_limit', 10))
        if limit < 1 or limit > 100:
            limit = 10
    except (ValueError, TypeError):
        limit = 10

    try:
        offset = int(request.args.get('_offset', 0))
        if offset < 0:
            offset = 0
    except (ValueError, TypeError):
        offset = 0

    return limit, offset

def build_pagination_response(key_name, items, total, limit, offset, base_path, extra_params=None):
    if extra_params is None:
        extra_params = {}

    def make_url(off):
        params = extra_params.copy()
        params['_limit'] = limit
        params['_offset'] = off
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_path}?{query_string}"

    last_offset = max(0, ((total - 1) // limit) * limit) if total > 0 else 0

    return {
        key_name: items,
        "_links": {
            "_first": make_url(0),
            "_last": make_url(last_offset),
            "_prev": make_url(max(0, offset - limit)) if offset > 0 else None,
            "_next": make_url(offset + limit) if (offset + limit) < total else None
        }
    }

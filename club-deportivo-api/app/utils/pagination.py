from flask import request


def get_pagination_params():
    try:
        limit = int(
            request.args.get(
                '_limit',
                10,
            )
        )
    except (ValueError, TypeError):
        return None, None, "_limit debe ser un entero"

    if limit < 1 or limit > 100:
        return None, None, "_limit debe estar entre 1 y 100"

    try:
        offset = int(
            request.args.get(
                '_offset',
                0,
            )
        )
    except (ValueError, TypeError):
        return None, None, "_offset debe ser un entero"

    if offset < 0:
        return None, None, "_offset debe ser mayor o igual a 0"

    return limit, offset, None

def build_pagination_response(key_name,items,total,limit,offset,base_path,extra_params=None,):
    if extra_params is None:
        extra_params = {}

    def make_url(off):
        params = extra_params.copy()

        params["_limit"] = limit
        params["_offset"] = off

        query_string = "&".join(
            [
                f"{key}={value}"
                for key, value
                in params.items()
            ]
        )

        return (
            f"{base_path}?"
            f"{query_string}"
        )

    last_offset = max(
        0,
        ((total - 1) // limit)
        * limit,
    )

    links = {
        "_first": {
            "href": make_url(0)
        },
        "_last": {
            "href": make_url(
                last_offset
            )
        },
    }

    if offset > 0:
        links["_prev"] = {
            "href": make_url(
                max(
                    0,
                    offset - limit,
                )
            )
        }

    if offset + limit < total:
        links["_next"] = {
            "href": make_url(
                offset + limit
            )
        }

    return {
        key_name: items,
        "_links": links,
    }
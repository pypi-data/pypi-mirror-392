import rigs


def _convert(domains, map):
    for k, v in map.items():
        if k != v:
            domains[domains == k] = v


def which_domain(vertices, **params):
    domains = rigs.which_domain(vertices, root=params["domains_root"], **params)
    _convert(domains, params["domains_map"])
    return domains

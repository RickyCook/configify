#!/usr/bin/env python
from jinja2 import (BaseLoader,
                    ChoiceLoader,
                    contextfilter,
                    Environment,
                    FileSystemLoader,
                    )
from yaml import safe_load as yaml_load

class StraightThroughLoader(BaseLoader):
    def get_source(self, environment, template):
        return (template, None, lambda: True)

@contextfilter
def inline_tpl_filter(ctx, val, **kwargs):
    params = dict(ctx.get('envs')[0].items() + kwargs.items())
    return JINJA.get_template(val).render(**params)

JINJA = Environment(loader=ChoiceLoader((
    FileSystemLoader('.'),
    StraightThroughLoader(),
)))
JINJA.filters['inline_tpl'] = inline_tpl_filter

def get_conf(conf_file):
    with open(conf_file) as fh:
        return yaml_load(fh.read().decode())

def parse_params_tpls_level(params, level_idx, level):
    if level is None:
        level = params

    if isinstance(level, dict):
        for idx, val in level.iteritems():
            level[idx] = parse_params_tpls_level(params, idx, val)

    elif isinstance(level, (tuple, list)):
        for idx, val in enumerate(level):
            level[idx] = parse_params_tpls_level(params, idx, val)

    else:
        if isinstance(level_idx, str) and level_idx.startswith('$'):
            return JINJA.get_template(level).render(**params)

    return level

def parse_params_tpls(params):
    return parse_params_tpls_level(params, None, params)

def load_params_layer(params_file):
    yaml_string = JINJA.get_template(params_file).render(**G['params'])
    G['params'].update(yaml_load(yaml_string))

def load_params(params_files):
    for params_file in params_files:
        load_params_layer(params_file)

G = {
    'params': {}
}

G['conf'] = get_conf('conf.yaml')
load_params(G['conf']['params'])
G['params'] = parse_params_tpls(G['params'])

print JINJA.get_template(G['conf']['template']).render(**G['params'])

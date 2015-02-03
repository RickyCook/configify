#!/usr/bin/env python
"""
Configify generates output, based on templates, and templated context
parameters
"""

import glob
import os

import yaml

from jinja2 import (BaseLoader,
                    ChoiceLoader,
                    contextfilter,
                    Environment,
                    FileSystemLoader)
from yaml import safe_load as yaml_load


DEFAULT_CONFIG_NAME = 'Configifile'


# pylint:disable=too-few-public-methods
class StraightThroughLoader(BaseLoader):
    """
    Jinja2 loader to just return the template name as the template source
    """
    def get_source(self, environment, template):
        return (template, None, lambda: True)


@contextfilter
def inline_tpl_filter(ctx, val, **kwargs):
    """
    Template filter to load the given template (likely StraightThroughLoader),
    and render it with the current context params, as well as any kwargs passed
    """
    params = dict(ctx.items() + kwargs.items())
    # pylint:disable=star-args
    return ctx.environment.get_template(val).render(**params)


def yaml_filter(val):
    """
    Output a value as YAML
    """
    return yaml.dump(val)


class Configify(object):
    """
    Configify object that loads all configs, generates params, and then
    generates the output
    """

    def __init__(self, config_path=None, params=None):
        if config_path is None:
            config_path = os.path.join('.', DEFAULT_CONFIG_NAME)

        if os.path.isdir(config_path):
            config_path = os.path.join(config_path, DEFAULT_CONFIG_NAME)

        self.config_path = config_path

        self.params = params or {}
        self._env = None
        self._config = None

    @property
    def env(self):
        """
        Get the Jinja2 environment
        """
        if self._env is None:
            self._env = Environment(loader=ChoiceLoader((
                FileSystemLoader('.'),
                StraightThroughLoader(),
            )))
            self._env.filters['inline_tpl'] = inline_tpl_filter
            self._env.filters['yaml'] = yaml_filter

        return self._env

    @property
    def config(self):
        """
        Load the config from config_path
        """
        if self._config is None:
            with open(self.config_path) as handle:
                self._config = yaml_load(handle.read().decode())

        return self._config

    def _parse_params_tpls_level(self, level_idx, level):
        """
        Parse an individual level of the params for any templated variables
        """
        if isinstance(level, dict):
            for idx, val in level.iteritems():
                level[idx] = self._parse_params_tpls_level(idx, val)

        elif isinstance(level, (tuple, list)):
            for idx, val in enumerate(level):
                level[idx] = self._parse_params_tpls_level(idx, val)

        else:
            if isinstance(level_idx, str) and level_idx.startswith('$'):
                return self.env.get_template(level).render(**self.params)

        return level

    def parse_params_tpls(self):
        """
        Parse the full params for any templated variables
        """
        return self._parse_params_tpls_level(None, self.params)

    def load_params_layer(self, params_file):
        """
        Load an individual layer of params from file on to params
        """
        yaml_string = self.env.get_template(params_file).render(**self.params)
        yaml_dict = yaml_load(yaml_string)
        self.params.update(yaml_dict)
        self.params.setdefault('_files', {})[params_file] = yaml_dict

    def load_params_layer_glob(self, params_file):
        """
        Wrapper around load_params_layer that expands the params file from a
        possible glob first
        """
        for filename in glob.glob(params_file):
            self.load_params_layer(filename)

    def load_params(self):
        """
        Load all params given in the config
        """
        params_vals = self.config['params']
        if isinstance(params_vals, (tuple, list)):
            for params_file in params_vals:
                self.load_params_layer_glob(params_file)
        else:
            self.load_params_layer_glob(params_vals)

        self.params = self.parse_params_tpls()

    def generate(self):
        """
        Return the generated config string
        """
        self.load_params()

        return self.env.get_template(
            self.config['template']
        ).render(self.params)

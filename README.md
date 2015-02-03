## Configify
Configify lets you write templates in Jinja2, which get context variables from
a hierarchy of parameter YAML files.

### Simple templates
Params are loaded from yaml files, in sequence, where the later files override
any keys from earlier files.

**nginx_vhost.conf.j2**
```
server {
    listen {{ port }};
    {% for alias in aliases -%}
    location /{{ alias.name }} { alias {{ alias.path }}; autoindex on; }
    {% endfor -%}
}
```

**nginx.yaml**
```yaml
port: 80
aliases:
 - name: doc
   path: /opt/app/doc
 - name: video
   path: /home/myuser/video
```

**Configifile**
```yaml
template: nginx_vhost.conf.j2
params:
 - nginx.yaml
```

**OUTPUT**
```
server {
    listen 80;
    location /doc { alias /opt/app/doc; autoindex on; }
    location /video { alias /home/myuser/video; autoindex on; }

}
```

### Initial context via CLI
You can set an initial set of context parameters right from the CLI. You might
want to use this as some sort of an argument to filter output in the template,
or just as extra input.

**Configifile**

Same as simple templates example above

**nginx_vhost.conf.j2**
```
server {
    listen {{ port }};
    {% for alias in aliases %}{% if not only_alias or alias.name == only_alias -%}
    location /{{ alias.name }} { alias {{ alias.path }}; autoindex on; }
    {% endif %}{% endfor -%}
}
```

**nginx.yaml**
```yaml
aliases:
 - name: doc
   path: /opt/app/doc
 - name: video
   path: /home/myuser/video
```

**OUTPUT**
`configify port=8080 only_alias=doc`
```
server {
    listen 8080;
    location /doc { alias /opt/app/doc; autoindex on; }

}
```

### Templated context parameters
Params YAML files are also run throught Jinja2 before being parsed as YAML.
The context parameters they get are all the parameters that have been parsed
up until that point (any previous YAML parameters files).

**nginx_vhost.conf.j2**

Same as simple templates example above

**nginx_base.yaml**
```yaml
port: 80
app_docs:
 - first_app
 - second_app
 - other_app
```

**nginx_generated.yaml**
```
aliases:
{%- for app in app_docs %}
 - name: doc/{{ app }}
   path: /opt/{{ app }}/doc
{% endfor -%}
```

**Configifile**
```yaml
template: nginx_vhost.conf.j2
params:
 - nginx_base.yaml
 - nginx_generated.yaml
```

**OUTPUT**
```
server {
    listen 80;
    location /doc/first_app { alias /opt/first_app/doc; autoindex on; }
    location /doc/second_app { alias /opt/second_app/doc; autoindex on; }
    location /doc/other_app { alias /opt/other_app/doc; autoindex on; }

}
```

### Post-processed variables
You can defer the procesing of a parameter until after all parameters have been
loaded by putting a $ in front of it. This way, you can have parameters that
depend on values that have yet to be processed. Remembor to enclose any template
values in a `raw` tag.

```yaml
port: 80
$logfile: {% raw %}/var/log/server_{{ port }}{% endraw %}
```

### Inline template filter
In your parameters, you may like to use a lightweight, partial template similar
to a format string. There's the `inline_tpl` filter that we've added so
that you can do just this. The template in the parameter will recieve the
current context parameters, as well as any extra kwargs passed to the filter.
It will _not_ receieve the local context (eg loop variables).

**params.yaml**
```yaml
servername_tpl: "{% raw %}{{ subdomain.name }}.mydomain.com{% endraw %}"
subdomains:
 - name: doc
   port: 80
 - name: app
   port: 443
```

**nginx_vhosts.conf.j2**
```
{%- for subdomain in subdomains %}
server {
    listen {{ subdomain.port }};
    servername {{ servername_tpl | inline_tpl(subdomain=subdomain) }};
}
{% endfor -%}
```

**OUTPUT**
```
server {
    listen 80;
    servername doc.mydomain.com;
}

server {
    listen 443;
    servername app.mydomain.com;
}
```

### Params file globs
You can load up your params files from file globs, making it easy to add new
variables and overrides.

**Configifile**
```yaml
template: tpl.j2
params:
 - dev-*.yaml
 - test-?.yaml
 - prod-[au,uk,us].yaml
```

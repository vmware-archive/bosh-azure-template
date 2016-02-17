import yaml
import os
from jinja2 import Template


def do_step(context):

    settings = context.meta['settings']

    f = open('manifests/index.yml')
    manifests = yaml.safe_load(f)
    f.close()

    m_list = []
    for m in manifests['manifests']:
        m_list.append("manifests/{0}".format(m['file']))

    m_list.append('bosh.yml')

    # Normalize settings from ARM template
    norm_settings = {}
    norm_settings["DIRECTOR_UUID"] = "{{ DIRECTOR_UUID }}"
    norm_settings["CF_PUBLIC_IP_ADDRESS"] = settings["cf-ip"]

    for setting in context.meta['settings']:
        norm_settings[setting.replace("-", "_")] = settings[setting]

    # Render the yml template for bosh-init
    for template_path in m_list:

        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                contents = f.read()
                template = Template(contents)
                contents = template.render(norm_settings)

        with open(os.path.join('bosh', template_path), 'w') as f:
            f.write(contents)

    return context

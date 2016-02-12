def do_step(context):
    f = open('manifests/index.yml')
    manifests = yaml.safe_load(f)
    f.close()

    m_list = []
    for m in manifests['manifests']:
        m_list.append("manifests/{0}".format(m['file']))

    m_list.append('bosh.yml')

    # Get github path
    github_path = "https://raw.githubusercontent.com/cf-platform-eng/bosh-azure-template/master"

    # Normalize settings from ARM template
    norm_settings = {}
    norm_settings["DIRECTOR_UUID"] = "{{ DIRECTOR_UUID }}"
    norm_settings["CF_PUBLIC_IP_ADDRESS"] = settings["cf-ip"]

    for setting in context['meta']['settings']:
        norm_settings[setting.replace("-", "_")] = settings[setting]

    # Render the yml template for bosh-init
    for template_path in m_list:

        # Download the manifest if it doesn't exits
        if not os.path.exists(template_path):
            urllib.urlretrieve("{0}/{1}".format(github_path, template_path), template_path)

        if os.path.exists(template_path):
            with open (template_path, 'r') as f:
                contents = f.read()
                template = Template(contents)
                contents = template.render(norm_settings)

        with open (os.path.join('bosh', template_path), 'w') as f:
            f.write(contents)

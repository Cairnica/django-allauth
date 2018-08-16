
import os
import re

DIR = './allauth/socialaccount/providers'
for filename in os.listdir(DIR):
    file = os.path.join(DIR, filename)
    if os.path.isdir(file):
        views_path = os.path.join(file, 'views.py')
        prov_path = os.path.join(file, 'provider.py')
        if os.path.exists(views_path) and os.path.exists(prov_path):
            delete_views = True
            copy_lines = []
            class_name = None

            with open(views_path, 'r') as views_file:
                lines = list(views_file)
                i = 0
                while i < len(lines):
                    line = lines[i]
                    match = re.match(r'class (\w+)\(OAuth2Adapter\)', line)
                    if match:
                        if class_name is not None:
                            delete_views = False
                            break
                        class_name = match.group(1)
                        while True:
                            copy_lines.append(line)
                            i+=1
                            line = lines[i]
                            if not re.match(r'\s+', line): break

                    elif re.match(r'^(class|def)', line):
                        delete_views = False
                    i+= 1

            if delete_views and class_name is not None:
                provider_lines = []
                added_aclass = False
                added_adapter = False
                with open(prov_path, 'r') as provider_file:
                    for line in provider_file:
                        if re.match(r'class \w+ ?\(OAuth2Provider\)', line):
                            provider_lines.extend(copy_lines)
                            if added_aclass:
                                print(f'Added AdapterClass def multiple times: {filename}')
                            added_aclass = True
                        
                        provider_lines.append(line)

                        match = re.match(r'(\s+)account_class = ', line)
                        if match:
                            provider_lines.append(f'{match.group(1)}adapter_class = {class_name}\n')
                            if added_adapter:
                                print(f'Added adapter_class multiple times: {filename}')
                            added_adapter = True

                with open(prov_path, 'w') as provider_file:
                    provider_file.write(''.join(provider_lines))

                if added_aclass and added_adapter:
                    os.remove(views_path)
                else:
                    print(f'Failed to add AdapterClass or adapter_class field: {filename}')
            else:
                print(f'Additional classes and defs in views.py: {filename}')
        else:
            print(f'Missing View or Provider file: {filename}')

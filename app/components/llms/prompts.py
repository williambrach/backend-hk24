
from jinja2 import Environment, FileSystemLoader


def create_prompt_for_summary(function_content : str):
    env = Environment(loader=FileSystemLoader('app/components/llms/agent_templates'))
    user_template = env.get_template('summarisation_user.txt')
    data = {
        'function_code': function_content,
    }
    user_text = user_template.render(data)

    system_template = env.get_template('summarisation_system.txt')
    system_text = system_template.render()
    return user_text, system_text

def create_prompt_for_commenting(function_content : str):
    env = Environment(loader=FileSystemLoader('app/components/llms/agent_templates'))
    user_template = env.get_template('comments_user.txt')
    data = {
        'function_code': function_content,
    }
    user_text = user_template.render(data)

    system_template = env.get_template('comments_system.txt')
    system_text = system_template.render()
    return user_text, system_text
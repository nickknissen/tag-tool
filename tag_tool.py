# coding: utf8
"""
TODO:
* Clean up and reuse code
* Use a file to instead of template to easier customization.
* Use Request instead of CURL to make it platform platform agnostic.
* get_merges_into_master_after -> get_merges_into_current_branch_after.
* Config file for input and output format for tagname.
"""
import click
import json
import subprocess
import re
import jinja2
import tempfile

RALLY_ITERATIONS_LIST_URL = ("https://rally1.rallydev.com/slm/webservice/v3.0/"
                             "iteration\?query\=\&"
                             "order\=EndDate%20desc\&start\=1\&pagesize\=1")


class EnvironmentVariableError(Exception):
    pass


class ExecutionError(RuntimeError):
    def __init__(self, *args, **kwargs):
        self.stdout = kwargs.pop("stdout")
        self.stderr = kwargs.pop("stderr")
        super(ExecutionError, self).__init__(*args, **kwargs)


def execute(cmd, workdir=None, can_fail=True, log=False):
    """
    Runs shell command cmd. If can_fail is set to True RuntimeError
    is raised if command returned non-zero return code. Otherwise
    returns return code and content of stdout and content of stderr.

    Taken from https://github.com/paramite/bade/blob/master/bade/utils.py#L32
    """
    log_msg = "Executing command: {}".format(cmd)
    if log:
        print(log_msg)

    proc = subprocess.Popen(
        cmd, cwd=workdir, shell=True, close_fds=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = proc.communicate()

    if proc.returncode and can_fail:
        raise ExecutionError("Failed to execute command: ".format(cmd),
                             stdout=out, stderr=err)
    return out, err, proc.returncode


def get_lastest_git_tag():
    cmd = "git log --tags --simplify-by-decoration --pretty='format:%d'"
    stdout, stderr, rc = execute(cmd)
    return stdout.splitlines()[0].strip()[1:-1].split(": ")[1]


def get_current_version():
    """ lastest_git_tag format: "sprint-56.2.0-remove-beta-logos"."""
    lastest_git_tag = get_lastest_git_tag()

    return lastest_git_tag.split("-")[1]


def get_sprint_number(current_sprint_name):
    """ current_sprint_name format: "Sprint 56: Browser testet". """
    return current_sprint_name.split()[1][:-1]


def style_green(text):
    return click.style(text, fg="green")


def get_current_sprint_name(rally_user, rally_password):
    result, _, _ = execute(
        "curl -s --user {user}:{password} {url}".format(
            user=rally_user,
            password=rally_password,
            url=RALLY_ITERATIONS_LIST_URL))
    json_result = json.loads(result)

    try:
        return json_result["QueryResult"]["Results"][0]["_refObjectName"]
    except KeyError:
        return None


def get_latest_release_tag_date():
    cmd = ("git log --tags='\(test-sprint-5\)' "
           "--simplify-by-decoration --format='%ci'")
    tag_dates, sterr, r_code = execute(cmd)
    return tag_dates.splitlines()[1]


def get_merges_into_master_after(latest_tag_date):
    cmd = "git log --merges --format='%s' --after='{}'".format(latest_tag_date)
    merges_raw, sterr, r_code = execute(cmd)
    merges_raw = merges_raw.strip()

    p = re.compile(ur'(branch \')(?<=\')(.*?)(?=\')')
    merges = re.findall(p, merges_raw)

    return [merge[1] for merge in merges]


def is_new_sprint(current_sprint_name):
    sprint_number = get_sprint_number(current_sprint_name)
    current_version = get_current_version()
    return current_version.split(".")[0] != sprint_number


def genereate_new_sprint_version(current_version):
    version_splited = current_version.split(".")
    version_splited[0] = str(int(version_splited[0]) + 1)
    version_splited[1] = version_splited[2] = "0"
    return ".".join(version_splited)


def genereate_new_major_version(current_version):
    version_splited = current_version.split(".")
    version_splited[1] = str(int(version_splited[1]) + 1)
    return ".".join(version_splited)


def genereate_new_minor_version(current_version):
    version_splited = current_version.split(".")
    version_splited[2] = str(int(version_splited[2]) + 1)
    return ".".join(version_splited)


def genereate_new_tag_name(version, tag_title):
    return "sprint-{version}-{title}".format(version=version, title=tag_title)


def generate_tagging_message(sprint_number, latest_tag_date):
    merges_into_branch = get_merges_into_master_after(latest_tag_date)

    template = """Sprint {{sprint_number}}

{% for branch in branches %}* {{branch}}\n{% endfor %}
"""
    return jinja2.Template(template).render(sprint_number=sprint_number,
                                            branches=merges_into_branch)


@click.option("rally_pass", "--rally-pass", envvar="RALLY_PASS", required=True,
              prompt=True, hide_input=True,
              help="Password to rally1.rallydev.com")
@click.option("rally_user", "--rally-user", envvar="RALLY_USER", required=True,
              prompt=True, help="Username to rally1.rallydev.com")
@click.command()
def cli(rally_user, rally_pass):
    lastest_git_tag = get_lastest_git_tag()
    current_version = get_current_version()

    click.echo("Current release: {}".format(style_green(lastest_git_tag)))

    current_sprint_name = get_current_sprint_name(rally_user, rally_pass)

    if current_sprint_name is None:
        click.secho("Couldn't retrieve latest sprint from Rally",
                    bg="red", fg="white")
    else:
        click.echo(
            "Current sprint name: {}".format(style_green(current_sprint_name)))
        sprint_number = get_sprint_number(current_sprint_name)

    click.echo("Current sprint number: {}".format(style_green(sprint_number)))

    if is_new_sprint(current_sprint_name):
        click.echo("New sprint has started")
        new_version = genereate_new_sprint_version(current_version)
    else:
        is_major_version = click.prompt(
            "Is this major version (new features added)",
            type=bool, default=False)

        if is_major_version:
            new_version = genereate_new_major_version(current_version)
        else:
            new_version = genereate_new_minor_version(current_version)

    tag_title = click.prompt(
        """Please enter tag title. You "-" instead of whitespace""",
        type=unicode)

    tagname = genereate_new_tag_name(new_version, tag_title)

    click.echo("That tag will be named: {}".format(style_green(tagname)))

    latest_tag_date = get_latest_release_tag_date()

    git_message = generate_tagging_message(sprint_number, latest_tag_date)
    click.secho("Following message with be used as git tagging message:")
    click.secho(git_message, fg='yellow')

    with tempfile.NamedTemporaryFile() as temp:
        temp.write(git_message)
        temp.flush()

        if click.confirm(
            "Do you want to create the tag with the information from above?"
        ):
            execute("git tag -a {} -F {}".format(tagname, temp.name))
            execute("git push --tags")


if __name__ == "__main__":
    cli()

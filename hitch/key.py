from hitchstory import StoryCollection, BaseEngine, exceptions
from hitchstory import GivenDefinition, GivenProperty
from hitchstory import validate, no_stacktrace_for
from hitchrun import hitch_maintenance, expected, DIR
from pathquery import pathquery
from strictyaml import MapPattern, Optional, Map, Str, Int
from commandlib import python, Command
import strictyaml
from hitchrunpy import ExamplePythonCode, HitchRunPyException
from templex import Templex
import hitchpylibrarytoolkit


class Engine(BaseEngine):
    given_definition = GivenDefinition(
        python_version=GivenProperty(Str()),
        build_py=GivenProperty(Str()),
        setup=GivenProperty(Str()),
        files=GivenProperty(MapPattern(Str(), Str())),
    )

    def __init__(self, paths, settings):
        self.path = paths
        self.settings = settings

    def set_up(self):
        self.path.build_directory = self.path.gen / "build"
        self.path.state = self.path.gen.joinpath("state")

        if self.path.state.exists():
            self.path.state.rmtree()
        self.path.state.mkdir()

        if self.given.get('build.py') is not None:
            self.path.state.joinpath("build.py").write_text(
                self.given['build.py']
            )

        self.path.key.joinpath("code_that_does_things.py").copy(self.path.state)

        self.python = hitchpylibrarytoolkit.project_build(
            "hitchbuild",
            self.path,
            self.given["python version"],
        ).bin.python

        for filename, contents in self.given.get('files', {}).items():
            filepath = self.path.state.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().makedirs()
            filepath.write_text(contents)

    def _story_friendly_output(self, output):
        """
        Takes output and replaces with a deterministic, representative or
        more human readable output.
        """
        return output.replace(self.path.state, "/path/to")

    @no_stacktrace_for(AssertionError)
    @no_stacktrace_for(HitchRunPyException)
    @validate(
        code=Str(),
        will_output=Str(),
        environment_vars=MapPattern(Str(), Str()),
        raises=Map({
            Optional("type"): Str(),
            Optional("message"): Str(),
        })
    )
    def run_code(self, code, will_output=None, environment_vars=None, raises=None):
        self.example_py_code = ExamplePythonCode(self.python, self.path.gen)\
            .with_terminal_size(160, 100)\
            .with_env(**{} if environment_vars is None else environment_vars)\
            .with_setup_code(self.given['setup'])\
            .in_dir(self.path.state)

        to_run = self.example_py_code.with_code(code)

        if self.settings.get("cprofile"):
            to_run = to_run.with_cprofile(
                self.path.profile.joinpath("{0}.dat".format(self.story.slug))
            )

        result = to_run.expect_exceptions().run() if raises is not None else to_run.run()

        actual_output = self._story_friendly_output(result.output)

        if will_output is not None:
            try:
                Templex(will_output).assert_match(actual_output)
            except AssertionError:
                if self.settings.get("overwrite artefacts"):
                    self.current_step.update(**{"will output": actual_output})
                else:
                    raise

        if raises is not None:
            exception_type = raises.get('type')
            message = raises.get('message')

            try:
                result.exception_was_raised(exception_type)
                exception_message = self._story_friendly_output(result.exception.message)
                Templex(exception_message).assert_match(message)
            except AssertionError:
                if self.settings.get("overwrite artefacts"):
                    new_raises = raises.copy()
                    new_raises['message'] = exception_message
                    self.current_step.update(raises=new_raises)
                else:
                    raise

    def exception_raised_with(self, code, exception_type, message):
        result = ExamplePythonCode(code).with_setup_code(self.given.setup)\
                                        .expect_exceptions()\
                                        .run(self.path.gen, self.python)
        result.exception_was_raised(exception_type, message)

    def touch_file(self, filename):
        self.path.state.joinpath(filename).write_text("\nfile touched!", append=True)

    def write_file(self, filename, content):
        self.path.state.joinpath(filename).write_text(content)

    @no_stacktrace_for(AssertionError)
    def file_exists(self, filename):
        assert self.path.state.joinpath(filename).exists(), \
           "{0} does not exist".format(filename)

    def _rewritten_output(self, text):
        return text.replace(self.path.state, "/path/to")

    @no_stacktrace_for(FileNotFoundError)
    @no_stacktrace_for(AssertionError)
    def file_contents_will_be(self, filename, text=None):
        rewritten_contents = self._rewritten_output(
            self.path.state.joinpath(filename).text()
        )
        try:
            Templex(text).assert_match(rewritten_contents)
        except AssertionError:
            if self.settings.get("overwrite artefacts"):
                self.current_step.update(
                    text=rewritten_contents
                )
            else:
                raise

    def file_does_not_exist(self, filename):
        return not self.path.build_directory.joinpath(filename).exists()

    @validate(seconds=Int())
    def sleep(self, seconds):
        import time
        time.sleep(int(seconds))

    def on_success(self):
        if self.settings.get("overwrite artefacts"):
            self.new_story.save()


@expected(exceptions.HitchStoryException)
def bdd(*keywords):
    """
    Run story matching keywords specified.
    """
    StoryCollection(
        pathquery(DIR.key).ext("story"),
        Engine(DIR, {"overwrite artefacts": False})
    ).shortcut(*keywords).play()


@expected(strictyaml.exceptions.YAMLValidationError)
@expected(exceptions.HitchStoryException)
def rbdd(*keywords):
    """
    Run story matching keywords specified.
    """
    StoryCollection(
        pathquery(DIR.key).ext("story"),
        Engine(DIR, {"overwrite artefacts": True})
    ).shortcut(*keywords).play()


def regression():
    """
    Run all stories.
    """
    lint()
    StoryCollection(
        pathquery(DIR.key).ext("story"), Engine(DIR, {})
    ).ordered_by_name().play()


def hitch(*args):
    """
    Use 'h hitch --help' to get help on these commands.
    """
    hitch_maintenance(*args)


def rerun(version="3.5.0"):
    """
    Rerun last example code block with specified version of python.
    """
    Command(DIR.gen.joinpath("py{0}".format(version), "bin", "python"))(
        DIR.gen.joinpath("working", "working", "examplepythoncode.py")
    ).in_dir(DIR.gen.joinpath("working")).run()


def lint():
    """
    Lint all code.
    """
    python("-m", "flake8")(
        DIR.project.joinpath("hitchbuild"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    python("-m", "flake8")(
        DIR.key.joinpath("key.py"),
        "--max-line-length=100",
    ).run()
    print("Lint success!")


def deploy(version):
    """
    Deploy to pypi as specified version.
    """
    NAME = "hitchbuild"
    git = Command("git").in_dir(DIR.project)
    version_file = DIR.project.joinpath("VERSION")
    old_version = version_file.bytes().decode('utf8')
    if version_file.bytes().decode("utf8") != version:
        DIR.project.joinpath("VERSION").write_text(version)
        git("add", "VERSION").run()
        git("commit", "-m", "RELEASE: Version {0} -> {1}".format(
            old_version,
            version
        )).run()
        git("push").run()
        git("tag", "-a", version, "-m", "Version {0}".format(version)).run()
        git("push", "origin", version).run()
    else:
        git("push").run()

    # Set __version__ variable in __init__.py, build sdist and put it back
    initpy = DIR.project.joinpath(NAME, "__init__.py")
    original_initpy_contents = initpy.bytes().decode('utf8')
    initpy.write_text(
        original_initpy_contents.replace("DEVELOPMENT_VERSION", version)
    )
    python("setup.py", "sdist").in_dir(DIR.project).run()
    initpy.write_text(original_initpy_contents)

    # Upload to pypi
    python(
        "-m", "twine", "upload", "dist/{0}-{1}.tar.gz".format(NAME, version)
    ).in_dir(DIR.project).run()

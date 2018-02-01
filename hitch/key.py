from hitchstory import StoryCollection, BaseEngine, exceptions
from hitchstory import GivenDefinition, GivenProperty, InfoDefinition, InfoProperty
from hitchstory import validate, no_stacktrace_for
from hitchrun import hitch_maintenance, expected, DIR
from pathquery import pathq
from strictyaml import MapPattern, Optional, Map, Str, Int
from commandlib import python, Command
import hitchpython
import strictyaml
import hitchtest
from hitchrunpy import ExamplePythonCode, HitchRunPyException
from templex import Templex


class Engine(BaseEngine):
    given_definition = GivenDefinition(
        python_version=GivenProperty(Str()),
        build_py=GivenProperty(Str()),
        setup=GivenProperty(Str()),
        files=GivenProperty(MapPattern(Str(), Str())),
    )

    info_definition = InfoDefinition(
        about=InfoProperty(),
    )

    def __init__(self, paths, settings):
        self.path = paths
        self.settings = settings

    def set_up(self):
        self.path.state = self.path.gen.joinpath("state")

        if self.path.state.exists():
            self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        for filename, contents in self.given.files.items():
            filepath = self.path.state.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().makedirs()
            filepath.write_text(contents)

        if self.given.build_py is not None:
            self.path.state.joinpath("build.py").write_text(
                self.given.build_py
            )

        self.path.key.joinpath("code_that_does_things.py").copy(self.path.state)

        self.python_package = hitchpython.PythonPackage(self.given.python_version)
        self.python_package.build()

        self.pip = self.python_package.cmd.pip
        self.python = self.python_package.cmd.python

        with hitchtest.monitor([self.path.key.joinpath("debugrequirements.txt")]) as changed:
            if changed:
                self.pip("install", "-r", "debugrequirements.txt").in_dir(self.path.key).run()

        with hitchtest.monitor(
            pathq(self.path.project.joinpath("hitchbuild")).ext("py")
        ) as changed:
            if changed:
                self.pip("uninstall", "hitchbuild", "-y").ignore_errors().run()
                self.pip("install", ".").in_dir(self.path.project).run()

        self.example_py_code = ExamplePythonCode(self.python, self.path.state)\
            .with_setup_code(self.given.setup)\
            .with_terminal_size(160, 100)

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
        raises=Map({
            Optional("type"): Str(),
            Optional("message"): Str(),
        })
    )
    def run_code(self, code, will_output=None, raises=None):
        self.example_py_code = ExamplePythonCode(self.python, self.path.state)\
            .with_terminal_size(160, 100)\
            .with_setup_code(self.given.setup)
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
                result = self.example_py_code.expect_exceptions().run()
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
                                        .run(self.path.state, self.python)
        result.exception_was_raised(exception_type, message)

    def touch_file(self, filename):
        self.path.state.joinpath(filename).write_text("\nfile touched!", append=True)

    @no_stacktrace_for(AssertionError)
    def file_exists(self, filename):
        assert self.path.state.joinpath(filename).exists(), \
           "{0} does not exist".format(filename)

    @no_stacktrace_for(FileNotFoundError)
    @no_stacktrace_for(AssertionError)
    def file_contents_will_be(self, filename, text=None):
        try:
            Templex(self.path.state.joinpath(filename).text()).assert_match(text)
        except AssertionError:
            if self.settings.get("overwrite artefacts"):
                self.current_step.update(
                    text=self.path.state.joinpath(filename).text()
                )
            else:
                raise

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
        pathq(DIR.key).ext("story"),
        Engine(DIR, {"overwrite artefacts": False})
    ).shortcut(*keywords).play()


@expected(strictyaml.exceptions.YAMLValidationError)
@expected(exceptions.HitchStoryException)
def rbdd(*keywords):
    """
    Run story matching keywords specified.
    """
    StoryCollection(
        pathq(DIR.key).ext("story"),
        Engine(DIR, {"overwrite artefacts": True})
    ).shortcut(*keywords).play()


def regression():
    """
    Run all stories.
    """
    lint()
    StoryCollection(
        pathq(DIR.key).ext("story"), Engine(DIR, {})
    ).ordered_by_name().play()


def hitch(*args):
    """
    Use 'h hitch --help' to get help on these commands.
    """
    hitch_maintenance(*args)


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

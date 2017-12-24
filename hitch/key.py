from hitchstory import StoryCollection, StorySchema, BaseEngine, exceptions, validate
from hitchrun import hitch_maintenance, expected, DIR
from pathquery import pathq
from strictyaml import Optional, MapPattern, Str, Int
from commandlib import python, Command
import hitchpython
import strictyaml
import hitchtest
from hitchrunpy import ExamplePythonCode


class Engine(BaseEngine):
    schema = StorySchema(
        given={
            Optional("files"): MapPattern(Str(), Str()),
            Optional("variables"): MapPattern(Str(), Str()),
            Optional("python version"): Str(),
            Optional("build.py"): Str(),
            Optional("sourcefile.txt"): Str(),
            Optional("setup"): Str(),
        },
        params={
            "python version": Str(),
        },
    )

    def __init__(self, paths, settings):
        self.path = paths
        self.settings = settings

    def set_up(self):
        self.path.state = self.path.gen.joinpath("state")

        if self.path.state.exists():
            self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        for filename in ["build.py", "sourcefile.txt", ]:
            if filename in self.given:
                filepath = self.path.state.joinpath(filename)
                if not filepath.dirname().exists():
                    filepath.dirname().mkdir()
                filepath.write_text(str(self.given[filename]))

        self.path.key.joinpath("code_that_does_things.py").copy(self.path.state)

        self.python_package = hitchpython.PythonPackage(
            self.given.get('python_version', self.given['python version'])
        )
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

    def run_code(self, code):
        ExamplePythonCode(code).with_setup_code(self.given.get('setup', ''))\
                               .run(self.path.state, self.python)

    def exception_raised_with(self, code, exception_type, message):
        result = ExamplePythonCode(code).with_setup_code(self.given.get('setup', ''))\
                                        .expect_exceptions()\
                                        .run(self.path.state, self.python)
        result.exception_was_raised(exception_type, message)

    def run(self, command):
        self.ipython_step_library.run(command)

    def touch_file(self, filename):
        self.path.state.joinpath(filename).write_text("\nfile touched!", append=True)

    def _will_be(self, content, text, reference, changeable=None):
        if text is not None:
            if content.strip() == text.strip():
                return
            else:
                raise RuntimeError("Expected to find:\n{0}\n\nActual output:\n{1}".format(
                    text,
                    content,
                ))

        artefact = self.path.key.joinpath(
            "artefacts", "{0}.txt".format(reference.replace(" ", "-").lower())
        )

        from simex import DefaultSimex
        simex = DefaultSimex(
            open_delimeter="(((",
            close_delimeter=")))",
        )

        simex_contents = content

        if changeable is not None:
            for replacement in changeable:
                simex_contents = simex.compile(replacement).sub(replacement, simex_contents)

        if not artefact.exists():
            artefact.write_text(simex_contents)
        else:
            if self.settings.get('overwrite artefacts'):
                artefact.write_text(simex_contents)
            else:
                if simex.compile(artefact.bytes().decode('utf8')).match(content) is None:
                    raise RuntimeError("Expected to find:\n{0}\n\nActual output:\n{1}".format(
                        artefact.bytes().decode('utf8'),
                        content,
                    ))

    def file_contents_will_be(self, filename, text=None, reference=None, changeable=None):
        output_contents = self.path.state.joinpath(filename).bytes().decode('utf8')
        self._will_be(output_contents, text, reference, changeable)

    def output_will_be(self, text=None, reference=None, changeable=None):
        output_contents = self.path.state.joinpath("output.txt").bytes().decode('utf8')
        self._will_be(output_contents, text, reference, changeable)

    @validate(seconds=Int())
    def sleep(self, seconds):
        import time
        time.sleep(int(seconds))


@expected(strictyaml.exceptions.YAMLValidationError)
@expected(exceptions.HitchStoryException)
def tdd(*words):
    """
    Run test with words.
    """
    StoryCollection(
        pathq(DIR.key).ext("story"), Engine(DIR, {"overwrite artefacts": False})
    ).shortcut(*words).play()


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

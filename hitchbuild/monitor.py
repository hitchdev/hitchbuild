from peewee import ForeignKeyField, CharField, FloatField, BooleanField, DateTimeField, TextField
from peewee import SqliteDatabase, Model
from datetime import timedelta as python_timedelta
from hitchbuild import condition
import pickle


class BuildContextManager(object):
    def __init__(self, monitor):
        self._monitor = monitor

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        model = self._monitor.build_model
        model.exception_raised = traceback is not None
        model.save()


class Monitor(object):
    """
    The HitchBuild Monitor keeps track of things which
    determine whether to trigger a rebuild.
    """
    def __init__(self, name, sqlite_filename):
        self._name = name

        class BaseModel(Model):
            class Meta:
                database = SqliteDatabase(sqlite_filename)

        class Build(BaseModel):
            name = CharField(primary_key=True)
            exception_raised = BooleanField()
            last_run = DateTimeField(null=True)
            was_triggered_on_last_run = BooleanField(null=True)

        class File(BaseModel):
            build = ForeignKeyField(Build)
            filename = CharField(max_length=640)
            last_modified = FloatField()

        if not Build.table_exists():
            Build.create_table()
        if not File.table_exists():
            File.create_table()

        self.BaseModel = BaseModel
        self.File = File
        self.Build = Build

    @property
    def build_model(self):
        if self.Build.filter(name=self._name).first() is None:
            model = self.Build(
                name=self._name,
                exception_raised=False,
                last_run=None,
                was_triggered_on_last_run=None
            )
            model.save(force_insert=True)
        else:
            model = self.Build.filter(name=self._name).first()
        return model

    @property
    def last_run_had_exception(self):
        return self.build_model.exception_raised

    def is_modified(self, path_list):
        return condition.Modified(self, path_list)

    def non_existent(self, path_to_check):
        return condition.NonExistent(path_to_check)

    def context_manager(self):
        return BuildContextManager(self)

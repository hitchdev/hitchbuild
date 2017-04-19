from os import path as ospath
from path import Path


class Change(object):
    def __nonzero__(self):
        return self.__bool__()


class YesChange(Change):
    def __bool__(self):
        return True


class NoChange(Change):
    def __bool__(self):
        return False


class FileChange(Change):
    def __init__(self, new, modified):
        self._new = new
        self._modified = modified

    @property
    def why(self):
        contents = ""
        if len(self._new) > 0:
            contents += "New file(s) / director(ies) detected:\n"
            for new in self._new:
                contents += "  - {0}\n".format(new)
        if len(self._modified) > 0:
            contents += "File(s) / director(ies) changed:\n"
            for modified in self._modified:
                contents += "  - {0}\n".format(modified)
        return contents

    def __bool__(self):
        return len(self._new) > 0 or len(self._modified) > 0


class Condition(object):
    def __init__(self):
        self._other_condition = None

    def __or__(self, other):
        self._other_condition = other
        return self

    def all_conditions(self):
        conditions = [self, ]
        other_condition = self._other_condition

        while other_condition is not None:
            conditions.append(other_condition)
            other_condition = other_condition._other_condition
        return conditions


class Always(Condition):
    def check(self):
        return YesChange()


class Never(Condition):
    def check(self):
        return NoChange()


class NonExistent(Condition):
    def __init__(self, path_to_check):
        self._path_to_check = Path(path_to_check)

    def check(self):
        return not self._path_to_check.exists()


class Modified(Condition):
    def __init__(self, monitor, paths):
        self._monitor = monitor
        self._paths = paths
        super(Modified, self).__init__()

    def check(self):
        new_files = list(self._paths)
        modified_files = []

        for monitored_file in self._monitor.File.filter(build=self._monitor.build_model):
            filename = monitored_file.filename
            if filename in self._paths:
                new_files.remove(filename)

                if ospath.getmtime(filename) > monitored_file.last_modified:
                    modified_files.append(filename)
                    monitored_file.last_modified = ospath.getmtime(filename)
                    monitored_file.save()

        for filename in new_files:
            file_model = self._monitor.File(
                build=self._monitor.build_model,
                filename=filename,
                last_modified=ospath.getmtime(filename),
            )
            file_model.save()

        return FileChange(new_files, modified_files)

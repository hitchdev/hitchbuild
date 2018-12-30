{% if readme -%}
# HitchBuild
{%- else -%}
---
title: HitchBuild
---
{% endif %}

HitchBuild is a build framework written in python for building code largely for use in
a development and test environment. It is currently used to build isolated virtualenvs,
postgres databases, vagrant boxes as well as django environments.

Priorities:

- Small amount of easily readable code required to create a build.
- Usefulness in a development and test environment.
- Unopinionated about implementation details.
- Loosely coupled from but easily integrated with hitchkey and hitchstory.
- Being a sound basis for an ecosystem of python packages for building things.

Currently it is in alpha so APIs might break. That said, these packages currently built
with it will be upgraded in sync:

- [hitchbuildpy](/hitchbuildpy) (pyenv and virtualenv)
- [hitchbuildpg](/hitchbuildpg)
- [hitchbuildvagrant](/hitchbuildvagrant)

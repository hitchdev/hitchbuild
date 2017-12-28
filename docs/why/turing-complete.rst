Turing completeness
===================

Turing completeness is not always a feature of build systems. There
are many build systems which do not exhibit this feature.

The decision where to use turing completeness in an application is
a delicate one. If you put it where it isn't required - e.g. in
user stories - then the resultant code can be much more unreadable
than it would otherwise for no real gain.

If you don't put it where it is required (e.g. in a build), then
you end up being unable to achieve much of what you need the system
to do without hacks.

Some systems (notably ant) started off turing incomplete by design
and then became turing complete as features were added. These are
often the worst designed languages.

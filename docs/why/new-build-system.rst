Why build a new build system at all?
====================================

Frankly, I think all of them suck.

Make can handle simple use cases acceptably well, but as soon as the use cases grow complex the whole system starts to falter. I think that there is a need for a simple build system that handles complex use cases.

I think that there is a number of reasons for this:

1. There's a common misconception that build systems are just a set of simple scripts.
2. The more abstract use cases are not perceived and fully understood by creators of build systems.
3. Creating build systems is often seen as a chore that junior developers can take care of.
4. There's a cultural bias towards using DSLs and plugins for build tools instead of fully turing complete languages. I think turing complete is the way to go.

The approach I have taken here is, I think a new one.

Firstly, I've started from the presumption that I am probably going to create a bad API to begin with. I have no preconceptions that my original architecture will be poor and unfit for purpose. The second version will likely be bad too. The third might be ok.

Secondly, I am sourcing the proper use cases by dogfooding. I am building build tools on top of this and using them in a production environment to draw out subtle use cases that I didn't understand before.

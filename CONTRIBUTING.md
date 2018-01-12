## You want to start contributing? Here's some advice for a quicker start!

If you just want to help our cause and don't know where to start, take a look [at the GitHub issues](https://github.com/ZeroPhone/ZPUI/issues). If you want to know which issue is more important and would help us the most, contact us and we'll let you know!

If you already have some kind of idea in mind, but it's not listed among the issues, we likely could make use of it, too! Contact us to let us know about it - it's likely we could help you, maybe suggest a good way to implement your idea, get started with the codebase etc.

You can contact us about ZPUI in one of those ways:

1. Open an issue here, on GitHub (if you're interested in working on it yourself, let us know!)
2. [Get in touch with us](CONTACT.md)

### Making a pull request

We love pull requests! Here are some suggested steps to ensure that your improvements don't break ZPUI or its documentation, and to make sure we can merge them quickly.

* Fork our repository
* Make sure you can run tests and they pass: (`./test.sh`)
* We highly suggest you commit your changes in a separate branch - that'll save you from problems when sending pull requests in the future
* Make your changes, test them using [the emulator](http://zpui.readthedocs.io/en/latest/setup.html#emulator) or a real ZeroPhone
* Run the tests again to make sure they still pass
* If your changes concern the documentation, it'd be great if you could check that the documentation [still builds correctly and looks right](http://zpui.readthedocs.io/en/latest/docs_development.html#testing-your-changes-locally)
* Send in your PR, we'll review and comment on it as soon as possible!
* Take some time to explain what your PR is about, and how you implemented your feature, it'll help us review it faster

If your PR won't have any issues, we'll merge it right away. If we find some problems, we might fix them ourselves, but we'll likely ask you to fix them yourself in the meantime before we can get to them.

-----

**After your PR is reviewed, doesn't break anything and complies to our guidelines, it'll be merged!** Once your PR is merged, it'll likely go in the `devel` branch - unless it's a bugfix, in which case it'll go in all branches affected. If you need your changes in the master branch ASAP, let us know - we can speed up the merge.

#### Possible issues with your PR that you should watch out for:
* it's not documented enough. If you're adding features, they need to be documented. If you're changing an existing feature, keep the comments up-to-date. If you find some area lacking documentation that you want to see documented, let us know! 
* it has multiple commits that concern two or more unrelated problems. It makes it harder to discuss, review, and merge right away if you solved the problem in a clean way. It's better if you send multiple PRs when you want to tackle multiple problems - that way, your changes will be merged quicker!
* it changes the UI element or helper function API that's established and might be used in both in-ZPUI and user-written apps.
* it breaks some functionality (which isn't obvious for some reason - not covered by tests etc.) - we'll point it out to you if you don't notice it yourself during testing, don't worry!

## Code guidelines

### Formatting guidelines

* 4 space offsets in Python code
* One newline between function/method definitions
* Two newlines between class definitions
* If a docstring is used in our documentation, it should remain valid ReStructuredText - in RST, formatting and newlines matter. So, it's best if you make sure documentation still compiles after you've changed the docstring.

### Commit guidelines

* Your commit messages should be readable and describe - what was it that you added/improved/fixed?
* Each commit should contain one unit of work - if you're working on two separate features, don't mix them in one commit.
* If you're making two different-purpose changes concerning one feature, it's best if you split them into two separate commits - but not strictly necessary.
* Best practice: one commit describes one unit of work, say, "fixed a bug with Menu entry labels being truncated"
* If you're solving a GitHub issue, please tag the issue in the commit messages ("added scrolling to DialogBox message, closes #21")

Why these rules? This way, it's easier for us to investigate bugs, track progress on issues, as well as review, merge, cherry-pick and revert your commits. 

### UI element and helper function change guidelines

* UI elements and helper functions are what's exposed to app developers. If we break them, we might break somebody's app - so, be careful with your changes
Specifically, watch out for changes concerning UI element/helper object `__init__` attributes and helper function parameters, as well as any methods/attributes that are exposed in the UI element's documentation (and thus are considered user-exposed).
* If you're fixing an UI element bug, consider adding tests for it! If there's no UI-element related file with tests in the "ui/tests" folder, let us know - we haven't covered all of the UI elements, but we strive to do so.
* You can run the UI-element related test file quicker by going into the `ui/tests` folder and executing the test file directly, with `python test_{ui_element}.py`

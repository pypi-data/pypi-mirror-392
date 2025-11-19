# Elite Relay
Elite: Dangerous Journal Event Handler

> [!IMPORTANT]
> This document is a work-in-progress and may contain incomplete information.

## Introduction
`elite-relay` is a small program that tracks events recorded in your [Elite: Dangerous journal file](https://elite-journal.readthedocs.io/en/latest/)
and allows you respond to them in certain ways, including:
* Sending an HTTP request with the event data, e.g. firing a webhook to a service like Home Assistant or Zapier.
* Copying text to your clipboard, e.g. the name of the star system you just jumped to.
* Opening a templated URL in your browser, e.g. opening an [Inara.cz "search nearest"](https://inara.cz/elite/nearest/)
  page when jumping to a new system.

Event handlers ("plugins") are defined in `.edr/config.yaml` located in your home directory. See ["Configuring plugins"](#configuring-plugins)
for more information, or check out some examples in [`examples.yaml`](examples.yaml).

## Installation

### Using the MSI installer

The easiest way to install `elite-relay` is via the MSI installer included in the [latest release](https://github.com/amickael/elite-relay/releases/latest).
Simply download the file and open it, the program will then be installed to your $FOLDER folder. Open the `main.exe` file
to start it.

### Using `pip`

Alternatively, you may install `elite-relay` via Python's `pip` package manager (or any other Python package manager of your choosing):
```shell
pip install --upgrade elite-relay
```

You can now run `elite-relay` in a terminal to start the program.

## Configuring plugins

Event handlers ("plugins") are defined in `.edr/config.yaml` located in your home directory. There are a few basic options
that apply to all plugins, as well as plugin-specific options that are defined under the `options` key. Let's start with a
basic example that will copy the name of the star system to our clipboard whenever an `FSDJump` event occurs:
```yaml
plugins:
  - plugin: clipboard
    action: copy
    filters:
      - key: type
        eq: FSDJump
    options:
      text: ${data.StarSystem}
```
Let's break it down:

### Global options

#### Plugins & actions
The `plugin: clipboard` key tells the program which "plugin" to use when responding to an event. All plugins are comprised
of different "actions," in this example it's `copy`.

#### Filters
Filters allow us to only respond to events that we care about. In this example we only want to copy text to our clipboard
whenever the `FSDJump` event type is recorded, hence the `filters` block above:
```yaml
filters:
  - key: type
    eq: FSDJump
```

In this instance we're telling the program to only respond to events where the `type` is _exactly equal_ to `FSDJump`.

Filters can also use [regular expressions](https://regexone.com/) (regex) for more complex filtering operations. To use
regex filtering enable it by setting `regex: true` in the filter; now the expression in the `eq` key will be evaluated
as regex. For example if we wanted to narrow our filter further by only triggering on systems that begin with "HIP" we
could do the following:
```yaml
filters:
  - key: type
    eq: FSDJump
  - key: data.StarSystem
    eq: ^HIP (.*)$
    regex: true
```

Filter keys may also use [JMESPath](https://jmespath.org/tutorial.html) syntax to reference deeply-nested information within
the event data. For example, if we wanted to trigger if the first power in the system is "Li Yong-Rui" we would do:
```yaml
filters:
  - key: type
    eq: FSDJump
  - key: data.Powers[0]
    eq: Li Yong-Rui
```

### Plugin-specific options
The `options` key above provides _plugin-specific_ options that are documented alongside the code for each plugin
in the [plugins directory](elite_relay/plugins).

In this example the `clipboard.copy` action has a required option for the text we wish to copy. The text is _templated_,
meaning that we can reference data within the event to copy. In this instance `${data.StarSystem}` will be converted to
the name of the actual star system we just jumped to:
```yaml
options:
  text: ${data.StarSystem}
```

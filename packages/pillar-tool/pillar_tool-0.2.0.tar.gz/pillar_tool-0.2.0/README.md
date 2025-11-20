# Tool to manage Salt pillars via cli

By default, manages `/srv/pillar/defaults.sls` providing a CLI to manage pillars similar ot the `grains.set` module on Salt servers.


```bash
pillar 
Usage: pillar [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  --file PATH                    Path to pillar file  [default:
                                 /opt/pillar/defaults.sls]
  --output [yaml|expand|pprint]  How to format output  [default: yaml]
  --help                         Show this message and exit.

Commands:
  config
  get
  list
  rotate
  set
```

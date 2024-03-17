# i3 Autopause Screenkey
To disable `screenkey` during password prompts or other sensitive inputs you can
press [left control and right control] at the same time to temporarily pause
showing of inputs. This however require to remember to do so before typing the
first letter(s).

`i3-autopause-screenkey.py` starts and stops `screenkey` (kill the process), if
it matches a certain window.

- Documentation (and FAQ – if any) can be found in this README.
- Feel free to file issues to report bus, ask questions, or request features.
- Feel free to open a pull request.

## Requirements
The script requires python3.6+ and `i3ipc` to be installed.
```
pip install --user -r ./requirements.txt
```

## Installation
There is currently no classic installation/package. Clone the repo or download
`i3-autopause-screenkey.py` and put it into your preferred bin place (e.g.
`~/.local/bin/`).


## Usage
Provide multiple strings per "unsafe" argument. Use `./i3-autopause-screenkey.py
--help` to see all arguments.

### Example
```
./i3-autopause-screenkey.py \
    --unsafe-class pinentry polkit \
    --unsafe-title 1password \
    --unsafe-instance foobar
```

## Know Issues
- Instead of pausing `screenkey`, the script kills the entire process. This
  means that visible input will instantly disappear.
- Logging Level is set globally (including for `asyncio`) instead of only
  setting it for the logger.

## Feature Ideas
- I was unaware at time of writing that `screenkey` was python-based itself.
  Currently the script uses `subprocess` to start and stop `screenkey` when I
  could have imported it into the script directly. Maybe this would enable the
  next feature idea.
- Don't restart `screenkey` every time but pause visibility only
- Provide list of "safe" matches instead of "unsafe" ones. I am not sure how the
  options would then interact. Only either safe-listing or unsafe-listing? One
  overrides the other? Which one overrides? Make overriding dependent on
  ordering?
- `--unsafe-outputs`
- `--unsafe-workspaces`
- Provide options how to call `screenkey`


[left control and right control]:
https://gitlab.com/screenkey/screenkey#controlling-visibility

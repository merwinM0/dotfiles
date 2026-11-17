[中文](README.md) | [English](README.en.md)

# Personal terminal and desktop configuration

Configuration for this Linux workstation, organized as GNU Stow packages. Includes Fish, tmux, foot, Helix, Niri, Yazi, Zellij, package-management scripts, and local Pi display patches.

## Usage

Check existing target files before simulating links for the packages you need:

```sh
cd ~/dotfiles
stow --simulate --target="$HOME" fish foot
stow --target="$HOME" fish foot
```

Link only the packages you need. Do not overwrite existing configuration with `--adopt`. Personal paths, Fish universal variables, and runtime state are excluded from version control; see `.gitignore`.

## tmux key routing

Link the configuration with `stow --target="$HOME" tmux`. tmux handles the custom Alt shortcuts by default. In Fish, run `tmkeys fish` to pass them to the foreground application, `tmkeys tmux` to restore tmux handling, and `tmkeys status` to check the current pane's mode.

## Documentation

- [Configuration and usage notes](Config.md)
- [Fish function guide](fish/.config/fish/functions/函数说明.md)
- [Development conventions](AGENTS.md)
- [Roadmap](READMAP.md)
- [Pi display patches](pi-ui/README.md)

# Install AnnotatedEquations

The repository is public and licensed under Apache 2.0. You can clone it over HTTPS without a GitHub account. These commands use a macOS/Linux shell and Git; use an equivalent folder copy with your preferred Git client on other platforms.

## 1. Get the repository

```sh
git clone https://github.com/BennettLandman/AnnotatedEquations.git
cd AnnotatedEquations
```

## 2. Make the skill available to your agent

For Codex, copy the complete folder into your configured user skills directory. For a setup using `~/.codex/skills`:

```sh
mkdir -p ~/.codex/skills
cp -R skills/annotated-equations ~/.codex/skills/
```

If that destination already exists, back it up or review local modifications before replacing it. Keep the whole folder, including LICENSE and NOTICE: the instructions refer to its scripts, references, and examples. Start a new chat/session and invoke `$annotated-equations`. If it is not discovered, check the host's configured skill directory; copying to an arbitrary folder does not register a skill.

Other agents that support folder-based Agent Skills can use the same `skills/annotated-equations` folder in their own skill location. Discovery and invocation syntax depend on the host. The host needs file access, code execution, and image inspection to complete the full workflow. A text-only host can discuss annotations but cannot claim to have rendered and visually checked them.

## 3. Install rendering dependencies

Create a virtual environment beside the copied skill:

```sh
python3 -m venv ~/.codex/skills/annotated-equations/.venv
~/.codex/skills/annotated-equations/.venv/bin/python -m pip install -r ~/.codex/skills/annotated-equations/requirements.txt
```

Use that Python executable for rendering. Python 3.9+ and Matplotlib are required. Matplotlib includes the default fonts; no external LaTeX installation or OpenAI API key is needed. Do not copy a virtual environment between computers.

## 4. Check the installation

Render one bundled example to a new output directory:

```sh
~/.codex/skills/annotated-equations/.venv/bin/python \
  ~/.codex/skills/annotated-equations/scripts/render_equation.py \
  ~/.codex/skills/annotated-equations/examples/area.json \
  --output ./equation-install-check
```

Expect four SVGs, four PNGs, an editable JSON file, caption/alt text, and a checks report. Exit code 0 means the automated layout checks passed. Open the PNGs as well: successful execution does not establish visual or mathematical quality.

Now try:

> Use $annotated-equations to explain the difference between the goat's reachable volume and its reachable fraction. Follow the book examples, but use my presentation's colors.

## Update

From the cloned repository, run `git pull --ff-only`. The installed folder is a copy, so pulling does not update it. Review changes, back up any installed modifications, replace the installed folder with the updated complete skill, and update its virtual environment from `requirements.txt` if dependencies changed. Start a new chat/session after updating.

## Remove

Remove the installed `annotated-equations` folder from your agent's skill directory when you no longer need it. This is separate from the repository clone and from any figures you exported. Keep those if you want reproducible source or access to previous work.

## Common problems

| What happened | What to check |
| --- | --- |
| Clone fails | Check the public repository URL, your network, and whether Git is installed. No GitHub login is required for HTTPS cloning. |
| The agent cannot find the skill | Check its configured skill directory, complete folder copy, and new-session discovery. |
| `No module named matplotlib` | Use the virtual environment's Python, not a different `python3`. |
| A math expression fails | This renderer supports Matplotlib mathtext, not arbitrary LaTeX packages or macros. See the rendering reference. |
| Exit code 1 | Files were written, but the checks report contains layout/readability problems. Revise and rerender. |
| Exit code 2 | The JSON input or rendering failed. Read the printed error. |
| PNG looks right but SVG looks wrong on a slide | SVG backgrounds are transparent; use the matching theme/background or the opaque PNG. |

Continue with [use and reproduction](use.md).

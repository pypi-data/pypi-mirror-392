# Hypersonic-HeyGen

**Phase-1 · Educational CLI · v0.1.0**

`Hypersonic-HeyGen` is a tiny command-line tool, `hayg`, that drops a ready-to-run **HeyGen streaming avatar** notebook into your working folder.

The generated notebook walks through a minimal, classroom-friendly flow:

1. Capture your **HeyGen API key** safely  
2. Create a **streaming session** and **session token**  
3. Fill an HTML viewer template with session details  
4. Render the avatar **inline in Jupyter**  
5. Send a sample text task  
6. Close the session cleanly

The focus is on **clarity and teaching**, not on building a full production stack.

---

## Table of Contents

1. [Installation (Part 1)](#installation-part1)
   - [Requirements](#requirements)
   - [Virtual environments (recommended)](#virtual-environments-recommended)
   - [Install from PyPI](#install-from-pypi)
   - [Install from TestPyPI](#install-from-testpypi)
   - [Using a wheel file directly](#using-a-wheel-file-directly)
   - [Install from source](#install-from-source)
   - [Upgrade / uninstall](#upgrade--uninstall)
2. [CLI usage & workflow (Part 2)](#cli-usage--workflow-part2)
   - [Quick start](#quick-start)
   - [Command-line options](#command-line-options)
   - [Typical teaching workflow](#typical-teaching-workflow)
3. [Inside the generated notebook (Part 3)](#inside-the-generated-notebook-part3)
   - [0) Overall flow](#0-overall-flow)
   - [HeyGen docs referenced](#heygen-docs-referenced)
   - [1) Setup & imports](#1-setup--imports)
   - [2) API key handling](#2-api-key-handling)
   - [3) Streaming endpoints & headers](#3-streaming-endpoints--headers)
   - [4) Helper functions](#4-helper-functions)
   - [5) Avatar, voice & pose inputs](#5-avatar-voice--pose-inputs)
   - [6) Start a streaming session](#6-start-a-streaming-session)
   - [7) Prepare and fill `viewer.html`](#7-prepare-and-fill-viewerhtml)
   - [8) Launch the inline viewer](#8-launch-the-inline-viewer)
   - [9) Send a sample text task](#9-send-a-sample-text-task)
   - [10) Close the session](#10-close-the-session)
4. [Further study & example projects](#further-study--example-projects)
5. [Project layout](#project-layout)
6. [License](#license)
7. [Author](#author)

---

<a id="installation-part1"></a>
## 1. Installation (Part 1)

This section mirrors the detailed installation style used in the earlier **hypersonic-eda** project, but adapted for the HeyGen avatar workflow and the `hayg` CLI.

### Requirements

- **Python**: 3.8 or later
- **Jupyter** (or JupyterLab / VS Code with notebook support) to run the generated `.ipynb`
- A **HeyGen account** and **API key**

The package itself is pure Python and very small; it ships a notebook template and a simple CLI, with no heavy runtime dependencies.

---

### Virtual environments (recommended)

To keep things tidy, use a virtual environment. The exact commands depend on your OS and Python setup.

#### Windows (PowerShell / Command Prompt)

```bash
# Pick a folder for your work
mkdir HeyGenDemo
cd HeyGenDemo

# Create a venv
python -m venv .venv

# Activate it
# PowerShell:
. .venv/Scripts/Activate.ps1
# or CMD:
rem .venv\Scripts\activate.bat
```

#### macOS / Linux

```bash
mkdir HeyGenDemo
cd HeyGenDemo

python3 -m venv .venv
source .venv/bin/activate
```

Once activated, `pip` and `python` will only affect this environment.

---

### Install from PyPI

When the package is published to the main index:

```bash
# Windows (inside venv)
python -m pip install hypersonic-heygen

# macOS / Linux
python3 -m pip install hypersonic-heygen
```

`pip` will:

- Download the **universal wheel** (`py3-none-any`) for your platform
- Install the Python package `hypersonic_HeyGen`
- Register the console script `hayg` on your PATH (inside the venv)

#### Verify the installation

```bash
python -c "import hypersonic_HeyGen as h; print(getattr(h, '__version__', 'unknown'))"
hayg --help
```

You should see the version printed and a short help message describing the CLI.

---

### Install from TestPyPI

For pre-release testing:

```bash
python -m pip install -i https://test.pypi.org/simple/ hypersonic-heygen \
  --extra-index-url https://pypi.org/simple
```

This tells `pip`:

- “Look on **TestPyPI** first for this project”
- Fall back to the main PyPI index for any dependencies

You can use the same verification commands afterward.

---

### Using a wheel file directly

If you have already built or downloaded a wheel
(e.g. `Hypersonic_HHeyGen-0.1.0-py3-none-any.whl`):

```bash
# Replace the filename with the actual wheel you have
python -m pip install ./Hypersonic_HHeyGen-0.1.0-py3-none-any.whl
```

This is useful when:

- Installing on a machine without internet access
- Testing locally built artifacts (`dist/*.whl` from `python -m build`)

---

### Install from source

If you are working directly from the project repository:

```bash
# From the repository root
python -m pip install .
```

For editable development (changes to the package are picked up immediately):

```bash
python -m pip install -e .
```

This will still register the `hayg` console script.

---

### Upgrade / uninstall

To upgrade to the latest version from PyPI:

```bash
python -m pip install --upgrade hypersonic-heygen
```

To uninstall:

```bash
python -m pip uninstall hypersonic-heygen
```

---

<a id="cli-usage--workflow-part2"></a>
## 2. CLI usage & workflow (Part 2)

The CLI is intentionally minimal—roughly the same pattern as the earlier *hypersonic* tools, but tailored for HeyGen.

### Quick start

From any working directory (with your venv activated):

```bash
hayg
```

This creates a notebook named:

```text
HeyGen.ipynb
```

in the **current folder**.

To choose your own filename:

```bash
hayg --output MyHeyGenDemo.ipynb
# or
hayg -o MyHeyGenDemo.ipynb
```

Then launch Jupyter / JupyterLab in that folder and open the notebook:

```bash
jupyter notebook
# or
jupyter lab
```

---

### Command-line options

```bash
hayg --help
```

The CLI currently supports:

- `--output`, `-o`  
  Path to the output notebook file.  
  Default: `HeyGen.ipynb` in the current directory.

There is no provider or avatar argument: this tool is dedicated to **HeyGen’s streaming avatar** workflow.

---

### Typical teaching workflow

1. **Create a clean folder** for your class or lab.
2. **Activate a venv** and install `hypersonic-heygen`.
3. Run:

   ```bash
   hayg --output ClassDemo.ipynb
   ```

4. Open `ClassDemo.ipynb` in Jupyter.
5. Walk students through each cell, letting them:
   - Paste their own **HeyGen API key**
   - Choose their own **avatar / voice**
   - Launch and interact with the avatar inline
6. Encourage them to duplicate the notebook and tweak it for their own experiments.

---

<a id="inside-the-generated-notebook-part3"></a>
## 3. Inside the generated notebook (Part 3)

This section summarizes the structure and logic of `HeyGen.ipynb`, extracted and condensed from the actual notebook template shipped with the package.

The notebook is heavily commented and designed for **step-by-step teaching**.

---

### 0) Overall flow

The first markdown cell outlines the plan:

1. Capture your **HeyGen API key**
2. Define streaming **endpoints** and **headers**
3. Create a **new streaming session**
4. Request a **session token**
5. Generate a filled **HTML viewer**
6. Render the viewer inline
7. Send a **sample text task**
8. Close the session

This keeps every stage visible and debuggable during a live demonstration.

---

### HeyGen docs referenced

The notebook links back to specific HeyGen documentation pages, so learners can see the API in its original context:

- **Streaming API overview** – high-level explanation of the streaming avatar API and WebRTC flow  
- **Create New Session** – starts a streaming session and returns SDP offer and ICE configuration  
- **Create Session Token** – issues a short-lived token for the browser side client  
- **Send Task** – sends a task (here: a text message to speak) to the active session  
- **Close Session** – ends the streaming session
- **List All Avatars (V2)** – discover `avatar_id` values you can use  
- **List All Voices (V2)** – browse available voices and note their IDs  

The README you’re reading is meant to be read alongside those docs when you want more depth.

---

### 1) Setup & imports

The first code cell:

- Imports standard modules: `json`, `os`, `requests`, `pathlib.Path`, and `getpass`
- Imports `IFrame` / `display` from `IPython.display`
- Defines a simple `debug()` helper that prints messages with a `[DEBUG]` prefix

This keeps diagnostics lightweight and visible in the notebook output.

---

### 2) API key handling

The next section obtains your **HeyGen API key** in a secure, repeatable way:

```python
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY") or getpass("Enter HEYGEN_API_KEY: ")

if not HEYGEN_API_KEY:
    raise RuntimeError("HEYGEN_API_KEY is required to run this notebook.")
```

Key points:

- If `HEYGEN_API_KEY` is already set in your environment, it’s used directly.
- Otherwise, you are prompted via `getpass()`, so the key is never echoed.
- The notebook refuses to continue without a valid key.

On macOS / Linux you might set the variable in a shell before launching Jupyter:

```bash
export HEYGEN_API_KEY="sk_..."
jupyter lab
```

On Windows PowerShell:

```powershell
setx HEYGEN_API_KEY "sk_..."
# then open a new terminal / Jupyter session
```

---

### 3) Streaming endpoints & headers

The notebook then defines core URLs for the streaming workflow:

```python
BASE = "https://api.heygen.com/v1"
API_STREAM_NEW   = f"{BASE}/streaming.new"          # Create New Session
API_CREATE_TOKEN = f"{BASE}/streaming.create_token" # Create Session Token
API_STREAM_TASK  = f"{BASE}/streaming.task"         # Send Task
API_STREAM_STOP  = f"{BASE}/streaming.stop"         # Close Session
```

It also builds two kinds of HTTP headers:

- A default header with `X-API-KEY: <HEYGEN_API_KEY>`
- A “bearer token” header used when calling endpoints that require a **session token**

Two small helper functions wrap `requests.post(...)` so students don’t have to write repetitive boilerplate each time.

---

### 4) Helper functions

A dedicated section introduces the key functions:

- `new_session(avatar_id, voice_id=None)`  
  Calls the *Create New Session* endpoint and returns a dictionary with:
  - `session_id`
  - `offer_sdp`
  - `rtc_config` (ICE server configuration)
- `create_session_token(session_id)`  
  Calls the *Create Session Token* endpoint and returns a token string.
- `send_text_to_avatar(session_id, session_token, text)`  
  Sends a “repeat” text task via the *Send Task* endpoint, telling the avatar what to say.
- `stop_session(session_id, session_token)`  
  Calls the *Close Session* endpoint to finish the session and clean up resources.

These functions keep the main demo code compact and give clear extension points for custom experiments.

---

### 5) Avatar, voice & pose inputs

Rather than hard-coding constants, the notebook prompts you to enter your IDs:

```python
avatar_id = input("Enter Avatar ID name: ")   # e.g. "June_HR_public"
voice_id  = input("Enter Voice ID string: ")  # e.g. "68dedac41a9f46a6a4271a95c733823c"
pose_name = input("Enter Pose Name: ")        # e.g. "June HR"
```

To find valid IDs, you can:

- Use the **List All Avatars (V2)** endpoint in the HeyGen console or via API  
- Use the **List All Voices (V2)** endpoint to see available voices and their IDs  

The notebook keeps example values as comments so you can quickly try a known-good configuration during demos.

---

### 6) Start a streaming session

Once avatar and voice are chosen, the notebook starts a session:

```python
created = new_session(avatar_id, voice_id)
SESSION_ID = created["session_id"]
OFFER_SDP  = created["offer_sdp"]
RTC_CONFIG = created["rtc_config"]

SESSION_TOKEN = create_session_token(SESSION_ID)
```

It prints short debug messages with a truncated session ID and token length so you can confirm that:

- The HeyGen API key works
- The selected avatar and voice are valid
- The streaming backend is reachable from your machine

At this point the backend is ready; the remaining steps are about wiring the browser / HTML viewer to this session.

---

### 7) Prepare and fill `viewer.html`

The notebook contains an HTML template string, `TEMPLATE`, which is written to `viewer.html` if the file does not already exist.

That template:

- Loads the appropriate HeyGen streaming libraries via `<script>` tags
- Sets up a basic layout with:
  - A title bar
  - A main **16:9 video area**
  - A minimal control area (mute, etc.)
- Contains placeholder tokens to be replaced at runtime:
  - `__SESSION_TOKEN__`
  - `__SESSION_ID__`
  - `__AVATAR_NAME__`
  - `__OFFER_SDP__`
  - `__RTC_CONFIG__`

The notebook then fills those placeholders and writes `viewer_filled.html`:

```python
filled = (
    html_path.read_text(encoding="utf-8")
    .replace("__SESSION_TOKEN__", SESSION_TOKEN)
    .replace("__AVATAR_NAME__", pose_name or avatar_id)
    .replace("__SESSION_ID__", SESSION_ID)
    .replace("__OFFER_SDP__", json.dumps(OFFER_SDP)[1:-1])
    .replace("__RTC_CONFIG__", json.dumps(RTC_CONFIG or {}))
)

filled_path = Path("viewer_filled.html")
filled_path.write_text(filled, encoding="utf-8")
```

Conceptually, this mirrors how the official Next.js demo passes session details to the client side, but compressed into a single self-contained HTML file.  

---

### 8) Launch the inline viewer

To keep everything inside the notebook, the viewer is displayed with an `IFrame`:

```python
from pathlib import Path
from IPython.display import IFrame, display

p = Path("viewer_filled.html").resolve()
display(IFrame(src=str(p), width="100%", height=380))
```

This gives you a live, embedded avatar without any extra browser windows.

(There is also a commented-out example of opening the same HTML file in an external browser if you prefer.)

---

### 9) Send a sample text task

To prove that the session is active and the avatar is responsive, the notebook sends a simple text message:

```python
send_text_to_avatar(
    SESSION_ID,
    SESSION_TOKEN,
    "Hello! I am your HeyGen avatar inside Jupyter Notebook."
)
```

Under the hood this calls the **Send Task** endpoint with:

- `task_type="repeat"`
- `task_mode="sync"`
- A `text` payload

You can run this cell multiple times with different phrases, or adapt it to accept user input from a text field.

---

### 10) Close the session

Finally, the notebook provides a clean shutdown:

```python
stop_session(SESSION_ID, SESSION_TOKEN)
print("Session stopped.")
```

This signals to the HeyGen backend that the streaming session is finished and releases associated resources.

Encourage students to **always** run this cell at the end of their experiments.

---

## 4. Further study & example projects

Once you understand the notebook flow, you can explore more advanced integration patterns:

- **HeyGen Streaming API docs and guides** – full reference, including integration patterns and WebRTC details  
- **Interactive Avatar Next.js Demo** – official Next.js sample showing a multi-page UI, token handling, and real-world UX patterns  
- **Streaming Avatar SDK Reference** – deeper client-side SDK documentation, event handling, and quality settings for rich front-ends  
- **Integration guide** at HeyGen Labs – broader architectural overview and deployment-oriented guidance:  
  https://labs.heygen.com/integration-guide

You can treat `HeyGen.ipynb` as the “minimal lab version,” then migrate concepts into a web or mobile app based on the official samples above.

---

## 5. Project layout

For maintainers and advanced users, the installed project structure looks like:

```text
.
├─ LICENSE
├─ README.md
├─ pyproject.toml
├─ MANIFEST.in
└─ src/
   └─ hypersonic_HeyGen/
      ├─ __init__.py          # version, package metadata
      ├─ hayg.py              # CLI entry point (console script)
      └─ templates/
         └─ HeyGen.ipynb      # bundled notebook template
```

The only “magic” performed by `hayg` is:

1. Locating `templates/HeyGen.ipynb` inside the installed package
2. Copying it to the path you specify with `--output`

This keeps the tool transparent and easy to maintain.

---

## 6. License

MIT License – see `LICENSE` in the distribution for full details.

---

## 7. Author

Author: Krish Ambady  
email: ambay1960@hotmail.com

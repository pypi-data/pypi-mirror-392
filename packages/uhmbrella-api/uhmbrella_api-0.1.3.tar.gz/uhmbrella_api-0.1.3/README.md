# Uhmbrella AIMD API – CLI and HTTP reference

This document describes how to use the `uhmbrella-api` Python package via:

- The CLI command: `uhmbrella-api`
- The equivalent raw HTTP API calls (for curl or backend use)

It only covers behaviour that exists in the current `cli.py`.

Default base URL:

```text
https://api.uhmbrella.io
```

You can override this with:

- `--api-base https://your-api-host`
- or environment variable `UHM_API_BASE`

All public endpoints require:

```http
x-api-key: YOUR_API_KEY
```

You can supply the API key either as a CLI flag or via environment variable.

---

## 0. Authentication and globals

### CLI

You can pass the API key directly:

```bash
uhmbrella-api --api-key YOUR_API_KEY usage
```

Or set an environment variable:

```bash
export UHM_API_KEY="YOUR_API_KEY"
uhmbrella-api usage
```

The CLI understands the following global options:

- `--api-key`  - API key for auth (or set `UHM_API_KEY`)
- `--api-base` - override the API base URL

These flags can appear anywhere in the command. For example, all of these are equivalent:

```bash
uhmbrella-api --api-key KEY usage
uhmbrella-api usage --api-key KEY
uhmbrella-api usage --api-key=KEY
```

The CLI normalises the arguments before parsing.

---

## 1. Check usage

Shows current quota and usage for the API key.

### CLI

```bash
uhmbrella-api usage --api-key YOUR_API_KEY
```

### HTTP

```bash
curl "https://api.uhmbrella.io/usage" -H "x-api-key: YOUR_API_KEY"
```

The response is a JSON object similar to:

```json
{
  "user_id": "test_user",
  "plan_name": "trial_100min",
  "quota_seconds": 6000,
  "used_seconds": 765,
  "remaining_seconds": 5235
}
```

---

## 2. Synchronous scan

The `scan` command uploads audio for immediate analysis.

Behaviour:

- If `--input` points to a single file, the CLI calls `POST /v1/analyze`.
- If `--input` points to a directory, the CLI calls `POST /v1/analyze-batch` for up to 40 files.
- Results are written as JSON files in the chosen output directory.

During upload, a `tqdm` progress bar shows bytes sent.

### 2.1 Single file

Results are saved as `<output-dir>/<filename>.analysis.json`.

#### CLI

```bash
uhmbrella-api scan --input "/path/to/audio.mp3" --output-dir "./uhm_results" --api-key YOUR_API_KEY
```

Key options:

- `--input`      - path to an audio file
- `--output-dir` - directory to write JSON results (default `./uhm_results`)

#### HTTP

```bash
curl -X POST "https://api.uhmbrella.io/v1/analyze" -H "x-api-key: YOUR_API_KEY" -F "file=@/path/to/audio.mp3"
```

The HTTP response is a single analysis object that includes:

- predicted class percentages
- segments and segmentsVox arrays
- audio length and billed seconds
- usage details for the API key

### 2.2 Small folder (up to 40 files)

If the input is a folder, the CLI will:

- collect audio files based on patterns
- upload them in a batch to `/v1/analyze-batch`
- write one JSON result per file

If more than 40 files are found, the CLI exits with an error and asks you to use `jobs create` instead.

#### CLI

```bash
uhmbrella-api scan --input "./audio_folder" --output-dir "./uhm_results" --recursive --api-key YOUR_API_KEY
```

Options:

- `--input`      - directory containing audio files
- `--output-dir` - directory to write JSON results
- `--recursive`  - recurse into subdirectories
- `--patterns`   - override patterns, for example:
  ```bash
  --patterns "*.wav" "*.flac"
  ```

Default patterns are:

```text
*.mp3 *.wav *.flac *.m4a
```

#### HTTP

```bash
curl -X POST "https://api.uhmbrella.io/v1/analyze-batch" -H "x-api-key: YOUR_API_KEY" -F "files=@/path/to/track1.wav" -F "files=@/path/to/track2.mp3"
```

The response contains:

- `results` - list of per file analysis objects
- `usage`   - updated usage summary

Each result item has the same shape as a single file analysis.

---

## 3. Create async job

For larger sets of files, the CLI supports async jobs via the `/v1/jobs` endpoint. Files are uploaded once and processed in the background.

### CLI

```bash
uhmbrella-api jobs create --input "./audio_folder" --recursive --api-key YOUR_API_KEY
```

Options:

- `--input`     - file or directory
- `--recursive` - recurse into directories when `--input` is a folder
- `--patterns`  - override default file patterns

Example with custom patterns:

```bash
uhmbrella-api jobs create --input "./audio_folder" --recursive --patterns "*.wav" "*.flac" --api-key YOUR_API_KEY
```

The CLI prints the JSON response and, if possible, a convenient reminder of follow up commands, for example:

```text
[JOB CREATED]
{
  "job_id": "7f3f696c-8052-43f8-a5c5-08b3767b030e",
  "status": "queued",
  "total_files": 123,
  ...
}

You can now run:
  uhmbrella-api jobs status --job-id 7f3f696c-8052-43f8-a5c5-08b3767b030e
  uhmbrella-api jobs results --job-id 7f3f696c-8052-43f8-a5c5-08b3767b030e --output-dir ./results
```

Uploads use `tqdm` to show total bytes sent.

### HTTP

```bash
curl -X POST "https://api.uhmbrella.io/v1/jobs" -H "x-api-key: YOUR_API_KEY" -F "files=@/path/to/track1.wav" -F "files=@/path/to/track2.wav"
```

The HTTP response includes at least:

- `job_id`
- `status`
- `total_files`
- fields relating to billed and remaining seconds

---

## 4. Job status

Check the status and progress of a previously created job.

### CLI

```bash
uhmbrella-api jobs status --job-id JOB_ID --api-key YOUR_API_KEY
```

The CLI prints the JSON returned by the API.

### HTTP

```bash
curl "https://api.uhmbrella.io/v1/jobs/JOB_ID/status" -H "x-api-key: YOUR_API_KEY"
```

The response includes fields such as:

- `job_id`
- `status` (for example queued, processing, done, error, cancelling, cancelled)
- `total_files`
- counts per status
- quota and usage information

---

## 5. Job results

Fetch per file results for a job. The CLI can either print the full JSON or write individual result files to disk.

### CLI

```bash
uhmbrella-api jobs results --job-id JOB_ID --output-dir "./results" --api-key YOUR_API_KEY
```

Behaviour:

- Always prints a summary to stdout:
  - `job_id`
  - `status`
  - `results_count`
- If `--output-dir` is omitted:
  - prints the full raw JSON to stdout and exits.
- If `--output-dir` is provided:
  - creates the directory if needed
  - for each item in `results`:
    - if `status == "done"`, writes `<filename>.analysis.json`
    - otherwise, writes `<filename>.error.json`

This lets you separate successful analyses from errors.

### HTTP

```bash
curl "https://api.uhmbrella.io/v1/jobs/JOB_ID/results" -H "x-api-key: YOUR_API_KEY"
```

The response JSON includes:

- overall `job_id` and `status`
- `results`: a list where each item contains:
  - `filename`
  - `status`
  - possibly `error`
  - `result` (same shape as `/v1/analyze`) when status is done

---

## 6. Cancel job

Request cooperative cancellation of a long running job. The worker finishes the current file then stops.

### CLI

```bash
uhmbrella-api jobs cancel --job-id JOB_ID --api-key YOUR_API_KEY
```

The CLI prints the JSON response from the API.

### HTTP

```bash
curl -X POST "https://api.uhmbrella.io/v1/jobs/JOB_ID/cancel" -H "x-api-key: YOUR_API_KEY"
```

Typical responses:

If cancellation is accepted:

```json
{
  "job_id": "JOB_ID",
  "status": "cancelling"
}
```

If the job has already finished or been cancelled, you get its current status instead, for example:

```json
{
  "job_id": "JOB_ID",
  "status": "done"
}
```

or

```json
{
  "job_id": "JOB_ID",
  "status": "cancelled"
}
```

---

## 7. Environment helper

The `env` subcommand prints OS specific commands for setting your API key in the environment.

### CLI

```bash
uhmbrella-api env --api-key YOUR_API_KEY
```
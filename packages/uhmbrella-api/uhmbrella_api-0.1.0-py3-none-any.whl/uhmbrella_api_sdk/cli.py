import argparse
import json
import os
import sys
import platform
from pathlib import Path
from typing import List, Tuple
import requests
from tqdm import tqdm


DEFAULT_API_BASE = os.environ.get("UHM_API_BASE", "https://api.uhmbrella.io")


# -------------------- Helpers --------------------


def resolve_api_key(args) -> str:
    """
    Resolve API key from CLI args or environment.
    """
    if getattr(args, "api_key", None):
        return args.api_key

    env_key = os.environ.get("UHM_API_KEY")
    if env_key:
        return env_key

    print(
        "ERROR: API key not provided.\n"
        "Use --api-key, set UHM_API_KEY environment variable,\n"
        "or run: uhmbrella-api env --api-key YOUR_KEY",
        file=sys.stderr,
    )
    sys.exit(1)


def resolve_api_base(args) -> str:
    """
    Resolve API base URL from CLI args or environment.
    """
    if getattr(args, "api_base", None):
        return args.api_base.rstrip("/")
    return DEFAULT_API_BASE.rstrip("/")


def print_json(data) -> None:
    """
    Pretty-print JSON to stdout.
    """
    print(json.dumps(data, indent=2, sort_keys=False))


def find_audio_files(
    input_path: Path,
    recursive: bool = False,
    patterns: Tuple[str, ...] = ("*.mp3", "*.wav", "*.flac", "*.m4a"),
) -> List[Path]:
    """
    Find audio files under a given path.
    """
    files: List[Path] = []
    if input_path.is_file():
        files.append(input_path)
        return files

    if not input_path.is_dir():
        print(f"ERROR: Input path is not a file or directory: {input_path}", file=sys.stderr)
        sys.exit(1)

    for pattern in patterns:
        if recursive:
            for p in input_path.rglob(pattern):
                if p.is_file():
                    files.append(p)
        else:
            for p in input_path.glob(pattern):
                if p.is_file():
                    files.append(p)

    return sorted(set(files))


def build_files_payload_with_progress(
    files_list: List[Path],
    field_name: str,
    desc: str,
):
    """
    Build a requests-compatible files payload where each file is wrapped
    with a tqdm progress bar that tracks bytes read during upload.

    Returns (files_payload, opened_files, pbar).
    Caller must close all opened_files and pbar.
    """
    total_bytes = 0
    for p in files_list:
        try:
            total_bytes += p.stat().st_size
        except OSError:
            # If we cannot stat the file, just skip its size.
            pass

    pbar = tqdm(
        total=total_bytes,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=desc,
        disable=(total_bytes == 0),
    )

    class TqdmFile:
        def __init__(self, f):
            self._f = f

        def read(self, n):
            data = self._f.read(n)
            if data:
                pbar.update(len(data))
            return data

        def __getattr__(self, name):
            # Delegate everything else to the underlying file (e.g. fileno, tell, seek)
            return getattr(self._f, name)

    opened_files = []
    files_payload = []

    for p in files_list:
        f = p.open("rb")
        opened_files.append(f)
        wrapped = TqdmFile(f)
        files_payload.append(
            (field_name, (p.name, wrapped, "application/octet-stream"))
        )

    return files_payload, opened_files, pbar


# -------------------- Commands --------------------


def cmd_usage(args) -> None:
    api_key = resolve_api_key(args)
    api_base = resolve_api_base(args)

    url = f"{api_base}/usage"
    headers = {"x-api-key": api_key}

    resp = requests.get(url, headers=headers, timeout=60)
    if resp.status_code != 200:
        print(f"ERROR: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    print_json(resp.json())


MAX_SYNC_FILES = 40  # hard cap for scan() directory mode


def cmd_scan(args) -> None:
    """
    Simple client-side scan helper:
    - If input is a file: send one request to /v1/analyze
    - If input is a directory:
        * If <= MAX_SYNC_FILES: send one request to /v1/analyze-batch
        * If >  MAX_SYNC_FILES: refuse and tell user to use jobs create
    - Save results to JSON on disk
    """
    api_key = resolve_api_key(args)
    api_base = resolve_api_base(args)

    input_path = Path(args.input).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    headers = {"x-api-key": api_key}

    # ---------------- Single file ----------------
    if input_path.is_file():
        url = f"{api_base}/v1/analyze"

        # Use the same helper with a single file, field name "file"
        files_payload, opened_files, pbar = build_files_payload_with_progress(
            [input_path],
            field_name="file",
            desc="Uploading file",
        )

        try:
            resp = requests.post(url, headers=headers, files=files_payload, timeout=600)
        finally:
            for f in opened_files:
                try:
                    f.close()
                except Exception:
                    pass
            pbar.close()

        if resp.status_code != 200:
            print(f"ERROR: {resp.status_code} {resp.text}", file=sys.stderr)
            sys.exit(1)

        data = resp.json()

        out_path = output_dir / f"{input_path.name}.analysis.json"
        with out_path.open("w", encoding="utf-8") as f_out:
            json.dump(data, f_out, indent=2)

        print(f"[OK] Saved analysis to: {out_path}")
        return

    # ---------------- Directory mode ----------------
    files_list = find_audio_files(
        input_path,
        recursive=args.recursive,
        patterns=tuple(args.patterns) if args.patterns else ("*.mp3", "*.wav", "*.flac", "*.m4a"),
    )

    if not files_list:
        print(f"ERROR: No matching audio files found in {input_path}", file=sys.stderr)
        sys.exit(1)

    if len(files_list) > MAX_SYNC_FILES:
        print(
            f"ERROR: scan() is limited to {MAX_SYNC_FILES} files for synchronous use.\n"
            f"Found {len(files_list)} files in {input_path}.\n\n"
            f"Please use the async jobs API instead, for example:\n"
            f"  uhmbrella-api jobs create --input \"{input_path}\"\n"
            f"then:\n"
            f"  uhmbrella-api jobs status  --job-id <id>\n"
            f"  uhmbrella-api jobs results --job-id <id> --output-dir {output_dir}\n",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[INFO] Found {len(files_list)} audio files. Uploading synchronous batch...")

    url = f"{api_base}/v1/analyze-batch"

    files_payload, opened_files, pbar = build_files_payload_with_progress(
        files_list,
        field_name="files",
        desc="Uploading batch",
    )

    try:
        resp = requests.post(url, headers=headers, files=files_payload, timeout=3600)
    finally:
        for f in opened_files:
            try:
                f.close()
            except Exception:
                pass
        pbar.close()

    if resp.status_code != 200:
        print(f"ERROR: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()

    # Expecting { total_files, results: [ ... ] , usage: {...} }
    results = data.get("results", [])
    if not isinstance(results, list):
        print("[WARN] Unexpected response format; dumping raw JSON.")
        print_json(data)
        return

    for item in results:
        filename = item.get("uhm_filename") or item.get("filename") or "unknown"
        out_path = output_dir / f"{filename}.analysis.json"
        with out_path.open("w", encoding="utf-8") as f_out:
            json.dump(item, f_out, indent=2)
        print(f"[OK] Saved: {out_path}")

    usage = data.get("usage")
    if usage:
        print("\n[USAGE]")
        print_json(usage)


def cmd_jobs_create(args) -> None:
    """
    Create a bulk job:
      uhmbrella-api jobs create --input ./audio_dir
    """
    api_key = resolve_api_key(args)
    api_base = resolve_api_base(args)

    input_path = Path(args.input).expanduser()

    files_list = find_audio_files(
        input_path,
        recursive=args.recursive,
        patterns=tuple(args.patterns) if args.patterns else ("*.mp3", "*.wav", "*.flac", "*.m4a"),
    )

    if not files_list:
        print(f"ERROR: No matching audio files found in {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Found {len(files_list)} audio files. Creating job...")

    url = f"{api_base}/v1/jobs"
    headers = {"x-api-key": api_key}

    files_payload, opened_files, pbar = build_files_payload_with_progress(
        files_list,
        field_name="files",
        desc="Uploading job files",
    )

    try:
        resp = requests.post(url, headers=headers, files=files_payload, timeout=3600)
    finally:
        for f in opened_files:
            try:
                f.close()
            except Exception:
                pass
        pbar.close()

    if resp.status_code != 200:
        print(f"ERROR: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    print("[JOB CREATED]")
    print_json(data)

    job_id = data.get("job_id")
    if job_id:
        print(
            f"\nYou can now run:\n  uhmbrella-api jobs status --job-id {job_id}\n"
            f"  uhmbrella-api jobs results --job-id {job_id} --output-dir ./results"
        )
    else:
        print("[WARN] No job_id returned from server.")


def cmd_jobs_status(args) -> None:
    """
    Check status for a job:
      uhmbrella-api jobs status --job-id <id>
    """
    api_key = resolve_api_key(args)
    api_base = resolve_api_base(args)

    job_id = args.job_id
    if not job_id:
        print("ERROR: --job-id is required", file=sys.stderr)
        sys.exit(1)

    url = f"{api_base}/v1/jobs/{job_id}/status"
    headers = {"x-api-key": api_key}

    resp = requests.get(url, headers=headers, timeout=60)
    if resp.status_code != 200:
        print(f"ERROR: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    print_json(data)


def cmd_jobs_results(args) -> None:
    """
    Fetch results for a job and optionally write per-file JSONs:
      uhmbrella-api jobs results --job-id <id> --output-dir ./results
    """
    api_key = resolve_api_key(args)
    api_base = resolve_api_base(args)

    job_id = args.job_id
    if not job_id:
        print("ERROR: --job-id is required", file=sys.stderr)
        sys.exit(1)

    url = f"{api_base}/v1/jobs/{job_id}/results"
    headers = {"x-api-key": api_key}

    resp = requests.get(url, headers=headers, timeout=3600)
    if resp.status_code != 200:
        print(f"ERROR: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()

    # Always print a summary to stdout
    print("[JOB RESULTS]")
    print_json(
        {
            "job_id": data.get("job_id"),
            "status": data.get("status"),
            "results_count": len(data.get("results", [])),
        }
    )

    output_dir = args.output_dir
    if not output_dir:
        # If no output-dir: just dump full JSON and exit
        print("\n[FULL RAW RESULTS JSON]")
        print_json(data)
        return

    out_dir = Path(output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    results = data.get("results", [])
    for item in results:
        filename = item.get("filename") or "unknown"
        status = item.get("status")

        if status != "done":
            # Save error stub
            out_path = out_dir / f"{filename}.error.json"
            with out_path.open("w", encoding="utf-8") as f_out:
                json.dump(item, f_out, indent=2)
            print(f"[WARN] {filename} status={status}; saved error stub to {out_path}")
            continue

        result = item.get("result")
        if not result:
            out_path = out_dir / f"{filename}.error.json"
            with out_path.open("w", encoding="utf-8") as f_out:
                json.dump(item, f_out, indent=2)
            print(f"[WARN] {filename} has no result; saved stub to {out_path}")
            continue

        out_path = out_dir / f"{filename}.analysis.json"
        with out_path.open("w", encoding="utf-8") as f_out:
            json.dump(result, f_out, indent=2)
        print(f"[OK] Saved: {out_path}")


def cmd_jobs_cancel(args) -> None:
    """
    Cancel a bulk job:
      uhmbrella-api jobs cancel --job-id <id>
    """
    api_key = resolve_api_key(args)
    api_base = resolve_api_base(args)

    job_id = args.job_id
    if not job_id:
        print("ERROR: --job-id is required", file=sys.stderr)
        sys.exit(1)

    url = f"{api_base}/v1/jobs/{job_id}/cancel"
    headers = {"x-api-key": api_key}

    resp = requests.post(url, headers=headers, timeout=60)
    if resp.status_code != 200:
        print(f"ERROR: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    print_json(data)


def cmd_show_env(args) -> None:
    """
    Show OS-specific commands to set the UHM_API_KEY environment variable.

    Example:
      uhmbrella-api env --api-key YOUR_KEY
      UHM_API_KEY=YOUR_KEY uhmbrella-api env
    """
    # Try CLI flag first, then env var
    api_key = getattr(args, "api_key", None) or os.environ.get("UHM_API_KEY")
    if not api_key:
        print(
            "ERROR: No API key provided.\n"
            "Use --api-key or set UHM_API_KEY, for example:\n"
            "  uhmbrella-api env --api-key YOUR_KEY",
            file=sys.stderr,
        )
        sys.exit(1)

    system = platform.system()
    print(f"[INFO] Detected platform: {system}")

    if system == "Windows":
        print("\n# Windows (PowerShell or CMD)")
        print(f'setx UHM_API_KEY "{api_key}"')
        print("\nAfter running setx, close and reopen your terminal for it to take effect.")
    else:
        print("\n# Linux / macOS (bash / zsh)")
        print(f'export UHM_API_KEY="{api_key}"')
        print("To persist it, add the line above to your shell profile, e.g.:")
        print("  ~/.bashrc, ~/.bash_profile, or ~/.zshrc")


# -------------------- Main / Argparse --------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uhmbrella-api",
        description="Uhmbrella AIMD API CLI client",
    )

    parser.add_argument(
        "--api-base",
        default=None,
        help=f"Base URL for the API (default: {DEFAULT_API_BASE})",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key for authentication (or set UHM_API_KEY env var)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # usage
    p_usage = subparsers.add_parser("usage", help="Show current usage / quota for the API key")
    p_usage.set_defaults(func=cmd_usage)

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan a file or directory (synchronous)")
    p_scan.add_argument(
        "--input",
        required=True,
        help="Path to an audio file or directory",
    )
    p_scan.add_argument(
        "--output-dir",
        default="./uhm_results",
        help="Directory to write JSON results into (default: ./uhm_results)",
    )
    p_scan.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse into subdirectories when input is a folder",
    )
    p_scan.add_argument(
        "--patterns",
        nargs="*",
        default=None,
        help="Filename patterns to include (default: *.mp3 *.wav *.flac *.m4a)",
    )
    p_scan.set_defaults(func=cmd_scan)

    # jobs
    p_jobs = subparsers.add_parser("jobs", help="Manage bulk analysis jobs")
    jobs_sub = p_jobs.add_subparsers(dest="jobs_command", required=True)

    # jobs create
    p_jobs_create = jobs_sub.add_parser("create", help="Create a bulk job from a file or directory")
    p_jobs_create.add_argument(
        "--input",
        required=True,
        help="Path to an audio file or directory",
    )
    p_jobs_create.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse into subdirectories when input is a folder",
    )
    p_jobs_create.add_argument(
        "--patterns",
        nargs="*",
        default=None,
        help="Filename patterns to include (default: *.mp3 *.wav *.flac *.m4a)",
    )
    p_jobs_create.set_defaults(func=cmd_jobs_create)

    # jobs status
    p_jobs_status = jobs_sub.add_parser("status", help="Check status of a bulk job")
    p_jobs_status.add_argument(
        "--job-id",
        required=True,
        help="Job ID returned from 'jobs create'",
    )
    p_jobs_status.set_defaults(func=cmd_jobs_status)

    # jobs results
    p_jobs_results = jobs_sub.add_parser("results", help="Fetch results for a bulk job")
    p_jobs_results.add_argument(
        "--job-id",
        required=True,
        help="Job ID returned from 'jobs create'",
    )
    p_jobs_results.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Directory to write per-file JSON results. "
            "If omitted, prints full JSON to stdout only."
        ),
    )
    p_jobs_results.set_defaults(func=cmd_jobs_results)

    # jobs cancel
    p_jobs_cancel = jobs_sub.add_parser("cancel", help="Cancel a bulk job")
    p_jobs_cancel.add_argument(
        "--job-id",
        required=True,
        help="Job ID returned from 'jobs create'",
    )
    p_jobs_cancel.set_defaults(func=cmd_jobs_cancel)

    # env helper
    p_env = subparsers.add_parser("env", help="Show commands to set UHM_API_KEY in your shell")
    p_env.set_defaults(func=cmd_show_env)

    return parser


def normalize_argv(argv=None) -> List[str]:
    """
    Normalise argv so that global flags like --api-key / --api-base
    are always moved in front of the subcommands.

    This allows all of the following to work identically:

        uhmbrella-api --api-key KEY jobs create --input ./dir
        uhmbrella-api jobs create --api-key KEY --input ./dir
        uhmbrella-api jobs create --input ./dir --api-key KEY

    Also supports forms like --api-key=KEY.
    """
    if argv is None:
        argv = sys.argv[1:]

    args = list(argv)
    global_opts: List[str] = []
    value_flags = {"--api-key", "--api-base"}

    i = 0
    while i < len(args):
        token = args[i]

        # Handle --api-key=KEY or --api-base=URL forms
        handled_equals = False
        for flag in value_flags:
            if token.startswith(flag + "="):
                value = token.split("=", 1)[1]
                global_opts.append(flag)
                global_opts.append(value)
                del args[i]
                handled_equals = True
                break

        if handled_equals:
            continue

        if token in value_flags:
            value = None
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                value = args[i + 1]
                del args[i : i + 2]
            else:
                del args[i]

            global_opts.append(token)
            if value is not None:
                global_opts.append(value)
            continue

        i += 1

    return global_opts + args


def main(argv=None) -> None:
    parser = build_parser()
    norm_argv = normalize_argv(argv)
    args = parser.parse_args(norm_argv)
    args.func(args)


if __name__ == "__main__":
    main()

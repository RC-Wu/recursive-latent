#!/usr/bin/env python3
"""Resume-safe downloader for HunyuanDiT v1.1 Diffusers Distilled.

This helper exists because the remote network often terminates large
Hugging Face transfers with curl error 18. The script never deletes partial
files during ordinary failures; it checks exact byte sizes and resumes with
``curl --continue-at -`` until every required file matches the manifest.

Keep authentication out of argv. Pass an existing private curl config that
contains the Authorization header, or a private file containing just that
header. The header is copied only into temporary chmod-600 curl configs.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


REPO_ID = "Tencent-Hunyuan/HunyuanDiT-v1.1-Diffusers-Distilled"
DEFAULT_ENDPOINT = "https://huggingface.co"


@dataclass(frozen=True)
class RemoteFile:
    relpath: str
    size: int


FILES = [
    RemoteFile(".gitattributes", 1519),
    RemoteFile("README.md", 3812),
    RemoteFile("model_index.json", 636),
    RemoteFile("scheduler/scheduler_config.json", 566),
    RemoteFile("text_encoder/config.json", 840),
    RemoteFile("text_encoder/model.safetensors", 1_408_188_288),
    RemoteFile("text_encoder_2/config.json", 776),
    RemoteFile("text_encoder_2/model-00001-of-00002.safetensors", 4_993_585_936),
    RemoteFile("text_encoder_2/model-00002-of-00002.safetensors", 1_686_275_552),
    RemoteFile("text_encoder_2/model.safetensors.index.json", 19_885),
    RemoteFile("tokenizer/special_tokens_map.json", 695),
    RemoteFile("tokenizer/tokenizer_config.json", 1241),
    RemoteFile("tokenizer/vocab.txt", 316_627),
    RemoteFile("tokenizer_2/special_tokens_map.json", 416),
    RemoteFile("tokenizer_2/spiece.model", 4_309_802),
    RemoteFile("tokenizer_2/tokenizer_config.json", 861),
    RemoteFile("transformer/config.json", 488),
    RemoteFile("transformer/diffusion_pytorch_model.safetensors", 6_066_290_824),
    RemoteFile("vae/config.json", 730),
    RemoteFile("vae/diffusion_pytorch_model.safetensors", 334_643_268),
]


def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def log(line: str, log_path: Path | None = None) -> None:
    text = f"[{now()}] {line}"
    print(text, flush=True)
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(text + "\n")


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0


def read_auth_header(path: Path | None) -> str | None:
    if path is None:
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "Authorization:" in line:
            _, value = line.split("Authorization:", 1)
            return "Authorization:" + value.strip()
    return None


def curl_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def curl_config_text(
    *,
    url: str,
    output: Path,
    auth_header: str | None,
    proxy: str | None,
    connect_timeout: int,
    speed_time: int,
    speed_limit: int,
    retries: int,
) -> str:
    lines = [
        "location",
        "fail",
        "show-error",
        "continue-at = -",
        f"retry = {retries}",
        "retry-all-errors",
        "retry-delay = 5",
        f"connect-timeout = {connect_timeout}",
        f"speed-time = {speed_time}",
        f"speed-limit = {speed_limit}",
        f"output = {curl_quote(str(output))}",
        f"url = {curl_quote(url)}",
        'write-out = "HTTP=%{http_code} SIZE=%{size_download} TIME=%{time_total}\\n"',
    ]
    if proxy:
        lines.insert(10, f"proxy = {proxy}")
    if auth_header:
        lines.insert(10, f"header = {curl_quote(auth_header)}")
    return "\n".join(lines) + "\n"


def run_curl(args: argparse.Namespace, item: RemoteFile, auth_header: str | None, attempt: int) -> int:
    out_path = args.model_dir / item.relpath
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_dir = args.tmp_dir
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cfg_dir / f"curl_hydit_resume_{os.getpid()}_{attempt}_{Path(item.relpath).name}.cfg"
    url = f"{args.endpoint.rstrip('/')}/{REPO_ID}/resolve/main/{item.relpath}"
    cfg_path.write_text(
        curl_config_text(
            url=url,
            output=out_path,
            auth_header=auth_header,
            proxy=args.proxy,
            connect_timeout=args.connect_timeout,
            speed_time=args.speed_time,
            speed_limit=args.speed_limit,
            retries=args.curl_retries,
        ),
        encoding="utf-8",
    )
    cfg_path.chmod(0o600)
    try:
        with args.log.open("a", encoding="utf-8") as f:
            f.write(f"[{now()}] CURL_START {item.relpath} attempt={attempt} current={file_size(out_path)} expected={item.size}\n")
            rc = subprocess.call(["curl", "--config", str(cfg_path)], stdout=f, stderr=f)
            f.write(f"[{now()}] CURL_RC {item.relpath} attempt={attempt} rc={rc} size={file_size(out_path)} expected={item.size}\n")
        return rc
    finally:
        if args.keep_configs:
            log(f"kept private curl config: {cfg_path}", args.log)
        else:
            try:
                cfg_path.unlink()
            except FileNotFoundError:
                pass


def check_all(model_dir: Path) -> tuple[bool, list[str]]:
    return check_all_subset(model_dir, FILES)


def check_all_subset(model_dir: Path, files: list[RemoteFile]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for item in files:
        size = file_size(model_dir / item.relpath)
        if size != item.size:
            missing.append(f"{item.relpath}: {size}/{item.size}")
    return not missing, missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--auth-config", type=Path, default=None)
    parser.add_argument("--proxy", default="http://127.0.0.1:27890")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--tmp-dir", type=Path, default=Path("cache/tmp"))
    parser.add_argument("--log", type=Path, default=Path("logs/hunyuan_dit_resume_downloader_20260511.log"))
    parser.add_argument("--max-file-attempts", type=int, default=80)
    parser.add_argument("--curl-retries", type=int, default=8)
    parser.add_argument("--connect-timeout", type=int, default=30)
    parser.add_argument("--speed-time", type=int, default=300)
    parser.add_argument("--speed-limit", type=int, default=1024)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--keep-configs", action="store_true")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Download only this relative file path. May be passed multiple times.",
    )
    args = parser.parse_args()

    selected_files = FILES
    if args.only:
        wanted = set(args.only)
        selected_files = [item for item in FILES if item.relpath in wanted]
        missing_selection = sorted(wanted - {item.relpath for item in selected_files})
        if missing_selection:
            print("Unknown --only file(s): " + ", ".join(missing_selection), file=sys.stderr)
            return 64

    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.model_dir.mkdir(parents=True, exist_ok=True)
    auth_header = read_auth_header(args.auth_config)
    if args.auth_config and not auth_header:
        log(f"AUTH_HEADER_MISSING path={args.auth_config}", args.log)

    complete, missing = check_all_subset(args.model_dir, selected_files)
    if complete:
        log(f"MODEL_COMPLETE {args.model_dir}", args.log)
        return 0
    log("MODEL_INCOMPLETE " + "; ".join(missing), args.log)
    if args.check_only:
        return 2

    for item in selected_files:
        out_path = args.model_dir / item.relpath
        for attempt in range(1, args.max_file_attempts + 1):
            size = file_size(out_path)
            if size == item.size:
                log(f"SKIP_COMPLETE {item.relpath} size={size}", args.log)
                break
            if size > item.size:
                quarantine = out_path.with_name(out_path.name + f".oversize.{int(time.time())}")
                out_path.rename(quarantine)
                log(f"QUARANTINE_OVERSIZE {item.relpath} {size}>{item.size} -> {quarantine}", args.log)
                size = 0
            log(f"DOWNLOAD {item.relpath} attempt={attempt} current={size} expected={item.size}", args.log)
            rc = run_curl(args, item, auth_header, attempt)
            size_after = file_size(out_path)
            if size_after == item.size:
                log(f"COMPLETE {item.relpath} size={size_after}", args.log)
                break
            log(f"INCOMPLETE {item.relpath} rc={rc} size={size_after} expected={item.size}", args.log)
            time.sleep(min(30, 2 + attempt))
        else:
            log(f"GIVE_UP {item.relpath} size={file_size(out_path)} expected={item.size}", args.log)
            return 1

    complete, missing = check_all_subset(args.model_dir, selected_files)
    if complete:
        log(f"MODEL_COMPLETE {args.model_dir}", args.log)
        return 0
    log("MODEL_STILL_INCOMPLETE " + "; ".join(missing), args.log)
    return 1


if __name__ == "__main__":
    sys.exit(main())

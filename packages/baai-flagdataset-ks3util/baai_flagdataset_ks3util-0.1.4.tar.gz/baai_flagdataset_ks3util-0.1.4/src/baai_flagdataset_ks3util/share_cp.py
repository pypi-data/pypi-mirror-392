import pathlib
import subprocess
from collections import deque


from .baai_prepare import ks3util


def debug_cmd_share_cp(cmd_args):
    print(" ".join(cmd_args))


def share_cp_with_cmdargs_output(
        share_url,
        access_code,
        use_loc,
        max_parallel: int,
        config_path:str,
        prefix=None,
        key=None,
        debug=False
):

    local_dir = pathlib.Path(use_loc).absolute().__str__()

    cmd_args = [
        ks3util(),
        "share-cp",
        share_url,
        local_dir,
        "--access-code",
        access_code,
        "-c",
        config_path,
        "-u",
        "-j",
        f"{max_parallel}"
    ]

    if prefix:
        cmd_args.append("--prefix")
        cmd_args.append(prefix)

    if key:
        cmd_args.append("--key")
        cmd_args.append(key)

    if debug:
        debug_cmd_share_cp(cmd_args)


    process = subprocess.Popen(
        cmd_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        bufsize=1 # 行缓冲
    )

    output = deque([])
    while True:
        if len(output) > 2:
            p1 = output.popleft()
            p2 = output.popleft()
            p3 = "".join([p1, p2])
            if p3.count('[') == 2:
                start = p3.find('[')
                end = p3[start:]
                pbar_format_output(p3[start:end])
                output.appendleft(p3[end:])
            else:
                output.appendleft(p3)

        chunk = process.stdout.read(150)
        if process.poll() is not None:
            break

        if len(output) == 1:
            chunk = output.popleft() +  chunk
        if chunk.count("[") == 0:
            continue

        pos  = chunk.find("[")
        end_ = chunk[pos+1:].find("[")
        if end_ != -1:
            pbar_format_output(chunk[pos:end_+1])
            output.append(chunk[end_+1:])
            continue
        output.append(chunk[pos:])

    output.append(process.stdout.read())
    print("")
    end_lines = "".join(output).split("\n")
    last_output = end_lines[0]
    if last_output.count("[") != 0:
        last_pos = last_output.rfind("Succeed")
        print(last_output[last_pos:])

    print("\n".join(end_lines[1:]))


def pbar_format_output(message):
    print('\033[2K\033[1G' + message.replace('\n', '').replace('\r', ''), end="", flush=True)
    pass

import subprocess

def vtofloat(vers):
    ls = vers.split('.')
    startidx = 1 if vers.startswith("1.") else 0
    endidx = min(2 + startidx, len(ls))
    return float('.'.join(ls[startidx:endidx]))


def validate_java(verbose = True):
    if not verbose:
        def stdout(*args, **kwargs):
            pass
    else:
        def stdout(*args, **kwargs):
            print(*args, **kwargs)

    stdout("This script uses tabula-py, which requires a Java runtime, version 8+. Checking Java version...")
    out = subprocess.run(["java", "-version"], capture_output=True, text=True)
    if out.returncode > 0:
        raise SystemExit(out.stderr) #forward stderr msg from java
    txt = (out.stdout + ' ' + out.stderr).strip().lower()
    version = ""
    for char in txt[txt.find("version ")+len("version "): ]:
        if char in [' ', '\n']:
            break
        version += char
    version = version.replace('"', "").replace("'", "")
    stdout(f"Found Java version {version},", end=" ")
    v_num = vtofloat(version)

    if v_num >= 8:
        stdout("this should work.")
    else:
        stdout("this version may be too low. Continuing, but be prepared for an error.")

if __name__ == "__main__":
    validate_java()
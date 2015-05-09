export PYTHONPATH=".:$PYTHONPATH"

check ()
{
    python3 /usr/bin/flake8 --max-line-length=99 --ignore=H101 "$@" .
}

coinamon()
{
    check && ./coinamon.py "$@"
}

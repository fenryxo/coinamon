check ()
{
    flake8 --max-line-length=99 "$@" .
}

coinamon()
{
    check && ./coinamon.py "$@"
}

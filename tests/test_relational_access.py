"""Tests for relational access."""

from access.relational import SQLAccess

def  test_create_connection(capsys):
    connxn_success = "Connection to PostgresSQL DB successful"
    connxn_closed = "PostgresSQL connection is closed"
    sa = SQLAccess()
    sa.__int__()
    sa.create_connection()
    captured = capsys.readouterr()
    assert connxn_success in captured.out
    assert connxn_closed in captured.out
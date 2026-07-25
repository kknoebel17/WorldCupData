"""Tests for relational access."""

from access.relational import SQLAccess

def  test_connection(capsys):
    connxn_success = "Connection to PostgresSQL DB successful"
    connxn_closed = "PostgresSQL connection is closed"
    sa = SQLAccess()
    cursor = sa.create_connection()
    sa.close_connection(cursor)
    captured = capsys.readouterr()
    assert connxn_success in captured.out
    assert connxn_closed in captured.out
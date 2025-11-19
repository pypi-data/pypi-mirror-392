from fgmutils import utils


def test_return_value():
    assert utils.return_value("Abc") == "Abc"
    assert utils.return_value("02/2014") == "02/2014"
    assert utils.return_value(1) == 1.0


def test_check_integer():
    assert utils.check_integer(5) is True
    assert utils.check_integer(5.0) is True
    assert utils.check_integer(5.5) is False
    assert utils.check_integer("abc") is False


def test_verifica_tipo_coluna():
    assert utils.verifica_tipo_coluna([1, 2, 3]) == "as.numeric()"
    assert utils.verifica_tipo_coluna(["a", "b"]) == "as.character()"

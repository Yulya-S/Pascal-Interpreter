import pytest
from interpreter import Interpreter, BinOp, UnOp, Number, NodeVisitor, Variable, Empty, Semi, Assigment
from interpreter import Token, TokenType, Parser


@pytest.fixture(scope="function")
def interpreter():
    return Interpreter()


@pytest.fixture(scope="function")
def parser():
    return Parser()


class TestInterpreter:
    interpreter = Interpreter()

    def test_empty_program(self, interpreter):
        assert interpreter.eval("BEGIN END.") == {}

    def test_with_variable(self, interpreter):
        assert interpreter.eval("BEGIN x:= 2 + 3 * (2 + 3); END.") == {'x': 17.0}

    def test_complex_statement(self, interpreter):
        assert interpreter.eval(
            "BEGIN  y: = 2; BEGIN a := 3; a := a; b := -10 + +a + 10 * y / 4; c := a - b END; END.") == {'y': 2.0,
                                                                                                         "a": 3.0,
                                                                                                         "b": -2.0,
                                                                                                         "c": 5.0}

    def test_NodeVisitor(self):
        assert NodeVisitor().visit() is None

    def test_uninitialized_variable(self, interpreter):
        with pytest.raises(ValueError):
            interpreter.eval("BEGIN b := -10 + +a + 10 * y / 4; END.")

    def test_bad_token(self, interpreter):
        with pytest.raises(SyntaxError):
            interpreter.eval("BEGIN b = -10 + +a + 10 * y / 4; END.")

    def test_bad_token_ASSIGN(self, interpreter):
        with pytest.raises(SyntaxError):
            interpreter.eval("BEGIN b :s -10 + +a + 10 * y / 4; END.")

    def test_invalid_token_order(self, parser):
        parser._current_token = Token(TokenType.NUMBER, "2")
        with pytest.raises(SyntaxError):
            parser.check_token(TokenType.OPERATOR)

    def test_Invalid_factor(self, parser):
        parser._current_token = Token(TokenType.ASSIGN, ":=")
        with pytest.raises(SyntaxError):
            parser.factor()

    def test_Invalid_statement(self, parser):
        parser._current_token = Token(TokenType.ASSIGN, ":=")
        with pytest.raises(SyntaxError):
            parser.statement()

    def test_BinOp_invalid_operator(self, interpreter):
        with pytest.raises(ValueError):
            interpreter.visit_binop(BinOp(Number(Token(TokenType.NUMBER, "2")), Token(TokenType.OPERATOR, "&"),
                                          Number(Token(TokenType.NUMBER, "2"))))

    def test_UnOp_invalid_operator(self, interpreter):
        with pytest.raises(ValueError):
            interpreter.visit_unop(UnOp(Token(TokenType.OPERATOR, "&"), Number(Token(TokenType.NUMBER, "2"))))

    def test_None_current_char(self, parser):
        parser._lexer.init("2+2")
        parser._current_token = parser._lexer.next()
        assert parser.expr().__str__() == BinOp(Number(Token(TokenType.NUMBER, "2")), Token(TokenType.OPERATOR, "+"),
                                                Number(Token(TokenType.NUMBER, "2"))).__str__()

    def test_ast_Number_str(self):
        assert Number(Token(TokenType.NUMBER, "2")).__str__() == f"Number (Token(TokenType.NUMBER, 2))"

    def test_ast_BinOp_str(self):
        assert BinOp(Number(Token(TokenType.NUMBER, "2")), Token(TokenType.OPERATOR, "+"),
                     Number(Token(TokenType.NUMBER, "2"))).__str__() == \
               f"BinOp+ (Number (Token(TokenType.NUMBER, 2)), Number (Token(TokenType.NUMBER, 2)))"

    def test_ast_UnOp_str(self):
        assert UnOp(Token(TokenType.OPERATOR, "+"), Number(Token(TokenType.NUMBER, "2"))).__str__() == \
               f"UnOp+ (Number (Token(TokenType.NUMBER, 2)))"

    def test_ast_Variable_str(self):
        assert Variable(Token(TokenType.ID, 'hello')).__str__() == f"Variable (Token(TokenType.ID, hello))"

    def test_ast_Empty_str(self):
        assert Empty(Token(TokenType.ID, "h")).__str__() == f"Empty (Token(TokenType.ID, h))"

    def test_ast_Semi_str(self):
        assert Semi(Variable(Token(TokenType.ID, "h")), Variable(Token(TokenType.ID, "j"))).__str__() == \
               f"Semi (Variable (Token(TokenType.ID, h)), Variable (Token(TokenType.ID, j)))"

    def test_ast_Assigment_str(self):
        assert Assigment(Variable(Token(TokenType.ID, "h")), Number(Token(TokenType.NUMBER, "2"))).__str__() == \
               f"Assigment Variable (Token(TokenType.ID, h)) (Number (Token(TokenType.NUMBER, 2)))"

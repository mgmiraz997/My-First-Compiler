LEXER = lexer.l
PARSER = parser.y
TARGET = compiler
SRC = sample.src

$(TARGET): $(LEXER) $(PARSER)
	bison -d $(PARSER)
	flex $(LEXER)
	gcc lex.yy.c parser.tab.c -o $(TARGET) -lfl

run: $(TARGET)
	@echo "\n🚀 Running Mini Compiler (All Tasks 1–7)..."
	./$(TARGET) $(SRC)
	python3 optimize.py
	python3 tac_to_asm.py
	@echo "\n✅ All Tasks Completed Successfully!\n"

clean:
	rm -f $(TARGET) lex.yy.c parser.tab.c parser.tab.h out.tac out_opt.tac out.asm


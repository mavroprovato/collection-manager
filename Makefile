UI_DIR = collectionmanager/ui

all: $(UI_DIR)/main_window.py

$(UI_DIR)/%.py: $(UI_DIR)/%.ui
	pyuic5 $< -o $@

clean:
	@rm $(UI_DIR)/*.py

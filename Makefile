UI_DIR = collectionmanager/ui/ui

all: $(UI_DIR)/main_window.py $(UI_DIR)/main_widget.py $(UI_DIR)/track_details.py

$(UI_DIR)/%.py: $(UI_DIR)/%.ui
	pyuic5 $< -o $@

clean:
	@rm $(UI_DIR)/*.py

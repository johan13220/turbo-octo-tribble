.PHONY: install run test appimage clean

install:
	pip install -r requirements.txt

run:
	streamlit run app.py

test:
	python -m pytest tests/ -v

appimage:
	bash packaging/build_appimage.sh

clean:
	rm -rf build/ *.AppImage squashfs-root/ __pycache__/ .pytest_cache/

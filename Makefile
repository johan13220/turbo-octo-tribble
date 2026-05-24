.PHONY: install run test appimage android android-release clean

install:
	pip install -r requirements.txt

run:
	streamlit run app.py

run-android:
	python android_app.py

test:
	python -m pytest tests/ -v

appimage:
	bash packaging/build_appimage.sh

android:
	bash packaging/build_android.sh debug

android-release:
	bash packaging/build_android.sh release

clean:
	rm -rf build/ .buildozer/ *.AppImage *.apk squashfs-root/ __pycache__/ .pytest_cache/

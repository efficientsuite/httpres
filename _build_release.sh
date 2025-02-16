source .venv/Scripts/activate
rm -rf build
rm -rf dist
pyinstaller --onefile --noconsole --icon=images/icon.ico --add-data "images;images" --add-data "fonts;fonts" main.py
rm -rf build
rm -f *.spec
rm -f *.toc
mv dist/main.exe dist/HttpRes.exe
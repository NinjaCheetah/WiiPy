CC=python -m nuitka

all:
	$(CC) --show-progress --assume-yes-for-downloads --onefile wiipy.py --onefile-tempdir-spec="{CACHE_DIR}/NinjaCheetah/WiiPy" -o wiipy

install:
	install wiipy /usr/bin/

clean:
	rm wiipy
	rm -rd wiipy.build
	rm -rd wiipy.dist
	rm -rd wiipy.onefile-build

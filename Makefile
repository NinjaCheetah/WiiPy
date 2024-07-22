CC=python -m nuitka

linux:
	$(CC) --show-progress --assume-yes-for-downloads --onefile wiipy.py -o wiipy

linux-install:
	install wiipy /usr/bin/

clean:
	rm wiipy

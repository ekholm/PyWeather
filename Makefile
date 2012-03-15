# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>

NAME=PyWeather
RES=pyqt4

SRC=src/contents/code

UI_FILES=$(wildcard forms/*.ui)
RES_FILES=$(patsubst %,$(SRC)/%_resource.py,$(RES)) 

all: $(RES_FILES) $(UI_FILES)
	@echo "Creating plasmoid \"$(NAME)\""
	@(cd src; zip -q -r ../$(NAME).plasmoid .)

resources: $(RES_FILES)
$(SRC)/pyqt4_resource.py: resource.qrc $(UI_FILES)
	@echo "Buildning resource file: \"$@\""
	@pyrcc4 -o $@ $<

$(SRC)/pyside_resource.py: resource.qrc $(UI_FILES)
	@echo "Buildning resource file: \"$@\""
	@pyside-rcc -o $@ $<

.PHONY: resource.qrc
resource.qrc: cleanRes
	@echo "Generating resource file \"$@\""
	@echo "<RCC>" > $@
	@echo "  <qresource prefix=\"/\">" >> $@
	@find forms  -type f | awk  '{printf("    <file>%s</file>\n", $$1)}' >> $@
	@find images -type f | awk  '{printf("    <file>%s</file>\n", $$1)}' >> $@
	@find icons  -type f | awk  '{printf("    <file>%s</file>\n", $$1)}' >> $@
	@echo "  </qresource>" >> $@
	@echo "</RCC>" >> $@

cleanRes:
	@find . -name '*~'         -exec rm '{}' \;

clean:
	@echo "Cleaning"
	@rm -f $(NAME).plasmoid
	@find . -name 'resource.qrc' -exec rm '{}' \;
	@find . -name '.zip' -exec rm '{}' \;
	@find . -name '.pyc' -exec rm '{}' \;
	@find . -name '*~'   -exec rm '{}' \;
	@find . -name '*_resource.py*' -exec rm '{}' \;
	@find . -name '*_resource.py*' -exec rm '{}' \;




test: resources
	plasmoidviewer src

remove:
	plasmapkg -r $(NAME)

install: clean remove all
	plasmapkg -i $(NAME).plasmoid


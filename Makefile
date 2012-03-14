# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>

NAME=plasma_pyweather
RES=resource
UI=main config

all: resources plasmoid

forms: $(patsubst %,src/contents/code/form_%.py,$(UI))
src/contents/code/form_%.py: forms/%.ui
	@echo buildning ui form file: $@
	@pykdeuic4 -o $@ $<

resources: $(patsubst %,src/contents/code/app_%.py,$(RES)) 
src/contents/code/app_resource.py: $(patsubst %,%.qrc,$(RES)) $(patsubst %,forms/%.ui,$(UI))
	@echo buildning resource file: $@
	@pyrcc4 -o $@ $<

test: resources
	plasmoidviewer src

plasmoid: # clean
	@echo buildning $@
	@(cd src; zip -q -r ../$(NAME).$@ .)

remove:
	plasmapkg -r $(NAME)

install: clean remove all
	plasmapkg -i $(NAME).plasmoid

clean:
	@rm -f $(NAME).plasmoid
	@find . -name '.zip' -exec rm '{}' \;
	@find . -name '.pyc' -exec rm '{}' \;
	@find . -name '*~'   -exec rm '{}' \;
	@find . -name 'app_*.py*' -exec rm '{}' \;
	@find . -name 'form_*.py*' -exec rm '{}' \;

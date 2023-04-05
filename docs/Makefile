ENTRY=main
OUTPUTDIR=result

all:
	latexmk -xelatex -f -output-directory=$(OUTPUTDIR) $(ENTRY).tex
	cp result/$(ENTRY).pdf .

.PHONY: clean
clean:
	latexmk -C
	rm -r $(OUTPUTDIR)

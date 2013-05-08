SHELL=/bin/bash

.PHONY: css

css:
	#@rm -f ./css/square.css
	#@rm -f ./css/square.min.css
	@lessc ./less/square.less > ../project_static/square/css/square.css
	#@recess --compress ./css/square.css > ./css/square.min.css



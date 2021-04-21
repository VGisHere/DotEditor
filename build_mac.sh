#!/bin/sh

### Copyright (R) 2021 Vaibhav.Gilhotra <spaceholder_email>
###
### Published under Apache 2.0 License (http://www.apache.org/licenses/LICENSE-2.0.html).
### -------------------------------------------------------------------------------------

# Build DotEditor.app
pyinstaller pyinstaller_mac.spec

# Package to dmg
hdiutil create ./dist/DotEditor.dmg -srcfolder ./dist/DotEditor.app -ov

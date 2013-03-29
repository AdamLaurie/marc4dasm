marc4dasm
=========

Atmel MARC4 disassembler

Known limitations:

ROM variables (i.e. static values loaded into memory with the TABLE
command) cannot be easily identified as they utilise the Return Stack
for addressing, so only become visible when the code is running. This
means that during disassembly they will be mistakenly treated as code,
which may break the following code due to incorrect instruction lengths
etc.

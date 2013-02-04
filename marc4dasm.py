#! /usr/bin/env python

#  marc4dasm.py - disassemble atmel marc4
# 
#  Adam Laurie <adam@aperturelabs.com>
#  http://www.aperturelabs.com
# 
#  This code is copyright (c) Aperture Labs Ltd., 2013, All rights reserved.
#
#    This code is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#

import sys

# Comments
COMM=	{
	0x00:'Add the top 2 stack digits',
	0x01:'Add with carry the top 2 stack digits',
	0x02:"2's complement subtraction of the top 2 digits",
	0x03:"1's complemen subtraction of the top 2 digits",
	0x04:'Exclusive-OR top 2 stack digits',
	0x05:'Bitwise-AND top 2 stack digits',
	0x06:'Equality test for top 2 stack digits',
	0x07:'Inequality test for top 2 stack digits',
	0x08:'Less-than test for top 2 stack digits',
	0x09:'Less-or-equal for top 2 stack digits',
	0x0A:'Greater-than for top 2 stack digits',
	0x0B:'Greater-or-equal for top 2 stack digits',
	0x0C:'Bitwise-OR top 2 stack digits',
	0x0D:'Copy condition code onto TOS',
	0x0E:'Restore condition codes',
	0x0F:"CPU in 'sleep mode', interrupts enabled",
	0x10:'Shift TOS left into carry',
	0x11:'Rotate TOS left through carry',
	0x12:'Shift TOS right into Carry',
	0x13:'Rotate TOS right through carry',
	0x14:'Increment TOS',
	0x15:'Decrement TOS',
	0x16:'Decimal adjust for addition (in BCD arithmetic)',
	0x17:"1's complement of TOS",
	0x18:'Toggle Branch flag',
	0x19:'Set Branch and Carry flag',
	0x1A:'Disable all interrupts',
	0x1B:'Read 4-bit I/O port to TOS',
	0x1C:'Decrement index on return stack',
	0x1D:'Return from interrupt routine; enable all interrupts',
	0x1E:'Software interrupt',
	0x1F:'Write TOS to 4-bit I/O port',
	0x20:'Fetch an 8-bit ROM constant and performs an EXIT to Ret_PC',
	0x21:'Fetch an 8-bit ROM constant and performs an EXIT to Ret_PC',
	0x22:'Move (loop) index onto Return Stack',
	0x23:'Copy (loop) index from the Return Stack onto TOS',
	0x24:"Return from subroutine (';')",
	0x25:"Return from subroutine (';')",
	0x26:'Exchange the top 2 digits',
	0x27:'Push a copy of TOS-1 onto TOS',
	0x28:'Move top 2 digits onto Return Stack',
	0x29:'Move top 3 digits onto Return Stack',
	0x2A:'Copy 2 digits from Return to Expression Stack',
	0x2B:'Copy 3 digits from Return to Expression Stack',
	0x2C:'Move third digit onto TOS',
	0x2D:'Duplicate the TOS digit',
	0x2E:'Remove TOS digit from the Expression Stack',
	0x2F:'Remove one entry from the Return Stack',
	0x30:'Indirect fetch from RAM addressed by the X register',
	0x31:'Indirect fetch from RAM addressed by preincremented X register',
	0x32:'Indirect fetch from RAM addressed by the postdecremented X register',
	0x33:'Direct fetch from RAM addressed by the X register',
	0x34:'Indirect fetch from RAM addressed by the Y register',
	0x35:'Indirect fetch from RAM addressed by preincremented Y register',
	0x36:'Indirect fetch from RAM addressed by postdecremented Y register',
	0x37:'Direct fetch from RAM addressed by the Y register',
	0x38:'Indirect store into RAM addressed by the X register',
	0x39:'Indirect store into RAM addressed by pre-incremented X register',
	0x3A:'Indirect store into RAM addressed by the postdecremented X reg.',
	0x3B:'Direct store into RAM addressed by the X register',
	0x3C:'Indirect store into RAM addressed by the Y register',
	0x3D:'Indirect store into RAM addressed by pre-incremented Y register',
	0x3E:'Indirect store into RAM addressed by the post-decremented Y reg.',
	0x3F:'Direct store into RAM addressed by the Y register',
	0x70:'Fetch the current Expression Stack Pointer',
	0x71:'Fetch current Return Stack Pointer',
	0x72:'Fetch current X register contents',
	0x73:'Fetch current Y register contents',
	0x74:'Move address into the Expression Stack Pointer',
	0x75:'Move address into the Return Stack Pointer',
	0x76:'Move address into the X register',
	0x77:'Move address into the Y register',
	0x78:'Set Expression Stack Pointer',
	0x79:'Set return Stack Pointer direct',
	0x7A:'Set RAM address register X direct',
	0x7B:'Set RAM address register Y direct',
	0x7C:'No operation',
	}

# Zero Address Instructions
ZAI=	{
	0x00:'ADD',
	0x01:'ADDC',
	0x02:'SUB',
	0x03:'SUBB',
	0x04:'XOR',
	0x05:'AND',
	0x06:'CMP_EQ',
	0x07:'CMP_NE',
	0x08:'CMP_LT',
	0x09:'CMP_LE',
	0x0A:'CMP_GT',
	0x0B:'CMP_GE',
	0x0C:'OR',
	0x0D:'CCR@',
	0x0E:'CCR!',
	0x0F:'SLEEP',
	0x10:'SHL',
	0x11:'ROL',
	0x12:'SHR',
	0x13:'ROR',
	0x14:'INC',
	0x15:'DEC',
	0x16:'DAA',
	0x17:'NOT',
	0x18:'TOG_BF',
	0x19:'SET_BCF',
	0x1A:'DI',
	0x1B:'IN',
	0x1C:'DECR',
	0x1D:'RTI',
	0x1E:'SWI',
	0x1F:'OUT',
	0x20:'TABLE',
	0x21:'TABLE',
	0x22:'>R',
	0x23:'I',
	0x24:'EXIT',
	0x25:'EXIT',
	0x26:'SWAP',
	0x27:'OVER',
	0x28:'2>R',
	0x29:'3>R',
	0x2A:'2R@',
	0x2B:'3R@',
	0x2C:'ROT',
	0x2D:'DUP',
	0x2E:'DROP',
	0x2F:'DROPR',
	0x30:'[X]@',
	0x31:'[+X]@',
	0x32:'[X-]@',
	0x34:'[Y]@',
	0x35:'[+Y]@',
	0x36:'[Y-]@',
	0x38:'[X]!',
	0x39:'[+X]!',
	0x3A:'[X-]!',
	0x3C:'[Y]!',
	0x3D:'[+Y]!',
	0x3E:'[Y-]!',
	0x70:'SP@',
	0x71:'RP@',
	0x72:'X@',
	0x73:'Y@',
	0x74:'SP!',
	0x75:'RP!',
	0x76:'X!',
	0x77:'Y!',
	0x7C:'NOP',
	0x7D:'---',
	0x7E:'---',
	0x7F:'---',
	}

# Long RAM Address Instructions (INS $XX)
LRAI=	{
	0x33:'[>X]@',
	0x3B:'[>X]!',
	0x3F:'[>Y]!',
	0x37:'[>Y]@',
	0x78:'>SP',
	0x79:'>RP',
	0x7A:'>X',
	0x7B:'>Y',
	}

# CALL $nXX
CALL=	{
	0x40:'CALL',
	0x41:'CALL',
	0x42:'CALL',
	0x43:'CALL',
	0x44:'CALL',
	0x45:'CALL',
	0x47:'CALL',
	0x48:'CALL',
	0x49:'CALL',
	0x4A:'CALL',
	0x4B:'CALL',
	0x4C:'CALL',
	0x4D:'CALL',
	0x4E:'CALL',
	0x4F:'CALL',
	}

# BRANCH $nXX
BRANCH=	{
	0x50:'BRA',
	0x51:'BRA',
	0x52:'BRA',
	0x53:'BRA',
	0x54:'BRA',
	0x55:'BRA',
	0x56:'BRA',
	0x57:'BRA',
	0x58:'BRA',
	0x59:'BRA',
	0x5A:'BRA',
	0x5B:'BRA',
	0x5C:'BRA',
	0x5D:'BRA',
	0x5E:'BRA',
	0x5F:'BRA',
	}

# LITERAL 0-F
LIT=	{
	0x60:'LIT_0',
	0x61:'LIT_1',
	0x62:'LIT_2',
	0x63:'LIT_3',
	0x64:'LIT_4',
	0x65:'LIT_5',
	0x66:'LIT_6',
	0x67:'LIT_7',
	0x68:'LIT_8',
	0x69:'LIT_9',
	0x6A:'LIT_A',
	0x6B:'LIT_B',
	0x6C:'LIT_C',
	0x6D:'LIT_D',
	0x6E:'LIT_E',
	0x6F:'LIT_F',
	}

# Fixed ROM addresses
ROMADD=	{
	0x000:'$AUTOSLEEP',
	0x008:'$RESET',
	0x040:'INTERRUPT_0',
	0x080:'INTERRUPT_1',
	0x0C0:'INTERRUPT_2',
	0x100:'INTERRUPT_3',
	0x140:'INTERRUPT_4',
	0x180:'INTERRUPT_5',
	0x1C0:'INTERRUPT_6',
	0x1E0:'INTERRUPT_7',
	}

# Variables in RAM (as yet unknown)
RAMADD=	{
	}

# Short branch inside current page: 0x80 - 0xBF (SBRA $XXX)
# dealt with entirely in later code

# Short subroutine CALL into 'zero page': 0xC0 - 0xFF (SCALL $XXX) 
# dealt with entirely in later code

# setup
if len(sys.argv) < 2:
	print
	print 'usage: %s <INFILE> [QUIET]' % sys.argv[0]
	exit()

def print_with_comment(address, data, ins, arg, comment):
	global Quiet

	if arg != None:
		arg= '%02X' % arg
	else:
		arg= '  '

	if not Quiet:
		address= '%04X ' % address
		original= '%02X %s           ' % (ins, arg)
	else:
		address= ''
		original= '              '

	pad= ' ' * (40 - len(data))

	if comment:
		print '%s%s  %s %s \\ %s' % (address, original, data, pad, comment)
		return

	if COMM.has_key(ins):
		print '%s%s  %s %s \\ %s' % (address, original, data, pad, COMM[ins])
	else:
		print '%s%s  %s %s \\ %s' % (address, original, data, pad, 'Illegal instruction!')

# start main code
infile= open(sys.argv[1],'r')

Quiet= False
if len(sys.argv) == 3:
	if sys.argv[2].upper() == 'Q':
		Quiet= True

data= infile.read()
infile.close()

# first pass - create labels
p= 0
label= 0
rams= 0
# last two bytes are CRC
while p < len(data) - 2:
	x= ord(data[p])
	p += 1

	# skip over instructions that have no args or implicit addresses
	if ZAI.has_key(x) or LIT.has_key(x):
		continue

	# create address labels for everything else...

	if CALL.has_key(x) or BRANCH.has_key(x):
		address= ord(data[p])
		address += (x & 0x0f) << 8
		p += 1
		if ROMADD.has_key(address):
			continue
		ROMADD[address]= 'LABEL_%03X' % label
		label += 1
		continue

	if LRAI.has_key(x):
		address= ord(data[p])
		p += 1
		if RAMADD.has_key(address):
			continue
		RAMADD[address]= 'VAR_%02X' % rams
		rams += 1
		continue

	# Short branch inside current page
	if x >= 0x80 and x <= 0xBF:
		# current page is 64 bytes
		address= p - (p % 64) + (x - 0x80)
	# Short subroutine CALL into 'zero page'
	if x >= 0xC0 and x <= 0xFF:
		# ROM is 64 evenly spaced addresses between 0x00 and 0x1F8)
		address= (x - 0xC0) * (0x200 / 64)
	if ROMADD.has_key(address):
		continue
	ROMADD[address]= 'LABEL_%03X' % label
	label += 1
	continue

# second pass - look for orphan code (chunks of code that is never directly called)
p= 1
orphan= 0
while p < len(data) - 2:
	x= ord(data[p])
	prev= ord(data[p - 1])
	# previous instruction was UNUSED, EXIT or RTI
	if x != 0xC1 and (prev == 0xC1 or prev == 0x25 or prev == 0x1D) and not ROMADD.has_key(p):
		ROMADD[p]= 'ORPHAN_%03X' % orphan
		orphan += 1
	p += 1

# output addresses
print '\\'
print '\\'
print '\\       %s' % sys.argv[1]
print '\\'
print '\\'
print '\\       ROM ADDRESS       LABEL'
print '\\'
for address in sorted(ROMADD.iterkeys()):
	print '\\       $%03X              %s' % (address, ROMADD[address])
print '\\'
print '\\'
print '\\'
print '\\       RAM VARIABLE      LABEL'
print '\\'
for address in sorted(RAMADD.iterkeys()):
	print '\\       $%02X               %s' % (address, RAMADD[address])
print '\\'
print '\\'
print '\\'
print '\\'

# third pass - disassemble
p= 0
while p < len(data) - 2:
	ins= ord(data[p])
	arg= None
	code_add= p

	# print labels
	if ROMADD.has_key(p):
		if not Quiet:
	 		out= '%04X\n' % p
			out += '%04X        ORIGIN $%03X\n' % (p, p)
			out += '%04X        : %s' % (p,ROMADD[p])
		else:
	 		out= '\n'
			out += 'ORIGIN $%03X\n' % p
			out += ': %s' % ROMADD[p]
		print out

	# Zero Address Instructions
	if ZAI.has_key(ins):
		p += 1
		print_with_comment(code_add, ZAI[ins], ins, arg, '')
		continue
	
	# Long RAM Address Instructions (INS $XX)
	if LRAI.has_key(ins):
		p += 1
		arg= ord(data[p])
		p += 1
		out= '%s %s' % (LRAI[ins], RAMADD[arg])
		print_with_comment(code_add, out, ins, arg, '')
		continue

	# CALL $nXX
	if CALL.has_key(ins):
		p += 1
		arg= ord(data[p])
		p += 1
		address= ((ins & 0x0f) << 8) + arg
		out= '%s %s' % (CALL[ins], ROMADD[address])
		print_with_comment(code_add, out, ins, arg, 'Unconditional long CALL ($%03X)' % address)
		continue

	# BRANCH $nXX
	if BRANCH.has_key(ins):
		p += 1
		arg= ord(data[p])
		p += 1
		address= ((ins & 0x0f) << 8) + arg
		out= '%s %s' % (BRANCH[ins], ROMADD[address])
		print_with_comment(code_add, out, ins, arg, 'Conditional long branch ($%03X)' % address)
		continue

	# Literal
	if LIT.has_key(ins):
		p += 1
		print_with_comment(code_add, LIT[ins], ins, arg, 'Push literal/constant $%01X onto TOS' % (ins & 0x0F))
		continue

	# Short BRANCH inside current page
	if ins >= 0x80 and ins <= 0xBF:
		# current page is 64 bytes
		address= p - (p % 64) + (ins - 0x80)
		p += 1
		out= 'SBRA %s' % ROMADD[address]
		print_with_comment(code_add, out, ins, arg, 'Conditional short branch in page ($%03X)' % address)
		continue

	# Short subroutine CALL into 'zero page'
	if ins >= 0xC0 and ins <= 0xFF:
		p += 1
		# ROM is 64 evenly spaced addresses between 0x00 and 0x1F8)
		address= (ins - 0xC0) * (0x200 / 64)
		out= 'SCALL %s' % ROMADD[address]
		print_with_comment(code_add, out, ins, arg, 'Unconditional short CALL ($%03X)' % address)
		continue

	# code should never reach here!
	p += 1
	print_with_comment(code_add, '???', ins, arg, 'UNKNOWN')	

# check CRC (only we can't because we don't know algorithm!)
crc0= ord(data[p])
p += 1
crc1= ord(data[p])
print
print 'CRC: %02X %02X' % (crc0, crc1)

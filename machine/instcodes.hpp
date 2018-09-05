#ifndef INSTCODES_HPP
#define INSTCODES_HPP

typedef unsigned char word;

enum class ICs : word {
  NOP = 0xc,
  DROP = 0x1,
  POP = 0x2,
  PUSH = 0x3,
  PUSHVAL = 0x4,
  DUP = 0x5,
  SWAP = 0x6,
  INC = 0x7,
  DEC = 0x8,
  JMPIF = 0x9,
  RET = 0xa,
  CALL = 0xb,
  GOTO = 0x10,
  ENDMARK = 0x0,
/** Unimplemented
  CPUSH = 0xd,
  METASEP = 0x12,
  BOOL = 0x20,
  NOT = 0x21,
  EQUALS = 0x22,
  LESS = 0x23,
  GREATER = 0x24,
  CMP = 0x25,
  ADD = 0x30,
  SUB = 0x31,
  MUL = 0x32,
  DIV = 0x33,
  BITNEG = 0x40,
  BITOR = 0x41,
  BITAND = 0x42,
  BITXOR = 0x43,
  BITLEFT = 0x44,
  BITRIGHT = 0x45,
*/
};


#endif

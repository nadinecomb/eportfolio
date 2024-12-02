
/*
 *
 * pipeline.c
 *
 This is the primary place for student's code.

*/

#include "fu.h"
#include "pipeline.h"
#include <stdlib.h>
#include <string.h>

float bintofloat(unsigned int x) {
    float f = 0.0f;
    memcpy(&f, &x, sizeof(f) < sizeof(x) ? sizeof(f) : sizeof(x));
    return f;
}

void writeback(state_t *state, int *num_insn) {
  // unstall pipeline here when branch instruction reaches here
  // perform load and store operations here
  int rd = FIELD_RD(state->int_wb.instr);
  int r2 = FIELD_RS2(state->int_wb.instr);
  const op_info_t *op = NULL;
  const op_info_t *fop = NULL;
  if (state->int_wb.instr != 0)
    op = state->int_wb.info;
  if (state->fp_wb.instr != 0)
    fop = state->fp_wb.info;
  if (op != NULL) {
    (*num_insn)++;
    if (op->data_type != DATA_TYPE_F) {
      if (op->operation == OPERATION_STORE) {
        state->mem[state->int_wb.result.integer.wu] =
          state->rf_int.reg_int[r2].wu;
      } else if (op->operation == OPERATION_LOAD)
        state->rf_int.reg_int[rd].wu =
          state->mem[state->int_wb.result.integer.wu];
      else {
        if (op->operation != OPERATION_BNE && op->operation != OPERATION_BEQ) {
          if (op->operation != OPERATION_ADD && op->operation != OPERATION_SUB)
            state->rf_int.reg_int[rd].wu = state->fp_wb.pc;
          else
            state->rf_int.reg_int[rd].w = state->int_wb.result.integer.w;
        }
        if (op->fu_group_num == FU_GROUP_BRANCH) {
          state->branch = 0;
          state->pc = state->int_wb.pc;
          if(op->operation == OPERATION_JAL || op -> operation == OPERATION_JALR ||
              ((op -> operation == OPERATION_BNE || op -> operation == OPERATION_BEQ)
               && state->int_wb.result.integer.w)){
              state -> if_id.instr = NOP;
          }
        }
      }
    } else {
      if (op->fu_group_num == FU_GROUP_MEM) {
        if (op->operation == OPERATION_STORE) {
          state->mem[state->int_wb.result.integer.wu] = *(unsigned int*) &(state->rf_fp.reg_fp[r2]) & (0x000000FF);
          state->mem[state->int_wb.result.integer.wu + 1] = *(unsigned int*) &(state->rf_fp.reg_fp[r2])>>8 & (0x000000FF);
          state->mem[state->int_wb.result.integer.wu + 2] = *(unsigned int*) &(state->rf_fp.reg_fp[r2])>>16 & (0x000000FF);
          state->mem[state->int_wb.result.integer.wu + 3] = *(unsigned int*) &(state->rf_fp.reg_fp[r2])>>24 & (0x000000FF);
        } else {
          r2 = state->int_wb.result.integer.wu;
          state->rf_fp.reg_fp[rd] = bintofloat(((state->mem[r2 + 3]) << 24 |
                             (state->mem[r2 + 2]) << 16 |
                             (state->mem[r2 + 1]) << 8 |
                             (state->mem[r2])));
        }
      } else
        state->rf_fp.reg_fp[rd] = state->fp_wb.result.flt;
    }
    // set instr to nop once done
    state->int_wb.instr = 0;
  }
  if (fop != NULL) {
    (*num_insn)++;
    rd = FIELD_RD(state->fp_wb.instr);

    state->rf_fp.reg_fp[rd] = state->fp_wb.result.flt;
    // set op to 0 once done
    state->fp_wb.instr = 0;
  }
}

void execute(state_t *state) {
  int i;
  // update scoreboards, subtract each value by 1, unless already -1
  for (i = 0; i < NUMREGS; i++) {
    if (state->f_scoreboard[i] != -1)
      state->f_scoreboard[i] -= 1;
    if (state->int_scoreboard[i] != -1)
      state->int_scoreboard[i] -= 1;
  }
  advance_fu_int(state->fu_int_list, &state->int_wb);
  advance_fu_fp(state->fu_add_list, &state->fp_wb);
  advance_fu_fp(state->fu_mult_list, &state->fp_wb);
  advance_fu_fp(state->fu_div_list, &state->fp_wb);
}

int decode(state_t *state) {
  int instr = (state->if_id).instr;
  int flag, r1, r2, rd, stall = 0, imm = 0, i, length;
  operand_t immediate, rs1, rs2;
  const op_info_t *op = decode_instr(instr, &imm);
  // note that loads and stores do not acutally save their values until
  // writeback
  if (op != NULL && instr != NOP) {
    r1 = FIELD_RS1(instr);
    r2 = FIELD_RS2(instr);
    rd = FIELD_RD(instr);
    if (op->fu_group_num == FU_GROUP_HALT) {
      if(state -> branch){
        stall = state->int_scoreboard[r2] + 1;
      }
      else{
        state->fetch_lock = 1;
        stall = 132742;
      }
    } else if (op->data_type != DATA_TYPE_F) {
      length = 2;
      // set the pipeline register instr value equal to the current instr
      rs1.integer = state->rf_int.reg_int[r1];
      rs2.integer = state->rf_int.reg_int[r2];
      // ensure there is no possibility for a RAW hazard
      if (state->int_scoreboard[r1] != -1)
        stall = state->int_scoreboard[r1] + 1;
      else if ((op->operation == OPERATION_STORE ||
            op->operation == OPERATION_BEQ ||
            op->operation == OPERATION_BNE || !imm) &&
          op->operation != OPERATION_LOAD &&
          state->int_scoreboard[r2] != -1)
        stall = state->int_scoreboard[r2] + 1;
      else {
        state->id_ex_int.info = op;
        state->id_ex_int.instr = instr;
        if (op->fu_group_num == FU_GROUP_BRANCH ||
            (!imm && op->fu_group_num == FU_GROUP_INT)) {
          if (op->operation == OPERATION_LOAD) {
            immediate.integer.w = FIELD_IMM_I(instr);
            perform_operation(instr, rs1, immediate, &state->id_ex_int.result);
          } else
            perform_operation(instr, rs1, rs2, &state->id_ex_int.result);
          // check if branch
          if (op->fu_group_num == FU_GROUP_BRANCH) {
            state -> branch = 1;
            for (i = 0; i < NUMREGS; i++) {
              state->f_scoreboard[i] = length;
              state->int_scoreboard[i] = length;
            }
            // branch hazard, stop fetching, if_id will not change for next
            // instruction
            // if the operation is JAL or JALR, set the destination register to
            // pc + 4, and set the new pc to the value held in the result field
            if (op->operation == OPERATION_JAL ||
                op->operation == OPERATION_JALR) {
              state->id_ex_int.pc = state->id_ex_int.result.integer.w + state -> pc - 4;
              state->id_ex_int.result.integer.wu = state->pc + 4;
            } else {
              // if the branch was beq or bne, set the pipeline pc to the
              // current pc + the immediate of the instr
              if (state->id_ex_int.result.integer.wu)
                state->id_ex_int.pc = state->pc + FIELD_IMM_S(instr) - 4;
              else
                state->id_ex_int.pc = state->pc + 4;
            }
          } // create a case for stores
          else {
            // save the current pc
            state->id_ex_int.pc = state->pc;
            // loads and stores check if needs floating point registers
          }
        } else {
          if (op->operation == OPERATION_STORE)
            immediate.integer.w = FIELD_IMM_S(instr);
          else
            immediate.integer.w = FIELD_IMM_I(instr);
          perform_operation(instr, rs1, immediate, &state->id_ex_int.result);
        }
        issue_fu_int(state->fu_int_list, state->id_ex_int);
        // update scoreboard
        if (op->operation != OPERATION_BEQ && op->operation != OPERATION_BNE &&
            op->operation != OPERATION_STORE)
          state->int_scoreboard[rd] = length;
      }
    } else { // the current instruction is a float type
             // set the stall length
      switch (op->fu_group_num) {
        case FU_GROUP_ADD: // delay is 3
          length = 3;
          break;
        case FU_GROUP_MULT: // delay is 4
          length = 4;
          break;
        case FU_GROUP_DIV: // delay is 8
          length = 8;
          break;
        case FU_GROUP_MEM: // delay is 2
          length = 2;
          break;
      }

      if (op->fu_group_num != FU_GROUP_MEM) {
        rs1.flt = state->rf_fp.reg_fp[r1];
        rs2.flt = state->rf_fp.reg_fp[r2];
        // check WAR
        if (state->f_scoreboard[r1] != -1)
          stall = state->f_scoreboard[r1] + 1;
        else if (state->f_scoreboard[r2] != -1)
          stall = state->f_scoreboard[r2] + 1;
        // check WAW
        else if (state->f_scoreboard[rd] > length)
          stall = state->f_scoreboard[rd] - length + 1;
        // check structural
        else {
          for (i = 0; i < NUMREGS && !stall; i++) {
            if (length == state->f_scoreboard[i])
              stall = 1;
          }
        }
      } else { // MEM operation
        rs1.integer = state->rf_int.reg_int[r1];
        // check WAR for r1
        if (state -> int_scoreboard[r1] != -1)
          stall = state->int_scoreboard[r1] + 1;
        else
          if (op->operation == OPERATION_STORE) {
            // check WAR and structural hazards for r2
            if(state -> f_scoreboard[r2] != -1)
              stall = state->f_scoreboard[r2] + 1;
            rs2.flt = state->rf_fp.reg_fp[r2];
          } // check for WAW hazards for load
          else if (state->f_scoreboard[r2] > length) {
            stall = state->f_scoreboard[r2] - length + 1;
          } //check structural hazards for load
        for (i = 0; i < NUMREGS && !stall; i++) {
          if (length == state->f_scoreboard[i])
            stall = 1;
        }
      }
      if (op->fu_group_num != FU_GROUP_MEM)
        perform_operation(instr, rs1, rs2, &state->id_ex_f.result);
      else {
        if (op->operation == OPERATION_LOAD)
          immediate.integer.w = FIELD_IMM_I(instr);
        else
          immediate.integer.w = FIELD_IMM_S(instr);
        perform_operation(instr, rs1, immediate, &state->id_ex_int.result);
      }

      if (!stall) {
        if (op->fu_group_num == FU_GROUP_MEM) {
          state->id_ex_int.instr = instr;
          state->id_ex_int.info = op;
        } else {
          state->id_ex_f.instr = instr;
          state->id_ex_f.info = op;
        }
        switch (op->fu_group_num) {
          case FU_GROUP_MEM:
            flag = issue_fu_int(state->fu_int_list, state->id_ex_int);
            break;
          case FU_GROUP_ADD:
            flag = issue_fu_fp(state->fu_add_list, state->id_ex_f);
            break;
          case FU_GROUP_DIV:
            flag = issue_fu_fp(state->fu_div_list, state->id_ex_f);
            break;
          case FU_GROUP_MULT:
            flag = issue_fu_fp(state->fu_mult_list, state->id_ex_f);
            break;
        }
        if (!flag) {
          if (op->operation != OPERATION_STORE)
            state->f_scoreboard[rd] = length;
        } else
          stall = 1;
      }
    }
  }
  return stall;
}

void fetch(state_t *state) {
  if (state->new_instr != NOP) {
    state->if_id.instr = state->new_instr;
    state->if_id.pc = state->pc;
    state->pc += 4;
  }
}

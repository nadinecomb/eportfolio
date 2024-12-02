
/*
 *
 * main.c
 *
 * Donald Yeung
 */

#include "fu.h"
#include "pipeline.h"
#include "output.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char usage[] = "usage: %s <options>\n"
                     "\toptions:\n"
                     "\t-b"
                     "\t<binary file>\n"
                     "\t-o"
                     "\t<functional unit options file>\n";

void parse_args(int, char **);

static char *bin_file_name = NULL;
static char *fu_file_name = NULL;
static FILE *bin_file, *fu_file;
static int wbpi = -1;
static int wbpf = -1;

/************************************************************/
int main(int argc, char *argv[]) {
  state_t *state;
  int data_count;
  int num_insn, i, stall = 0, end = 0;

  parse_args(argc, argv);
  state = state_create(&data_count, bin_file, fu_file);

  if (state == NULL) {
    fclose(bin_file);
    fclose(fu_file);
    return -1;
  }

  fclose(bin_file);
  fclose(fu_file);

  /* main sim loop */
  for (i = 0, num_insn = 0; !end; i++) {

    printf("\n\n*** CYCLE %d\n", i);
    print_state(state, data_count);
    // check if instruction was a branch (unstall) and that all of the
    // scoreboard values are -1
    writeback(state, &num_insn);
    if (fu_int_done(state->fu_int_list) && fu_fp_done(state->fu_add_list) &&
        fu_fp_done(state->fu_mult_list) && fu_fp_done(state->fu_div_list) &&
        state->fetch_lock) {
      execute(state);
      end = 1;
    } else {
      execute(state);
      if(!state -> fetch_lock){
        stall = decode(state);
        if (stall > 0 && !state->fetch_lock) {
          state->new_instr = NOP;
          stall--;
        } else {
          state->new_instr = (state->mem[state->pc + 3]) << 24 |
                             (state->mem[state->pc + 2]) << 16 |
                             (state->mem[state->pc + 1]) << 8 |
                             (state->mem[state->pc]);
        }
        fetch(state);
      }

    }
  }
  printf("\n\n*** CYCLE %d\n", i);
  print_state(state, data_count);
  num_insn++;
  printf("SIMULATION COMPLETE!\n");
  printf("EXECUTED %d INSTRUCTIONS IN %d CYCLES\n", num_insn, i);
  printf("CPI:  %.2f\n", (float)i / (float)num_insn);

  return 0;
}
/************************************************************/

void parse_args(int argc, char **argv) {
  int i;

  for (i = 1; i < argc; i++) {
    if (strcmp(argv[i], "-b") == 0) {
      if (bin_file_name == NULL && i + 1 < argc) {
        bin_file_name = argv[++i];
      } else {
        fprintf(stderr, usage, argv[0]);
        exit(-1);
      }
    } else if (strcmp(argv[i], "-o") == 0) {
      if (fu_file_name == NULL && i + 1 < argc) {
        fu_file_name = argv[++i];
      } else {
        fprintf(stderr, usage, argv[0]);
        exit(-1);
      }
    } else {
      fprintf(stderr, usage, argv[0]);
      exit(-1);
    }
  }

  if (bin_file_name == NULL || fu_file_name == NULL) {
    fprintf(stderr, usage, argv[0]);
    exit(-1);
  }

  bin_file = fopen(bin_file_name, "r");
  if (bin_file == NULL) {
    fprintf(stderr, "error: cannot open binary file '%s'\n", bin_file_name);
    exit(-1);
  }

  fu_file = fopen(fu_file_name, "r");
  if (fu_file == NULL) {
    fclose(bin_file);
    fprintf(stderr, "error: cannot open functional unit options file '%s'\n",
            fu_file_name);
    exit(-1);
  }
}

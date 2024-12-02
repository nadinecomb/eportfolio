
/*
 *
 * pipeline.h
 *
 * Donald Yeung
 *:
result.wu = pc + 1;/
fetch/decode pipeline register */
#define TRUE 1
#define FALSE 0
typedef struct _if_id_t {
  int instr;
  unsigned long pc;
} if_id_t;

/* Register state */
typedef struct _rf_int_t {
  int_t reg_int[NUMREGS];
} rf_int_t;

typedef struct _rf_fp_t {
  float reg_fp[NUMREGS];
} rf_fp_t;

/* Overall processor state */
typedef struct _state_t {
  /* memory */
  unsigned char mem[MAXMEMORY];
  int branch;

  /* register files */
  rf_int_t rf_int;
  rf_fp_t rf_fp;

  /* pipeline registers */
  unsigned long pc;
  if_id_t if_id;
  prop_t id_ex_int;
  prop_t id_ex_f;
  prop_t int_wb;
  prop_t fp_wb;
  int new_instr;

  fu_int_t *fu_int_list;
  fu_fp_t *fu_add_list;
  fu_fp_t *fu_mult_list;
  fu_fp_t *fu_div_list;

  int fetch_lock;
  int f_scoreboard[NUMREGS];
  int int_scoreboard[NUMREGS];
} state_t;

extern state_t *state_create(int *, FILE *, FILE *);
extern void writeback(state_t *, int *);
extern void execute(state_t *);
extern int decode(state_t *);
extern void fetch(state_t *);

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cache.h"
#include "main.h"

/* cache configuration parameters */
static int cache_csize = DEFAULT_CACHE_SIZE;
static int cache_block_size = DEFAULT_CACHE_BLOCK_SIZE;
static int words_per_block = DEFAULT_CACHE_BLOCK_SIZE / WORD_SIZE;
static int cache_assoc = DEFAULT_CACHE_ASSOC;
static int num_core = DEFAULT_NUM_CORE;

/* cache model data structures */
/* max of 8 cores */
static cache mesi_cache[8];
static cache_stat mesi_cache_stat[8];

/************************************************************/
void set_cache_param(param, value) int param;
int value;
{
  switch (param) {
  case NUM_CORE:
    num_core = value;
    break;
  case CACHE_PARAM_BLOCK_SIZE:
    cache_block_size = value;
    words_per_block = value / WORD_SIZE;
    break;
  case CACHE_PARAM_CSIZE:
    cache_csize = value;
    break;
  case CACHE_PARAM_ASSOC:
    cache_assoc = value;
    break;
  default:
    printf("error set_cache_param: bad parameter value\n");
    exit(-1);
  }
}
/************************************************************/

/************************************************************/
void init_cache() {
  /* initialize the cache, and cache statistics data structures */
  mesi_cache[0].id = 0;
  mesi_cache[0].size = cache_csize;
  mesi_cache[0].associativity = cache_assoc;
  mesi_cache[0].n_sets =
      mesi_cache[0].size / (mesi_cache[0].associativity * cache_block_size);
  if (cache_assoc != 1)
    mesi_cache[0].LRU_tail =
        (Pcache_line *)malloc(sizeof(Pcache_line) * mesi_cache[0].n_sets);
  mesi_cache[0].LRU_head =
      (Pcache_line *)malloc(sizeof(Pcache_line) * mesi_cache[0].n_sets);
  mesi_cache_stat[0] =
      *(cache_stat *)(memset(&mesi_cache_stat[0], 0, sizeof(cache_stat)));
  mesi_cache[0].index_mask_offset = LOG2(cache_block_size);
  mesi_cache[0].index_mask = (unsigned int)(mesi_cache[0].n_sets - 1)
                             << mesi_cache[0].index_mask_offset;
  mesi_cache[0].tag_shift =
      mesi_cache[0].index_mask_offset + LOG2(mesi_cache[0].n_sets);
  mesi_cache[0].tag_mask =
      (unsigned long)(pow(2, 32 - mesi_cache[0].tag_shift) - 1)
      << mesi_cache[0].tag_shift;
}
/************************************************************/

/************************************************************/
void perform_access(addr, access_type, pid) unsigned addr, access_type, pid;
{ /* handle accesses to the mesi caches */
  int index;
  index = (addr & mesi_cache[0].index_mask) >> mesi_cache[0].index_mask_offset;
  mesi_cache_stat[0].accesses += 1;
  if (mesi_cache[0].LRU_head[index] == NULL) {
    // fetch the new value from memory
    mesi_cache_stat[0].demand_fetches += words_per_block;
    // increment the number of misses
    mesi_cache_stat[0].misses += 1;
    // allocate memory for the new cache line and update all of the new values
    mesi_cache[0].LRU_head[index] = (Pcache_line)malloc(sizeof(cache_line));
    mesi_cache[0].LRU_head[index]->tag =
        (addr & mesi_cache[0].tag_mask) >> mesi_cache[0].tag_shift;
    mesi_cache[0].LRU_head[index]->LRU_next = NULL;
    mesi_cache[0].LRU_head[index]->LRU_prev = NULL;
    // let the tail point to the same variable as the head if the access_type is
    // not dm
    if (mesi_cache[0].associativity != 1) {
      mesi_cache[0].LRU_tail[index] = mesi_cache[0].LRU_head[index];
    }
    switch (access_type) {
    case TRACE_LOAD:
      mesi_cache[0].LRU_head[index]->state = STATE_EXCLUSIVE;
      break;
    case TRACE_STORE:
      mesi_cache[0].LRU_head[index]->state = STATE_MODIFIED;
      break;
    }
  } else if (mesi_cache[0].LRU_head[index]->tag !=
             (addr & mesi_cache[0].tag_mask) >> mesi_cache[0].tag_shift) {
    // if the value is not dm, check every other node in the cache line
    // (may still be a hit) -- update values accordingly
    if (mesi_cache[0].associativity != 1) {
      Pcache_line head = mesi_cache[0].LRU_head[index];
      Pcache_line tail = mesi_cache[0].LRU_tail[index];
      Pcache_line curr = mesi_cache[0].LRU_head[index];
      int count = 0;
      while (curr != NULL && curr->tag != (addr & mesi_cache[0].tag_mask) >>
                                              mesi_cache[0].tag_shift) {
        curr = curr->LRU_next;
        count += 1;
      }
      // make a statement if it is a hit -> delete and insert it to put at head
      // just change state
      if (curr != NULL) {
        delete (&head, &tail, curr);
        curr->LRU_next = NULL;
        curr->LRU_prev = NULL;
        insert(&head, &tail, curr);
        switch (access_type) {
        case (TRACE_LOAD):
          break;
        case (TRACE_STORE):
          head->state = STATE_MODIFIED;
          break;
        }
      }
      // make a statement if it is a miss and there is still space -> insert it
      // update as above
      else if (count < mesi_cache[0].associativity) {
        curr = (Pcache_line)malloc(sizeof(cache_line));
        curr->tag = (addr & mesi_cache[0].tag_mask) >> mesi_cache[0].tag_shift;
        curr->LRU_next = NULL;
        curr->LRU_prev = NULL;
        insert(&head, &tail, curr);
        // fetch the new value from memory
        mesi_cache_stat[0].demand_fetches += words_per_block;
        // increment the number of misses
        mesi_cache_stat[0].misses += 1;
        switch (access_type) {
        case TRACE_LOAD:
          head->state = STATE_EXCLUSIVE;
          break;
        case TRACE_STORE:
          head->state = STATE_MODIFIED;
          break;
        }
      }
      // make a statement if it is just a miss -> delete tail and insert new
      // update as below
      else {
        Pcache_line temp = tail;
        curr = (Pcache_line)malloc(sizeof(cache_line));
        curr->tag = (addr & mesi_cache[0].tag_mask) >> mesi_cache[0].tag_shift;
        curr->LRU_next = NULL;
        curr->LRU_prev = NULL;
        if (mesi_cache[0].LRU_tail[index]->state == STATE_MODIFIED)
          mesi_cache_stat[0].copies_back += words_per_block;
        delete (&head, &tail, tail);
        insert(&head, &tail, curr);
        mesi_cache_stat[0].demand_fetches += words_per_block;
        // increment the miss value
        mesi_cache_stat[0].misses += 1;
        // if the current value in the cache has been accessed, write back to
        // memory

        // increment the replacement value
        mesi_cache_stat[0].replacements += 1;
        switch (access_type) { // read miss
        case TRACE_LOAD:
          head->state = STATE_EXCLUSIVE;
          break;
        case TRACE_STORE: // write miss
          head->state = STATE_MODIFIED;
          break;
        }
      }
      mesi_cache[0].LRU_head[index] = head;
      mesi_cache[0].LRU_tail[index] = tail;
    }
    if (mesi_cache[0].associativity == 1) {
      mesi_cache_stat[0].demand_fetches += words_per_block;
      // increment the miss value
      mesi_cache_stat[0].misses += 1;
      // if the current value in the cache has been accessed, write back to
      // memory
      if (mesi_cache[0].LRU_head[index]->state == STATE_MODIFIED)
        mesi_cache_stat[0].copies_back += words_per_block;
      // increment the replacement value
      mesi_cache_stat[0].replacements += 1;
      // replace the tag
      mesi_cache[0].LRU_head[index]->tag =
          (addr & mesi_cache[0].tag_mask) >> mesi_cache[0].tag_shift;
      switch (access_type) {
      case TRACE_LOAD:
        mesi_cache[0].LRU_head[index]->state = STATE_EXCLUSIVE;
        break;
      case TRACE_STORE:
        mesi_cache[0].LRU_head[index]->state = STATE_MODIFIED;
        break;
      }
    }
  } else { // the value is already in the cache
           // and if it is not dm nothing changes
    switch (access_type) {
    case TRACE_LOAD:
      break;
    case TRACE_STORE:
      mesi_cache[0].LRU_head[index]->state = STATE_MODIFIED;
      break;
    }
  }
}
/************************************************************/

/************************************************************/
void flush() { /* flush the mesi caches */
  int i = 0;
  for (; i < mesi_cache[0].n_sets; i++) {
    if (mesi_cache[0].LRU_head[i] != NULL) {
      Pcache_line curr = mesi_cache->LRU_head[i];
      Pcache_line prev = NULL;
      while (curr != NULL) {
        prev = curr;
        if (curr->state == STATE_MODIFIED)
          mesi_cache_stat[0].copies_back += words_per_block;
        curr = curr->LRU_next;
        free(prev);
      }
    }
  }
}
/************************************************************/

/************************************************************/
void delete(head, tail, item)Pcache_line *head, *tail;
Pcache_line item;
{
  if (item->LRU_prev) {
    item->LRU_prev->LRU_next = item->LRU_next;
  } else {
    /* item at head */
    *head = item->LRU_next;
  }

  if (item->LRU_next) {
    item->LRU_next->LRU_prev = item->LRU_prev;
  } else {
    /* item at tail */
    *tail = item->LRU_prev;
  }
}
/************************************************************/

/************************************************************/
/* inserts at the head of the list */
void insert(head, tail, item) Pcache_line *head, *tail;
Pcache_line item;
{
  item->LRU_next = *head;
  item->LRU_prev = (Pcache_line)NULL;

  if (item->LRU_next)
    item->LRU_next->LRU_prev = item;
  else
    *tail = item;

  *head = item;
}
/************************************************************/

/************************************************************/
void dump_settings() {
  printf("Cache Settings:\n");
  printf("\tSize: \t%d\n", cache_csize);
  printf("\tAssociativity: \t%d\n", cache_assoc);
  printf("\tBlock size: \t%d\n", cache_block_size);
}
/************************************************************/

/************************************************************/
void print_stats() {
  int i;
  int demand_fetches = 0;
  int copies_back = 0;
  int broadcasts = 0;

  printf("*** CACHE STATISTICS ***\n");

  for (i = 0; i < num_core; i++) {
    printf("  CORE %d\n", i);
    printf("  accesses:  %d\n", mesi_cache_stat[i].accesses);
    printf("  misses:    %d\n", mesi_cache_stat[i].misses);
    printf("  miss rate: %f (%f)\n",
           (float)mesi_cache_stat[i].misses /
               (float)mesi_cache_stat[i].accesses,
           1.0 - (float)mesi_cache_stat[i].misses /
                     (float)mesi_cache_stat[i].accesses);
    printf("  replace:   %d\n", mesi_cache_stat[i].replacements);
  }

  printf("\n");
  printf("  TRAFFIC\n");
  for (i = 0; i < num_core; i++) {
    demand_fetches += mesi_cache_stat[i].demand_fetches;
    copies_back += mesi_cache_stat[i].copies_back;
    broadcasts += mesi_cache_stat[i].broadcasts;
  }
  printf("  demand fetch (words): %d\n", demand_fetches);
  /* number of broadcasts */
  printf("  broadcasts:           %d\n", broadcasts);
  printf("  copies back (words):  %d\n", copies_back);
}
/************************************************************/

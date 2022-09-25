#include "tree.h"
#include "memory_pool.h"

#include <tuple>
#include <string>
#include <iostream>
#include <array>
#include <unordered_map>
#include <cstring>

using namespace std;

bool nullPtr = false;

// a node consist of a list of key:pointers
Node::Node(int maxKeys)
{

  // a tuple array, each tuple contains a pointer to a block and an offset
  pointers = new std::tuple<void*, size_t>[maxKeys + 1];

  // Initialize empty array of keys, int type numVotes
  keys = new int[maxKeys];

  int numKeys = 0;

  for (int i = 0; i < maxKeys + 1; i++)
  {
    // assign a tuple of (void*, size_t) to be used as a null pointer
    pointers[i] = std::make_tuple((void*)nullPtr, 0);
  }
  
}

BPlusTree::BPlusTree(std::size_t blockSize, MemoryPool *disk, MemoryPool *index)
{
  // Get size left for keys and pointers in a node after accounting for node's isLeaf and numKeys attributes.
  size_t nodeBufferSize = blockSize - sizeof(bool) - sizeof(int);

  // Set max keys available in a node. Each key is an integer, each pointer is a tuple - {void *blockAddress, short int offset}.
  // Therefore, each key is 4 bytes. Each pointer is around 16 bytes.

  // Initialize node buffer with a pointer. P | K | P , always one more pointer than keys.
  size_t sum = sizeof(std::tuple<void*, size_t>);
  maxKeys = 0;

  // Try to fit as many pointer key pairs as possible into the node block.
  while (sum + sizeof(std::tuple<void*, size_t>) + sizeof(int) <= nodeBufferSize)
  {
    sum += (sizeof(std::tuple<void*, size_t>) + sizeof(int));
    maxKeys += 1;
  }

  if (maxKeys == 0)
  {
    throw std::overflow_error("Error: Keys and pointers too large to fit into a node!");
  }

  // Initialize root to NULL
  rootAddress = nullptr;
  root = nullptr;

  // 1 node consist of many key:value pairs, 1 node size = 1 block size
  // Set node size to be equal to block size.
  nodeSize = blockSize;

  // Initialize initial variables
  levels = 0;
  numNodes = 0;

  // Initialize disk space for index and set reference to disk.
  this->disk = disk;
  this->index = index;
}


#include "memory_pool.h"

#include <iostream>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <math.h>
#include <string.h>

using namespace std;

int main()
{
  int BLOCKSIZE = 0;
  int choice = 0;
  std :: cout <<"Choose your block size: "<<endl;

  while (choice != 1 && choice != 2)
  {
    std :: cout <<"1. 200 BYTES"<<endl;
    std :: cout <<"2. 500 BYTES"<<endl;
    std :: cin >> choice;

    if (choice == 1)
    {
      BLOCKSIZE = 200;
    }
    else if (choice == 2)
    {
      BLOCKSIZE = 500;
    }
    else
    {
      std :: cout <<"Invalid choice. Please try again."<<endl;
      cin.clear();
    }
  }

  // MemoryPool(maxPoolSize, blockSize);
  // 1st param - maxPoolSize 500MB
  // 2nd param - blockSize
  MemoryPool memory_pool(500*(pow(10,6)), int(BLOCKSIZE)); // 500 MB

  // Open test data
  // test data so its only 300 records
  std::ifstream file("../data/test_data.tsv");

  if (file.is_open())
  {
    std::string line;
    int recordNum = 1;
    while (std::getline(file, line))
    {
      Record rec;
      stringstream linestream(line);
      string data;

      // reading each record, store the string into rec.tconst, consist of 3 fields
      strcpy(rec.tconst, line.substr(0, line.find("\t")).c_str());

      std::getline(linestream, data, '\t');
      linestream >> rec.averageRating >> rec.numVotes;

      // allocate memory for 1 record tuple
      std::tuple<void *, std::size_t> record = memory_pool.allocate(sizeof(rec));

      // copy the tuple record into the previously allocated mem
      // memcpy(destination ptr, source ptr, size)
      // get<0>(record) is the starting of pointer
      // get<1> is the size of the record, aka offset
      memcpy(std::get<0>(record) + std::get<1>(record), &rec, sizeof(rec));

      std :: cout << "Reading line " << recordNum << " of movie data" << '\n';
      std :: cout << "Size of a record: " << sizeof(rec) << " bytes" << '\n';
      std :: cout << "Inserted record " << recordNum << " at address: " << std::get<0>(record) + std::get<1>(record) << '\n';

      // checking if the record is inserted correctly by printing out record tconst
      Record check = *(Record *)(std::get<0>(record) + std::get<1>(record));
      std :: cout << "get<0> record:" << std::get<0>(record) << '\n';
      std :: cout << "get<1> record:" << std::get<1>(record) << '\n';
      std :: cout << check.tconst << '\n';

      // keep a running count
      recordNum += 1;
    }
    file.close();
  };

  std :: cout << "Current blocks used: " << memory_pool.getAllocated() << " blocks" << '\n';
  std :: cout << "Actual size used: " << memory_pool.getActualSizeUsed() << " bytes" << '\n';
  std :: cout << "Total size occupied: " << memory_pool.getSizeUsed() << " bytes" << '\n';

  return 0;
}
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
	std ::cout << "Choose your block size: " << endl;

	while (choice != 1 && choice != 2)
	{
		std ::cout << "1. 200 BYTES" << endl;
		std ::cout << "2. 500 BYTES" << endl;
		std ::cin >> choice;

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
			std ::cout << "Invalid choice. Please try again." << endl;
			cin.clear();
		}
	}

	MemoryPool memory_pool(500 * (pow(10, 6)), int(BLOCKSIZE)); // 500 MB

	// Open test data
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

			strcpy(rec.tconst, line.substr(0, line.find("\t")).c_str());

			std::getline(linestream, data, '\t');
			linestream >> rec.averageRating >> rec.numVotes;

			std::tuple<void *, std::size_t> record = memory_pool.allocate(sizeof(rec));

			memcpy(std::get<0>(record) + std::get<1>(record), &rec, sizeof(rec));

			std ::cout << "Reading line " << recordNum << " of movie data" << '\n';
			std ::cout << "Size of a record: " << sizeof(rec) << " bytes" << '\n';
			std ::cout << "Inserted record " << recordNum << " at address: " << std::get<0>(record) + std::get<1>(record) << '\n';

			Record check = *(Record *)(std::get<0>(record) + std::get<1>(record));
			std ::cout << check.tconst << '\n';

			recordNum += 1;
		}
		file.close();
	};

	std ::cout << "Current blocks used: " << memory_pool.getAllocated() << " blocks" << '\n';
	std ::cout << "Actual size used: " << memory_pool.getActualSizeUsed() << " bytes" << '\n';
	std ::cout << "Total size occupied: " << memory_pool.getSizeUsed() << " bytes" << '\n';
	return 0;
}
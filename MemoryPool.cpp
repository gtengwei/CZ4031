//Written by LR
//Stores both btree index and the disk
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <functional>
#include <algorithm>
#include <math.h>

#include "Tree.cpp"
#include "Disk.cpp"

class MemoryPool {
    private:
        string filename; //tsv data we want to import
        Disk * disk; //for now 3 for testing
        bTree * btree;

        vector<string> split(string stringToSplit){
            char delimiter = '\t';
            vector<string> result;
            int indexOfLastDelimiter = -1;
            for (int i=0;i<stringToSplit.size();i++){
                if (stringToSplit[i] == delimiter){
                    string substring = stringToSplit.substr(indexOfLastDelimiter+1, i-indexOfLastDelimiter);
                    result.push_back(substring);
                    indexOfLastDelimiter = i;
                } else if (i==(stringToSplit.size()-1)){
                    string substring = stringToSplit.substr(indexOfLastDelimiter+1, i-indexOfLastDelimiter);
                    result.push_back(substring);
                }
            }
            return result;
        }

    public:
        MemoryPool(string filename, int blockSize){
            this->filename= filename;
            int numKeys = numberOfKeysInBplusTree(blockSize);
            this->btree = new bTree(numKeys);
            this->disk = new Disk(blockSize);
        } 

        //For experiment 1:
        //Experiment 1: Store the data and report the following statistics:
        //- the number of blocks
        //- the size of database (in terms of MB)
        void experiment1(int BLOCKSIZE){
            //read file
            ifstream file(this->filename);
            //read each line from the tsv file
            string line;
            int i = 0;
            int recordNum = 0;
            while (getline (file, line)) {
                // checking data loading progress
                if (recordNum % 50000 == 0) {
                    cout << "Record " << recordNum << " Read" << endl;
                }
                recordNum++;

                // cout << "Size of a record: " << sizeof(line) << " bytes" << '\n';
                this->disk->insert(line); //add tuple to disk
            }
            file.close();
            //number of blocks output
            int numBlocks = disk->getTotalNumberOfBlocks();
            cout << "Total Number of Blocks: " << numBlocks <<"\n";
            //the size of database (in terms of MB)
            // int blocksize = disk->getBlockSizeinByte();
            cout<<"Block size: "<< BLOCKSIZE << "\n";
            float database_size = (float(numBlocks * BLOCKSIZE) / float((pow(10,6)))); // 1MB = 10^6 bytes
            cout <<  "Size of database (in terms of MB): " << database_size << "\n";
        }

        void addToDiskAndBplus(){
            //read file
            ifstream file(this->filename);
            int i = 0;
            //read each line from the tsv file
            string line;
            int recordNum = 0;
            while (getline (file, line)) {
                // checking data loading progress
                if (recordNum % 50000 == 0) {
                    cout << "Record " << recordNum << " Read" << endl;
                }
                recordNum++;
                
                void * pointer = this->disk->insert(line);
                int key = stoi(split(line)[2]);
                this->btree->insertToBTree(key,pointer);
            }
            file.close();
        }


//         Experiment 2: build a B+ tree on the attribute "numVotes" by inserting the
//          records sequentially and report the following statistics:
//          - the parameter n of the B+ tree
//          - the number of nodes of the B+ tree
//          - the height of the B+ tree, i.e., the number of levels of the B+ tree
//          - the content of the root node and its 1st child node
        void experiment2(){
            cout << "Parameter, n: " << btree->getN() << "\n";
            cout << "Number Of Nodes in B+ Tree: " << btree->getNumberOfNodes() <<"\n";
            cout << "Height of B+ tree: " << btree->getHeight() <<"\n";
            cout << "Content of root node: ";
            btree->getRoot()->printAllKeys();
            cout << "\n";
            cout << "Content of 1st child node: ";
            Node * firstChild = (Node *)btree->getRoot()->children[0];
            firstChild->printAllKeys();
            cout << "\n";
        }

        void experiment3()
        {
            vector<pair<int,int> > result=btree->search(500);
            
            float sumOfAvgRatings=0;
            int counter = 0;

            vector<float> allRatings;
            vector<float> allnumVotes;
            vector<int> visited_block;
            // cout<<"size of result is"<<result.size();
            for(auto x: result)
            {
                //If block has been visited, proceed to next index_key pointer.
                //All records in a block is read when block is accessed
                if (find(visited_block.begin(), visited_block.end(), x.first) != visited_block.end()){
                    continue;
                }

                //Currently at unvisited data block
                //Add pointer to visited_block for future reference
                //Adding from the back, index[0] to [4] will be the first 5 data block to print
                Block temp_block = disk->getBlock(x.first);
                visited_block.push_back(x.first);
                counter++;

                //Iterate through records of entire data block.
                //Only care about records with numVotes 30000<=x<=40000
                for (int i = 0; i < temp_block.numberSlot; i++){
                    if (temp_block.getRecord(i).numVotes==500){
                        allRatings.push_back(disk->getRecord(x.first,x.second).avgRating);
                        allnumVotes.push_back(disk->getRecord(x.first,x.second).numVotes);
                    }
                }
            }

            //Sum up AvgRatings to find average of AvgRatings
            for(auto avgRating: allRatings){
                sumOfAvgRatings+=avgRating;
            } 

            cout<<"First 5 Data Block Read:"<<endl;
            for (int i = 0; i < 5; i++){
                cout<<"Data Block "<<to_string(i+1)<<endl;
                cout<<string(10, '-')<<endl;
                disk->getBlock(visited_block[i]).print();
                cout<<string(10, '-')<<endl;
            }            
            cout<<"Number of data blocks the process accesses: "<<counter<<endl;
            cout<<"Average of \"averageRatings\" of the records: "<<sumOfAvgRatings/allRatings.size()<<endl;
        }

         void experiment4()
        {
            vector<pair<int,int> > result=btree->searchRange(30000,40000);

            float sumOfAvgRatings=0;
            int counter = 0;

            vector<float> allRatings;
            vector<float> allnumVotes;
            vector<int> visited_block;
            // cout<<"size of result is"<<result.size();
            for(auto x: result)
            {
                //If block has been visited, proceed to next index_key pointer.
                //All records in a block is read when block is accessed
                if (find(visited_block.begin(), visited_block.end(), x.first) != visited_block.end()){
                    continue;
                }

                //Currently at unvisited data block
                //Add pointer to visited_block for future reference
                //Adding from the back, index[0] to [4] will be the first 5 data block to print
                Block temp_block = disk->getBlock(x.first);
                visited_block.push_back(x.first);
                counter++;

                //Iterate through records of entire data block.
                //Only care about records with numVotes 30000<=x<=40000
                for (int i = 0; i < temp_block.numberSlot; i++){
                    if (temp_block.getRecord(i).numVotes>=30000 && temp_block.getRecord(i).numVotes<=40000){
                        allRatings.push_back(disk->getRecord(x.first,x.second).avgRating);
                        allnumVotes.push_back(disk->getRecord(x.first,x.second).numVotes);
                    }
                }
            }

            //Sum up AvgRatings to find average of AvgRatings
            for(auto avgRating: allRatings){
                sumOfAvgRatings+=avgRating;
            } 

            cout<<"First 5 Data Block Read:"<<endl;
            for (int i = 0; i < 5; i++){
                cout<<"Data Block "<<to_string(i+1)<<endl;
                cout<<string(10, '-')<<endl;
                disk->getBlock(visited_block[i]).print();
                cout<<string(10, '-')<<endl;
            }            
            cout<<"Number of data blocks the process accesses: "<<counter<<endl;
            cout<<"Average of \"averageRatings\" of the records: "<<sumOfAvgRatings/allRatings.size()<<endl;
        }

        //Experiment 5: delete those movies with the attribute “numVotes” equal to1,000, update the B+ tree accordingly, and report the following statistics:
        // -the number of times that a node is deleted (or two nodes are merged)during the process of the updating the B+ tree
        // -the number nodes of the updated B+ tree
        // -the height of the updated B+ tree
        // -the content of the root node and its 1st child node of the updated B+tree
        void experiment5(){
            int totalNumKeysToDelete = btree->getNumberOfKeysToDelete(1000);
            int merged_node_count = 0;
            int mergeCount=0;
            for (int i=0;i<totalNumKeysToDelete;i++){
                pair<int,int> * pair = btree->deleteOneKey(1000, &mergeCount);
                cout << "Deleting key: " << pair->first << " from block: " << pair->second << "\n";
                merged_node_count= merged_node_count + mergeCount;
                cout << "Merged node count: " << merged_node_count << "\n";
                disk->deleteRecord(pair->first,pair->second);
            }
            cout << "Number of times that a node is deleted: "<<merged_node_count<<endl;
            cout << "Number of nodes in updated B+ tree: "<< btree->getNumberOfNodes()<<endl;
            cout << "Height of the updated B+ tree:" << btree->getHeight()<<endl;
            cout << "Content of the root node: " ;
            btree->getRoot()->printAllKeys();
            cout << endl;
            cout << "Content of first child node: ";
            ((Node *)btree->getRoot()->children[0])->printAllKeys();
            cout << endl;
        }

        int numberOfKeysInBplusTree(int blockSize){
            int numBytesPerKey = 4; //since it is an integer
            int numBytesPerValue = 8; //8 bytes for a pointer in 64bit computer
            //bytesUsed = numBytesPerKey * numKeys + numBytesPerValue * (numKeys+1);
            //So numKeys = floor((numBytes-numBytesPerValue)/(numBytesPerKey+numBytesPerValue))
            return floor((blockSize-numBytesPerValue)/(numBytesPerKey+numBytesPerValue));
        }

        void printBlocks(){
            this->disk->printRecords();
        }

        void printTree(){
            this->btree->printNodeTree();
        }

        void printLastRowOfPointers(){
            this->btree->printLastRowPointers();
            cout << endl;
        }

        void printAllRecordsAccordingToIndex(){
            cout << "printAllRecordsAccordingToIndex"<<endl;
            vector<void *> children =  this->btree->returnLastRowPointers();
            for (auto child:children){
                pair<int,int>* castedChild = (pair<int,int>*) child;
                cout<< "<"<<castedChild->first<<","<<castedChild->second<<">"<<": ";
                cout<<disk->getRecord(castedChild->first,castedChild->second).toString();
            }
        }

         void printAllRecords(){
            cout << "printAllRecords"<<endl;
            vector<void *> children =  this->btree->returnLastRowPointers();
            cout <<"|";
            for (int i=0;i<children.size();i++){
                pair<int,int>* castedChild = (pair<int,int>*) children[i];
                cout<<disk->getRecord(castedChild->first,castedChild->second).NumberOfVotes()<<"|";
            }
            cout<<endl;
        }

    ~MemoryPool(){
        free(disk);
        free(btree);
    }
};
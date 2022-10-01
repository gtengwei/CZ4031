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
                // cout << "Size of a record: " << sizeof(line) << " bytes" << '\n';
                this->disk->insert(line); //add tuple to disk
                recordNum++;
            }
            file.close();
            //number of blocks output
            int numOfBlocks = disk->getTotalNumberOfBlocks();
            cout << "Total Number of Blocks: " << numOfBlocks <<"\n";
            //the size of database (in terms of MB)
            // int blocksize = disk->getBlockSizeinByte();
            cout<<"Block size: "<< BLOCKSIZE << "\n";
            float database_size = (float(numOfBlocks * BLOCKSIZE) / float((pow(10,6)))); // 1MB = 10^6 bytes
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
                void * pointer = this->disk->insert(line);
                int key = stoi(split(line)[2]);
                this->btree->insertToBTree(key,pointer);
                recordNum++;
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
            float SUM=0;

            vector<float> allRatings;
            vector<int> allnumVotes;
            // cout<<"Size of result: "<<result.size()<<"\n";
            cout<<"Content of top 5 data blocks accessed: "<<endl;
            int counter = 0;
            for(auto x: result)
            {
                //print out the top 5 the datablocks
                if (counter<5){
                    cout << "Data block "<<counter<<":"<<endl;
                    disk->getBlock(x.first).print();
                }
                Record tempRec = disk->getRecord(x.first,x.second);
                float temp=tempRec.avgRating;
                int temp2=tempRec.numVotes;
                allRatings.push_back(temp);
                allnumVotes.push_back(temp2);
                counter++;
            }
            // cout << endl;
            for(auto x: allRatings){
                SUM+=x;
            } 
            int ratingsSize = allRatings.size();
            cout<<"Number of data blocks accessed: "<<ratingsSize<<"\n";
            cout<<"Average of \"averageRating\"s of the records: "<<SUM/ratingsSize<<"\n";
        }

         void experiment4()
        {
            vector<pair<int,int> > result=btree->searchRange(30000,40000);

            float SUM=0;
            int counter = 0;

            vector<float> allRatings;
            vector<float> allnumVotes;
            // cout<<"size of result is"<<result.size();
            for(auto x: result)
            {
                //print out the top 5 the datablocks
                if (counter<5){
                    cout << "Data block "<<counter<<":"<<endl;
                    disk->getBlock(x.first).print();
                }
                float temp=disk->getRecord(x.first,x.second).avgRating;
                allRatings.push_back(temp);
                int temp2=disk->getRecord(x.first,x.second).numVotes;
                allnumVotes.push_back(temp2);
                counter++;
            }
            for(auto x: allRatings){
                SUM+=x;
                // cout <<x<<",";
            } 
            // cout << endl;
            // for(auto x: allnumVotes){
            //     cout <<x<<",";
            // }
            // cout <<"sum:" << SUM<<endl;
            cout<<"Number of data blocks the process accesses: "<<allRatings.size()<<endl;
            cout<<"Average of \"averageRatings\" of the records: "<<SUM/allRatings.size()<<endl;
        }

        //Experiment 5: delete those record with number of votes = 1000, report the folowing
        // - how many nodes purged/deleted
        // -the number nodes of the new B+ tree
        // -the height of the new B+ tree
        // -the content of the root node and its 1st child node of the updated B+tree
        void experiment5(){
            int totalNumKeysToDelete = btree->getNumberOfKeysToDelete(1000);
            int numOfPurgedNodes = 0;
            int mergeCount=0;
            cout << "Number of keys to be deleted (occurence of NumVote=1000):" << totalNumKeysToDelete << "\n";
            for (int i=0;i<totalNumKeysToDelete;i++){
                pair<int,int> * pair = btree->deleteOneKey(1000, &mergeCount);
                // cout << "Deleting key: " << pair->first << " from block: " << pair->second << "\n";
                numOfPurgedNodes= numOfPurgedNodes + mergeCount;
                // cout << "Merged node count: " << numOfPurgedNodes << "\n";
                disk->deleteRecord(pair->first,pair->second);
            }
            cout << "Node count in new B+ tree: "<< btree->getNumberOfNodes()<<endl;
            cout << "Node count that a node is deleted: "<<numOfPurgedNodes<<endl;
            cout << "Height of the new B+ tree:" << btree->getHeight()<<endl;
            cout << "Keys/Content of the root node: " ;
            btree->getRoot()->printAllKeys();
            cout << endl;
            cout << "keys/Content of first child node (smallest value in db):";
            ((Node *)btree->getRoot()->children[0])->printAllKeys();
            cout << endl;
        }

        int numberOfKeysInBplusTree(int blockSize){
            // 4 bytes for an integer type
            int numBytesPerKey = 4; 
            // 8 bytes for a pointer in 64bit computer
            int numBytesPerValue = 8; 
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

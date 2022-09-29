//Written by LR
//Stores both btree index and the disk
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <functional>
#include <algorithm>
#include "Tree.cpp"
#include "Disk.cpp"

class Database {
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
        Database(string filename, int numBytes){
            this->filename= filename;
            int numKeys = numberOfKeysInBplusTree(numBytes);
            this->btree = new bTree(numKeys);
            this->disk = new Disk(numBytes);
        } 

        //For experiment 1:
        //Experiment 1: Store the data and report the following statistics:
        //- the number of blocks
        //- the size of database (in terms of MB)
        void addAllRecordsWithNoIndex(){
            //read file
            ifstream file(this->filename);
            //read each line from the tsv file
            string line;
            int i = 0;
            while (getline (file, line)) {
                if (i==0){ //ignore header
                    i++;
                    continue;
                }
                this->disk->insert(line); //add tuple to disk
            }
            file.close();
            //number of blocks output
            int numBlocks = disk->getTotalBlocks();
            cout << "Total Number of Blocks: " << numBlocks <<"\n";
            //the size of database (in terms of MB)
            int blocksize = disk->getBlockSizeinByte();
            // cout<<"the block size is "<<blocksize;
            float mb = (float(numBlocks * blocksize) / float(1024*1024));
            cout <<  "Size of database (in terms of MB): " << mb << "\n";
        }

        void addToDiskAndBplus(){
            //read file
            ifstream file(this->filename);
            int i = 0;
            //read each line from the tsv file
            string line;
            while (getline (file, line)) {
                if (i==0){ //ignore header
                    i++;
                    continue;
                }
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
            float SUM=0;

            vector<float> allRatings;
            vector<float> allnumVotes;
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
                // cout<< "<"<<x.first<<","<<x.second<<">"<<",";
                float temp=disk->getRecord(x.first,x.second).rating;
                int temp2=disk->getRecord(x.first,x.second).numVotes;
                allRatings.push_back(temp);
                allnumVotes.push_back(temp2);
                counter++;
            }
            // cout << endl;
            for(auto x: allRatings){
                SUM+=x;
                // cout <<x<<",";
            } 
            // cout << endl;
            // for(auto x: allnumVotes){
            //     cout <<x<<",";
            // }
            // cout <<"sum:" << SUM<<endl;
            cout<<"Number of data blocks accessed: "<<allRatings.size()<<"\n";
            cout<<"Average of \"averageRating\"s of the records: "<<SUM/allRatings.size()<<"\n";
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
                float temp=disk->getRecord(x.first,x.second).rating;
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
                merged_node_count= merged_node_count +mergeCount;
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

        int numberOfKeysInBplusTree(int numBytes){
            int numBytesPerKey = 4; //since it is an integer
            int numBytesPerValue = 8; //8 bytes for a pointer in 64bit computer
            //bytesUsed = numBytesPerKey * numKeys + numBytesPerValue * (numKeys+1);
            //So numKeys = floor((numBytes-numBytesPerValue)/(numBytesPerKey+numBytesPerValue))
            return floor((numBytes-numBytesPerValue)/(numBytesPerKey+numBytesPerValue));
        }

        void printBlocks(){
            this->disk->printAllRecord();
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
                cout<<disk->getRecord(castedChild->first,castedChild->second).getNumVotes()<<"|";
            }
            cout<<endl;
        }

    ~Database(){
        free(disk);
        free(btree);
    }
};

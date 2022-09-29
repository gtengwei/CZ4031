// double linkedlist(database)    containing page and record id
// blocks are vector of block
// getBlock(int pageid)
// insertBlock()
// go pageRecord(int pageid,recordid)

//

#include "Block.cpp"
#include <list>
#include <iterator>
#include <unordered_set>
// 
using namespace std;
class Disk
{
    public: 
    vector<Block> blocks;
    list<pair<int,int> > database;
    unordered_set<int> unoccupiedblocks;
    int numBytes;
    

    Disk (int numBytes){
        this->numBytes = numBytes;
        blocks.push_back(Block(this->numBytes));

    }

    void readBlock(int blockid)
    {
        blocks[blockid].print();
    }
    void readRecord(int blockid,int recordid)
    {
        blocks[blockid].getRecord(recordid).toString();
    }
    Record getRecord(int blockid,int recordid)
    {
        return blocks[blockid].getRecord(recordid);
    }

    void deleteRecord(int blockid, int recordid)
    {
        // deletion is inefficient.
        // assume the blockid and recordid are correct
        blocks[blockid].deleteSlot(recordid);
        unoccupiedblocks.insert(blockid);
        database.remove(make_pair(blockid,recordid));

    }

    void deleteBypointer(void* p)
    {
        auto temp=(pair<int,int> *) p;
        deleteRecord((*temp).first,(*temp).second);
        // blocks[(*temp).first].deleteSlot((*temp).second);
        // unoccupiedblocks.insert((*temp).first);

        // list<pair<int,int> >::iterator it( p );
        // database.erase(it);
    }

    int getTotalNumberOfBlocks()
    {
        return blocks.size();
    }

    // Commented out this part because it is not used
    // int getBlockSizeinByte()
    // {   
    
    //     // if (blocks.size()>0) return blocks.back().size;
    //     // else return 0;
    //     return blocks.back().size;
    // }

    void * insert(string s)
    {
        // insert at the end 
        Record record = Record(s);

        // Commented out this part because it is not used

        // while (unoccupiedblocks.size()>0)
        // {
        //     int i=*unoccupiedblocks.begin();
        //     int recordIdTemp=blocks[i].add(temp);
        //     if (recordIdTemp==-1)
        //     {
        //         unoccupiedblocks.erase(i);
        //     }
        //     else
        //     {
        //         // insert record into database at the end
        //         database.push_back(make_pair(i,recordIdTemp));
        //         //cout<<"inserting into "<<i<<recordIdTemp;
        //         return &database.back();
        //     }

        // }
        int recordId=blocks.back().add(record);
         //cout<<"the record Id is "<<recordId<<"-------";
        if (recordId==-1)
        {
            // cout<<"disk overflow \n";
            blocks.push_back(Block(this->numBytes));
            recordId=blocks.back().add(record);
        }
        cout << "Record size: " << sizeof(record) << endl;
        cout << "Tconst size: " << sizeof(record.tconst) << endl;
        cout << "Rating size: " << sizeof(record.avgRating) << endl;
        cout << "Votes size: " << sizeof(record.numVotes) << endl;
        //cout<<"inserting into "<<blocks.size()-1<<recordId;
        database.push_back(make_pair(blocks.size()-1,recordId));
        return &database.back();
    }

    void printRecords()
    {
        cout<<"size of blocks is "<<blocks.size()<<endl;
        for(int i=0;i<blocks.size();i++)
        {
            blocks[i].print();
        }
    }

    Block getBlock(int i){
        return blocks[i];
    }

};
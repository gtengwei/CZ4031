// double linkedlist(directory)    containing page and record id
// blocks are vector of block
// getBlock(int pageid)
// insertBlock()
// go pageRecord(int pageid,recordid)

//

#include "Block.cpp"
#include <list>
#include <iterator>
# include <unordered_set>
// 
using namespace std;
class Disk
{
    public: 
    vector<Block> blocks;
    list<pair<int,int> > directory;
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
        directory.remove(make_pair(blockid,recordid));

    }

    void deleteBypointer(void* p)
    {
        auto temp=(pair<int,int> *) p;
        deleteRecord((*temp).first,(*temp).second);
        // blocks[(*temp).first].deleteSlot((*temp).second);
        // unoccupiedblocks.insert((*temp).first);

        // list<pair<int,int> >::iterator it( p );
        // directory.erase(it);
    }

    int getTotalBlocks()
    {
        return blocks.size();
    }

    int getBlockSizeinByte()
    {
        if (blocks.size()>0) return blocks.back().size;
        else return 0;
    }

    void * insert(string s)
    {
        // insert at the end 
        Record temp=Record(s);
        while (unoccupiedblocks.size()>0)
        {
            int i=*unoccupiedblocks.begin();
            int recordIdTemp=blocks[i].add(temp);
            if (recordIdTemp==-1)
            {
             unoccupiedblocks.erase(i);
            }
            else{
                directory.push_back(make_pair(i,recordIdTemp));
                // cout<<"inserting into "<<i<<recordIdTemp;
                return &directory.back();
            }

        }
        int recordId=blocks.back().add(temp);
         //cout<<"the record Id is "<<recordId<<"-------";
        if (recordId==-1)
        {
            // cout<<"disk overflow \n";
            blocks.push_back(Block(this->numBytes));
            recordId=blocks.back().add(temp);
        }
        //cout<<"inserting into "<<blocks.size()-1<<recordId;
        directory.push_back(make_pair(blocks.size()-1,recordId));
        return &directory.back();
    }

    void printAllRecord()
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
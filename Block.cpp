#include <vector>
#include <iostream>
#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <vector>
#include <utility>
#include "Record.cpp"
#include "constant.hpp"
using namespace std;

class Block {
    public:
    int numberSlot;
    int lastPosition;
    int size;
    char* m;



   Block (int x) : m(new char[x-2]){
       size=x;
       numberSlot=0;
       lastPosition=x;
    //    lastPosition = x-2;

   }

   int add(Record a)
   {   
       int temp1=lastPosition-(int)sizeof(a);
       int temp2=numberSlot*sizeof(int);
       
       //cout << std::boolalpha;  
       //cout<< ((lastPosition-(int)sizeof(a))< numberSlot*sizeof(int));
       //if ((lastPosition-(int)sizeof(a)) < numberSlot*sizeof(int)) { cout<<"overrrrrrrrrrflow";return -1;   }              // overflow, not possible to add more
       
       // Currently one block has only 8 records for BLOCKSIZE = 200 for the condition ( temp1 < temp2)
       // Changing to temp1 < 0 means that we will have 10 records in the block
       // However, this will result in experiment 5 not working
       if (temp1 < 0) {
        //    cout<<"block overflow \n";
           return -1;}
       int newSlotId=0;
        while (newSlotId<numberSlot && *((int *)(m+4*newSlotId))!=0)      // find the empty one 
           {
            newSlotId+=1;
           }
        //cout<<newslotId<<",,,,";
           
       memcpy(m+lastPosition-sizeof(a),&a,sizeof(a));
       lastPosition-=sizeof(a);
       //cout<<"last position is "<< lastPosition;
       memcpy(m+4*newSlotId,&lastPosition,sizeof(lastPosition));
       //*((int *)(m+4*numberSlot)) = lastPosition;
       //
       //*((int *)(m+4*numberSlot)) = lastPosition;
       //m[numberSlot-1]=lastPosition;
       if (!(newSlotId<numberSlot)) numberSlot+=1;
       return newSlotId;
   }

   Record getRecord(int slotId)
   {
       int lastPosition=*((int *)(m+4*slotId));
       return  *(Record *)(m+lastPosition);
   }

   void deleteSlot(int slotId)
   {    
    int oldLastposition=*((int *)(m+4*slotId));

    memmove( m+lastPosition+sizeof(Record), m+lastPosition, oldLastposition-lastPosition);
    lastPosition+=sizeof(Record);
        for(int i=slotId+1;i<numberSlot;i++)
        {
            int tempPosition=*((int *)(m+4*i));
            //cout<<"old"<<tempPosition;
            if (tempPosition!=0) *((int *)(m+4*i))=tempPosition+sizeof(Record); // shift the slot reference by Record id.
            // new 
        }
       *((int *)(m+4*slotId))=0;
       //numberSlot-=1;

   }


   void print()
   {
       for(int i=0;i<numberSlot;i++)
       {
           int temp=*((int *)(m+4*i));
           cout<<temp<<"|";
       }

       for(int i=numberSlot;i<lastPosition;i++)
       {

           cout<<".";
       }

        cout<<"\n";
        cout << "tconst\taverageRating\tnumVotes"<<endl;
       for(int i=lastPosition;i+sizeof(Record)<=size-2;i+=(sizeof(Record)))
       {
           Record temp= *(Record *) (m+i);
           cout<<temp.toString();
       }
   }    

};


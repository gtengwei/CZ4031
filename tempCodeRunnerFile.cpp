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
        //         // cout<<"inserting into "<<i<<recordIdTemp;
        //         return &database.back();
        //     }

        // }
        // int recordId=blocks.back().add(temp);
        //  //cout<<"the record Id is "<<recordId<<"-------";
        // if (recordId==-1)
        // {
        //     // cout<<"disk overflow \n";
        //     blocks.push_back(Block(this->numBytes));
        //     recordId=blocks.back().add(temp);
        // }
        // //
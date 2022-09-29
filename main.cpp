#include <iostream> 
#include <string> 
#include "Database.cpp"

// /*
// result from python script
// experiment 3:
// 110
// 6.731818181818184

// b+tree result:
// ize of result is110number of records is110
// the average of “averageRating’s” of the records: is 6.76273 


// experiement 4:
// 953
// 6.727911857292764

// b+ tree: 953number of records is953the average of “averageRating’s” of the records: is 6.72844


// experient 5 
// 42 by b+ tree


int main(){
    //100 is the number of bytes for a node
    //The number of keys in a node is calculated like this
    //floor((numBytes-numBytesPerValue)/(numBytesPerKey+numBytesPerValue));
    Database database1("tsv_files/data.tsv",100);
    Database database2("tsv_files/data.tsv",500);

    
    int choice;
    cout << "Which experiment result to view? (Type 1-10)\n";
    cout << "Experiment 1: Store data in disk (100 Bytes)\n";
    cout << "Experiment 2: Build a B+ tree on the attribute \"numVotes\" (100 Bytes)\n";
    cout << "Experiment 3: Retrieve movies with attribute \"numVotes\" equal to 500 (100 Bytes)\n";
    cout << "Experiment 4: Retrieve movies with attribute \"numVotes\" from 30,000 to 40,000, both inclusively (100 Bytes)\n";
    cout << "Experiment 5: Delete those movies with the attribute \"numVotes\" equal to 1,000 (100 Bytes)"<<endl;
    cout << "Experiment 6: Store data in disk (500 Bytes)\n";
    cout << "Experiment 7: Build a B+ tree on the attribute \"numVotes\" (500 Bytes)\n";
    cout << "Experiment 8: Retrieve movies with attribute \"numVotes\" equal to 500 (500 Bytes)\n";
    cout << "Experiment 9: Retrieve movies with attribute \"numVotes\" from 30,000 to 40,000, both inclusively (500 Bytes)\n";
    cout << "Experiment 10: Delete those movies with the attribute \"numVotes\" equal to 1,000 (500 Bytes)"<<endl;
    cout << "Choice: ";

    cin >> choice;
    cout << "================================================================================================================="<<endl;
    while (cin.fail() || choice < 1 || choice > 10 ) {
        cout << "Please insert a valid integer from 1-10!\n";
        cout << "Which experiment result to view? (Type 1-10)\n";
        cin.clear();
        cin.ignore(256,'\n');
        cin >> choice;
    }
    switch(choice){
        case 1:
            cout << "Experiment 1: Store data in disk (100 Bytes)\n";
            database1.addAllRecordsWithNoIndex();
            // database.printBlocks(); //for debugging
            break;
        case 2: 
            cout << "Experiment 2: Build a B+ tree on the attribute \"numVotes\" (100 Bytes)\n";
            database1.addToDiskAndBplus();
            database1.experiment2();
            // database.printTree(); //for debugging
            // database.printLastRowOfPointers();
            // database.printAllRecords();
            // database.printAllRecordsAccordingToIndex();
            break;
        case 3:
            cout<<"Experiment 3: Retrieve movies with attribute \"numVotes\" equal to 500 (100 Bytes)\n";
            database1.addToDiskAndBplus();
            database1.experiment3();
            break;
        case 4:
            cout<<"Experiment 4: Retrieve movies with attribute \"numVotes\" from 30,000 to 40,000, both inclusively (100 Bytes)\n";
            database1.addToDiskAndBplus();
            database1.experiment4();
            break;
        case 5:
            cout<<"Experiment 5: Delete those movies with the attribute \"numVotes\" equal to 1,000 (100 Bytes)"<<endl;
            database1.addToDiskAndBplus();
            database1.experiment5();
            break;
        case 6: 
            cout << "Experiment 6: Store data in disk (500 Bytes)\n";
            database2.addAllRecordsWithNoIndex();
            break;
        case 7:
            cout << "Experiment 7: Build a B+ tree on the attribute \"numVotes\" (500 Bytes)\n";
            database2.addToDiskAndBplus();
            database2.experiment2();
            break;
        case 8:
            cout << "Experiment 8: Retrieve movies with attribute \"numVotes\" equal to 500 (500 Bytes)\n";
            database2.addToDiskAndBplus();
            database2.experiment3();
            break;
        case 9:
            cout << "Experiment 9: Retrieve movies with attribute \"numVotes\" from 30,000 to 40,000, both inclusively (500 Bytes)\n";
            database2.addToDiskAndBplus();
            database2.experiment4();
            break;
        case 10:
            cout << "Experiment 10: Delete those movies with the attribute \"numVotes\" equal to 1,000 (500 Bytes)"<<endl;
            database2.addToDiskAndBplus();
            database2.experiment5();
            break;
        default:
            cout << "Not coded yet";
            break;
    }
    
    return 0;
}


// int main() 
// { 
// //testing for record 
//     Record c=Record("tt00000c	5.3   	1807");
//     Record a=Record("tt00000a	5.3   	1807");
//     Record b=Record("tt00000b	5.3   	1807");
    

//     Block block=Block();
//     //cout<<c.toString();
//     // block.add(a);
//     // block.add(a);
//     // block.add(c);
//     //block.add(b);
//     // block.add(c);
//     //block.deleteSlot(3);
//     // block.deleteSlot(0);
//     // block.deleteSlot(1);
//     // block.deleteSlot(2);
//     // cout<<block.numberSlot;
//     // block.add(a);
    
//     //block.deleteSlot(0);
//     // block.add(c);
//     //block.deleteSlot(1);
//     // block.deleteSlot(0);
//     // //block.deleteSlot(1);
//     // //block.add(c);
//     // //block.add(b);
//     // block.add(a);
//     // block.add(c);
//     //  block.deleteSlot(0);
//     //   block.deleteSlot(1);
//     //    block.deleteSlot(2);
    
//     //  Record d=Record("tt00000d	5.3   	1807");
//     //   block.add(a);
//     //   Record e=Record("tt00000e	5.3   	1807");
//     //   block.add(b);
//     //   block.add(c);
//     //   block.add(d);
//     // block.deleteSlot(0);
//     // block.deleteSlot(1);
//     // block.deleteSlot(2);
//     // block.deleteSlot(3);
//     // block.add(d);
//     // block.add(a);
//     // //cout<<block.numberSlot;
//     // block.deleteSlot(0);
//     // block.deleteSlot(1);
//     // block.add(a);
//     // block.add(d);
//     // block.deleteSlot(0);
//     // block.deleteSlot(1);
//     //  block.add(a);
//     // block.add(d);
//     // block.deleteSlot(0);
//     // block.deleteSlot(1);



//     //block.deleteSlot(0);
//     //block.add(c);
//     // block.deleteSlot(1);
//     // block.deleteSlot(0);
//     // block.add(a);
//     // block.add(c);
//     // block.deleteSlot(1);
//     // block.deleteSlot(0);
//     //block.add(c);
//     //block.add(c);
//     // block.add(c);
//     // block.deleteSlot(0);
//     //  block.deleteSlot(1);
//     // block.add(b);
//     // cout<<block.add(b);
    
//     // cout<<block.add(c);
//     // cout<<block.add(b);
//     // cout<<block.add(b);
//     // cout<<block.add(b);
//     // block.deleteSlot(1);
//     //block.deleteSlot(1);
//      //block.deleteSlot(2);
//      //block.deleteSlot(0);
//     //block.print();
//     //cout<<block.add(c)<<"_______";
//     //cout<<block.getRecord(0).toString();


   
//     //testing for disk
//     Disk d=Disk();
//     d.insert("tt00000a	5.3   	1807");
//     d.insert("tt00001a	5.3   	1807");
//     d.insert("tt00002a	5.3   	1807");
//     d.insert("tt00003a	5.3   	1807");
//     d.insert("tt00004a	5.3   	1807");
//     d.insert("tt00005a	5.3   	1807");
//     d.deleteRecord(0,0);
//     d.deleteRecord(1,1);
//     d.insert("tt00008a	5.3   	1807");
//     d.insert("tt00009a	5.3   	1807");
//     d.insert("tt000010a	5.3   	1807");
//     d.insert("tt000011a	5.3   	1807");
//     d.insert("tt00000a	5.3   	1807");
//     d.deleteRecord(0,0);
//     d.deleteRecord(1,1);
//      d.insert("tt00008a	5.3   	1807");
//     d.insert("tt00009a	5.3   	1807");
//     d.insert("tt000010a	5.3   	1807");
//     d.insert("tt000011a	5.3   	1807");
//     d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     // d.insert("tt00000a	5.3   	1807");
//     //d.blocks[0].deleteSlot(0);
//     //cout<<"__"<<d.getTotalBlocks();
//     //d.printAllRecord();
//     //d.blocks[1].print();
//     //d.blocks[0].deleteSlot(0);
//     //d.blocks[0].print();
//     //cout<<"::::"<<d.blocks[1].numberSlot;
//     d.printAllRecord();
//     // cout<<"size is "<<sizeof(d.blocks[0])*d.getTotalBlocks();

    
//     return 0; 
    
// }
// */
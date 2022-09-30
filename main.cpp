#include <iostream> 
#include <string> 
#include "MemoryPool.cpp"

int main(){
    //100 is the number of bytes for a node
    //The number of keys in a node is calculated like this
    //floor((numBytes-numBytesPerValue)/(numBytesPerKey+numBytesPerValue));
    bool terminate = false;
    int BLOCKSIZE = 0;
    int choice_BLOCKSIZE = 0;
    int choice_experiment = 0;
    

    cout<<"==== start program===="<<endl;
    std :: cout <<"Choose your block size: "<<endl;
    
    while (terminate == false){
            cout <<"1. 200 BYTES"<<endl;
            cout <<"2. 500 BYTES"<<endl;
            cin >> choice_BLOCKSIZE;

            if (choice_BLOCKSIZE == 1)
            {
                BLOCKSIZE = 200;
            }
            else if (choice_BLOCKSIZE == 2)
            {
                BLOCKSIZE = 500;
            }
            else
            {
            cout <<"Invalid choice. Please try again."<<endl;
            cin.clear();
            }
        
        MemoryPool memorypool("tsv_files/data.tsv",BLOCKSIZE);

        cout << "Current block size is " << BLOCKSIZE << " bytes" << endl;
        cout << "View experiment result(1-5): \n";
        cout << "1. Experiment 1: Store data in disk \n";
        cout << "2. Experiment 2: Build a B+ tree on the attribute \"numVotes\" \n";
        cout << "3. Experiment 3: Retrieve movies with attribute \"numVotes\" equal to 500 \n";
        cout << "4. Experiment 4: Retrieve movies with attribute \"numVotes\" from 30,000 to 40,000, both inclusively \n";
        cout << "5. Experiment 5: Delete those movies with the attribute \"numVotes\" equal to 1,000"<<endl;
        cout << "6. Exit the program"<<endl;
        cout << "Enter your choice: ";
        cin >> choice_experiment;
        cout << "================================================================================================================="<<endl;
        
        while (cin.fail() || choice_experiment < 1 || choice_experiment > 6 ) {
            cout << "Invalid choice. Please try again \n";
            cout << "View experiment result(1-5): \n";
            cout << "Enter your choice: ";
            cin.clear();
            cin.ignore(256,'\n');
            cin >> choice_experiment;
        }
        switch(choice_experiment){
            case 1:
                cout << "Experiment 1: Store data in disk for block size "<< BLOCKSIZE << " bytes\n";
                memorypool.insertRecords(BLOCKSIZE);
                // database.printBlocks(); //for debugging
                continue;
            case 2: 
                cout << "Experiment 2: Build a B+ tree on the attribute \"numVotes\" for block size "<< BLOCKSIZE << " bytes\n";
                memorypool.addToDiskAndBplus();
                memorypool.experiment2();
                // database.printTree(); //for debugging
                // database.printLastRowOfPointers();
                // database.printAllRecords();
                // database.printAllRecordsAccordingToIndex();
                continue;
            case 3:
                cout<<"Experiment 3: Retrieve movies with attribute \"numVotes\" equal to 500 for block size "<< BLOCKSIZE << " bytes\n";
                memorypool.addToDiskAndBplus();
                memorypool.experiment3();
                continue;
            case 4:
                cout<<"Experiment 4: Retrieve movies with attribute \"numVotes\" from 30,000 to 40,000, both inclusively for block size "<< BLOCKSIZE << " bytes\n";
                memorypool.addToDiskAndBplus();
                memorypool.experiment4();
                continue;
            case 5:
                cout<<"Experiment 5: Delete those movies with the attribute \"numVotes\" equal to 1,000 for block size "<< BLOCKSIZE << " bytes"<<endl;
                memorypool.addToDiskAndBplus();
                memorypool.experiment5();
                continue;
            
            case 6:
                cout << "Exiting program..."<<endl;
                terminate = true;
                break;
            default:
                cout << "Not coded yet";
                continue;
        }
        
    }
    
    return 0;
}
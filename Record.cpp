#include <iostream>
#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <vector>
#include <string.h>

//Written by LR & ZY
using namespace std;
class Record {       
    public:             
        char tconst[11];     // 10+1
        float avgRating;
        int numVotes;

    Record(string s){
    
    vector<string> tokens;
    istringstream iss(s);
    copy(istream_iterator<string>(iss), istream_iterator<string>(), back_inserter(tokens));

    strcpy(tconst, tokens[0].c_str());
    avgRating=stof(tokens[1]);
    numVotes=stoi(tokens[2]);

    }
    string Tconst(){
            return this->tconst;
        }

    double AvgRating(){
        return this->avgRating;
    }

    int NumberOfVotes(){
        return this->numVotes;
    }

    string toString(){
        ostringstream out;
        out << this->tconst << "\t" << this->avgRating << "\t" << this->numVotes<<"\n";
        return out.str();
    }


        

};

#include <vector>
#include <list>
#include <iterator>
#include <iostream>
#include <string>
#include <sstream>
#include <algorithm>
#include <math.h>

using namespace std;

// https://www.youtube.com/watch?v=kjBI0rimo-w&t=1401s&ab_channel=Mayopepeweezy
// https://www.cs.usfca.edu/~galles/visualization/BPlusTree.html
struct Node
{

    /* data */
    vector<int> keys;
    vector< void*> children;
    bool leaf;
    int fullSize;
    Node* previousLeaf;
    Node* nextLeaf;
    // it is must to store NULL when it is the end 

    // if it is leave, point to iterator in double linkedlist 
    // if it is inner node, point  to the next node. 
    /*
    |*|*|*|      3 keys
    /  \ \ \     4 children
      */
    
    Node(int n)
    {
        fullSize=n;
        leaf=true;    // when it is created it is true;
        previousLeaf=NULL;
        nextLeaf=NULL;
    }

    bool isFull(){
        return (keys.size()>=fullSize);
    }

    int getNumKeys(){
        return keys.size();
    }
    int getNumValues(){
        return children.size();
    }

    int getMiniNoKeys(){
        return floor((this->fullSize+1) / 2);
    }

    //take note for root, it is 1
    int getMinNumValues(){
        //if this is a leaf
        if (leaf){
            return floor((this->fullSize+1)/2);
        } else { //if this is non leaf
            return floor((this->fullSize)/2)+1;
        }
    }

    bool hasMininumValues(){
        return this->getNumValues()>=this->getMinNumValues();
    }

    bool hasExtraValues(){
        return this->getNumValues()>this->getMinNumValues();
    }

    void addToKeys(int key, int index){
        keys.insert(keys.begin() + index , key);
    }

    void addToValues(void * value, int index){
        children.insert(children.begin() + index , value);
    }

    void insertKeysFromOtherNode(Node * otherNode, int startIndex, int endIndex){
        keys.insert(keys.begin(),otherNode->keys.begin()+startIndex, otherNode->keys.begin()+endIndex);
    }

    void eraseKey(int idx) {
        keys.erase(keys.begin()+idx);
    }

    void eraseValue(int idx) {
        children.erase(children.begin()+idx);
    }


    void eraseKeys(int startIndex, int endIndex){
        keys.erase(keys.begin()+startIndex, keys.begin()+endIndex);
    }

    void insertValuesFromOtherNode(Node * otherNode, int startIndex, int endIndex){
        children.insert(children.begin(),otherNode->children.begin()+startIndex, otherNode->children.begin()+endIndex);
    }

    void eraseValues(int startIndex, int endIndex){
        children.erase(children.begin()+startIndex, children.begin()+endIndex);
    }

    void setLeafOrNot(bool leaf){
        this->leaf = leaf;
    }

    void printAllKeys(){
        cout << "|";
        for (auto key : keys){
            cout << key << "|";
        }
        cout << "\t";
    }

    //Meaning no more next leaf node (it's the last of all the leaf nodes)
    bool isTerminalLeafNode(){
        return (nextLeaf==NULL);
    }

    //get next node
    //Eg. [1,3] -> [4, 5] return Node with [4, 5]
    Node * getNextNode(){
        if (isTerminalLeafNode()){
            return NULL;
        }
        else{
            return (Node *) nextLeaf;
        }
    }

    //For actual data 
    void printAllChildren(){
        cout << "|";
        for (int i=0;i<getNumKeys();i++){
            pair<int,int> * pointerToRecord = (pair<int,int> *)children[i];
            cout <<"<" <<pointerToRecord->first<<","<<pointerToRecord->second<<">";
            cout << "|";
        }
        cout << "\t";
    }

    ~Node(){
        for (auto child : children){
            free(child);
        }
    }

};


class bTree
{
    private: 
        Node* _root;
        int degree;
        int totalNode;
        int numOfNodes = 0;
    public:
        

        bTree(int n)
        {   
            _root=NULL;
            degree=n;
            totalNode=0;
        }

        Node * getRoot()
        {
            return _root;
        }

        /*vector<void*> getbyIndex(int i){
            // to some search and return vector of pointer
        }
        */

       void insertToBTree(int key, void * value){
            //Case 1: Empty tree 
            if (_root == NULL){
                _root = createNewLeafNode();
                //add 1 key and 1 child to the new root node
                _root->addToKeys(key,0);
                _root->addToValues(value, 0);
                return;
            }

            //For all other cases, find the leaf node we are inserting into 
            vector<Node *> traversedPath = traversalPathOfInsertion(key);
            Node * nodeToInsertInto = traversedPath.back();
            traversedPath.pop_back();

            //starting from this leaf node
            while (true){ 
                //Case 2: Current node is not full
                if (!nodeToInsertInto->isFull()){
                    int keyIndexToInsertAt = findKeyIndexToInsert(nodeToInsertInto, key);
                    int valueIndexToInsertAt = findValueIndexToInsert(nodeToInsertInto, key);
                    nodeToInsertInto->addToKeys(key, keyIndexToInsertAt);
                    nodeToInsertInto->addToValues(value, valueIndexToInsertAt);
                    break; //stop adding once it has been added to an empty node
                } else {
                    //Case 3: A leaf node is full;
                    if (nodeToInsertInto->leaf){
                        //Split node [1, 2, 3] + 4 -> [1,2] [3, 4]
                        Node * newLeafNode = splitLeafNode(nodeToInsertInto, key, value);

                        key = newLeafNode->keys[0]; //this will be the smallest
                        value = newLeafNode; //Next node to insert
    
                        //if there is no parent (this is root)
                        if (traversedPath.empty()) {
                            Node * parentNode = createNewNonLeafNode(); //no longer leaf
                            parentNode->addToValues(nodeToInsertInto, 0);
                            nodeToInsertInto = parentNode;
                            _root = parentNode;
                        } else {
                            Node * parentNode = traversedPath.back();//get this leaf node's parent
                            traversedPath.pop_back(); 
                            nodeToInsertInto = parentNode;
                        }
                    } 
                    //Case 4: A non-leaf node is full;
                    else { 
                        //Split node [1, 2, 3] + 4 -> [1,2] [3, 4]
                        Node * newNonLeafNode = splitNonLeafNode(nodeToInsertInto, key, value);
                        key = newNonLeafNode->keys[0]; //this will be the smallest (used for root)
                        newNonLeafNode->eraseKeys(0, 1); //Node [1,2] [3, 4] -> Node [1,2] [4]
                        value = newNonLeafNode; //next value to insert
                       
                        
                        //if there is no parent (this is root)
                        if (traversedPath.empty()) {
                            Node * parentNode = createNewNonLeafNode(); //no longer leaf
                            parentNode->addToValues(nodeToInsertInto, 0);
                            nodeToInsertInto = parentNode;
                            _root = parentNode;
                        } else {
                             Node * parentNode = traversedPath.back();//get this non leaf node's parent
                            traversedPath.pop_back(); 
                            nodeToInsertInto = parentNode;
                        }
                    }
                }
            }
       }

        Node * splitLeafNode(Node * oldNode, int key, void * value){
            //Create new leaf node 
            Node * newLeafNode = createNewLeafNode();
            //temporarily insert into the old node (this node will overflow)

            int keyIndexToInsertAt = findKeyIndexToInsert(oldNode, key);     
            int valueIndexToInsertAt = findValueIndexToInsert(oldNode, key);
            oldNode->addToKeys(key, keyIndexToInsertAt);
            oldNode->addToValues(value, valueIndexToInsertAt);
            
            //get index to split (everything at & after the index will be shifted to new node)
            //eg. 1 2 [3 4] (degree=3) then return index=2
            //eg. 1 2 [3 4 5] (degree=4) then return index=2
            //eg. 1 2 3 [4 5 6] (degree=5) then return index=3
            int indexToSplit = floor((degree+1)/2);

            //Populate the new leaf node with [3, 4] and remove [3, 4] from old leaf node
            newLeafNode->insertKeysFromOtherNode(oldNode, 
                                                indexToSplit, 
                                                oldNode->getNumKeys());
            oldNode->eraseKeys(indexToSplit, oldNode->getNumKeys()) ;
            newLeafNode->insertValuesFromOtherNode(oldNode, 
                                                    indexToSplit, 
                                                    oldNode->getNumValues());
            oldNode->eraseValues(indexToSplit, oldNode->getNumValues());          

            // //add the new leaf node's pointer to the end of old leaf node
            // //[1 2] -> [3 4]  old<->new
            // Node * prevNextLeafNode = oldNode->nextLeaf;
            // newLeafNode->previousLeaf=oldNode;
            // oldNode->nextLeaf=newLeafNode;
            // // //[1 2] -> [3 4]  new <-> prevNextNode
            // if (prevNextLeafNode!=NULL){
            //     newLeafNode->nextLeaf = prevNextLeafNode;
            //     prevNextLeafNode->previousLeaf = newLeafNode->previousLeaf;
            // } 
            Node * prevNextLeafNode = oldNode->nextLeaf;
            newLeafNode->previousLeaf=oldNode;
            newLeafNode->nextLeaf=oldNode->nextLeaf;
            if (oldNode->nextLeaf!=NULL) oldNode->nextLeaf->previousLeaf=newLeafNode;
            oldNode->nextLeaf=newLeafNode;


            return newLeafNode;
        }

        //This function splits the values differently than splitLeafNode
        Node * splitNonLeafNode(Node * oldNode, int key, void * value){
            //Create new nonleaf node 
            Node * newNonLeafNode = createNewNonLeafNode();
            //temporarily insert into the old node (this node will overflow)
            
            int keyIndexToInsertAt = findKeyIndexToInsert(oldNode, key);
            int valueIndexToInsertAt = findValueIndexToInsert(oldNode, key);;
            oldNode->addToKeys(key, keyIndexToInsertAt);
            oldNode->addToValues(value, keyIndexToInsertAt+1);
            
            //get index to split (everything at & after the index will be shifted to new node)
            //eg. 1 2 [3 4] (degree=3) then return index=2
            //eg. 1 2 [3 4 5] (degree=4) then return index=2
            //eg. 1 2 3 [4 5 6] (degree=5) then return index=3
            int indexToSplit = floor((degree+1)/2);

            
            //Populate the new leaf node with [3, 4] and remove [3, 4] from old leaf node
            newNonLeafNode->insertKeysFromOtherNode(oldNode, 
                                                indexToSplit, 
                                                oldNode->getNumKeys());
            
            oldNode->eraseKeys(indexToSplit, oldNode->getNumKeys()) ;
            
            newNonLeafNode->insertValuesFromOtherNode(oldNode, 
                                                    indexToSplit+1,  //difference is here
                                                    oldNode->getNumValues());
            oldNode->eraseValues(indexToSplit+1, //difference is here
                            oldNode->getNumValues());
             
            return newNonLeafNode;
        }

        //find index in keys of node to insert into
        int findKeyIndexToInsert(Node * nodeToInsert, int key){
            //compare the key with the keys of the current node
            for (int i=0;i<nodeToInsert->keys.size();i++){
                //imagine keys 2, 3, 5
                //insert 4
                if (nodeToInsert->keys[i] > key){
                    return i;
                }
            }
            //if the key is bigger than all the keys in current node
            //imagine keys 2, 3, 4
            //insert 5
            return (nodeToInsert->getNumKeys());
        }

        //find index in values of node to insert into
        int findValueIndexToInsert(Node * nodeToInsert, int key){
            if (nodeToInsert->leaf){
                //compare the key with the keys of the current node
                for (int i=0;i<nodeToInsert->keys.size();i++){
                    //imagine keys 2, 3, 5
                    //insert 4
                    if (nodeToInsert->keys[i] > key){
                        return i;
                    }
                }
                //if the key is bigger than all the keys in current node
                //imagine keys 2, 3, 4
                //insert 5
                return (nodeToInsert->getNumValues());
            } else {
                for (int i=0;i<nodeToInsert->keys.size();i++){
                    //imagine keys 2, 3, 5
                    //insert 4
                    if (nodeToInsert->keys[i] > key){
                        return i+1;
                    }
                }
                //if the key is bigger than all the keys in current node
                //imagine keys 2, 3, 4
                //insert 5
                return (nodeToInsert->getNumValues());
            }
            
        }

        //vector<Node*> (traversal path to get the parents of all)
        //[root,nonleaf,leaf]
        vector<Node*> traversalPathOfInsertion(int key){
            //traverse the tree downwards until we find the leaf node
                vector <Node*> traversalNodes;
                Node * current_node = _root;
                traversalNodes.push_back(current_node);
                //if it is not a leaf
                while (!current_node->leaf){
                    //compare the key with the keys of the current node
                    for (int i=0;i<current_node->keys.size();i++){
                        //imagine keys 2, 3, 5
                        //insert 4
                        if (current_node->keys[i] > key){
                            //go to the left of the key
                            current_node = (Node *)current_node->children[i]; 
                            break;
                        }
                        //if the key is bigger than all the keys in current node
                        //imagine keys 2, 3, 4
                        //insert 5
                        if (i==current_node->getNumKeys()-1){
                            current_node = (Node *) current_node->children[current_node->getNumValues()-1];
                            break;
                        }
                    }
                    traversalNodes.push_back(current_node);
                }
                return traversalNodes;
        }

        vector<Node*> traversalPathOfDeletion(int key){
            //traverse the tree downwards until we find the leaf node
                vector <Node*> traversalNodes;
                Node * current_node = _root;
                traversalNodes.push_back(current_node);
                // cout << "Traversed Path: ";
                // current_node->printAllKeys();
                //if it is not a leaf
                while(!current_node->leaf){
                    int childrenIndex=upper_bound(current_node->keys.begin(),current_node->keys.end(),key)-current_node->keys.begin();
                    current_node=(Node* )current_node->children[childrenIndex];
                    traversalNodes.push_back(current_node);
                    // current_node->printAllKeys();
                }
                // cout << endl;

                return traversalNodes;
        }

        //bfs print from node
        void printNodeTree(){
            if (_root == NULL){
                cout << "No nodes yet";
                return;
            }
            list<Node *> parent_queue;
            list<Node *> child_queue;
            parent_queue.push_back(_root);
            _root->printAllKeys();
            cout << "\n";
            //bfs
            while (true){
                Node * parent_node = (Node * )parent_queue.front();
                parent_queue.pop_front();
                if (parent_node->leaf){ //stop once we reach the leaf
                    break;
                }
                //for all children in parent node
                for (int j=0;j<parent_node->getNumValues();j++){
                    Node * child_node = (Node * ) parent_node->children[j];
                    child_queue.push_back(child_node);
                    child_node->printAllKeys();
                }
                if (parent_queue.size()==0){
                    parent_queue = child_queue;
                    child_queue.clear();
                    cout << "\n";
                }
                
                
            }
        }

        //To check
        void printLastRow(){
            cout << "printLastRow:\n";
            vector<Node *> traversedPath = traversalPathOfInsertion(-1);
            Node * node = (Node *) traversedPath.back();
            while (true){
                node->printAllKeys();
                if (node->isTerminalLeafNode()){
                    break;
                }
                node = node->getNextNode();
            }
        }

        void printLastRowReverse()
        {
            cout<<"printinglastROw in reverse";
             Node * current_node = _root;

            while(!current_node->leaf)
            {
                
                current_node=(Node* )current_node->children.back();
            }

             while(current_node!=NULL)
            {
                current_node->printAllKeys();
                current_node=current_node->previousLeaf;

            } 
            cout << endl;

        }

        //To check that the leaf node pointers are right
        void printLastRowPointers(){
            cout << "printLastRowPointers:\n";
            vector<Node *> traversedPath = traversalPathOfInsertion(-1);
            Node * node = (Node *) traversedPath.back();
            while (true){
                node->printAllChildren();
                if (node->isTerminalLeafNode()){
                    break;
                }
                node = node->getNextNode();
            }
        }

        vector<void*> returnLastRowPointers(){
            vector<void*> children;
            vector<Node *> traversedPath = traversalPathOfInsertion(-1);
            Node * node = (Node *) traversedPath.back();
            while (true){
                children.insert(children.end(), node->children.begin(), node->children.end());
                if (node->isTerminalLeafNode()){
                    break;
                }
                node = node->getNextNode();
            }
            return children;
        }

        Node * createNewLeafNode(){
            numOfNodes++;
            return (new Node(degree));
        }

        Node * createNewNonLeafNode(){
            numOfNodes++;
            Node * temp = new Node(degree);
            temp->setLeafOrNot(false);
            return (temp);
        }

        Node * deleteNode(Node * node){
            numOfNodes--;
            free(node);
        }

        int getNumberOfNodes(){
            return numOfNodes;
        }
        int getN(){
            return this->degree;
        }

        int getHeight(){
            int height = 1;
            Node * current_node = _root;
            //if it is not a leaf
            while (!current_node->leaf){
                current_node = (Node *)current_node->children[0];
                height++;
            }
            return height;
        }

        ~bTree(){
            delete _root;
        }

         vector<pair<int,int> > search(int numVotes)
        {
            // use of binary search
            // print all the content inside the data blocks, even if the numBVotes is not equal
            // return vector of directory pointer.
            Node * current_node = _root;
            vector<pair<int,int> > result;
            int counterIndex=5;
            int counterData=5;
            int indexNodeNumber=0;
            int dataNodeNumber=0;
            cout<<"Content of top 5 index node: "<<endl;

            while(!current_node->leaf)
            {
                indexNodeNumber+=1;
                if (counterIndex>0){ //first 5
                    current_node->printAllKeys();
                }
                if (counterIndex>0) {counterIndex-=1;}
                int childrenIndex=upper_bound(current_node->keys.begin(),current_node->keys.end(),numVotes)-current_node->keys.begin();
                current_node=(Node* )current_node->children[childrenIndex];
            }
            cout<<"\nTotal number of index nodes: "<<indexNodeNumber<<endl;

            // now reach leaf node
            // keep traversing to the left 23 33 33 33
            //current_node->printAllKeys();
            
            while(current_node!=NULL && current_node->keys[0]==numVotes)
            {
                // current_node->printAllKeys();
                current_node=current_node->previousLeaf;

            } 
            // cout<<"_________________________________________\n";
            

            // current_node->printAllKeys();
            // cout<<"debug______";

            // <999 999 999>   if the last element is not 1000, then current got to the next one
            if (current_node->keys.back()!=numVotes)
            {
                current_node=current_node->nextLeaf;
            }


            while(current_node!=NULL && current_node->keys[0]<=numVotes)
            {
                dataNodeNumber+=1;
                if (counterData>0){
                    // current_node->printAllKeys();
                    // current_node->printAllChildren();
                    counterData-=1;
                }

                for (int i=0;i<current_node->getNumKeys();i++){
                if (current_node->keys[i]==numVotes)
                
                {  
                pair<int,int> pointerToRecord = *(pair<int,int> *)current_node->children[i];
                result.push_back(pointerToRecord);}
        }
            current_node=current_node->nextLeaf;
            }

            

            // cout<<"\nTotal number of data nodes: "<<dataNodeNumber<<endl;
            return result;


        }


        vector<pair<int,int> > searchRange(int lower,int higher)
        {
            // use of binary search
            // print all the content inside the data blocks, even if the numBVotes is not equal
            // return vector of directory pointer.
            Node * current_node = _root;
            vector<pair<int,int> > result;
            int counterIndex=5;
            int counterData=5;
            int indexNodeNumber=0;
            int dataNodeNumber=0;
            cout<<"Content of top 5 index nodes: "<<endl;

            while(!current_node->leaf)
            {
                //current_node->printAllKeys();
                indexNodeNumber+=1;
                if (counterIndex>0) {current_node->printAllKeys();counterIndex-=1;}
                int childrenIndex=upper_bound(current_node->keys.begin(),current_node->keys.end(),lower)-current_node->keys.begin();
                current_node=(Node* )current_node->children[childrenIndex];
            }
            cout<<"Total number of index nodes: "<<indexNodeNumber<<endl;

            // cout<<endl;
            // cout<<"Content of t the dataNode: "<<endl;
            // now reach leaf node
            // keep traversing to the left 23 33 33 33
            //current_node->printAllKeys();
            
            while(current_node!=NULL && current_node->keys[0]==lower)
            {
                //current_node->printAllKeys();
                current_node=current_node->previousLeaf;

            } 
             //current_node->printAllKeys();
            while(current_node!=NULL && current_node->keys[0]<=higher)
            {
                dataNodeNumber+=1;
                if (counterData>0){
                    // current_node->printAllKeys();
                    // current_node->printAllChildren();
                    counterData-=1;
                }

                for (int i=0;i<current_node->getNumKeys();i++){
                if (current_node->keys[i]<=higher && current_node->keys[i]>=lower)
                
                {  
                pair<int,int> pointerToRecord = *(pair<int,int> *)current_node->children[i];
                result.push_back(pointerToRecord);}
        }
            current_node=current_node->nextLeaf;
            }
            cout << endl;
            // cout<<"Total number of data nodes: "<<dataNodeNumber<<endl;
            return result;
        }

        //deletes returned value so that we can delete it from the disk
        pair<int,int> * deleteOneKey(int key, int * counter = nullptr){
            int mergeCounter = 0;

            // cout << "deleted key:"<<key<<endl;
            //traverse all the way to the bottom of the tree where we delete the key
            vector<Node *> traversedPath = traversalPathOfDeletion(key);

            //get the current leaf node we are deleting from
            Node * currentNode = traversedPath.back();
            traversedPath.pop_back();

            //get the parent of the current leaf node we are deleting from
            Node * parentNode = traversedPath.back();
            traversedPath.pop_back();

            //find index to delete in leaf node
            int indexToDelete = getIndexOfKeyInNode(currentNode, key);

            //if the key is found in the leaf node, delete it
            if (indexToDelete!=-1){
                //Deleted value
                pair<int,int> * deletedValue = (pair<int,int> *) currentNode->children[indexToDelete];

                currentNode->eraseKey(indexToDelete);
                currentNode->eraseValue(indexToDelete);
                
                //if the current node is a root, deletion is complete
                if (currentNode == _root){
                    *counter = mergeCounter;
                    return deletedValue;
                } 
                
                //if the current node is not the root, 
                //continue on to check if it is 1 of the 3 cases iteratively (go up the tree)
                while (true){
                    //for the case we just merged the children of the root and the root is now too small
                    Node * leftSibling = NULL; 
                    Node * rightSibling = NULL; 
                    
                    // printNodeTree();
                    // cout << "parentnumvalues" << parentNode->getNumValues()<<endl;
                    // parentNode->printAllKeys();
                    // cout <<endl;
                    // cout << "currentnumvalues" << currentNode->getNumValues()<<endl;
                    // currentNode->printAllKeys();
                    // cout <<endl;

                    //Case 1: The current node is not too small (less than the mininum number of values)
                    if (currentNode->hasMininumValues()){ 
                        //no need to borrow or merge (just fix the indexes)  
                        fixIndexes(parentNode, currentNode);
                    } 
                    //Case 2&3:If current Node is too small move on to case 2 & 3
                    else {
                        
                        //Case 2: Too small but has siblings that can lend 
                        //Case 2a: Left Sibling has extra
                        if (leftSiblingHasExtraValues(parentNode, currentNode)){
                            borrowFromLeftSibling(parentNode, currentNode);
                            fixIndexes(parentNode, currentNode);
                        } 
                        //Case 2b: Right Sibling has extra
                        else if (rightSiblingHasExtraValues(parentNode, currentNode)){
                            
                            borrowFromRightSibling(parentNode, currentNode);
                            fixIndexes(parentNode, currentNode);
                        }
                        //Case 3: Merge the siblings
                        else{
                            
                            //Case 3a: It has a left sibling, merge with left sibling
                            if (hasLeftSibling(parentNode, currentNode)){
                                //if currentNode = 1, it means that the currentNode did not have a right sibling
                                leftSibling = mergeWithLeftSibling(parentNode, currentNode);                                
                                mergeCounter+=1;
                            } 
                            else if (hasRightSibling(parentNode, currentNode)){
                                rightSibling = mergeWithRightSibling(parentNode,currentNode);
                                mergeCounter+=1;
                            }
                            else {
                                cout << "Error: Node should have at least 1 sibling"<<endl;
                            }
                        } 
                        
                    }
                    
                    //If we just merged the children of the root and the root is now too small
                    if (parentNode == _root && parentNode->getNumValues()<2){
                        if (rightSibling!=NULL){
                            _root = rightSibling;
                        } 
                        else if (leftSibling!=NULL){
                            _root = leftSibling;
                        } else {
                            cout << "Error: For root node to become too small, a merging at the nodes before the root should have occured!"<<endl;
                        }
                        *counter = mergeCounter;
                        return deletedValue;
                    }

                    //if the parentNode is already root, stop repairing
                    if (parentNode==_root){
                        *counter = mergeCounter;
                        return deletedValue;
                    }  

                    //Go up the tree
                    //Next current node
                    currentNode = parentNode;
                    //Next parent node to fix
                    parentNode = traversedPath.back();
                    traversedPath.pop_back();

                }


            } else {
                cout << "Key is not found in the tree!"<<endl;
                *counter = mergeCounter;
                return nullptr;
            }

        }

        int getIndexOfKeyInNode(Node * currentNode, int key){
            //iterate through all keys and output the index of key
            for (int i = 0;i<currentNode->getNumKeys();i++){
                if (currentNode->keys[i]==key){
                    return i;
                }
            }
            return -1; //This means we didn't find the key in the node
        }

        int getIndexOfValueInNode(Node * parentNode, Node * currentNode){
            //iterate through all children and output the index of the child
            for (int i = 0;i<parentNode->getNumValues();i++){
                if (parentNode->children[i]==currentNode){
                    return i;
                }
            }
            return -1; //This means we didn't find the child in the node
        }

        int smallestLeafKeyOfRightSubtree(Node * currentNode){
            while (!currentNode->leaf){
                currentNode = (Node *)currentNode->children[0];
            }
            return currentNode->keys[0];
        }

        void fixIndexes(Node * parentNode, Node * currentNode){
            //Fixes the indexes as we go up the tree
            //Get index of key before the pointer pointing to this node
            //eg. |3 | 4| (parent node) 
            //       \
            //        |3|3| (current node) (leaf)
            //(return 0) in this case since 3 is the first key
            int indexOfCurrentNodeInParent = getIndexOfValueInNode(parentNode, currentNode);
            if (indexOfCurrentNodeInParent==-1){
                cout << "Error: Current node cannot be found in parent!" <<endl;
                return;
            }
            //In this case we don't need to fix the key of the parent
            //eg.      |3 | 4| (parent node) 
            //         /
            //    |1|2| (current node) (leaf)
            if (indexOfCurrentNodeInParent==0){
            } 
            //In this case we need to fix the key of the parent
            //eg. |4 | 7| (parent node) (key at index 0)
            //       \
            //        |5|6| (current node) (leaf) (child at index 1)
            else { 
                //in this example this would be: parentNode->keys[0] = 5;
                parentNode->keys[indexOfCurrentNodeInParent-1] = smallestLeafKeyOfRightSubtree(currentNode);
            }  
        }

        bool leftSiblingHasExtraValues(Node * parentNode, Node * currentNode){
            int indexOfCurentNode = getIndexOfValueInNode(parentNode, currentNode);
            
            //if it is the left most child, it cannot borrow from the left sibling
            if (indexOfCurentNode==0){
                return false;
            } 
            //if there is a left sibling and it has extra values, we can borrow
            else if (((Node *)parentNode->children[indexOfCurentNode-1])->hasExtraValues()){
                return true;
            }
            //if there is a left sibling but no extra values, we cannot borrow
            else {
                return false;
            }
        }

        void borrowFromLeftSibling(Node * parentNode, Node * currentNode){
            // cout << "borrowFromLeftSibling";
            int indexOfCurentNode = getIndexOfValueInNode(parentNode, currentNode);
            int indexOfLeftSibling = indexOfCurentNode-1;
            Node * leftSibling = (Node *)parentNode->children[indexOfLeftSibling];
            //if it is the leaf node, borrow in this way
            if (currentNode->leaf){
                // cout << "-leaf"<<endl;
                //transfer the last key and value of the left sibling to the right sibling
                // |1 2 3| |4| -> |1 2| |3 4|
                int lastKey = leftSibling->keys.back();
                void * lastValue = leftSibling->children.back();
                leftSibling->keys.pop_back();
                leftSibling->children.pop_back();

                currentNode->keys.insert(currentNode->keys.begin(), lastKey);
                currentNode->children.insert(currentNode->children.begin(), lastValue);
            } 
            //if it is the non leaf node, borrow in this way
            else {
                // cout << "-nonleaf"<<endl;
                //transfer the last value of the left sibling to the right sibling
                // |1 2| |4| -> |1| |otherKey|
                void * lastValue = leftSibling->children.back();
                leftSibling->keys.pop_back();
                leftSibling->children.pop_back();
                //add in a new key to the start of the current node
                //the value of the key = the smallest key of the first child node
                currentNode->keys.insert(currentNode->keys.begin(), smallestLeafKeyOfRightSubtree((Node *)currentNode->children[0]));
                //insert the child borrow from the left sibling
                currentNode->children.insert(currentNode->children.begin(), lastValue);
            }
        }

        bool rightSiblingHasExtraValues(Node * parentNode, Node * currentNode){
            int indexOfCurentNode = getIndexOfValueInNode(parentNode, currentNode);
            //if it is the right most child, it cannot borrow from the right sibling
            if (indexOfCurentNode==parentNode->getNumValues()-1){
                return false;
            } 
            //if there is a right sibling and it has extra values, we can borrow
            else if (((Node *)parentNode->children[indexOfCurentNode+1])->hasExtraValues()){
                return true;
            }
            //if there is a right sibling but no extra values, we cannot borrow
            else {
                return false;
            }
        }

        void borrowFromRightSibling(Node * parentNode, Node * currentNode){
            // cout << "borrowFromRightSibling";
            int indexOfCurentNode = getIndexOfValueInNode(parentNode, currentNode);
            int indexOfRightSibling = indexOfCurentNode+1;
            Node * rightSibling = (Node *)parentNode->children[indexOfRightSibling];
            //if it is the leaf node, borrow in this way
            if (currentNode->leaf){
                // cout << "-leaf"<<endl;
                //transfer the first key and value of the right sibling to the left sibling
                // |1| |2 3 4| -> |1 2| |3 4|
                int firstKey = rightSibling->keys[0];
                void * firstValue = rightSibling->children[0];
                rightSibling->eraseKey(0);
                rightSibling->eraseValue(0);

                currentNode->keys.push_back(firstKey);
                currentNode->children.push_back(firstValue);

                //we also have to fix the index of this rightsibling
                fixIndexes(parentNode, rightSibling);
            }
            //if this is not a leaf, borrow in this way 
            //eg.                      |7|14|
            //       |5|               |10|12|              |16|
            // |1|2|6|         |7|8|9| |10|11| |12|13| |14|15| |16|17|
            else{
                // cout << "-nonleaf"<<endl;
                //transfer the first value of the right sibling to the currentNode
                // |5| |10 12| -> |5| |12|
                void * rightValue = rightSibling->children[0];
                rightSibling->eraseValue(0);
                rightSibling->eraseKey(0);
                currentNode->children.push_back(rightValue);
                //fix the tree
                //|5| |12| --> |7| |12|
                fixIndexes(currentNode, (Node *)currentNode->children[currentNode->getNumValues()-1]);
                //Parent's key needs to be changed
                //eg.       parent --> |7|14|
                // current--> |7|              |12|           |16|
                // |1|2|6|       |7|8|9| |10|11| |12|13| |14|15| |16|17| 
                fixIndexes(parentNode, rightSibling);
            }
        }

        bool hasLeftSibling(Node * parentNode, Node * currentNode){
            int indexOfCurrentNode = getIndexOfValueInNode(parentNode, currentNode);
            //if it is not the left most child, it has a left sibling
            if (indexOfCurrentNode>0){
                return true;
            }
            return false;
        }

        bool hasRightSibling(Node * parentNode, Node * currentNode){
            int indexOfCurrentNode = getIndexOfValueInNode(parentNode, currentNode);
            //if it is not the right most child, it has a right sibling
            if (indexOfCurrentNode<parentNode->getNumValues()-1){
                return true;
            }
            return false;
        }

        //give back the left sibling (for case when parent is root that's small)
        Node * mergeWithLeftSibling(Node * parentNode, Node * currentNode){
            // cout << "mergeWithLeftSibling";
            int indexOfCurentNode = getIndexOfValueInNode(parentNode, currentNode);
            int indexOfLeftSibling = indexOfCurentNode-1;
            Node * leftSibling = (Node *)parentNode->children[indexOfLeftSibling];
            
            if (currentNode->leaf){
                // cout << "-leaf";
                //add all from currentNode to left sibling
                leftSibling->keys.insert(leftSibling->keys.end(), currentNode->keys.begin(), currentNode->keys.end());
                leftSibling->children.insert(leftSibling->children.end(), currentNode->children.begin(), currentNode->children.end());
                //if currentNode is a leaf, we need to connect left sibling with currentNode's previous right sibling
                // eg |1 2|<->||<->|5 6|  --> |1 2|<->|5 6|
                //|1 2|->|5 6|
                Node * nextLeafOfCurrentNode =currentNode->nextLeaf;
                leftSibling->nextLeaf = nextLeafOfCurrentNode;
                //if it is a terminal leaf node, nextLeafOfCurrent would be NULL
                if (!currentNode->isTerminalLeafNode()){
                    //|1 2|<-|5 6|
                    nextLeafOfCurrentNode->previousLeaf = leftSibling;
                }
                //remove the current node itself
                parentNode->eraseValue(indexOfCurentNode);
                deleteNode(currentNode);
                //remove extra keys
                //In this case, (num values of parent -1) = 2-1=1
                //eg.                 |7|
                //      remove this key--> |3|5|    |10|
                // |1|2|4|   |5|6|             |7|8|9| |10|11|12|
                parentNode->eraseKey(indexOfLeftSibling);
                //eg.                 |7|
                //        |5| <--change this key   |10|
                // |1|2|4|   |5|6|             |7|8|9| |10|11|12|
                // cout << endl;
                return leftSibling;
            } 
            //if currentNode is a nonleaf node, we need to fix the first key of currentNode
            //eg.          |20|
            //      |7|                || <--fix this
            //  |1|4| |7|10| |20|21|25|
            else {
                // cout << "-nonleaf";
                //eg.                          |7|14|
                //       |7|10|12| | <-- add in a key
                // |1|2|6|   |7|8|9| |10|11| |12|13| |14|15|17|
                //eg.                          |7|14|
                //       |7|10|12|14| <-- add in a key
                // |1|2|6|   |7|8|9| |10|11| |12|13| |14|15|17|
                leftSibling->keys.push_back(smallestLeafKeyOfRightSubtree((Node *)currentNode->children[0]));
                //add all from currentNode to left sibling
                leftSibling->keys.insert(leftSibling->keys.end(), currentNode->keys.begin(), currentNode->keys.end());
                leftSibling->children.insert(leftSibling->children.end(), currentNode->children.begin(), currentNode->children.end());
                //erase current node and key from the parent node
                parentNode->eraseValue(indexOfCurentNode);
                deleteNode(currentNode);
                parentNode->eraseKey(indexOfLeftSibling);

                // cout << endl;
                return leftSibling;
            }
        }

        Node * mergeWithRightSibling(Node * parentNode, Node * currentNode){
            // cout << "mergeWithRightSibling";
            int indexOfCurrentNode = getIndexOfValueInNode(parentNode, currentNode);
            
            int indexOfRightSibling = indexOfCurrentNode+1;
            Node * rightSibling = (Node *)parentNode->children[indexOfRightSibling];

            if (currentNode->leaf){
                // cout << "-leaf"<<endl;
                //add all right sibling keys and values into current node
                currentNode->keys.insert(currentNode->keys.end(), rightSibling->keys.begin(), rightSibling->keys.end());
                currentNode->children.insert(currentNode->children.end(), rightSibling->children.begin(), rightSibling->children.end());
                //since currentNode is a leaf
                //right sibling's next node should now be connected to current node
                // eg currentNode <-> rightSibling <-> right right sibling
                // --> currentNode <-> right right sibling
                //|1 2|->|5 6|
                Node * rightRightSibling = rightSibling->nextLeaf;
                currentNode->nextLeaf = rightRightSibling;
                //if right sibling is a terminal node, rightRightSibling == NULL
                if (!rightSibling->isTerminalLeafNode()){
                    rightRightSibling->previousLeaf = currentNode;
                }
                //remove the right sibling
                parentNode->eraseValue(indexOfRightSibling);
                deleteNode(rightSibling);
                //remove extra key
                parentNode->eraseKey(indexOfRightSibling-1);
                return currentNode;
            } 
            else{
                // cout << "-nonleaf"<<endl;
                int smallestLeafKeyOfRightSibling = smallestLeafKeyOfRightSubtree(rightSibling);
                currentNode->keys[currentNode->getNumKeys()-1] = smallestLeafKeyOfRightSibling;
                //add all right sibling keys and values into current node
                currentNode->keys.insert(currentNode->keys.end(), rightSibling->keys.begin(), rightSibling->keys.end());
                currentNode->children.insert(currentNode->children.end(), rightSibling->children.begin(), rightSibling->children.end());
                //remove the right sibling
                parentNode->eraseValue(indexOfRightSibling);
                deleteNode(rightSibling);
                //remove extra key
                // parentNode->eraseKey(indexOfRightSibling-1);
                return currentNode;
            }

        }

        int getNumberOfKeysToDelete(int numVotes){
            // use of binary search
            // print all the content inside the data blocks, even if the numBVotes is not equal
            // return vector of directory pointer.
            Node * current_node = _root;
            int counter =0;
            while(!current_node->leaf){
                int childrenIndex=upper_bound(current_node->keys.begin(),current_node->keys.end(),numVotes)-current_node->keys.begin();
                current_node=(Node* )current_node->children[childrenIndex];
            }
            // now reach leaf node
            // keep traversing to the left 23 33 33 33
            //current_node->printAllKeys();
            while(current_node!=NULL && current_node->keys[0]==numVotes){
                current_node=current_node->previousLeaf;
            } 
            while(current_node!=NULL && current_node->keys[0]<=numVotes){
                for (int i=0;i<current_node->getNumKeys();i++){
                    if (current_node->keys[i]==numVotes){  
                        counter+=1;
                    }
                }
                current_node=current_node->nextLeaf;
            }
            return counter;
        }
};



/*
int main()
{
    pair<int,int> a= make_pair(1, 1);
    pair<int,int> b= make_pair(1, 2);
    pair<int,int> c= make_pair(1, 3);
    pair<int,int> d= make_pair(1, 4);
    bTree tree=bTree(3);

    tree.insertToBTree(1,&a);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;
    tree.insertToBTree(4,&a);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;

    tree.insertToBTree(7,&b);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;
    tree.insertToBTree(10,&b);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;

    tree.insertToBTree(20,&b);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;
    tree.insertToBTree(21,&b);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;
    tree.insertToBTree(25,&b);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;
    tree.insertToBTree(31,&c);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;


    cout<<"deletion test now";

    tree.deleteOneKey(4);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;

        tree.deleteOneKey(10);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;

    tree.deleteOneKey(20);
    tree.printNodeTree();
    tree.printLastRowReverse();
    cout<<endl;



    // tree.insertToBTree(14,&c);
    // tree.printNodeTree();
    // tree.printLastRowReverse();
    // cout<<endl;





// }
*/

// int main()
// {
//     pair<int,int> a= make_pair(1, 1);
//     pair<int,int> b= make_pair(1, 2);
//     pair<int,int> c= make_pair(1, 3);
//     pair<int,int> d= make_pair(1, 4);
//     bTree tree=bTree(4);

//     for (int i=1;i<19;i++){
//         tree.insertToBTree(i, &b);
//     }
//     tree.printNodeTree();
//     // tree.printLastRowReverse();

//     tree.deleteOneKey(12);
//     tree.printNodeTree();
//     // tree.printLastRowReverse();

//     tree.deleteOneKey(15);
//     tree.printNodeTree();
//     // tree.printLastRowReverse();

//     tree.deleteOneKey(16);
//     tree.printNodeTree();

//      tree.deleteOneKey(14);
//     tree.printNodeTree();

//     tree.deleteOneKey(13);
//     tree.printNodeTree();

//     tree.deleteOneKey(11);
//     tree.printNodeTree();

//     tree.deleteOneKey(10);
//     tree.printNodeTree();
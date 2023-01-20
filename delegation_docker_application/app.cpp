#include "json.hpp"
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <stdlib.h>
#include <stdio.h>
#include <sys/time.h>
#include <ctime>

using namespace std;

int main()
{
    ifstream ramJson("testRAM.json");
    ifstream compJson("testOper.json");
    ifstream ioJson("testIO.json");
    stringstream ramBuffer, compBuffer, ioBuffer;
    ramBuffer << ramJson.rdbuf();
    compBuffer << compJson.rdbuf();
    ioBuffer << ioJson.rdbuf();
    auto ramStat = nlohmann::json::parse(ramBuffer.str());
    auto compStat = nlohmann::json::parse(compBuffer.str());
    auto ioStat = nlohmann::json::parse(ioBuffer.str());
    //auto json = nlohmann::json::parse(buffer.str());



    //string type = json["type"];
    string ramValue = ramStat["value"];
    string compValue = compStat["value"];
    string ioValue = ioStat["value"];
    
    //cout << "\nType of instruction: " << type << "\n";
    //cout << "\nValue of instruction: " << value << "\n";

    //if(type=="RAM"){
    cout << "Taking up RAM" << endl;
    
    int size = std::stoi(ramValue);

    size_t sz = size*1000000; //we set size it in MB unit
    cout << sz << "\n";
    char *a = (char*)malloc(sz);
    memset(a, 'a', sz); // put 'a' into 4GB
    printf("%.4s", &a[sz-5]);
    //}

    while(true){
    
    time_t now = time(nullptr);

    //if(type=="Operation"){
    cout << "Executing comptational operations" << endl;

    string opeType = compStat["opeType"];
    
    int times = std::stoi(compValue);
    int n=1;

    for(int i=0; i<times; i++){
        cout << "the operation is: " << opeType << endl;
        float f = static_cast <float> (remainder(rand(), 1000.0) + 1.0);
        // multiplication
        if(opeType=="add"){
            n+=f;
        }
        // substraction
        if(opeType=="sub"){
            n-=f;
        }
        // multiplication
        if(opeType=="mut"){
            n*=f;
        }
        // division
        if(opeType=="div"){
            n/=f;
        }
    }
    //}

    //if(type=="IO"){
    cout << "Executing I/O" << endl;

    string ioType = ioStat["IOType"];
    
    times = std::stoi(ioValue);
    n=1;

    cout << "test for: " << ioType << endl;

    
        // input a file
        if(ioType=="in"){
            string line;
            ifstream infile ("in.txt");
            if (infile.is_open())
            {
                for(int i=0; i<times; i++){
                    (getline (infile,line));
                    // cout << line << '\n';
                }
                infile.close();
            }

            else cout << "Unable to open file"; 
        }
        // output a file
        if(ioType=="out"){
            ofstream outfile ("out.txt");
            if (outfile.is_open())
            {
                for(int i=0; i<times; i++){
                    outfile << "This is a line.\n";
                }
                outfile.close();
            }
            else cout << "Unable to open file";
        }
        time_t now_2 = time(nullptr);
        while ((now_2 - now) < 1){
            now_2 = time(nullptr);
        }
    }
    //}   

    return 0;
}


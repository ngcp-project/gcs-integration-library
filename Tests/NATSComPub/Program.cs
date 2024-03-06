using System;
using NATSCommandsPub;

namespace NATS_Pub_Test
{
    public class Program
    {
        static void Main(string[] args)
        {
            //Creating the publisher
            CommandsNATS publisher = new CommandsNATS();
            
            //Setting up the features
            publisher.setup_NATS("foo","10.110.246.119");


            while (true){

                Console.WriteLine("Enter command:");
                string command = Console.ReadLine();
                if (command == "exit"){
                    break;
                }
                else{
                    publisher.publish_NATS(command);
                }
            }

        }
    }
}
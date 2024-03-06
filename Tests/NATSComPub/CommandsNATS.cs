using System;
using System.Text;
using NATS.Client;

namespace NATSCommandsPub
{
    public class CommandsNATS
    {
        //Creating the variables
        public string node_name;
        public string natsUrl;

        public IConnection connection;
        public void setup_NATS(string node_name, string ipv4)
        
        {
            try{
                //Setting the NATS URL and node name
                this.natsUrl = "nats://" + ipv4 + ":4222";
                this.node_name = node_name;
                Options opts = ConnectionFactory.GetDefaultOptions();
                opts.Url = natsUrl;

                //Connecting to the connection Factory
                ConnectionFactory cf = new ConnectionFactory();
                this.connection = cf.CreateConnection(opts);
                Console.WriteLine("Sucessfully connected to: " + this.natsUrl);
            }
            catch {
                Console.WriteLine("Failed To Connect to: " + this.natsUrl);
            }

        }
        
        //Method used to publish commands
        public void publish_NATS(string command)
        {
            this.connection.Publish("foo", Encoding.UTF8.GetBytes(command));
            Console.WriteLine("Message succesfully sent");

        }
    }
}


using System;
using System.Text;
using NATS.Client;

namespace NATSTelemetrySub{
    public class TelemetryNATS{
        public static void setup_NATS(String node_name){

            //Use if want to setup as an environment variable
            string natsUrl = Environment.GetEnvironmentVariable("NATS_URL");

            //Using a set one if not existenet, MUST EXPOSE THE PORT USING DOCKER
            if (natsUrl == null)
            {
                natsUrl = "nats://127.0.0.1:4222";
            }

            //Creating new connection factory
            Options opts = ConnectionFactory.GetDefaultOptions();
            opts.Url = natsUrl;

            //Creating the connection to the nats Server
            ConnectionFactory cf = new ConnectionFactory();
            
            try{
                IConnection c = cf.CreateConnection(opts);
                Console.WriteLine("Succesfully Connected to: "+ natsUrl);
                //Creating the message handler
                EventHandler<MsgHandlerEventArgs> handler = (sender, args) =>
                {
                    Msg m = args.Message;
                    string text = Encoding.UTF8.GetString(m.Data);
                    Console.WriteLine($"Async handler received the message '{text}' from subject '{m.Subject}'");
                    Thread.Sleep(1000);
                };

                //Creating the Subscriber
                IAsyncSubscription subAsync = c.SubscribeAsync("foo", handler);
                Console.WriteLine(subAsync);
                //Using a while loop to keep the programming running whilst subAsync recieves messages
                while (true){
                    string prompt = Console.ReadLine();
                    if (prompt == "exit"){
                        break;
                    }
                }
            } 
            catch (Exception e) {
                Console.WriteLine("Connection Failed: Closing...");
                System.Environment.Exit(1);
            }
        }

    }
}


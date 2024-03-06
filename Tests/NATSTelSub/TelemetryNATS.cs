using System;
using System.Text;
using NATS.Client;

namespace NATSTelemetrySub
{
    public class TelemetryNATS
    {
        public static void setup_NATS(string node_name, Action<string> messageCallback)
        {
            // Use if want to setup as an environment variable
            string natsUrl = Environment.GetEnvironmentVariable("NATS_URL");

            // Using a set one if not existent, MUST EXPOSE THE PORT USING DOCKER
            if (natsUrl == null)
            {
                natsUrl = "nats://127.0.0.1:4222";
            }

            // Creating new connection factory
            Options opts = ConnectionFactory.GetDefaultOptions();
            opts.Url = natsUrl;

            // Creating the connection to the NATS Server
            ConnectionFactory cf = new ConnectionFactory();

            // Checking connection to the publisher
            try
            {
                IConnection c = cf.CreateConnection(opts);
                Console.WriteLine("Successfully Connected to: " + natsUrl);

                // Creating the message handler
                EventHandler<MsgHandlerEventArgs> handler = (sender, args) =>
                {
                    Msg m = args.Message;
                    string text = Encoding.UTF8.GetString(m.Data);
                    messageCallback?.Invoke(text); // Invoke the callback with the received message
                };

                // Creating the Subscriber
                IAsyncSubscription subAsync = c.SubscribeAsync("foo", handler);

                // Wait for exit command
                while (true)
                {
                    string prompt = Console.ReadLine();
                    if (prompt == "exit")
                    {
                        break;
                    }
                }
            }
            catch (Exception e)
            {
                Console.WriteLine("Connection Failed: Closing...");
                System.Environment.Exit(1);
            }
        }
    }
}



using System;
using NATSTelemetrySub;

namespace NATS_Sub_Test
{
    public class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Running");

            // Define a callback function to handle the received message
            Action<string> messageCallback = (message) =>
            {
                Console.WriteLine("Received message: " + message);
                // You can perform any logic here using message
            };

            // Starting the subscriber
            try{
                TelemetryNATS.setup_NATS("foo", messageCallback);
            }
            catch {
                Console.WriteLine("Something Failed: Terminating Program");
            }
        }
    }
}


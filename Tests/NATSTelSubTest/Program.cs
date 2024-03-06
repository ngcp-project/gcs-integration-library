using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using NATSTelemetrySub;

namespace NATS_Sub_Test
{
    public class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Running");
            TelemetryNATS.setup_NATS("foo","127.0.0.1");

        }
    }
}

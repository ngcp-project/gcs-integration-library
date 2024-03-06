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
            //TelemetryNATS.setup_NATS("foo", "10.110.246.119");
            
            //Default Server if you want to use within the computer 
            TelemetryNATS.setup_NATS("foo");

        }
    }
}

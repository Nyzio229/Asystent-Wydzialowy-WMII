using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class KeyResponse
    {
        [JsonProperty("apiKey")]
        public string ApiKey { get; set; }
    }
}

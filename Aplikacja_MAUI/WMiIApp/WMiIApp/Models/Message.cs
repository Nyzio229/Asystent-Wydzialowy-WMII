using System.Text.Json.Serialization;

namespace WMiIApp.Models
{
    public class Message
    {
        public string Content { get; set; }
        public string Role { get; set; }
        public bool IsSent { get; set; }
    }

    [JsonSerializable(typeof(Message))]
    internal sealed partial class MessageContext : JsonSerializerContext
    {

    }
}
